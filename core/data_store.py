"""
Thread-safe central data store for instrument quotes.
Single source of truth — market data providers write, analytics reads.
"""

import asyncio
import math
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


def _safe_float(val: Any) -> float:
    """Extract a clean float, converting NaN/None to 0.0.

    tqsdk initialises price fields to ``float("nan")`` — ``val or 0`` does
    NOT protect against NaN because ``bool(NaN)`` is ``True``.
    """
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return 0.0 if math.isnan(val) else float(val)
    return 0.0


def _safe_int(val: Any) -> int:
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        if math.isnan(val):
            return 0
        return int(val)
    return 0


@dataclass
class Quote:
    ins_id: str
    last_price: float = 0.0
    highest: float = 0.0
    lowest: float = 0.0
    open: float = 0.0
    pre_settlement: float = 0.0
    volume: int = 0
    open_interest: int = 0
    pre_open_interest: int = 0
    datetime: str = ""
    updated_at: float = 0.0
    # OI bars from kline: period_name -> [7 deltas]  (close_oi - open_oi per bar)
    oi_bars: Optional[Dict[str, List[int]]] = None
    # Price change bars from kline: period_name -> [7 deltas]  (close - open per bar)
    price_bars: Optional[Dict[str, List[float]]] = None

    @property
    def is_valid(self) -> bool:
        return self.pre_settlement > 0 and self.last_price > 0

    @classmethod
    def from_tqsdk(cls, ins_id: str, q: Any) -> "Quote":
        return cls(
            ins_id=ins_id,
            last_price=_safe_float(getattr(q, "last_price", 0)),
            highest=_safe_float(getattr(q, "highest", 0)),
            lowest=_safe_float(getattr(q, "lowest", 0)),
            open=_safe_float(getattr(q, "open", 0)),
            pre_settlement=_safe_float(getattr(q, "pre_settlement", 0)),
            volume=_safe_int(getattr(q, "volume", 0)),
            open_interest=_safe_int(getattr(q, "open_interest", 0)),
            pre_open_interest=_safe_int(getattr(q, "pre_open_interest", 0)),
            datetime=str(getattr(q, "datetime", "") or ""),
            updated_at=time.time(),
        )

    def to_dict(self) -> dict:
        d = {
            "insId": self.ins_id,
            "lastPrice": self.last_price,
            "highest": self.highest,
            "lowest": self.lowest,
            "open": self.open,
            "preSettlement": self.pre_settlement,
            "volume": self.volume,
            "openInterest": self.open_interest,
            "preOpenInterest": self.pre_open_interest,
            "datetime": self.datetime,
            "updatedAt": self.updated_at,
        }
        if self.oi_bars is not None:
            d["oiBars"] = self.oi_bars
        if self.price_bars is not None:
            d["priceBars"] = self.price_bars
        return d


class DataStore:
    """Async-safe store for the latest quote of every subscribed instrument."""

    def __init__(self):
        self._quotes: Dict[str, Quote] = {}
        self._lock = asyncio.Lock()
        self._listeners: List[Callable] = []
        self._version: int = 0

    async def update(self, ins_id: str, quote: Quote) -> None:
        async with self._lock:
            self._quotes[ins_id] = quote
            self._version += 1

    async def get(self, ins_id: str) -> Optional[Quote]:
        async with self._lock:
            return self._quotes.get(ins_id)

    async def get_snapshot(self) -> Dict[str, Quote]:
        """Return a shallow copy of the current quote map."""
        async with self._lock:
            return dict(self._quotes)

    async def snapshot_quotes(self) -> Dict[str, dict]:
        """Return quotes as plain dicts, skipping invalid entries."""
        snap = await self.get_snapshot()
        return {k: v.to_dict() for k, v in snap.items() if v.is_valid}

    @property
    def version(self) -> int:
        return self._version

    def on_update(self, callback: Callable) -> None:
        """Register a callback invoked (with the DataStore) after each update batch."""
        self._listeners.append(callback)

    async def notify(self) -> None:
        for cb in self._listeners:
            if asyncio.iscoroutinefunction(cb):
                await cb(self)
            else:
                cb(self)
