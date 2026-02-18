"""Tests for core/portfolio.py - Portfolio class and holdings management."""

import numpy as np
import pytest

from core.portfolio import Portfolio, get_holdings_summary, add_holding, sell_holding


class MockState(dict):
    """Mock Streamlit session state."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, val):
        self[key] = val

    def __delattr__(self, key):
        del self[key]


@pytest.fixture(autouse=True)
def mock_session_state(monkeypatch):
    """Patch st.session_state for all tests."""
    state = MockState(holdings={})
    import streamlit as st
    monkeypatch.setattr(st, "session_state", state)
    return state


class TestPortfolioInit:
    def test_default_tickers(self):
        p = Portfolio()
        assert p.tickers == ["SPY", "TLT", "GLD"]

    def test_equal_weights_default(self):
        p = Portfolio(tickers=["A", "B", "C", "D"])
        np.testing.assert_allclose(p.weights, [0.25, 0.25, 0.25, 0.25])

    def test_custom_weights(self):
        w = np.array([0.5, 0.3, 0.2])
        p = Portfolio(tickers=["A", "B", "C"], weights=w)
        np.testing.assert_array_equal(p.weights, w)


class TestPortfolioProperties:
    def test_n_assets(self):
        p = Portfolio(tickers=["A", "B"])
        assert p.n_assets == 2

    def test_returns_from_prices(self, price_data):
        p = Portfolio(tickers=list(price_data.columns), prices=price_data)
        assert p.returns is not None
        assert p.returns.shape[0] == price_data.shape[0] - 1

    def test_returns_setter(self, returns_data):
        p = Portfolio(tickers=list(returns_data.columns))
        p.returns = returns_data
        assert p.returns is not None
        assert p.returns.shape == returns_data.shape

    def test_portfolio_returns(self, returns_data):
        tickers = list(returns_data.columns)
        p = Portfolio(tickers=tickers)
        p.returns = returns_data
        pr = p.portfolio_returns
        assert pr is not None
        assert len(pr) == len(returns_data)

    def test_portfolio_returns_none_without_data(self):
        p = Portfolio()
        assert p.portfolio_returns is None

    def test_returns_none_without_prices(self):
        p = Portfolio()
        assert p.returns is None

    def test_hhi_equal_weight(self):
        p = Portfolio(tickers=["A", "B", "C", "D", "E"])
        assert abs(p.hhi_concentration() - 0.2) < 1e-6

    def test_hhi_single_asset(self):
        p = Portfolio(tickers=["A"], weights=np.array([1.0]))
        assert abs(p.hhi_concentration() - 1.0) < 1e-6

    def test_effective_n(self):
        p = Portfolio(tickers=["A", "B", "C", "D"])
        assert abs(p.effective_n() - 4.0) < 1e-6


class TestPortfolioSummary:
    def test_summary_keys(self):
        p = Portfolio()
        s = p.summary()
        assert "tickers" in s
        assert "weights" in s
        assert "n_assets" in s
        assert "hhi" in s
        assert "effective_n" in s

    def test_summary_with_prices(self, price_data):
        p = Portfolio(tickers=list(price_data.columns), prices=price_data)
        s = p.summary()
        assert "data_points" in s
        assert "date_range" in s
        assert s["data_points"] == len(price_data)


class TestHoldings:
    def test_add_holding(self, mock_session_state):
        add_holding("SPY", 10, 450.0)
        assert "SPY" in mock_session_state.holdings
        assert mock_session_state.holdings["SPY"]["shares"] == 10
        assert mock_session_state.holdings["SPY"]["buy_price"] == 450.0

    def test_add_holding_avg_cost(self, mock_session_state):
        add_holding("SPY", 10, 400.0)
        add_holding("SPY", 10, 500.0)
        h = mock_session_state.holdings["SPY"]
        assert h["shares"] == 20
        assert abs(h["buy_price"] - 450.0) < 1e-6

    def test_sell_holding_partial(self, mock_session_state):
        add_holding("SPY", 10, 450.0)
        sell_holding("SPY", 3)
        assert mock_session_state.holdings["SPY"]["shares"] == 7

    def test_sell_holding_all(self, mock_session_state):
        add_holding("SPY", 10, 450.0)
        sell_holding("SPY", 10)
        assert "SPY" not in mock_session_state.holdings

    def test_sell_holding_over(self, mock_session_state):
        add_holding("SPY", 5, 450.0)
        sell_holding("SPY", 100)
        assert "SPY" not in mock_session_state.holdings

    def test_sell_nonexistent(self, mock_session_state):
        sell_holding("AAPL", 5)  # should not error
        assert "AAPL" not in mock_session_state.holdings

    def test_get_holdings_summary(self, mock_session_state):
        add_holding("SPY", 10, 450.0)
        add_holding("AAPL", 5, 180.0)
        prices = {"SPY": 460.0, "AAPL": 195.0}
        rows = get_holdings_summary(prices)
        assert len(rows) == 2
        spy = [r for r in rows if r["Ticker"] == "SPY"][0]
        assert spy["Shares"] == 10
        assert abs(spy["P&L"] - 100.0) < 1e-6

    def test_get_holdings_summary_missing_price(self, mock_session_state):
        add_holding("SPY", 10, 450.0)
        rows = get_holdings_summary({})  # no prices
        assert len(rows) == 0

    def test_get_holdings_summary_empty(self, mock_session_state):
        rows = get_holdings_summary({"SPY": 460.0})
        assert len(rows) == 0
