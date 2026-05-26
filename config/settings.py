"""
Global settings for the Commodity Dashboard.
Override values via environment variables (prefixed with CD_).
"""

import os
from dataclasses import dataclass, field
from typing import List


def _env(key: str, default: str) -> str:
    return os.environ.get(f"CD_{key}", default)


def _env_int(key: str, default: int) -> int:
    return int(_env(key, str(default)))


def _env_float(key: str, default: float) -> float:
    return float(_env(key, str(default)))


def _env_bool(key: str, default: bool) -> bool:
    val = _env(key, str(default)).lower()
    return val in ("1", "true", "yes")


@dataclass
class TqsdkSettings:
    username: str = _env("TQ_USERNAME", "15583300776")
    password: str = _env("TQ_PASSWORD", "Unfair4400")
    # Contract suffix is NOT used for tqsdk — tqsdk uses KQ.m@ main-contract
    # auto-resolution. Set ``contract_suffix`` on individual Instrument items
    # in instruments.py if you need to pin a specific contract month.
    contract_suffix: str = _env("TQ_CONTRACT_SUFFIX", "")

    @property
    def is_configured(self) -> bool:
        return bool(self.username and self.password)


@dataclass
class ServerSettings:
    host: str = _env("SERVER_HOST", "0.0.0.0")
    port: int = _env_int("SERVER_PORT", 8765)
    # Interval (seconds) at which processed data is pushed to web clients
    push_interval: float = _env_float("PUSH_INTERVAL", 0.5)


@dataclass
class DemoSettings:
    """Simulated-data generation parameters."""
    tick_interval: float = _env_float("DEMO_TICK_INTERVAL", 2.0)
    max_change_pct: float = _env_float("DEMO_MAX_CHANGE_PCT", 0.04)
    trend_persistence: float = _env_float("DEMO_TREND_PERSISTENCE", 0.95)


@dataclass
class AlertSettings:
    change_threshold: float = _env_float("ALERT_CHANGE_THRESHOLD", 2.5)   # |涨跌幅| >
    amplitude_threshold: float = _env_float("ALERT_AMPLITUDE_THRESHOLD", 4.0)  # 振幅 >


@dataclass
class AppSettings:
    tqsdk: TqsdkSettings = field(default_factory=TqsdkSettings)
    server: ServerSettings = field(default_factory=ServerSettings)
    demo: DemoSettings = field(default_factory=DemoSettings)
    alert: AlertSettings = field(default_factory=AlertSettings)
    # Run in demo mode (True) or connect to tqsdk (False)
    demo_mode: bool = _env_bool("DEMO_MODE", not TqsdkSettings().is_configured)


# Convenience singleton
settings = AppSettings()
