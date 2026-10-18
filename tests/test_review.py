from __future__ import annotations

import pandas as pd
import pytest

from rsi_bot.review import SignalSummary, summarize_signals


def _frame(closes, buy_at=(), sell_at=()):
    index = pd.RangeIndex(len(closes))
    buy = pd.Series(False, index=index)
    sell = pd.Series(False, index=index)
    buy.iloc[list(buy_at)] = True
    sell.iloc[list(sell_at)] = True
    return pd.DataFrame({"close": pd.Series(closes, dtype=float), "buy": buy, "sell": sell})


class TestSummarizeSignals:
    def test_rejects_invalid_horizon(self):
        with pytest.raises(ValueError):
            summarize_signals(_frame([1.0, 2.0]), horizon=0)

    def test_requires_expected_columns(self):
        with pytest.raises(ValueError):
            summarize_signals(pd.DataFrame({"close": [1.0]}))

    def test_reports_one_row_per_bucket(self):
        result = summarize_signals(_frame(list(range(1, 30)), buy_at=[0]), horizon=5)
        assert list(result.index) == ["buy", "sell", "unconditional"]

    def test_measures_forward_return_for_buy(self):
        result = summarize_signals(_frame([100.0, 110.0, 121.0], buy_at=[0]), horizon=1)
        assert result.loc["buy", "mean"] == pytest.approx(0.10)
        assert result.loc["buy", "hit_rate"] == pytest.approx(1.0)

    def test_inverts_forward_return_for_sell(self):
        result = summarize_signals(_frame([100.0, 90.0, 81.0], sell_at=[0]), horizon=1)
        assert result.loc["sell", "mean"] == pytest.approx(0.10)

    def test_empty_signal_bucket_is_reported_as_zero_count(self):
        result = summarize_signals(_frame([100.0, 110.0]), horizon=1)
        assert result.loc["sell", "count"] == 0
        assert pd.isna(result.loc["sell", "mean"])

    def test_summary_row_contains_human_readable_keys(self):
        summary = SignalSummary("buy", 3, 0.5, 0.4, 0.66, 0.9, -0.1)
        assert summary.as_row()["signal"] == "buy"
        assert summary.as_row()["hit_rate"] == 0.66
