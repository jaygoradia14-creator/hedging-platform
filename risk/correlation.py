"""
Correlation analysis module with emphasis on tail dependence and regime-aware metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional


def calculate_correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Calculate standard Pearson correlation matrix."""
    return returns.corr()


def calculate_rolling_correlation_matrix(
    returns: pd.DataFrame,
    window: int = 63
) -> Dict[pd.Timestamp, pd.DataFrame]:
    """
    Calculate rolling correlation matrices.

    Returns:
        Dictionary mapping dates to correlation matrices
    """
    matrices = {}
    for i in range(window, len(returns)):
        window_returns = returns.iloc[i - window:i]
        matrices[returns.index[i]] = window_returns.corr()
    return matrices


def calculate_tail_correlation(
    returns: pd.DataFrame,
    quantile: float = 0.05
) -> pd.DataFrame:
    """
    Calculate correlation during tail events (stress periods).

    This captures how assets correlate during market stress,
    which is typically higher than normal correlations.

    Args:
        returns: DataFrame of returns
        quantile: Tail threshold (0.05 = bottom 5% of market returns)

    Returns:
        Correlation matrix during tail events
    """
    # Use first column (usually SPY) as market proxy
    market_col = returns.columns[0]
    market_returns = returns[market_col]

    # Identify tail events
    threshold = market_returns.quantile(quantile)
    tail_mask = market_returns <= threshold

    # Calculate correlation during tail events
    tail_returns = returns[tail_mask]

    if len(tail_returns) < 10:
        return calculate_correlation_matrix(returns)

    return tail_returns.corr()


def calculate_upside_downside_correlation(
    returns: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculate separate correlations for up and down market days.

    Returns:
        Tuple of (downside_correlation, upside_correlation)
    """
    market_col = returns.columns[0]

    down_mask = returns[market_col] < 0
    up_mask = returns[market_col] >= 0

    down_corr = returns[down_mask].corr() if down_mask.sum() > 10 else returns.corr()
    up_corr = returns[up_mask].corr() if up_mask.sum() > 10 else returns.corr()

    return down_corr, up_corr


def calculate_correlation_asymmetry(returns: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate asymmetry between downside and upside correlations.
    Positive values = higher correlation during downturns (bad for hedging).
    """
    down_corr, up_corr = calculate_upside_downside_correlation(returns)
    return down_corr - up_corr


def calculate_diversification_ratio(
    returns: pd.DataFrame,
    weights: Optional[np.ndarray] = None
) -> float:
    """
    Calculate the diversification ratio of a portfolio.
    DR = weighted avg of individual vols / portfolio vol

    DR > 1 indicates diversification benefit.
    DR approaching 1 during stress = diversification failing.
    """
    if weights is None:
        weights = np.ones(len(returns.columns)) / len(returns.columns)

    weights = np.array(weights)

    # Individual volatilities
    individual_vols = returns.std()
    weighted_avg_vol = np.dot(weights, individual_vols)

    # Portfolio volatility
    cov_matrix = returns.cov()
    portfolio_var = np.dot(weights.T, np.dot(cov_matrix, weights))
    portfolio_vol = np.sqrt(portfolio_var)

    return weighted_avg_vol / portfolio_vol if portfolio_vol > 0 else 1.0


def calculate_correlation_heatmap_data(
    returns: pd.DataFrame,
    regime_df: Optional[pd.DataFrame] = None,
    regime_filter: Optional[str] = None
) -> pd.DataFrame:
    """
    Prepare correlation data for heatmap visualization.

    Args:
        returns: Asset returns
        regime_df: Regime classification DataFrame
        regime_filter: Optional regime to filter by

    Returns:
        Correlation matrix for visualization
    """
    if regime_df is not None and regime_filter is not None:
        # Filter returns by regime
        mask = regime_df['regime'] == regime_filter
        filtered_dates = regime_df.index[mask]
        common_dates = returns.index.intersection(filtered_dates)
        returns = returns.loc[common_dates]

    return returns.corr()


def get_correlation_stability(
    returns: pd.DataFrame,
    window: int = 63
) -> pd.DataFrame:
    """
    Measure how stable correlations are over time.
    High instability = correlations are regime-dependent.

    Returns:
        DataFrame with rolling correlation std for each pair
    """
    rolling_corr = returns.rolling(window=window).corr()

    # Calculate std of correlations over time for each pair
    stability_data = {}

    for i, col1 in enumerate(returns.columns):
        for col2 in returns.columns[i + 1:]:
            pair_name = f"{col1}-{col2}"
            try:
                pair_corr = rolling_corr.loc[:, col1].loc[:, col2]
                stability_data[pair_name] = pair_corr.std()
            except Exception:
                pass

    return pd.Series(stability_data).sort_values(ascending=False)
