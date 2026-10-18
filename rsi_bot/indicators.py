"""Relative Strength Index and derived trading signals."""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["DEFAULT_PERIOD", "rsi", "signal_mask", "signals"]

DEFAULT_PERIOD = 14
DEFAULT_OVERSOLD = 30.0
DEFAULT_OVERBOUGHT = 70.0


def _ratio_to_index(avg_gain: float, avg_loss: float) -> float:
    if avg_loss == 0.0:
        return 100.0 if avg_gain > 0.0 else 50.0
    return 100.0 - (100.0 / (1.0 + avg_gain / avg_loss))


def rsi(close: pd.Series, period: int = DEFAULT_PERIOD) -> pd.Series:
    """Return Wilder's Relative Strength Index for a price series.

    The average gain and average loss are seeded with a simple moving average
    over the first ``period`` changes and then smoothed recursively with
    ``avg = (avg * (period - 1) + current) / period``, which is Wilder's
    original definition. Values are bounded by ``[0, 100]`` and the first
    ``period`` entries are ``NaN`` because the seed is not complete yet.
    """
    if period < 1:
        raise ValueError("period must be at least 1")

    series = close.astype(float)
    name = f"RSI_{period}"
    prices = series.to_numpy()

    if prices.size <= period:
        return pd.Series(np.full(prices.size, np.nan), index=series.index, name=name, dtype=float)

    output = np.full(prices.size, np.nan, dtype=float)

    gains = 0.0
    losses = 0.0
    for i in range(1, period + 1):
        change = prices[i] - prices[i - 1]
        if change > 0.0:
            gains += change
        else:
            losses -= change

    avg_gain = gains / period
    avg_loss = losses / period
    output[period] = _ratio_to_index(avg_gain, avg_loss)

    for i in range(period + 1, prices.size):
        change = prices[i] - prices[i - 1]
        gain = change if change > 0.0 else 0.0
        loss = -change if change < 0.0 else 0.0
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        output[i] = _ratio_to_index(avg_gain, avg_loss)

    return pd.Series(output, index=series.index, name=name, dtype=float)


def signal_mask(
    rsi_values: pd.Series,
    *,
    oversold: float = DEFAULT_OVERSOLD,
    overbought: float = DEFAULT_OVERBOUGHT,
) -> tuple[pd.Series, pd.Series]:
    """Return ``(buy, sell)`` boolean masks for the given RSI thresholds."""
    if oversold >= overbought:
        raise ValueError("oversold threshold must be below the overbought threshold")

    buy = rsi_values < oversold
    sell = rsi_values > overbought
    return buy.fillna(False), sell.fillna(False)


def signals(
    close: pd.Series,
    *,
    period: int = DEFAULT_PERIOD,
    oversold: float = DEFAULT_OVERSOLD,
    overbought: float = DEFAULT_OVERBOUGHT,
) -> pd.DataFrame:
    """Return a frame with the close price, RSI and the buy/sell flags."""
    values = rsi(close, period=period)
    buy, sell = signal_mask(values, oversold=oversold, overbought=overbought)

    return pd.DataFrame(
        {
            "close": close.astype(float),
            "rsi": values,
            "buy": buy,
            "sell": sell,
        }
    )
