"""Tests for risk/hedge_analysis.py - 5 tests."""

import numpy as np
import pytest  # noqa: F401

from risk.hedge_analysis import (
    hedge_effectiveness,
    compare_hedges,
    optimal_hedge_ratio,
    var_impact,
)


@pytest.fixture
def port_ret(returns_data, equal_weights):
    return (returns_data * equal_weights).sum(axis=1)


class TestHedgeEffectiveness:
    def test_keys(self, port_ret, returns_data):
        metrics = hedge_effectiveness(port_ret, returns_data["TLT"])
        for key in ["correlation", "tail_correlation", "beta", "variance_reduction"]:
            assert key in metrics

    def test_variance_reduction_non_negative(self, port_ret, returns_data):
        metrics = hedge_effectiveness(port_ret, returns_data["TLT"])
        assert metrics["variance_reduction"] >= 0


class TestCompareHedges:
    def test_sorted_by_effectiveness(self, port_ret, returns_data):
        candidates = returns_data[["TLT", "GLD"]]
        df = compare_hedges(port_ret, candidates)
        assert df.index[0] in ["TLT", "GLD"]
        # Should be sorted descending by variance_reduction
        assert df["variance_reduction"].iloc[0] >= df["variance_reduction"].iloc[1]


class TestOptimalHedgeRatio:
    def test_finite(self, port_ret, returns_data):
        ratio = optimal_hedge_ratio(port_ret, returns_data["TLT"])
        assert np.isfinite(ratio)


class TestVarImpact:
    def test_impact_keys(self, port_ret, returns_data):
        ratio = optimal_hedge_ratio(port_ret, returns_data["TLT"])
        impact = var_impact(port_ret, returns_data["TLT"], ratio)
        for key in ["var_before", "var_after", "cvar_before",
                    "cvar_after", "reduction_pct", "hedge_ratio"]:
            assert key in impact
