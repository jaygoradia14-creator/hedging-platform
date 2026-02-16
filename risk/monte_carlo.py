"""
Monte Carlo simulation module.
Standard Cholesky decomposition and regime-aware simulation.
"""

import numpy as np
import pandas as pd
from typing import Optional


def simulate_paths(
    returns: pd.DataFrame,
    weights: np.ndarray,
    n_simulations: int = 1000,
    n_days: int = 252,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Standard Monte Carlo using Cholesky decomposition.

    Returns:
        Array of shape (n_simulations, n_days) with cumulative portfolio returns.
    """
    if seed is not None:
        np.random.seed(seed)

    mu = returns.mean().values
    cov = returns.cov().values

    L = np.linalg.cholesky(cov)

    sims = np.zeros((n_simulations, n_days))
    for i in range(n_simulations):
        daily = np.zeros(n_days)
        for t in range(n_days):
            z = np.random.randn(len(mu))
            asset_returns = mu + L @ z
            daily[t] = np.dot(weights, asset_returns)
        sims[i] = np.cumsum(daily)

    return sims


def regime_aware_simulation(
    returns: pd.DataFrame,
    weights: np.ndarray,
    regime_df: pd.DataFrame,
    n_simulations: int = 1000,
    n_days: int = 252,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Regime-aware Monte Carlo: uses per-regime mean/cov and transition probs.

    Returns:
        Array of shape (n_simulations, n_days) with cumulative portfolio returns.
    """
    if seed is not None:
        np.random.seed(seed)

    common = returns.index.intersection(regime_df.index)
    ret_aligned = returns.loc[common]
    reg_aligned = regime_df.loc[common, "regime"]

    regimes = reg_aligned.unique().tolist()

    # Per-regime statistics
    regime_params = {}
    for r in regimes:
        mask = reg_aligned == r
        r_ret = ret_aligned[mask]
        if len(r_ret) < 5:
            continue
        mu = r_ret.mean().values
        cov = r_ret.cov().values
        # Make cov positive definite
        eigvals = np.linalg.eigvalsh(cov)
        if eigvals.min() <= 0:
            cov += np.eye(len(mu)) * (abs(eigvals.min()) + 1e-8)
        L = np.linalg.cholesky(cov)
        regime_params[r] = {"mu": mu, "L": L}

    if not regime_params:
        return simulate_paths(returns, weights, n_simulations, n_days, seed)

    # Transition matrix
    regime_list = list(regime_params.keys())
    n_reg = len(regime_list)
    trans = np.ones((n_reg, n_reg)) / n_reg  # uniform prior

    for i in range(len(reg_aligned) - 1):
        curr = reg_aligned.iloc[i]
        nxt = reg_aligned.iloc[i + 1]
        if curr in regime_list and nxt in regime_list:
            ci = regime_list.index(curr)
            ni = regime_list.index(nxt)
            trans[ci, ni] += 1

    trans = trans / trans.sum(axis=1, keepdims=True)

    # Stationary distribution for starting regime
    regime_counts = reg_aligned.value_counts()
    start_probs = np.array([regime_counts.get(r, 1) for r in regime_list], dtype=float)
    start_probs /= start_probs.sum()

    sims = np.zeros((n_simulations, n_days))
    for i in range(n_simulations):
        curr_idx = np.random.choice(n_reg, p=start_probs)
        daily = np.zeros(n_days)
        for t in range(n_days):
            r = regime_list[curr_idx]
            p = regime_params[r]
            z = np.random.randn(len(p["mu"]))
            asset_returns = p["mu"] + p["L"] @ z
            daily[t] = np.dot(weights, asset_returns)
            curr_idx = np.random.choice(n_reg, p=trans[curr_idx])
        sims[i] = np.cumsum(daily)

    return sims


def simulation_statistics(sims: np.ndarray) -> dict:
    """Compute summary statistics from simulation paths.

    Args:
        sims: Array of shape (n_simulations, n_days), cumulative returns.

    Returns:
        Dict with percentiles and summary stats for the terminal distribution.
    """
    terminal = sims[:, -1]
    percentiles = [5, 25, 50, 75, 95]
    pcts = {f"p{p}": float(np.percentile(terminal, p)) for p in percentiles}
    pcts["mean"] = float(terminal.mean())
    pcts["std"] = float(terminal.std())
    pcts["prob_loss"] = float((terminal < 0).mean())
    return pcts


def percentile_bands(sims: np.ndarray) -> dict:
    """Compute percentile bands across all time steps for fan chart.

    Returns:
        Dict with keys p5, p25, p50, p75, p95 - each an array of length n_days.
    """
    return {
        f"p{p}": np.percentile(sims, p, axis=0)
        for p in [5, 25, 50, 75, 95]
    }
