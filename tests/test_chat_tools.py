"""Tests for chat/tools.py - tool execution."""

import json
import numpy as np
import pytest
from types import SimpleNamespace

from chat.tools import execute_tool, TOOL_DEFINITIONS
from core.portfolio import Portfolio


@pytest.fixture
def session_with_data(returns_data, price_data, regime_df):
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


class TestToolDefinitions:
    def test_five_tools_defined(self):
        assert len(TOOL_DEFINITIONS) == 5

    def test_tool_names(self):
        names = {t["function"]["name"] for t in TOOL_DEFINITIONS}
        assert names == {
            "get_correlation_matrix", "get_var_metrics",
            "compare_hedges", "get_regime_status", "get_holdings",
        }


class TestExecuteTool:
    def test_no_portfolio(self, empty_session):
        result = json.loads(execute_tool("get_var_metrics", {}, empty_session))
        assert "error" in result

    def test_correlation_normal(self, session_with_data):
        result = execute_tool("get_correlation_matrix", {}, session_with_data)
        data = json.loads(result)
        assert "SPY" in data

    def test_correlation_tail(self, session_with_data):
        result = execute_tool("get_correlation_matrix", {"tail": True}, session_with_data)
        data = json.loads(result)
        assert "SPY" in data

    def test_var_metrics(self, session_with_data):
        result = json.loads(execute_tool("get_var_metrics", {}, session_with_data))
        assert "historical_var" in result
        assert "historical_cvar" in result
        assert result["confidence"] == 0.95

    def test_var_metrics_custom_conf(self, session_with_data):
        result = json.loads(execute_tool("get_var_metrics", {"confidence": 0.99}, session_with_data))
        assert result["confidence"] == 0.99

    def test_compare_hedges(self, session_with_data):
        result = execute_tool("compare_hedges", {}, session_with_data)
        data = json.loads(result)
        assert len(data) > 0

    def test_regime_status(self, session_with_data):
        result = json.loads(execute_tool("get_regime_status", {}, session_with_data))
        assert "current_regime" in result
        assert "statistics" in result

    def test_regime_status_no_data(self, session_with_data):
        session_with_data.regime_df = None
        result = json.loads(execute_tool("get_regime_status", {}, session_with_data))
        assert "error" in result

    def test_holdings_empty(self, session_with_data):
        result = json.loads(execute_tool("get_holdings", {}, session_with_data))
        assert result["holdings"] == []

    def test_unknown_tool(self, session_with_data):
        result = json.loads(execute_tool("nonexistent", {}, session_with_data))
        assert "error" in result
        assert "Unknown tool" in result["error"]
