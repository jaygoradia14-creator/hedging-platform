"""Tests for chat/fallback.py - 5 tests."""

import numpy as np
import pandas as pd
import pytest
from types import SimpleNamespace

from chat.fallback import fallback_response
from core.portfolio import Portfolio


@pytest.fixture
def loaded_session(returns_data, price_data, regime_df):
    """Simulate a loaded session state."""
    portfolio = Portfolio(
        tickers=list(price_data.columns),
        weights=np.ones(5) / 5,
        prices=price_data,
    )
    portfolio.returns = returns_data
    return SimpleNamespace(
        portfolio=portfolio,
        regime_df=regime_df,
        data_loaded=True,
        chat_history=[],
    )


@pytest.fixture
def empty_session():
    return SimpleNamespace(portfolio=None, regime_df=None, data_loaded=False, chat_history=[])


class TestFallbackRouting:
    def test_no_data_prompt(self, empty_session):
        resp = fallback_response("What is my VaR?", empty_session)
        assert "load" in resp.lower()

    def test_correlation_query(self, loaded_session):
        resp = fallback_response("Tell me about correlation", loaded_session)
        assert "diversification" in resp.lower() or "correlation" in resp.lower()

    def test_var_query(self, loaded_session):
        resp = fallback_response("What is my value at risk?", loaded_session)
        assert "var" in resp.lower() or "%" in resp

    def test_regime_query(self, loaded_session):
        resp = fallback_response("What regime are we in?", loaded_session)
        assert "regime" in resp.lower()

    def test_help_query(self, loaded_session):
        resp = fallback_response("help me", loaded_session)
        assert "correlation" in resp.lower()
        assert "var" in resp.lower()
