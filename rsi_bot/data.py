"""Market data acquisition."""

from __future__ import annotations

import pandas as pd

__all__ = ["fetch_ohlc", "extract_close"]

_REQUIRED_COLUMNS = ("Open", "High", "Low", "Close", "Volume")


def _flatten_columns(frame: pd.DataFrame) -> pd.DataFrame:
    if isinstance(frame.columns, pd.MultiIndex):
        frame = frame.copy()
        frame.columns = [
            level[0] if isinstance(level, tuple) else level for level in frame.columns
        ]
    return frame


def extract_close(frame: pd.DataFrame) -> pd.Series:
    """Return the close series as a flat, float ``Series``.

    Yahoo Finance occasionally returns a multi-level column index, and a
    duplicated ``Close`` column collapses to a ``DataFrame`` when sliced.
    Normalising here keeps callers free of shape checks.
    """
    if frame.empty:
        raise ValueError("price history is empty")

    if "Close" not in frame.columns:
        raise ValueError(
            f"missing required column 'Close'; available columns: {list(frame.columns)}"
        )

    close = frame["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    return close.astype(float).rename("Close")


def fetch_ohlc(
    ticker: str,
    start: str,
    end: str | None = None,
    *,
    interval: str = "1d",
    auto_adjust: bool = True,
) -> pd.DataFrame:
    """Download historical OHLCV data for ``ticker`` from Yahoo Finance.

    Returns a frame indexed by date with the regular OHLCV columns. Raises
    :class:`ValueError` when the provider returns no rows, which normally
    means the symbol is unknown or the requested window is a market holiday.
    """
    import yfinance as yf

    raw = yf.download(
        ticker,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=auto_adjust,
        progress=False,
    )

    frame = _flatten_columns(raw)
    if frame.empty:
        raise ValueError(f"no price data returned for {ticker!r} between {start} and {end}")

    available = [column for column in _REQUIRED_COLUMNS if column in frame.columns]
    frame = frame.loc[:, available].sort_index()
    frame.index.name = "Date"
    return frame
