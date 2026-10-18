"""Matplotlib chart rendering."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

__all__ = ["render_chart"]

_BUY_COLOR = "#1a9850"
_SELL_COLOR = "#d73027"
_PRICE_COLOR = "#2c7fb8"
_RSI_COLOR = "#7b3294"


def render_chart(
    frame: pd.DataFrame,
    *,
    ticker: str,
    title: str | None = None,
    oversold: float = 30.0,
    overbought: float = 70.0,
    output: str | Path | None = None,
    show: bool = False,
) -> Path | None:
    """Draw the price panel and the RSI panel, optionally writing a PNG."""
    import matplotlib

    if output and not show:
        matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    figure, (price_axes, rsi_axes) = plt.subplots(
        2,
        1,
        figsize=(14, 8),
        sharex=True,
        gridspec_kw={"height_ratios": [2, 1]},
    )

    price_axes.plot(frame.index, frame["close"], color=_PRICE_COLOR, linewidth=1.1, label=ticker)
    price_axes.set_title(title or f"{ticker} — close price and RSI")
    price_axes.set_ylabel("Price")
    price_axes.legend(loc="upper left")
    price_axes.grid(alpha=0.25)

    rsi_axes.plot(frame.index, frame["rsi"], color=_RSI_COLOR, linewidth=1.1, label="RSI")
    rsi_axes.axhline(overbought, color=_SELL_COLOR, linestyle="--", linewidth=0.9, label=f"Overbought {overbought:g}")
    rsi_axes.axhline(oversold, color=_BUY_COLOR, linestyle="--", linewidth=0.9, label=f"Oversold {oversold:g}")
    rsi_axes.fill_between(frame.index, oversold, overbought, color="grey", alpha=0.06)
    rsi_axes.set_ylim(0, 100)
    rsi_axes.set_ylabel("RSI")
    rsi_axes.legend(loc="upper left", fontsize="small")
    rsi_axes.grid(alpha=0.25)

    buys = frame.index[frame["buy"].astype(bool)]
    sells = frame.index[frame["sell"].astype(bool)]
    price_axes.scatter(buys, frame.loc[buys, "close"], marker="^", s=55, color=_BUY_COLOR, label="Buy", zorder=3)
    price_axes.scatter(sells, frame.loc[sells, "close"], marker="v", s=55, color=_SELL_COLOR, label="Sell", zorder=3)
    price_axes.legend(loc="upper left")

    figure.tight_layout()

    written: Path | None = None
    if output:
        written = Path(output)
        written.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(written, dpi=140, bbox_inches="tight")

    if show:
        plt.show()

    plt.close(figure)
    return written
