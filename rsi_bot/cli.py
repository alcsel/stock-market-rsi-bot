"""Command line entry point for the RSI signal toolkit."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from .data import extract_close, fetch_ohlc
from .indicators import DEFAULT_OVERBOUGHT, DEFAULT_OVERSOLD, DEFAULT_PERIOD, signals
from .plotting import render_chart
from .review import DEFAULT_HORIZON, summarize_signals

_DEFAULT_TICKER = "MAVI.IS"
_DEFAULT_START = "2021-01-01"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rsi-bot",
        description="Download price history, compute the RSI and review its signals.",
    )
    parser.add_argument("ticker", nargs="?", default=_DEFAULT_TICKER, help=f"Yahoo Finance symbol (default: {_DEFAULT_TICKER})")
    parser.add_argument("--start", default=_DEFAULT_START, help=f"first date, YYYY-MM-DD (default: {_DEFAULT_START})")
    parser.add_argument("--end", default=None, help="last date, YYYY-MM-DD (default: today)")
    parser.add_argument("--period", type=int, default=DEFAULT_PERIOD, help=f"RSI lookback (default: {DEFAULT_PERIOD})")
    parser.add_argument("--oversold", type=float, default=DEFAULT_OVERSOLD, help=f"buy threshold (default: {DEFAULT_OVERSOLD:g})")
    parser.add_argument("--overbought", type=float, default=DEFAULT_OVERBOUGHT, help=f"sell threshold (default: {DEFAULT_OVERBOUGHT:g})")
    parser.add_argument("--horizon", type=int, default=DEFAULT_HORIZON, help=f"forward return window in sessions (default: {DEFAULT_HORIZON})")
    parser.add_argument("--output", "-o", default=None, help="write the chart to this PNG path")
    parser.add_argument("--show", action="store_true", help="open the chart in an interactive window")
    parser.add_argument("--tail", type=int, default=10, help="how many recent rows to print (default: 10)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        raw = fetch_ohlc(args.ticker, args.start, args.end)
        close = extract_close(raw)
        frame = signals(
            close,
            period=args.period,
            oversold=args.oversold,
            overbought=args.overbought,
        )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"error: could not load data ({error})", file=sys.stderr)
        return 1

    label = f"{args.start} → {args.end or 'today'}"
    print(f"{args.ticker}  ({label})")
    print(f"rows: {len(frame)}  period: {args.period}  thresholds: {args.oversold:g}/{args.overbought:g}")
    print()

    print(f"last {min(args.tail, len(frame))} sessions")
    preview = frame.tail(args.tail).copy()
    preview["close"] = preview["close"].round(2)
    preview["rsi"] = preview["rsi"].round(2)
    print(preview.to_string())
    print()

    print(f"forward returns over {args.horizon} sessions")
    print(summarize_signals(frame, horizon=args.horizon).round(4).to_string())
    print()

    if args.output or args.show:
        written = render_chart(
            frame,
            ticker=args.ticker,
            oversold=args.oversold,
            overbought=args.overbought,
            output=args.output,
            show=args.show,
        )
        if written:
            print(f"chart written to {written}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
