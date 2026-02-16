"""Tests for risk/var_cvar.py - 6 tests."""

from risk.var_cvar import (
    historical_var,
    historical_cvar,
    parametric_var,
    portfolio_var,
    portfolio_cvar,
    regime_conditional_var,
    var_cvar_summary,
)


class TestHistoricalVaR:
    def test_positive_loss(self, returns_data, equal_weights):
        port_ret = (returns_data * equal_weights).sum(axis=1)
        var = historical_var(port_ret, 0.95)
        assert var > 0  # VaR should be positive (loss)

    def test_cvar_greater_than_var(self, returns_data, equal_weights):
        port_ret = (returns_data * equal_weights).sum(axis=1)
        var = historical_var(port_ret, 0.95)
        cvar = historical_cvar(port_ret, 0.95)
        assert cvar >= var  # CVaR >= VaR always


class TestParametricVaR:
    def test_parametric_positive(self, returns_data, equal_weights):
        port_ret = (returns_data * equal_weights).sum(axis=1)
        var = parametric_var(port_ret, 0.95)
        assert var > 0

    def test_higher_confidence_higher_var(self, returns_data, equal_weights):
        port_ret = (returns_data * equal_weights).sum(axis=1)
        var_90 = parametric_var(port_ret, 0.90)
        var_99 = parametric_var(port_ret, 0.99)
        assert var_99 > var_90


class TestRegimeConditionalVaR:
    def test_returns_dict(self, returns_data, equal_weights, regime_df):
        result = regime_conditional_var(returns_data, equal_weights, regime_df, 0.95)
        assert isinstance(result, dict)
        assert len(result) > 0


class TestPortfolioVaR:
    def test_portfolio_var_historical(self, returns_data, equal_weights):
        v = portfolio_var(returns_data, equal_weights, 0.95, method="historical")
        assert v > 0

    def test_portfolio_var_parametric(self, returns_data, equal_weights):
        v = portfolio_var(returns_data, equal_weights, 0.95, method="parametric")
        assert v > 0

    def test_portfolio_cvar(self, returns_data, equal_weights):
        c = portfolio_cvar(returns_data, equal_weights, 0.95)
        assert c > 0


class TestVarCvarSummary:
    def test_summary_keys(self, returns_data, equal_weights):
        s = var_cvar_summary(returns_data, equal_weights, 0.95)
        assert "historical_var" in s
        assert "historical_cvar" in s
        assert "parametric_var" in s
        assert s["confidence"] == 0.95
