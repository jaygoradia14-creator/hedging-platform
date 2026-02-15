"""
Shared fixtures for the hedging platform test suite.
All data is synthetic (seeded np.random) - zero network calls.
"""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def seed():
    """Fixed random seed for determinism."""
    np.random.seed(42)
    return 42


@pytest.fixture
def price_data(seed):
    """Synthetic 5-asset price data: 504 trading days, realistic drift & vol."""
    n_days = 504
    tickers = ["SPY", "TLT", "GLD", "QQQ", "EFA"]
    dates = pd.bdate_range(start="2021-01-04", periods=n_days)

    # Annualized params
    drifts = np.array([0.08, 0.02, 0.04, 0.10, 0.05]) / 252
    vols = np.array([0.18, 0.12, 0.15, 0.22, 0.20]) / np.sqrt(252)

    # Correlated shocks via Cholesky
    corr = np.array([
        [1.0,  -0.3,  0.05,  0.85,  0.70],
        [-0.3,  1.0, -0.05, -0.25, -0.20],
        [0.05, -0.05,  1.0,  0.10,  0.15],
        [0.85, -0.25,  0.10,  1.0,   0.65],
        [0.70, -0.20,  0.15,  0.65,  1.0],
    ])
    L = np.linalg.cholesky(corr)

    log_returns = np.zeros((n_days, 5))
    for t in range(n_days):
        z = np.random.randn(5)
        log_returns[t] = drifts + vols * (L @ z)

    prices = np.exp(np.cumsum(log_returns, axis=0)) * 100
    return pd.DataFrame(prices, index=dates, columns=tickers)


@pytest.fixture
def returns_data(price_data):
    """Log returns derived from synthetic price data."""
    return np.log(price_data / price_data.shift(1)).dropna()


@pytest.fixture
def simple_returns(price_data):
    """Simple (arithmetic) returns."""
    return price_data.pct_change().dropna()


@pytest.fixture
def equal_weights():
    """Equal weights for 5 assets."""
    return np.ones(5) / 5


@pytest.fixture
def regime_df(returns_data):
    """Pre-computed regime DataFrame for tests."""
    from core.regime_detector import detect_regime
    return detect_regime(returns_data)
