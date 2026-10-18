from __future__ import annotations

import pandas as pd
import pytest

from rsi_bot.indicators import rsi, signal_mask, signals


def _series(values):
    return pd.Series(values, dtype=float)


class TestRsi:
    def test_rejects_invalid_period(self):
        with pytest.raises(ValueError):
            rsi(_series([1, 2, 3]), period=0)

    def test_empty_input_returns_empty_series(self):
        result = rsi(_series([]))
        assert result.empty

    def test_first_period_values_are_undefined(self):
        result = rsi(_series(range(1, 40)), period=14)
        assert result.iloc[:14].isna().all()
        assert result.iloc[14:].notna().all()

    def test_monotonic_rise_saturates_at_one_hundred(self):
        result = rsi(_series(range(1, 60)), period=14)
        assert result.dropna().eq(100.0).all()

    def test_monotonic_fall_bottoms_out_at_zero(self):
        result = rsi(_series(range(60, 1, -1)), period=14)
        assert result.dropna().eq(0.0).all()

    def test_flat_series_is_neutral(self):
        result = rsi(_series([100.0] * 40), period=14)
        assert result.dropna().eq(50.0).all()

    def test_values_stay_within_bounds(self):
        values = [100, 102, 99, 105, 107, 103, 101, 110, 108, 106, 112, 115, 111, 109, 108, 104, 102, 100, 98, 95]
        result = rsi(_series(values), period=14).dropna()
        assert result.between(0.0, 100.0).all()

    def test_series_shorter_than_the_period_is_all_nan(self):
        result = rsi(_series([1.0, 2.0, 3.0]), period=14)
        assert result.isna().all()
        assert len(result) == 3

    def test_matches_wilders_published_worked_example(self):
        closes = [
            44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
            45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00,
            46.03, 46.41, 46.22, 45.64,
        ]
        result = rsi(_series(closes), period=14)
        assert result.iloc[14] == pytest.approx(70.4648, abs=0.01)
        assert result.iloc[15] == pytest.approx(66.2496, abs=0.01)
        assert result.iloc[16] == pytest.approx(66.4800, abs=0.01)


class TestSignalMask:
    def test_rejects_crossed_thresholds(self):
        with pytest.raises(ValueError):
            signal_mask(_series([50.0]), oversold=70, overbought=30)

    def test_flags_oversold_and_overbought(self):
        values = _series([20.0, 50.0, 80.0])
        buy, sell = signal_mask(values)
        assert buy.tolist() == [True, False, False]
        assert sell.tolist() == [False, False, True]

    def test_nan_values_are_not_signals(self):
        buy, sell = signal_mask(_series([float("nan")]))
        assert not buy.any()
        assert not sell.any()


class TestSignalsFrame:
    def test_exposes_expected_columns(self):
        frame = signals(_series(range(1, 40)))
        assert list(frame.columns) == ["close", "rsi", "buy", "sell"]

    def test_flags_are_boolean(self):
        frame = signals(_series(range(1, 40)))
        assert frame["buy"].dtype == bool
        assert frame["sell"].dtype == bool
