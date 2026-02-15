"""Tests for risk/monte_carlo.py - 6 tests."""

import numpy as np
import pandas as pd
import pytest

from risk.monte_carlo import (
    simulate_paths,
    regime_aware_simulation,
    simulation_statistics,
    percentile_bands,
)


class TestSimulatePaths:
    def test_output_shape(self, returns_data, equal_weights):
        sims = simulate_paths(returns_data, equal_weights, n_simulations=50,
                              n_days=100, seed=42)
        assert sims.shape == (50, 100)

    def test_deterministic_with_seed(self, returns_data, equal_weights):
        s1 = simulate_paths(returns_data, equal_weights, 20, 50, seed=123)
        s2 = simulate_paths(returns_data, equal_weights, 20, 50, seed=123)
        np.testing.assert_array_equal(s1, s2)

    def test_cumulative_returns(self, returns_data, equal_weights):
        """First day should equal single-day return, not cumsum error."""
        sims = simulate_paths(returns_data, equal_weights, 10, 50, seed=42)
        # Values should be small initially
        assert np.abs(sims[:, 0]).max() < 0.2


class TestRegimeAwareSim:
    def test_output_shape(self, returns_data, equal_weights, regime_df):
        sims = regime_aware_simulation(returns_data, equal_weights, regime_df,
                                       n_simulations=30, n_days=60, seed=42)
        assert sims.shape == (30, 60)

    def test_deterministic(self, returns_data, equal_weights, regime_df):
        s1 = regime_aware_simulation(returns_data, equal_weights, regime_df,
                                     20, 50, seed=7)
        s2 = regime_aware_simulation(returns_data, equal_weights, regime_df,
                                     20, 50, seed=7)
        np.testing.assert_array_equal(s1, s2)


class TestStatistics:
    def test_statistics_keys(self, returns_data, equal_weights):
        sims = simulate_paths(returns_data, equal_weights, 50, 100, seed=42)
        stats = simulation_statistics(sims)
        for key in ["p5", "p25", "p50", "p75", "p95", "mean", "std", "prob_loss"]:
            assert key in stats
