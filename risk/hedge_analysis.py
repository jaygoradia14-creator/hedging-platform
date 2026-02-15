"""
Hedge effectiveness analysis module.
Compares hedging candidates, computes optimal hedge ratios, and measures VaR impact.
"""

import numpy as np
import pandas as pd
from typing import List, Optional

from risk.var_cvar import historical_var, historical_cvar


def hedge_effectiveness(
    portfolio_returns: pd.Series,
    hedge_returns: pd.Series,
) -> dict:
    """Measure how effective a hedge asset is.

    Returns dict with:
        - correlation: standard correlation
        - tail_correlation: correlation during worst 5% portfolio days
        - beta: hedge beta to portfolio
        - variance_reduction: fraction of portfolio variance reduced at optimal ratio
    """
    common = portfolio_returns.index.intersection(hedge_returns.index)
    pr = portfolio_returns.loc[common]
    hr = hedge_returns.loc[common]

    corr = float(pr.corr(hr))

    # Tail correlation
    threshold = pr.quantile(0.05)
    tail_mask = pr <= threshold
    if tail_mask.sum() >= 10:
        tail_corr = float(pr[tail_mask].corr(hr[tail_mask]))
    else:
        tail_corr = corr

    # Beta (OLS)
    cov = np.cov(pr, hr)[0, 1]
    var_p = np.var(pr)
    beta = cov / var_p if var_p > 0 else 0.0

    # Variance reduction at optimal ratio
    var_h = np.var(hr)
    if var_h > 0 and var_p > 0:
        optimal_ratio = -cov / var_h
        hedged_var = var_p + optimal_ratio ** 2 * var_h + 2 * optimal_ratio * cov
        variance_reduction = 1 - hedged_var / var_p
    else:
        variance_reduction = 0.0

    return {
        "correlation": corr,
        "tail_correlation": tail_corr,
        "beta": float(beta),
        "variance_reduction": float(max(0, variance_reduction)),
    }


def compare_hedges(
    portfolio_returns: pd.Series,
    hedge_candidates: pd.DataFrame,
) -> pd.DataFrame:
    """Compare multiple hedge candidates.

    Args:
        portfolio_returns: Series of portfolio returns.
        hedge_candidates: DataFrame where each column is a hedge candidate's returns.

    Returns:
        DataFrame with effectiveness metrics for each candidate, sorted by variance_reduction.
    """
    rows = []
    for col in hedge_candidates.columns:
        metrics = hedge_effectiveness(portfolio_returns, hedge_candidates[col])
        metrics["ticker"] = col
        rows.append(metrics)

    df = pd.DataFrame(rows).set_index("ticker")
    return df.sort_values("variance_reduction", ascending=False)


def optimal_hedge_ratio(
    portfolio_returns: pd.Series,
    hedge_returns: pd.Series,
) -> float:
    """Optimal hedge ratio via OLS (minimum variance).

    h* = -Cov(P, H) / Var(H)
    """
    common = portfolio_returns.index.intersection(hedge_returns.index)
    pr = portfolio_returns.loc[common]
    hr = hedge_returns.loc[common]

    cov = np.cov(pr, hr)[0, 1]
    var_h = np.var(hr)
    if var_h == 0:
        return 0.0
    return float(-cov / var_h)


def var_impact(
    portfolio_returns: pd.Series,
    hedge_returns: pd.Series,
    hedge_ratio: float,
    confidence: float = 0.95,
) -> dict:
    """Compute before/after VaR when adding hedge at given ratio.

    Returns:
        dict with var_before, var_after, cvar_before, cvar_after, reduction_pct.
    """
    common = portfolio_returns.index.intersection(hedge_returns.index)
    pr = portfolio_returns.loc[common]
    hr = hedge_returns.loc[common]

    hedged = pr + hedge_ratio * hr

    var_before = historical_var(pr, confidence)
    var_after = historical_var(hedged, confidence)
    cvar_before = historical_cvar(pr, confidence)
    cvar_after = historical_cvar(hedged, confidence)

    reduction = (var_before - var_after) / var_before if var_before > 0 else 0.0

    return {
        "var_before": var_before,
        "var_after": var_after,
        "cvar_before": cvar_before,
        "cvar_after": cvar_after,
        "reduction_pct": float(reduction),
        "hedge_ratio": hedge_ratio,
    }
