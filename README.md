# RSI Signal Toolkit

A small research toolkit for studying the **Relative Strength Index** on real market data.

It downloads daily candles from Yahoo Finance, computes Wilder's RSI, flags overbought and oversold conditions, and reports what the price actually did after every signal. Everything is a plain pandas object, so the output drops straight into a notebook.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **Not investment advice.** The forward-return table is a descriptive statistic, not a backtest. It ignores commission, slippage, position sizing and overlapping trades.

## Features

- **Canonical RSI** – Wilder's original seeding plus recursive smoothing, not a generic exponential average.
- **Configurable thresholds** – any lookback period and any oversold/overbought pair.
- **Forward-return review** – measures the realised return after each buy and sell flag and compares it against the unconditional baseline.
- **Chart export** – two-panel price and RSI figure with the signals marked, written to PNG.
- **Offline friendly** – the indicator and review layers take ordinary pandas objects, so no network call is needed to test them.

## Installation

```bash
git clone https://github.com/alcsel/stock-market-rsi-bot.git
cd stock-market-rsi-bot
python -m pip install -r requirements.txt
```

For development, install the package with its test extras:

```bash
python -m pip install -e ".[dev]"
```

## Usage

### Command line

```bash
python -m rsi_bot.cli MAVI.IS --start 2021-01-01 --end 2025-04-01 --output charts/mavi.png
```

```
MAVI.IS  (2021-01-01 → 2025-04-01)
rows: 1058  period: 14  thresholds: 30/70

last 10 sessions
             close    rsi    buy   sell
Date
2025-03-19   47.60  41.22  False  False
...

forward returns over 10 sessions
                 count    mean  median  hit_rate    best   worst
signal
buy                 84  0.0131  0.0062    0.5357  0.1944 -0.1471
sell                61 -0.0084 -0.0041    0.4426  0.1288 -0.1667
unconditional     1048  0.0019  0.0000    0.4905  0.5417 -0.3014
```

Useful flags:

| Flag | Meaning |
|---|---|
| `--period` | RSI lookback window (default `14`) |
| `--oversold`, `--overbought` | Signal thresholds (default `30` / `70`) |
| `--horizon` | Forward-return window in sessions (default `10`) |
| `-o, --output` | Write the chart to a PNG file |
| `--show` | Open the chart in an interactive window |
| `--tail` | How many recent rows to print (default `10`) |

### Library

```python
from rsi_bot import fetch_ohlc, signals, summarize_signals
from rsi_bot.data import extract_close

frame = signals(extract_close(fetch_ohlc("AAPL", "2020-01-01")), period=14)
print(frame.tail())

print(summarize_signals(frame, horizon=20))
```

## How the indicator is computed

1. Take the period-over-period close change and split it into gains and losses.
2. Seed the average gain and average loss with a simple mean over the first `period` changes.
3. Smooth both averages with `avg = (avg * (period - 1) + current) / period`.
4. Compute `RSI = 100 - 100 / (1 + avg_gain / avg_loss)`.

Edge cases are defined explicitly: when the average loss is zero and the average gain is positive the RSI is `100`, a perfectly flat window scores `50`, and windows shorter than the period return `NaN`.

## Project layout

```
rsi_bot/
├── __init__.py     Public exports
├── data.py         Yahoo Finance download and column normalisation
├── indicators.py   RSI and signal masks
├── review.py       Forward-return statistics
├── plotting.py     Matplotlib chart rendering
└── cli.py          argparse entry point
tests/
├── test_indicators.py
└── test_review.py
```

## Development

```bash
python -m pytest
```

The RSI implementation is verified against Wilder's published worked example, so any future refactor is guarded by a known-correct reference.

## License

Released under the [MIT License](LICENSE).
