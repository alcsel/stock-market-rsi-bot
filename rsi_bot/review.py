"""Forward-return statistics for generated signals."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

__all__ = ["DEFAULT_HORIZON", "SignalSummary", "summarize_signals"]

DEFAULT_HORIZON = 10


@dataclass(frozen=True)
class SignalSummary:
    """Aggregate statistics for one signal direction."""

    label: str
    count: int
    mean_forward_return: float
    median_forward_return: float
    hit_rate: float
    best_forward_return: float
    worst_forward_return: float

    def as_row(self) -> dict[str, object]:
        return {
            "signal": self.label,
            "count": self.count,
            "mean": self.mean_forward_return,
            "median": self.median_forward_return,
            "hit_rate": self.hit_rate,
            "best": self.best_forward_return,
            "worst": self.worst_forward_return,
        }


def _forward_returns(close: pd.Series, horizon: int) -> pd.Series:
    return close.shift(-horizon) / close - 1.0


def _summarize(label: str, returns: pd.Series) -> SignalSummary:
    clean = returns.dropna()
    if clean.empty:
        return SignalSummary(label, 0, float("nan"), float("nan"), float("nan"), float("nan"), float("nan"))

    return SignalSummary(
        label=label,
        count=int(clean.size),
        mean_forward_return=float(clean.mean()),
        median_forward_return=float(clean.median()),
        hit_rate=float((clean > 0).mean()),
        best_forward_return=float(clean.max()),
        worst_forward_return=float(clean.min()),
    )


def summarize_signals(
    frame: pd.DataFrame,
    *,
    horizon: int = DEFAULT_HORIZON,
) -> pd.DataFrame:
    """Describe what happened after each signal.

    For every buy and sell flag the function measures the realised return
    ``horizon`` sessions later and reports population statistics. This is a
    descriptive sanity check, not a backtest: it ignores fees, slippage,
    position sizing and overlapping trades.
    """
    if horizon < 1:
        raise ValueError("horizon must be at least 1 trading session")

    required = {"close", "buy", "sell"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"frame is missing required columns: {sorted(missing)}")

    forward = _forward_returns(frame["close"].astype(float), horizon)

    rows = [
        _summarize("buy", forward[frame["buy"].astype(bool)]),
        _summarize("sell", -forward[frame["sell"].astype(bool)]),
        _summarize("unconditional", forward),
    ]

    return pd.DataFrame([row.as_row() for row in rows]).set_index("signal")
