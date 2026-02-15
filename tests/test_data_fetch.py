"""Tests for core/data_fetch.py - 7 tests using synthetic data and mocked yfinance."""

import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from core.data_fetch import (
    fetch_stock_data,
    fetch_multi_asset_data,
    calculate_returns,
    ASSET_UNIVERSE,
    get_default_tickers,
)


class TestCalculateReturns:
    """Tests for the calculate_returns function (no network)."""

    def test_log_returns_shape(self, price_data):
        ret = calculate_returns(price_data, method="log")
        assert ret.shape == (len(price_data) - 1, price_data.shape[1])

    def test_log_returns_no_nan(self, price_data):
        ret = calculate_returns(price_data, method="log")
        assert not ret.isna().any().any()

    def test_simple_returns_shape(self, price_data):
        ret = calculate_returns(price_data, method="simple")
        assert ret.shape == (len(price_data) - 1, price_data.shape[1])

    def test_log_vs_simple_close(self, price_data):
        log_ret = calculate_returns(price_data, method="log")
        simple_ret = calculate_returns(price_data, method="simple")
        # For small returns, log ~ simple
        diff = (log_ret - simple_ret).abs().mean().mean()
        assert diff < 0.01

    def test_log_returns_values(self, price_data):
        ret = calculate_returns(price_data, method="log")
        # Manual check for first row
        expected = np.log(price_data.iloc[1] / price_data.iloc[0])
        pd.testing.assert_series_equal(ret.iloc[0], expected, check_names=False)


class TestAssetUniverse:
    def test_asset_universe_categories(self):
        assert set(ASSET_UNIVERSE.keys()) == {"equities", "bonds", "alternatives", "volatility"}

    def test_get_default_tickers(self):
        tickers = get_default_tickers()
        assert len(tickers) == 16
        assert "SPY" in tickers
        assert "TLT" in tickers


class TestPortfolioDataclass:
    """Tests for core/portfolio.py Portfolio class."""

    def test_default_weights(self):
        from core.portfolio import Portfolio
        p = Portfolio(tickers=["A", "B", "C"])
        np.testing.assert_array_almost_equal(p.weights, [1/3, 1/3, 1/3])

    def test_n_assets(self):
        from core.portfolio import Portfolio
        p = Portfolio(tickers=["A", "B", "C", "D"])
        assert p.n_assets == 4

    def test_hhi_equal_weights(self):
        from core.portfolio import Portfolio
        p = Portfolio(tickers=["A", "B", "C", "D"])
        assert abs(p.hhi_concentration() - 0.25) < 0.01

    def test_hhi_concentrated(self):
        from core.portfolio import Portfolio
        p = Portfolio(tickers=["A", "B"], weights=np.array([0.9, 0.1]))
        assert p.hhi_concentration() > 0.5

    def test_effective_n(self):
        from core.portfolio import Portfolio
        p = Portfolio(tickers=["A", "B", "C", "D"])
        assert abs(p.effective_n() - 4.0) < 0.01

    def test_returns_from_prices(self, price_data):
        from core.portfolio import Portfolio
        p = Portfolio(tickers=list(price_data.columns), prices=price_data)
        assert p.returns is not None
        assert p.returns.shape[0] == len(price_data) - 1

    def test_portfolio_returns(self, price_data):
        from core.portfolio import Portfolio
        p = Portfolio(tickers=list(price_data.columns), prices=price_data)
        pr = p.portfolio_returns
        assert pr is not None
        assert len(pr) == len(price_data) - 1

    def test_summary(self, price_data):
        from core.portfolio import Portfolio
        p = Portfolio(tickers=list(price_data.columns), prices=price_data)
        s = p.summary()
        assert "tickers" in s
        assert "hhi" in s
        assert "data_points" in s
        assert "date_range" in s
