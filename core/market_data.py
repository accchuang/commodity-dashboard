"""
Market data providers.

TqsdkProvider  — live data via tqsdk (requires credentials).
DemoProvider    — simulated data with realistic random-walk behaviour.

Both expose the same interface: async run(store, instruments, settings).
"""

import asyncio
import inspect
import logging
import math
import random
import time
from abc import ABC, abstractmethod
from typing import Dict, List

from config.instruments import Instrument, build_tqsdk_id
from config.settings import AppSettings
from core.data_store import DataStore, Quote

logger = logging.getLogger(__name__)


# ── Abstract base ───────────────────────────────────────────────────

class BaseProvider(ABC):
    @abstractmethod
    async def run(self, store: DataStore, instruments: List[Instrument], settings: AppSettings) -> None:
        """Continuously fetch / generate data and push to the DataStore."""
        ...


# ── Tqsdk provider ──────────────────────────────────────────────────

# Kline periods used for OI change bars
OI_KLINE_PERIODS = {
    "15m": 900,     # 15 minutes
    "30m": 1800,    # 30 minutes
    "1h": 3600,     # 1 hour
    "7h": 25200,    # 7 hours
    # "18h": 64800,   # 18 hours
}
OI_NUM_BARS = 60  # enough for MACD computation (need >= 35), first 7 used for UI bars


def _extract_oi_bars(kl) -> list:
    """Extract the last 7 OI-change bars from a kline serial.

    Each bar = ``close_oi - open_oi``.  Pads with zeros if fewer than
    *OI_NUM_BARS* bars are available yet.
    """
    n = len(kl)
    if n == 0:
        return None
    bars = []
    start = max(0, n - OI_NUM_BARS)
    for i in range(start, n):
        bar = kl.iloc[i]
        bars.append(int(bar.close_oi - bar.open_oi))
    while len(bars) < OI_NUM_BARS:
        bars.insert(0, 0)
    return bars


def _extract_price_bars(kl) -> list:
    """Extract the last 7 price-change bars from a kline serial.

    Each bar = ``close - open``.  Pads with zeros if fewer than
    *OI_NUM_BARS* bars are available yet.
    """
    n = len(kl)
    if n == 0:
        return None
    bars = []
    start = max(0, n - OI_NUM_BARS)
    for i in range(start, n):
        bar = kl.iloc[i]
        bars.append(float(bar.close - bar.open))
    while len(bars) < OI_NUM_BARS:
        bars.insert(0, 0.0)
    return bars


