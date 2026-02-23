"""
Portfolio management module.
Provides a Portfolio dataclass and session state integration for Streamlit.
"""

import json
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


def _holdings_path() -> Path:
    """Return writable path for holdings persistence."""
    local = Path("holdings.json")
    try:
        local.touch(exist_ok=True)
        return local
    except OSError:
        return Path("/tmp/holdings.json")


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


def save_holdings():
    """Save holdings to JSON file (uses /tmp on Streamlit Cloud)."""
    import streamlit as st
    try:
        path = _holdings_path()
        with open(path, "w") as f:
            json.dump(st.session_state.holdings, f)
    except OSError:
        pass


def load_holdings():
    """Load holdings from JSON file if it exists."""
    try:
        path = _holdings_path()
        if path.exists():
            with open(path) as f:
                return json.load(f)
    except (OSError, json.JSONDecodeError):
        pass
    return {}


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
    if "holdings" not in st.session_state:
        st.session_state.holdings = load_holdings()


def update_portfolio(tickers: List[str], weights: Optional[np.ndarray] = None):
    """Update the portfolio in session state and reset computed data."""
    import streamlit as st

    st.session_state.portfolio = Portfolio(tickers=tickers, weights=weights)
    st.session_state.data_loaded = False
    st.session_state.regime_df = None


def add_holding(ticker: str, shares: float, buy_price: float):
    """Add or update a holding in session state."""
    import streamlit as st

    holdings = st.session_state.holdings
    if ticker in holdings:
        # Average cost basis
        existing = holdings[ticker]
        total_shares = existing["shares"] + shares
        total_cost = (existing["shares"] * existing["buy_price"]) + (shares * buy_price)
        holdings[ticker] = {"shares": total_shares, "buy_price": total_cost / total_shares}
    else:
        holdings[ticker] = {"shares": shares, "buy_price": buy_price}


def sell_holding(ticker: str, shares_to_sell: float):
    """Sell shares of a holding. Remove the holding if shares reach 0."""
    import streamlit as st

    holdings = st.session_state.holdings
    if ticker not in holdings:
        return
    remaining = holdings[ticker]["shares"] - shares_to_sell
    if remaining <= 0:
        del holdings[ticker]
    else:
        holdings[ticker]["shares"] = remaining


def get_holdings_summary(current_prices: dict) -> List[dict]:
    """Build holdings summary with P&L using current prices.

    Args:
        current_prices: {ticker: current_price} mapping.

    Returns:
        List of dicts with ticker, shares, buy_price, current_price, value, pnl, pnl_pct.
    """
    import streamlit as st

    rows = []
    for ticker, info in st.session_state.holdings.items():
        cur = current_prices.get(ticker)
        if cur is None:
            continue
        value = info["shares"] * cur
        cost = info["shares"] * info["buy_price"]
        pnl = value - cost
        pnl_pct = (pnl / cost * 100) if cost != 0 else 0.0
        rows.append({
            "Ticker": ticker,
            "Shares": info["shares"],
            "Buy Price": info["buy_price"],
            "Current Price": cur,
            "Value": value,
            "P&L": pnl,
            "P&L %": pnl_pct,
        })
    return rows
