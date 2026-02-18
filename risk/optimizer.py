"""
Mean-variance portfolio optimization (Markowitz Efficient Frontier).
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Tuple


def portfolio_performance(weights: np.ndarray, mean_returns: np.ndarray,
                          cov_matrix: np.ndarray, risk_free: float = 0.0
                          ) -> Tuple[float, float, float]:
    """Calculate annualized return, volatility, and Sharpe ratio."""
    port_return = np.sum(mean_returns * weights) * 252
    port_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix * 252, weights)))
    sharpe = (port_return - risk_free) / port_vol if port_vol > 0 else 0.0
    return port_return, port_vol, sharpe


def min_variance_portfolio(returns: pd.DataFrame) -> dict:
    """Find the minimum variance portfolio."""
    n = returns.shape[1]
    mean_ret = returns.mean().values
    cov = returns.cov().values

    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
    bounds = tuple((0.0, 1.0) for _ in range(n))
    x0 = np.ones(n) / n

    result = minimize(
        lambda w: np.sqrt(np.dot(w, np.dot(cov * 252, w))),
        x0, method="SLSQP", bounds=bounds, constraints=constraints,
    )
    ret, vol, sharpe = portfolio_performance(result.x, mean_ret, cov)
    return {"weights": result.x, "return": ret, "volatility": vol, "sharpe": sharpe}


def max_sharpe_portfolio(returns: pd.DataFrame,
                         risk_free: float = 0.02) -> dict:
    """Find the maximum Sharpe ratio portfolio."""
    n = returns.shape[1]
    mean_ret = returns.mean().values
    cov = returns.cov().values

    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
    bounds = tuple((0.0, 1.0) for _ in range(n))
    x0 = np.ones(n) / n

    result = minimize(
        lambda w: -portfolio_performance(w, mean_ret, cov, risk_free)[2],
        x0, method="SLSQP", bounds=bounds, constraints=constraints,
    )
    ret, vol, sharpe = portfolio_performance(result.x, mean_ret, cov, risk_free)
    return {"weights": result.x, "return": ret, "volatility": vol, "sharpe": sharpe}


def efficient_frontier(returns: pd.DataFrame, n_points: int = 50,
                       risk_free: float = 0.02) -> dict:
    """Compute the efficient frontier curve.

    Returns dict with arrays: returns, volatilities, sharpes, weights.
    """
    n = returns.shape[1]
    mean_ret = returns.mean().values
    cov = returns.cov().values

    # Find return range from min-variance to max-return single asset
    mv = min_variance_portfolio(returns)
    min_ret = mv["return"]
    max_ret = float(np.max(mean_ret * 252)) * 1.1  # slight buffer

    target_returns = np.linspace(min_ret, max_ret, n_points)
    ef_vols = []
    ef_rets = []
    ef_sharpes = []
    ef_weights = []

    for target in target_returns:
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
            {"type": "eq", "fun": lambda w, t=target: np.sum(w * mean_ret) * 252 - t},
        ]
        bounds = tuple((0.0, 1.0) for _ in range(n))
        x0 = np.ones(n) / n

        result = minimize(
            lambda w: np.sqrt(np.dot(w, np.dot(cov * 252, w))),
            x0, method="SLSQP", bounds=bounds, constraints=constraints,
        )
        if result.success:
            ret, vol, sharpe = portfolio_performance(result.x, mean_ret, cov, risk_free)
            ef_rets.append(ret)
            ef_vols.append(vol)
            ef_sharpes.append(sharpe)
            ef_weights.append(result.x)

    return {
        "returns": np.array(ef_rets),
        "volatilities": np.array(ef_vols),
        "sharpes": np.array(ef_sharpes),
        "weights": ef_weights,
    }


def random_portfolios(returns: pd.DataFrame, n_portfolios: int = 2000,
                      risk_free: float = 0.02, seed: int = 42) -> dict:
    """Generate random portfolio allocations for scatter plot.

    Returns dict with arrays: returns, volatilities, sharpes.
    """
    rng = np.random.default_rng(seed)
    n = returns.shape[1]
    mean_ret = returns.mean().values
    cov = returns.cov().values

    all_rets = []
    all_vols = []
    all_sharpes = []

    for _ in range(n_portfolios):
        w = rng.random(n)
        w /= w.sum()
        ret, vol, sharpe = portfolio_performance(w, mean_ret, cov, risk_free)
        all_rets.append(ret)
        all_vols.append(vol)
        all_sharpes.append(sharpe)

    return {
        "returns": np.array(all_rets),
        "volatilities": np.array(all_vols),
        "sharpes": np.array(all_sharpes),
    }
