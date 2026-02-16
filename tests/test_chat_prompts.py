"""Tests for chat/prompts.py - context builders."""

import numpy as np
import pytest
from types import SimpleNamespace

from chat.prompts import (
    build_portfolio_context,
    build_analysis_context,
    build_system_message,
)
from core.portfolio import Portfolio


@pytest.fixture
def loaded_session(returns_data, price_data, regime_df):
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
        holdings={},
    )


@pytest.fixture
def empty_session():
    return SimpleNamespace(portfolio=None, regime_df=None, data_loaded=False, holdings={})


class TestContextBuilders:
    def test_portfolio_context_no_data(self, empty_session):
        ctx = build_portfolio_context(empty_session)
        assert "no portfolio" in ctx.lower()

    def test_portfolio_context_with_data(self, loaded_session):
        ctx = build_portfolio_context(loaded_session)
        assert "SPY" in ctx
        assert "HHI" in ctx

    def test_analysis_context_no_data(self, empty_session):
        ctx = build_analysis_context(empty_session)
        assert "no analysis" in ctx.lower()

    def test_analysis_context_with_data(self, loaded_session):
        ctx = build_analysis_context(loaded_session)
        assert "regime" in ctx.lower() or "var" in ctx.lower()

    def test_system_message_structure(self, loaded_session):
        msg = build_system_message(loaded_session)
        assert "financial advisor" in msg.lower()
        assert "SPY" in msg
