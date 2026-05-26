"""
Technical indicators — EMA, MACD, and divergence detection.
"""

from typing import List, Optional


def ema(data: List[float], period: int) -> List[float]:
    """Exponential Moving Average. Returns same-length list (early values are SMA)."""
    if len(data) < period:
        return [None] * len(data)
    k = 2.0 / (period + 1)
    result = [None] * (period - 1)
    sma = sum(data[:period]) / period
    result.append(sma)
    for val in data[period:]:
        sma = (val - sma) * k + sma
        result.append(sma)
    return result


def macd(close_prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9):
    """Compute MACD.

    Returns (dif, dea, histogram) — each a list of floats, with None for leading entries.
    """
    ema_fast = ema(close_prices, fast)
    ema_slow = ema(close_prices, slow)

    dif = [None] * len(close_prices)
    for i in range(len(close_prices)):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            dif[i] = ema_fast[i] - ema_slow[i]

    # DEA = EMA of DIF
    valid_dif = [v for v in dif if v is not None]
    dea_valid = ema(valid_dif, signal)
    dea = [None] * (len(dif) - len(dea_valid)) + dea_valid

    histogram = [None] * len(close_prices)
    for i in range(len(close_prices)):
        if dif[i] is not None and dea[i] is not None:
            histogram[i] = dif[i] - dea[i]

    return dif, dea, histogram


def detect_divergence(
    close_prices: List[float],
    histogram: List[float],
    lookback: int = 20,
) -> Optional[str]:
    """Detect MACD histogram divergence.

    Returns "bullish" (price lower low, histogram higher low),
    "bearish" (price higher high, histogram lower high), or None.

    Only examines the most recent *lookback* bars.
    """
    valid_idx = [i for i, v in enumerate(histogram) if v is not None]
    if len(valid_idx) < lookback:
        return None

    # Work on the last lookback valid entries
    recent_idx = valid_idx[-lookback:]
    recent_prices = [close_prices[i] for i in recent_idx]
    recent_hist = [histogram[i] for i in recent_idx]

    mid = lookback // 2

    # Split into left half and right half
    left_prices = recent_prices[:mid]
    right_prices = recent_prices[mid:]
    left_hist = recent_hist[:mid]
    right_hist = recent_hist[mid:]

    # Bullish divergence: price makes lower low, histogram makes higher low
    left_price_min = min(left_prices)
    right_price_min = min(right_prices)
    left_hist_min = min(left_hist)
    right_hist_min = min(right_hist)

    if right_price_min < left_price_min and right_hist_min > left_hist_min:
        return "bullish"

    # Bearish divergence: price makes higher high, histogram makes lower high
    left_price_max = max(left_prices)
    right_price_max = max(right_prices)
    left_hist_max = max(left_hist)
    right_hist_max = max(right_hist)

    if right_price_max > left_price_max and right_hist_max < left_hist_max:
        return "bearish"

    return None


def compute_macd_signals(price_bars: dict) -> dict:
    """For each period in price_bars, compute MACD divergence signal.

    *price_bars* is a dict like {"15m": [close-open, ...], "30m": [...], "1h": [...]}.
    We reconstruct approximate close prices from the deltas + a synthetic baseline,
    since only deltas are available. We use a cumulative sum approach.

    Returns {"15m": "bullish"|"bearish"|None, ...}
    """
    signals = {}
    for period_name, deltas in price_bars.items():
        if not deltas or len(deltas) < 30:
            signals[period_name] = None
            continue
        # Reconstruct approximate close prices from price-change deltas
        # Start from 0 (relative), accumulate
        closes = [0.0]
        for d in deltas:
            closes.append(closes[-1] + d)
        closes = closes[1:]  # same length as deltas

        _, _, hist = macd(closes)
        signal = detect_divergence(closes, hist)
        signals[period_name] = signal

    return signals
