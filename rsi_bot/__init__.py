"""RSI based swing signal research toolkit."""

from __future__ import annotations

from .data import fetch_ohlc
from .indicators import rsi, signal_mask, signals
from .review import SignalSummary, summarize_signals

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "SignalSummary",
    "fetch_ohlc",
    "rsi",
    "signal_mask",
    "signals",
    "summarize_signals",
]