class TqsdkProvider(BaseProvider):
    """Real-time market data from tqsdk — quotes + kline-based OI bars."""

    @staticmethod
    def _is_valid_quote(q: any) -> bool:
        lp = getattr(q, "last_price", float("nan"))
        ps = getattr(q, "pre_settlement", float("nan"))
        return (
            not math.isnan(lp) and lp > 0
            and not math.isnan(ps) and ps > 0
        )

    @staticmethod
    async def _wait_update(api, deadline=None) -> None:
        try:
            if inspect.iscoroutinefunction(api.wait_update):
                await asyncio.wait_for(api.wait_update(deadline=deadline), timeout=(deadline or 10) + 2)
            else:
                loop = asyncio.get_running_loop()
                await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: api.wait_update(deadline=deadline)),
                    timeout=(deadline or 10) + 2,
                )
        except asyncio.TimeoutError:
            logger.debug("wait_update timed out")

    async def run(self, store: DataStore, instruments: List[Instrument], settings: AppSettings) -> None:
        try:
            from tqsdk import TqApi, TqAuth
        except ImportError:
            logger.error("tqsdk not installed. Run: pip install tqsdk")
            return

        ins_ids = [build_tqsdk_id(inst) for inst in instruments]
        id_to_inst = dict(zip(ins_ids, instruments))

        while True:
            api = None
            quotes = {}
            klines = {}
            oi_cache = {}
            price_cache = {}
            try:
                api = TqApi(auth=TqAuth(settings.tqsdk.username, settings.tqsdk.password))

                # Subscribe to quotes
                for ins_id in ins_ids:
                    try:
                        quotes[ins_id] = api.get_quote(ins_id)
                    except Exception:
                        pass  # retry once below

                logger.info("TqsdkProvider: %d quotes subscribed", len(quotes))

                # Subscribe to klines — use executor to avoid blocking the event loop
                loop = asyncio.get_running_loop()
                for ins_id in list(quotes.keys()):
                    klines[ins_id] = {}
                    for period_name, dur_sec in OI_KLINE_PERIODS.items():
                        try:
                            klines[ins_id][period_name] = await asyncio.wait_for(
                                loop.run_in_executor(
                                    None,
                                    lambda i=ins_id, d=dur_sec: api.get_kline_serial(i, duration_seconds=d, data_length=OI_NUM_BARS),
                                ),
                                timeout=5,
                            )
                        except (asyncio.TimeoutError, Exception):
                            logger.debug("Kline not available for %s @ %s", ins_id, period_name)

                kline_count = sum(1 for kl_map in klines.values() for _ in kl_map)
                logger.info("TqsdkProvider: %d kline series subscribed", kline_count)

                # Wait for initial data with hard timeout
                try:
                    for i in range(20):
                        await asyncio.wait_for(
                            self._wait_update_inner(api),
                            timeout=5,
                        )
                        valid_now = sum(1 for q in quotes.values() if self._is_valid_quote(q))
                        if valid_now >= max(1, len(quotes) * 0.3):
                            logger.info("TqsdkProvider: got %d valid quotes after %d ticks", valid_now, i + 1)
                            break
                except asyncio.TimeoutError:
                    logger.warning("TqsdkProvider: initial wait timed out, pushing partial data")

                # Initial push — push whatever we have (even invalid quotes get pushed as-is)
                valid_count = 0
                for ins_id, q in quotes.items():
                    quote = Quote.from_tqsdk(ins_id, q)
                    oi_bars = self._build_oi_bars(ins_id, klines)
                    if oi_bars:
                        quote.oi_bars = oi_bars
                        oi_cache[ins_id] = oi_bars
                    price_bars = self._build_price_bars(ins_id, klines)
                    if price_bars:
                        quote.price_bars = price_bars
                        price_cache[ins_id] = price_bars
                    await store.update(ins_id, quote)
                    if quote.is_valid:
                        valid_count += 1
                await store.notify()
                logger.info("TqsdkProvider: initial push done (%d valid / %d total)", valid_count, len(quotes))

                # Stream loop
                while True:
                    try:
                        await asyncio.wait_for(
                            self._wait_update_inner(api),
                            timeout=15,
                        )
                    except asyncio.TimeoutError:
                        pass
                    changed = False
                    for ins_id, q in quotes.items():
                        oi_bars = self._build_oi_bars(ins_id, klines)
                        oi_changed = oi_bars and oi_bars != oi_cache.get(ins_id)
                        price_bars = self._build_price_bars(ins_id, klines)
                        price_changed = price_bars and price_bars != price_cache.get(ins_id)

                        try:
                            is_changing = api.is_changing(q)
                        except Exception:
                            is_changing = False

                        if is_changing or oi_changed or price_changed:
                            quote = Quote.from_tqsdk(ins_id, q)
                            if oi_bars:
                                quote.oi_bars = oi_bars
                                oi_cache[ins_id] = oi_bars
                            elif ins_id in oi_cache:
                                quote.oi_bars = oi_cache[ins_id]
                            if price_bars:
                                quote.price_bars = price_bars
                                price_cache[ins_id] = price_bars
                            elif ins_id in price_cache:
                                quote.price_bars = price_cache[ins_id]
                            await store.update(ins_id, quote)
                            changed = True
                    if changed:
                        await store.notify()

            except Exception as exc:
                logger.error("TqsdkProvider error: %s — reconnecting ...", exc, exc_info=True)
            finally:
                if api:
                    try:
                        api.close()
                    except Exception:
                        pass
                quotes.clear()
                klines.clear()
                oi_cache.clear()
                price_cache.clear()

    @staticmethod
    async def _wait_update_inner(api) -> None:
        """Thin wrapper that works with both sync and async wait_update."""
        if inspect.iscoroutinefunction(api.wait_update):
            await api.wait_update()
        else:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, api.wait_update)

    @staticmethod
    def _build_oi_bars(ins_id: str, klines: dict) -> dict | None:
        """Build oi_bars dict for one instrument.  Returns None if no kline data."""
        kl_map = klines.get(ins_id, {})
        if not kl_map:
            return None
        result = {}
        for period_name in OI_KLINE_PERIODS:
            kl = kl_map.get(period_name)
            if kl is None:
                continue
            bars = _extract_oi_bars(kl)
            if bars is not None:
                result[period_name] = bars
        return result if result else None

    @staticmethod
    def _build_price_bars(ins_id: str, klines: dict) -> dict | None:
        """Build price_bars dict for one instrument.  Returns None if no kline data."""
        kl_map = klines.get(ins_id, {})
        if not kl_map:
            return None
        result = {}
        for period_name in OI_KLINE_PERIODS:
            kl = kl_map.get(period_name)
            if kl is None:
                continue
            bars = _extract_price_bars(kl)
            if bars is not None:
                result[period_name] = bars
        return result if result else None


# ── Demo provider ───────────────────────────────────────────────────

