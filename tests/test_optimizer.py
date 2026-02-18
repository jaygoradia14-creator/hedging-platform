"""Tests for risk/optimizer.py - Efficient Frontier optimization."""

import numpy as np

from risk.optimizer import (
    portfolio_performance,
    min_variance_portfolio,
    max_sharpe_portfolio,
    efficient_frontier,
    random_portfolios,
)


class TestPortfolioPerformance:
    def test_equal_weight(self, returns_data):
        n = returns_data.shape[1]
        w = np.ones(n) / n
        mean_ret = returns_data.mean().values
        cov = returns_data.cov().values
        ret, vol, sharpe = portfolio_performance(w, mean_ret, cov, 0.02)
        assert isinstance(ret, float)
        assert isinstance(vol, float)
        assert vol > 0
        assert isinstance(sharpe, float)

    def test_single_asset(self, returns_data):
        n = returns_data.shape[1]
        w = np.zeros(n)
        w[0] = 1.0
        mean_ret = returns_data.mean().values
        cov = returns_data.cov().values
        ret, vol, sharpe = portfolio_performance(w, mean_ret, cov)
        assert vol > 0
        assert ret != 0


class TestMinVariance:
    def test_returns_dict(self, returns_data):
        result = min_variance_portfolio(returns_data)
        assert "weights" in result
        assert "return" in result
        assert "volatility" in result
        assert "sharpe" in result

    def test_weights_sum_to_one(self, returns_data):
        result = min_variance_portfolio(returns_data)
        assert abs(result["weights"].sum() - 1.0) < 1e-6

    def test_non_negative_weights(self, returns_data):
        result = min_variance_portfolio(returns_data)
        assert all(w >= -1e-6 for w in result["weights"])

    def test_lower_vol_than_equal(self, returns_data):
        mv = min_variance_portfolio(returns_data)
        n = returns_data.shape[1]
        eq_w = np.ones(n) / n
        mean_ret = returns_data.mean().values
        cov = returns_data.cov().values
        _, eq_vol, _ = portfolio_performance(eq_w, mean_ret, cov)
        assert mv["volatility"] <= eq_vol + 1e-6


class TestMaxSharpe:
    def test_returns_dict(self, returns_data):
        result = max_sharpe_portfolio(returns_data, risk_free=0.02)
        assert "weights" in result
        assert "sharpe" in result

    def test_weights_sum_to_one(self, returns_data):
        result = max_sharpe_portfolio(returns_data)
        assert abs(result["weights"].sum() - 1.0) < 1e-6

    def test_higher_sharpe_than_equal(self, returns_data):
        ms = max_sharpe_portfolio(returns_data, risk_free=0.02)
        n = returns_data.shape[1]
        eq_w = np.ones(n) / n
        mean_ret = returns_data.mean().values
        cov = returns_data.cov().values
        _, _, eq_sharpe = portfolio_performance(eq_w, mean_ret, cov, 0.02)
        assert ms["sharpe"] >= eq_sharpe - 1e-6


class TestEfficientFrontier:
    def test_returns_arrays(self, returns_data):
        ef = efficient_frontier(returns_data, n_points=10)
        assert "returns" in ef
        assert "volatilities" in ef
        assert "sharpes" in ef
        assert "weights" in ef
        assert len(ef["returns"]) > 0

    def test_frontier_is_sorted(self, returns_data):
        ef = efficient_frontier(returns_data, n_points=20)
        # Returns should be roughly increasing
        assert ef["returns"][-1] >= ef["returns"][0]


class TestRandomPortfolios:
    def test_shape(self, returns_data):
        rp = random_portfolios(returns_data, n_portfolios=100)
        assert len(rp["returns"]) == 100
        assert len(rp["volatilities"]) == 100
        assert len(rp["sharpes"]) == 100

    def test_deterministic(self, returns_data):
        rp1 = random_portfolios(returns_data, n_portfolios=50, seed=42)
        rp2 = random_portfolios(returns_data, n_portfolios=50, seed=42)
        np.testing.assert_array_equal(rp1["returns"], rp2["returns"])
