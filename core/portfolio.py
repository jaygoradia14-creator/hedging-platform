"""
Portfolio management module.
Provides a Portfolio dataclass and session state integration for Streamlit.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Portfolio:
    """Represents a portfolio of assets with weights and price/return data."""

    tickers: List[str] = field(default_factory=lambda: ["SPY", "TLT", "GLD"])
    weights: Optional[np.ndarray] = None
    prices: Optional[pd.DataFrame] = None
    _returns: Optional[pd.DataFrame] = None

    def __post_init__(self):
        if self.weights is None:
            self.weights = np.ones(len(self.tickers)) / len(self.tickers)
        self.weights = np.array(self.weights)

    @property
    def returns(self) -> Optional[pd.DataFrame]:
        if self._returns is not None:
            return self._returns
        if self.prices is not None:
            self._returns = np.log(self.prices / self.prices.shift(1)).dropna()
            return self._returns
        return None

    @returns.setter
    def returns(self, value):
        self._returns = value

    @property
    def n_assets(self) -> int:
        return len(self.tickers)

    @property
    def portfolio_returns(self) -> Optional[pd.Series]:
        """Weighted portfolio returns."""
        if self.returns is None:
            return None
        return (self.returns * self.weights).sum(axis=1)

    def hhi_concentration(self) -> float:
        """Herfindahl-Hirschman Index for portfolio concentration.
        Ranges from 1/n (perfectly diversified) to 1 (single asset).
        """
        return float(np.sum(self.weights ** 2))

    def effective_n(self) -> float:
        """Effective number of assets (inverse HHI)."""
        hhi = self.hhi_concentration()
        return 1.0 / hhi if hhi > 0 else 0.0

    def summary(self) -> dict:
        """Return a summary dict for display or chat context."""
        info = {
            "tickers": self.tickers,
            "weights": {t: round(float(w), 4) for t, w in zip(self.tickers, self.weights)},
            "n_assets": self.n_assets,
            "hhi": round(self.hhi_concentration(), 4),
            "effective_n": round(self.effective_n(), 2),
        }
        if self.prices is not None:
            info["data_points"] = len(self.prices)
            info["date_range"] = f"{self.prices.index[0].date()} to {self.prices.index[-1].date()}"
        return info


def init_session_state():
    """Initialize Streamlit session state with default portfolio and chat history."""
    import streamlit as st

    if "portfolio" not in st.session_state:
        st.session_state.portfolio = Portfolio()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "regime_df" not in st.session_state:
        st.session_state.regime_df = None
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False


def update_portfolio(tickers: List[str], weights: Optional[np.ndarray] = None):
    """Update the portfolio in session state and reset computed data."""
    import streamlit as st

    st.session_state.portfolio = Portfolio(tickers=tickers, weights=weights)
    st.session_state.data_loaded = False
    st.session_state.regime_df = None