class DemoProvider(BaseProvider):
    """Generates realistic simulated quotes for testing / demo."""

    def __init__(self):
        self._seeds: Dict[str, dict] = {}

    async def run(self, store: DataStore, instruments: List[Instrument], settings: AppSettings) -> None:
        cfg = settings.demo
        self._init_seeds(instruments, store)

        logger.info("DemoProvider: simulating %d instruments (tick=%.1fs)",
                     len(instruments), cfg.tick_interval)

        while True:
            await asyncio.sleep(cfg.tick_interval)
            for inst in instruments:
                ins_id = build_tqsdk_id(inst)
                seed = self._seeds[inst.code]
                quote = self._tick(ins_id, seed, cfg)
                await store.update(ins_id, quote)
            await store.notify()

    def _init_seeds(self, instruments: List[Instrument], store: DataStore) -> None:
        # Approximate real-world base prices for plausible simulation
        base_prices = {
            # ferrous
            "rb": 3700, "hc": 3850, "wr": 3800, "ss": 14000,
            "i": 780, "jm": 1350, "j": 2100,
            "SM": 6500, "SF": 6700, "FG": 1600, "SA": 1800,
            # energy (SHFE)
            "ru": 14500, "br": 13000, "bu": 3800, "fu": 3200, "sp": 5800,
            # energy (INE)
            "sc": 580, "lu": 4000,
            # energy (DCE)
            "l": 8000, "pp": 7500, "v": 5900, "eg": 4200, "eb": 8500, "pg": 4500,
            # energy (CZCE)
            "TA": 5200, "MA": 2450, "UR": 2100, "PF": 7200, "SH": 2700, "PX": 8000,
            # nonferrous
            "cu": 68500, "al": 19200, "zn": 21500, "pb": 15800, "ni": 135000,
            "sn": 220000, "ao": 3200, "au": 520, "ag": 6800, "bc": 68000,
            # agri (DCE)
            "m": 3400, "a": 4800, "b": 4200, "y": 8000, "p": 7600,
            "c": 2500, "cs": 2900, "rr": 3500, "jd": 4200, "lh": 16000,
            "fb": 1300, "bb": 180,
            # agri (CZCE)
            "RM": 2800, "OI": 8800, "RS": 5200, "PK": 9000,
            "SR": 6200, "CF": 15800, "CY": 22000,
            "AP": 7500, "CJ": 11000,
            "WH": 2800, "PM": 2500, "RI": 2700, "LR": 2700, "JR": 2900,
            # newenergy
            "lc": 120000, "si": 14000,
            # financial (CFFEX)
            "IF": 3800, "IC": 5500, "IH": 2600, "IM": 5800,
            "TS": 101, "TF": 102, "T": 100, "TL": 99,
        }
        for inst in instruments:
            base = base_prices.get(inst.code, 5000)
            self._seeds[inst.code] = {
                "base": base,
                "price": base + (random.random() - 0.5) * base * 0.02,
                "trend": (random.random() - 0.5) * 0.02,
            }

    def _tick(self, ins_id: str, seed: dict, cfg) -> Quote:
        base = seed["base"]
        price = seed["price"]
        trend = seed["trend"]

        # Mean-reverting random walk
        drift = (base - price) * 0.001 + (random.random() - 0.48) * base * cfg.max_change_pct * 0.2
        new_price = price + drift + trend * base

        # Update persistent trend
        seed["trend"] = trend * cfg.trend_persistence + (random.random() - 0.5) * 0.002
        seed["trend"] = max(-0.03, min(0.03, seed["trend"]))
        seed["price"] = new_price

        tick = round(new_price * 2) / 2
        day_range = base * (0.005 + random.random() * 0.025)
        high = round((tick + random.random() * day_range) * 2) / 2
        low = round((tick - random.random() * day_range) * 2) / 2
        open_ = round((low + random.random() * (high - low)) * 2) / 2

        # Synthetic OI bars for demo: random deltas per bar, net usually positive
        oi_bars = {}
        for period_name in OI_KLINE_PERIODS:
            bars = []
            for _ in range(OI_NUM_BARS):
                bars.append(random.randint(-300, 800))
            oi_bars[period_name] = bars

        # Synthetic price bars for demo: random close-open deltas per bar
        price_bars = {}
        for period_name in OI_KLINE_PERIODS:
            bars = []
            for _ in range(OI_NUM_BARS):
                bars.append(round((random.random() - 0.5) * base * 0.008, 2))
            price_bars[period_name] = bars

        return Quote(
            ins_id=ins_id,
            last_price=tick,
            highest=max(high, tick),
            lowest=min(low, tick),
            open=open_,
            pre_settlement=base,
            volume=random.randint(10000, 500000),
            open_interest=random.randint(5000, 300000),
            pre_open_interest=random.randint(4000, 280000),
            datetime=time.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=time.time(),
            oi_bars=oi_bars,
            price_bars=price_bars,
        )


# ── Provider factory ────────────────────────────────────────────────

def create_provider(settings: AppSettings) -> BaseProvider:
    if settings.demo_mode or not settings.tqsdk.is_configured:
        logger.info("Using DemoProvider (demo_mode=%s, tqsdk_configured=%s)",
                     settings.demo_mode, settings.tqsdk.is_configured)
        return DemoProvider()
    logger.info("Using TqsdkProvider")
    return TqsdkProvider()
