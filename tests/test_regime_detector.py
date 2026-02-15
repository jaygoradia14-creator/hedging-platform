"""Tests for core/regime_detector.py - 8 tests."""

import numpy as np
import pandas as pd
import pytest

from core.regime_detector import (
    MarketRegime,
    calculate_rolling_volatility,
    calculate_rolling_correlation,
    detect_regime,
    get_regime_statistics,
    get_regime_colors,
)


class TestRollingVolatility:
    def test_shape(self, returns_data):
        vol = calculate_rolling_volatility(returns_data, window=21)
        assert vol.shape[1] == returns_data.shape[1]

    def test_annualized(self, returns_data):
        vol = calculate_rolling_volatility(returns_data, window=21)
        # Annualized vol should be roughly 10-60% for typical assets
        mean_vol = vol.dropna().mean().mean()
        assert 0.05 < mean_vol < 0.80


class TestRollingCorrelation:
    def test_output_is_series(self, returns_data):
        rc = calculate_rolling_correlation(returns_data, window=63)
        assert isinstance(rc, pd.Series)

    def test_correlation_range(self, returns_data):
        rc = calculate_rolling_correlation(returns_data, window=63)
        assert rc.dropna().min() >= -1.0
        assert rc.dropna().max() <= 1.0


class TestDetectRegime:
    def test_output_columns(self, returns_data):
        df = detect_regime(returns_data)
        assert set(df.columns) == {"volatility", "correlation", "regime"}

    def test_regime_values_valid(self, returns_data):
        df = detect_regime(returns_data)
        valid = {r.value for r in MarketRegime}
        assert set(df["regime"].unique()).issubset(valid)

    def test_statistics_keys(self, returns_data):
        df = detect_regime(returns_data)
        stats = get_regime_statistics(df)
        for name, s in stats.items():
            assert "days" in s
            assert "pct_time" in s
            assert "avg_vol" in s
            assert "avg_corr" in s


class TestRegimeColors:
    def test_all_regimes_have_colors(self):
        colors = get_regime_colors()
        for regime in MarketRegime:
            assert regime.value in colors
