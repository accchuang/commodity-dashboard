"""
Analytics engine — pure functions that process raw quote snapshots into
structured dashboard data: sector scores, rankings, alerts, and instrument rows.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from config.instruments import INSTRUMENTS, SECTORS, SECTOR_BY_ID, Instrument, build_tqsdk_id, get_contract_suffix
from config.settings import AppSettings
from core.indicators import compute_macd_signals


@dataclass
class InstrumentRow:
    code: str
    exchange: str
    ins_id: str
    name: str
    sector_id: str
    last_price: float
    open: float
    high: float
    low: float
    pre_settlement: float
    change_pct: float
    amplitude: float
    volume: int
    open_interest: int
    has_alert: bool
    today_oi_delta: int = 0          # open_interest - pre_open_interest
    oi_bars: Optional[Dict[str, List[int]]] = None   # period_name -> [60 deltas]
    price_bars: Optional[Dict[str, List[float]]] = None  # period_name -> [60 deltas] (close - open)
    signals: Optional[Dict[str, Optional[str]]] = None  # period_name -> "bullish"|"bearish"|None

    @classmethod
    def from_quote(cls, inst: Instrument, ins_id: str, q: dict, settings: AppSettings) -> "InstrumentRow":
        lp = float(q.get("lastPrice", 0))
        ps = float(q.get("preSettlement", 0))
        hi = float(q.get("highest", 0))
        lo = float(q.get("lowest", 0))
        change_pct = ((lp - ps) / ps) * 100 if ps > 0 else 0.0
        amplitude = ((hi - lo) / ps) * 100 if ps > 0 else 0.0
        has_alert = abs(change_pct) > settings.alert.change_threshold and \
                    amplitude > settings.alert.amplitude_threshold

        price_bars_raw = q.get("priceBars")
        signals = compute_macd_signals(price_bars_raw) if price_bars_raw else None

        return cls(
            code=inst.code,
            exchange=inst.exchange,
            ins_id=ins_id,
            name=inst.name,
            sector_id=inst.sector_id,
            last_price=lp,
            open=float(q.get("open", 0)),
            high=hi,
            low=lo,
            pre_settlement=ps,
            change_pct=change_pct,
            amplitude=amplitude,
            volume=int(q.get("volume", 0)),
            open_interest=int(q.get("openInterest", 0)),
            has_alert=has_alert,
            today_oi_delta=int(q.get("openInterest", 0)) - int(q.get("preOpenInterest", 0)),
            oi_bars=q.get("oiBars"),
            price_bars=price_bars_raw,
            signals=signals,
        )

    def to_dict(self) -> dict:
        d = {
            "code": self.code,
            "exchange": self.exchange,
            "insId": self.ins_id,
            "name": self.name,
            "sectorId": self.sector_id,
            "lastPrice": self.last_price,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "preSettlement": self.pre_settlement,
            "changePct": round(self.change_pct, 2),
            "amplitude": round(self.amplitude, 2),
            "volume": self.volume,
            "openInterest": self.open_interest,
            "todayOiDelta": self.today_oi_delta,
            "hasAlert": self.has_alert,
        }
        if self.oi_bars is not None:
            d["oiBars"] = self.oi_bars
        if self.price_bars is not None:
            d["priceBars"] = self.price_bars
        if self.signals is not None:
            d["signals"] = self.signals
        return d


@dataclass
class SectorScore:
    id: str
    name: str
    icon: str
    avg_change: float
    count: int
    best: float
    worst: float
    rank: int  # 1 = strongest

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "avgChange": round(self.avg_change, 2),
            "count": self.count,
            "best": round(self.best, 2),
            "worst": round(self.worst, 2),
            "rank": self.rank,
        }


@dataclass
class DashboardSnapshot:
    timestamp: str
    sectors: List[SectorScore]
    instruments: List[InstrumentRow]

    def to_dict(self) -> dict:
        return {
            "type": "market_snapshot",
            "timestamp": self.timestamp,
            "sectors": [s.to_dict() for s in self.sectors],
            "instruments": [r.to_dict() for r in self.instruments],
        }


def compute(quotes: Dict[str, dict], settings: AppSettings) -> DashboardSnapshot:
    """Process a raw quote dict snapshot into the full dashboard data structure.
    `quotes` is a dict of insId -> camelCase dict (from DataStore.snapshot_quotes)."""

    rows: List[InstrumentRow] = []

    for inst in INSTRUMENTS:
        ins_id = build_tqsdk_id(inst, get_contract_suffix(inst, settings.tqsdk.get_effective_suffix(inst.code, inst.contract_suffix or "")))
        q = quotes.get(ins_id)
        if not q or float(q.get("preSettlement", 0)) <= 0:
            continue
        rows.append(InstrumentRow.from_quote(inst, ins_id, q, settings))

    # Ranking: sort by change_pct descending
    rows.sort(key=lambda r: r.change_pct, reverse=True)

    # Sector scores
    groups: Dict[str, List[float]] = {}
    for r in rows:
        groups.setdefault(r.sector_id, []).append(r.change_pct)

    scores: List[SectorScore] = []
    for s in SECTORS:
        changes = groups.get(s.id, [])
        if not changes:
            scores.append(SectorScore(id=s.id, name=s.name, icon=s.icon,
                                       avg_change=0.0, count=0, best=0.0, worst=0.0, rank=0))
        else:
            scores.append(SectorScore(
                id=s.id, name=s.name, icon=s.icon,
                avg_change=sum(changes) / len(changes),
                count=len(changes),
                best=max(changes),
                worst=min(changes),
                rank=0,
            ))

    # Assign ranks by avg_change descending
    scores.sort(key=lambda s: s.avg_change, reverse=True)
    for i, sc in enumerate(scores):
        sc.rank = i + 1 if sc.count > 0 else 0

    return DashboardSnapshot(
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        sectors=scores,
        instruments=rows,
    )
