"""Tests for core/signals.py - Signal dataclass reasoning field and signal generation."""

import numpy as np

from core.signals import (
    Signal,
    SignalType,
    regime_signals,
    holdings_signals,
    portfolio_signals,
    generate_all_signals,
    calculate_portfolio_health_score,
)


class TestSignalDataclass:
    """Tests for the Signal dataclass reasoning field."""

    def test_reasoning_field_exists(self):
        sig = Signal(
            ticker="AAPL",
            signal_type=SignalType.OPPORTUNITY,
            title="Test",
            description="Test desc",
            source="Test",
        )
        assert hasattr(sig, "reasoning")

    def test_reasoning_default_empty(self):
        sig = Signal(
            ticker="AAPL",
            signal_type=SignalType.OPPORTUNITY,
            title="Test",
            description="Test desc",
            source="Test",
        )
        assert sig.reasoning == ""

    def test_reasoning_can_be_set(self):
        sig = Signal(
            ticker="AAPL",
            signal_type=SignalType.OPPORTUNITY,
            title="Test",
            description="Test desc",
            source="Test",
            reasoning="This is a plain-English explanation.",
        )
        assert sig.reasoning == "This is a plain-English explanation."


class TestRegimeSignalsReasoning:
    """Tests that regime signals include reasoning."""

    def test_crisis_has_reasoning(self, regime_df):
        # Force crisis regime
        regime_df["regime"] = "Crisis"
        signals = regime_signals(regime_df)
        assert len(signals) >= 1
        assert signals[0].reasoning != ""
        assert "stress" in signals[0].reasoning.lower() or "crisis" in signals[0].reasoning.lower() or "safer" in signals[0].reasoning.lower()

    def test_low_vol_has_reasoning(self, regime_df):
        regime_df["regime"] = "Low Volatility"
        signals = regime_signals(regime_df)
        assert len(signals) >= 1
        assert signals[0].reasoning != ""

    def test_normal_has_reasoning(self, regime_df):
        regime_df["regime"] = "Normal"
        signals = regime_signals(regime_df)
        assert len(signals) >= 1
        assert signals[0].reasoning != ""


class TestHoldingsSignalsReasoning:
    """Tests that holdings signals include reasoning."""

    def test_large_gain_reasoning(self):
        holdings = {"AAPL": {"shares": 10, "buy_price": 100}}
        prices = {"AAPL": 200}  # 100% gain
        signals = holdings_signals(holdings, prices)
        assert len(signals) >= 1
        assert signals[0].reasoning != ""
        assert "AAPL" in signals[0].reasoning

    def test_cut_losses_reasoning(self):
        holdings = {"AAPL": {"shares": 10, "buy_price": 100}}
        prices = {"AAPL": 70}  # -30% loss
        signals = holdings_signals(holdings, prices)
        assert len(signals) >= 1
        assert signals[0].reasoning != ""
        assert "dropped" in signals[0].reasoning.lower() or "down" in signals[0].reasoning.lower()

    def test_no_signal_no_reasoning(self):
        holdings = {"AAPL": {"shares": 10, "buy_price": 100}}
        prices = {"AAPL": 105}  # 5% gain, no signal
        signals = holdings_signals(holdings, prices)
        assert len(signals) == 0


class TestGenerateAllSignals:
    """Tests for generate_all_signals including reasoning."""

    def test_all_signals_have_reasoning_field(self, price_data, regime_df):
        from core.portfolio import Portfolio
        p = Portfolio(tickers=list(price_data.columns), prices=price_data)
        signals = generate_all_signals(p, regime_df)
        for sig in signals:
            assert hasattr(sig, "reasoning")

    def test_health_score_range(self, price_data, regime_df):
        from core.portfolio import Portfolio
        p = Portfolio(tickers=list(price_data.columns), prices=price_data)
        signals = generate_all_signals(p, regime_df)
        score = calculate_portfolio_health_score(signals)
        assert 0 <= score <= 100
