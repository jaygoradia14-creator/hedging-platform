"""
VaR and CVaR computation module.
Historical, parametric, and regime-conditional approaches.
"""

import numpy as np
import pandas as pd
from typing import Optional
from scipy import stats as sp_stats


def historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Historical Value-at-Risk (loss is positive)."""
    return float(-np.percentile(returns.dropna(), (1 - confidence) * 100))


def historical_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    """Historical Conditional VaR (Expected Shortfall)."""
    var = historical_var(returns, confidence)
    tail = returns[returns <= -var]
    if len(tail) == 0:
        return var
    return float(-tail.mean())


def parametric_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Parametric (Gaussian) VaR."""
    mu = returns.mean()
    sigma = returns.std()
    z = sp_stats.norm.ppf(1 - confidence)
    return float(-(mu + z * sigma))


def portfolio_var(
    returns: pd.DataFrame,
    weights: np.ndarray,
    confidence: float = 0.95,
    method: str = "historical",
) -> float:
    """VaR for a weighted portfolio."""
    port_ret = (returns * weights).sum(axis=1)
    if method == "parametric":
        return parametric_var(port_ret, confidence)
    return historical_var(port_ret, confidence)


def portfolio_cvar(
    returns: pd.DataFrame,
    weights: np.ndarray,
    confidence: float = 0.95,
) -> float:
    """CVaR for a weighted portfolio."""
    port_ret = (returns * weights).sum(axis=1)
    return historical_cvar(port_ret, confidence)


def regime_conditional_var(
    returns: pd.DataFrame,
    weights: np.ndarray,
    regime_df: pd.DataFrame,
    confidence: float = 0.95,
) -> dict:
    """VaR computed separately for each regime.

    Returns:
        dict mapping regime name -> VaR value
    """
    port_ret = (returns * weights).sum(axis=1)
    common = port_ret.index.intersection(regime_df.index)
    port_ret = port_ret.loc[common]
    regime_series = regime_df.loc[common, "regime"]

    result = {}
    for regime_name in regime_series.unique():
        mask = regime_series == regime_name
        r = port_ret[mask]
        if len(r) >= 10:
            result[regime_name] = historical_var(r, confidence)
        else:
            result[regime_name] = np.nan
    return result


def var_cvar_summary(
    returns: pd.DataFrame,
    weights: np.ndarray,
    confidence: float = 0.95,
) -> dict:
    """Convenience function returning VaR, CVaR, parametric VaR."""
    port_ret = (returns * weights).sum(axis=1)
    return {
        "historical_var": historical_var(port_ret, confidence),
        "historical_cvar": historical_cvar(port_ret, confidence),
        "parametric_var": parametric_var(port_ret, confidence),
        "confidence": confidence,
    }
