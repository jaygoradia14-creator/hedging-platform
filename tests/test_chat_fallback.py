"""Tests for chat/fallback.py - comprehensive routing tests."""

import numpy as np
import pytest  # noqa: F401
from types import SimpleNamespace

from chat.fallback import (
    fallback_response,
    _has_action_intent,
    _has_educational_intent,
    _match_general_topic,
)
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
        holdings={},
    )


@pytest.fixture
def empty_session():
    return SimpleNamespace(portfolio=None, regime_df=None, data_loaded=False, chat_history=[], holdings={})


class TestIntentDetection:
    def test_action_intent_invest(self):
        assert _has_action_intent("what stocks to invest in")

    def test_action_intent_buy(self):
        assert _has_action_intent("should i buy apple")

    def test_action_intent_sell(self):
        assert _has_action_intent("should i sell my holdings")

    def test_action_intent_market(self):
        assert _has_action_intent("market outlook for 2024")

    def test_no_action_intent(self):
        assert not _has_action_intent("what is a stock")

    def test_educational_intent(self):
        assert _has_educational_intent("what is a bond")

    def test_educational_explain(self):
        assert _has_educational_intent("explain options trading")

    def test_educational_tell(self):
        assert _has_educational_intent("tell me about crypto")

    def test_no_educational_intent(self):
        assert not _has_educational_intent("best stocks to buy")


class TestGeneralKnowledge:
    def test_stock_topic(self):
        result = _match_general_topic("stock")
        assert result is not None
        assert "stock" in result.lower()

    def test_bond_topic(self):
        result = _match_general_topic("bond")
        assert result is not None
        assert "bond" in result.lower()

    def test_etf_topic(self):
        result = _match_general_topic("etf")
        assert result is not None

    def test_option_topic(self):
        result = _match_general_topic("option")
        assert result is not None

    def test_crypto_topic(self):
        result = _match_general_topic("crypto")
        assert result is not None

    def test_inflation_topic(self):
        result = _match_general_topic("inflation")
        assert result is not None

    def test_no_match(self):
        result = _match_general_topic("xyzzy foobar nonsense")
        assert result is None

    def test_retirement_topic(self):
        result = _match_general_topic("retirement")
        assert result is not None

    def test_rsi_topic(self):
        result = _match_general_topic("rsi")
        assert result is not None

    def test_moving_average_topic(self):
        result = _match_general_topic("moving average")
        assert result is not None

    def test_value_investing_topic(self):
        result = _match_general_topic("value invest")
        assert result is not None


class TestFallbackRouting:
    def test_greeting(self, loaded_session):
        resp = fallback_response("hello", loaded_session)
        assert "advisor" in resp.lower() or "hey" in resp.lower()

    def test_thanks(self, loaded_session):
        resp = fallback_response("thanks a lot", loaded_session)
        assert "welcome" in resp.lower()

    def test_help(self, loaded_session):
        resp = fallback_response("help me", loaded_session)
        assert "correlat" in resp.lower()
        assert "risk" in resp.lower() or "var" in resp.lower()

    def test_action_intent_routes_to_advice(self, loaded_session):
        resp = fallback_response("what stocks should I invest in", loaded_session)
        # Should give investment advice, NOT "What is a Stock?" definition
        assert "stock?" not in resp.lower() or "invest" in resp.lower()

    def test_sell_advice(self, loaded_session):
        resp = fallback_response("should I sell my holdings", loaded_session)
        assert isinstance(resp, str) and len(resp) > 10

    def test_market_outlook(self, loaded_session):
        resp = fallback_response("market outlook", loaded_session)
        assert isinstance(resp, str) and len(resp) > 10

    def test_educational_stock(self, empty_session):
        resp = fallback_response("what is a stock", empty_session)
        assert "stock" in resp.lower()

    def test_educational_bond(self, empty_session):
        resp = fallback_response("explain bonds", empty_session)
        assert "bond" in resp.lower()

    def test_educational_etf(self, empty_session):
        resp = fallback_response("what is an etf", empty_session)
        assert "etf" in resp.lower()

    def test_educational_option(self, loaded_session):
        resp = fallback_response("tell me about options trading", loaded_session)
        assert "option" in resp.lower()

    def test_no_data_prompt(self, empty_session):
        resp = fallback_response("What is my VaR?", empty_session)
        assert "load" in resp.lower() or "finance" in resp.lower()

    def test_correlation_query(self, loaded_session):
        resp = fallback_response("Tell me about correlation", loaded_session)
        assert "diversification" in resp.lower() or "correlation" in resp.lower()

    def test_var_query(self, loaded_session):
        resp = fallback_response("What is my value at risk?", loaded_session)
        assert "var" in resp.lower() or "%" in resp

    def test_regime_query(self, loaded_session):
        resp = fallback_response("What regime are we in?", loaded_session)
        assert "regime" in resp.lower()

    def test_hedge_query(self, loaded_session):
        resp = fallback_response("which asset is the best hedge", loaded_session)
        assert isinstance(resp, str) and len(resp) > 10

    def test_crypto_knowledge(self, empty_session):
        resp = fallback_response("crypto", empty_session)
        assert "crypto" in resp.lower() or "bitcoin" in resp.lower()

    def test_inflation_knowledge(self, empty_session):
        resp = fallback_response("inflation", empty_session)
        assert "inflat" in resp.lower()

    def test_default_response(self, loaded_session):
        resp = fallback_response("xyzzy gibberish random input", loaded_session)
        assert isinstance(resp, str) and len(resp) > 5

    def test_buy_advice_with_data(self, loaded_session):
        resp = fallback_response("best stocks to buy right now", loaded_session)
        assert isinstance(resp, str) and len(resp) > 20

    def test_interest_rate(self, empty_session):
        resp = fallback_response("what is an interest rate", empty_session)
        assert "interest" in resp.lower() or "rate" in resp.lower()

    def test_recession(self, empty_session):
        resp = fallback_response("recession", empty_session)
        assert "recession" in resp.lower() or "economic" in resp.lower()
