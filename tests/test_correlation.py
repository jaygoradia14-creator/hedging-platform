"""Tests for risk/correlation.py - 10 tests."""

import numpy as np
import pandas as pd

from risk.correlation import (
    calculate_correlation_matrix,
    calculate_tail_correlation,
    calculate_upside_downside_correlation,
    calculate_correlation_asymmetry,
    calculate_diversification_ratio,
    calculate_rolling_correlation_matrix,
    calculate_correlation_heatmap_data,
    get_correlation_stability,
)


class TestCorrelationMatrix:
    def test_shape(self, returns_data):
        corr = calculate_correlation_matrix(returns_data)
        n = returns_data.shape[1]
        assert corr.shape == (n, n)

    def test_diagonal_ones(self, returns_data):
        corr = calculate_correlation_matrix(returns_data)
        np.testing.assert_array_almost_equal(np.diag(corr.values), 1.0)

    def test_symmetric(self, returns_data):
        corr = calculate_correlation_matrix(returns_data)
        np.testing.assert_array_almost_equal(corr.values, corr.values.T)


class TestTailCorrelation:
    def test_shape_matches_normal(self, returns_data):
        normal = calculate_correlation_matrix(returns_data)
        tail = calculate_tail_correlation(returns_data, quantile=0.05)
        assert tail.shape == normal.shape

    def test_tail_correlation_bounded(self, returns_data):
        """Tail correlations should be valid correlation values."""
        tail = calculate_tail_correlation(returns_data, quantile=0.05)
        assert tail.min().min() >= -1.0
        assert tail.max().max() <= 1.0
        # Diagonal should be 1
        np.testing.assert_array_almost_equal(np.diag(tail.values), 1.0)

    def test_fallback_on_small_sample(self, seed):
        """With too few data points, should fall back to normal corr."""
        np.random.seed(seed)
        small = pd.DataFrame(np.random.randn(15, 3), columns=["A", "B", "C"])
        tail = calculate_tail_correlation(small, quantile=0.05)
        normal = calculate_correlation_matrix(small)
        pd.testing.assert_frame_equal(tail, normal)


class TestAsymmetry:
    def test_asymmetry_shape(self, returns_data):
        asym = calculate_correlation_asymmetry(returns_data)
        n = returns_data.shape[1]
        assert asym.shape == (n, n)

    def test_diagonal_zero(self, returns_data):
        asym = calculate_correlation_asymmetry(returns_data)
        np.testing.assert_array_almost_equal(np.diag(asym.values), 0.0)


class TestDiversificationRatio:
    def test_equal_weight_greater_than_one(self, returns_data, equal_weights):
        dr = calculate_diversification_ratio(returns_data, equal_weights)
        assert dr > 1.0  # diversified portfolio should have DR > 1

    def test_single_asset_ratio_one(self, returns_data):
        single = returns_data[["SPY"]]
        dr = calculate_diversification_ratio(single, np.array([1.0]))
        assert abs(dr - 1.0) < 0.01


class TestRollingCorrelationMatrix:
    def test_dict_output(self, returns_data):
        matrices = calculate_rolling_correlation_matrix(returns_data, window=63)
        assert isinstance(matrices, dict)
        assert len(matrices) > 0
        first_key = list(matrices.keys())[0]
        assert isinstance(matrices[first_key], pd.DataFrame)


class TestHeatmapData:
    def test_without_regime(self, returns_data):
        corr = calculate_correlation_heatmap_data(returns_data)
        assert corr.shape[0] == returns_data.shape[1]

    def test_with_regime_filter(self, returns_data, regime_df):
        corr = calculate_correlation_heatmap_data(returns_data, regime_df, "Normal")
        assert corr.shape[0] == returns_data.shape[1]


class TestCorrelationStability:
    def test_returns_series(self, returns_data):
        stability = get_correlation_stability(returns_data, window=63)
        assert isinstance(stability, pd.Series)
        assert len(stability) > 0

    def test_sorted_descending(self, returns_data):
        stability = get_correlation_stability(returns_data, window=63)
        vals = stability.values
        for i in range(len(vals) - 1):
            assert vals[i] >= vals[i + 1]


class TestUpsideDownsideCorrelation:
    def test_returns_two_matrices(self, returns_data):
        down, up = calculate_upside_downside_correlation(returns_data)
        assert down.shape == up.shape
        assert down.shape[0] == returns_data.shape[1]
