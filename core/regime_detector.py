"""
Regime detection module using volatility and correlation signals.
Identifies market regimes: Low Vol, Normal, High Vol, Crisis
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from enum import Enum


class MarketRegime(Enum):
    LOW_VOL = "Low Volatility"
    NORMAL = "Normal"
    HIGH_VOL = "High Volatility"
    CRISIS = "Crisis"


def calculate_rolling_volatility(
    returns: pd.DataFrame,
    window: int = 21
) -> pd.DataFrame:
    """Calculate rolling annualized volatility."""
    return returns.rolling(window=window).std() * np.sqrt(252)


def calculate_rolling_correlation(
    returns: pd.DataFrame,
    window: int = 63
) -> pd.DataFrame:
    """
    Calculate rolling average pairwise correlation.
    Returns a Series of average correlations over time.
    """
    rolling_corr = returns.rolling(window=window).corr()

    # Calculate average correlation at each timestamp
    avg_corr = []
    dates = returns.index[window - 1:]

    for date in dates:
        try:
            corr_matrix = rolling_corr.loc[date]
            if isinstance(corr_matrix, pd.DataFrame):
                # Get upper triangle (excluding diagonal)
                mask = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
                upper_triangle = corr_matrix.values[mask]
                avg_corr.append(np.nanmean(upper_triangle))
            else:
                avg_corr.append(np.nan)
        except Exception:
            avg_corr.append(np.nan)

    return pd.Series(avg_corr, index=dates, name='avg_correlation')


def detect_regime(
    returns: pd.DataFrame,
    vol_window: int = 21,
    corr_window: int = 63,
    vol_percentiles: Tuple[float, float, float] = (25, 75, 95),
    corr_threshold: float = 0.6
) -> pd.DataFrame:
    """
    Detect market regime based on volatility and correlation levels.

    Args:
        returns: DataFrame of asset returns
        vol_window: Window for volatility calculation
        corr_window: Window for correlation calculation
        vol_percentiles: Thresholds for Low/Normal/High/Crisis
        corr_threshold: Correlation level indicating stress

    Returns:
        DataFrame with regime classifications and metrics
    """
    # Calculate metrics
    rolling_vol = calculate_rolling_volatility(returns, vol_window)
    avg_vol = rolling_vol.mean(axis=1)

    rolling_corr = calculate_rolling_correlation(returns, corr_window)

    # Align indices
    common_idx = avg_vol.index.intersection(rolling_corr.index)
    avg_vol = avg_vol.loc[common_idx]
    rolling_corr = rolling_corr.loc[common_idx]

    # Calculate volatility percentiles from historical data
    vol_p25 = avg_vol.quantile(vol_percentiles[0] / 100)
    vol_p75 = avg_vol.quantile(vol_percentiles[1] / 100)
    vol_p95 = avg_vol.quantile(vol_percentiles[2] / 100)

    # Classify regimes
    regimes = []
    for date in common_idx:
        vol = avg_vol.loc[date]
        corr = rolling_corr.loc[date]

        if vol > vol_p95 or (vol > vol_p75 and corr > corr_threshold):
            regime = MarketRegime.CRISIS
        elif vol > vol_p75:
            regime = MarketRegime.HIGH_VOL
        elif vol < vol_p25:
            regime = MarketRegime.LOW_VOL
        else:
            regime = MarketRegime.NORMAL

        regimes.append(regime.value)

    result = pd.DataFrame({
        'volatility': avg_vol,
        'correlation': rolling_corr,
        'regime': regimes
    }, index=common_idx)

    return result


def get_regime_statistics(regime_df: pd.DataFrame) -> Dict:
    """Calculate statistics for each regime."""
    stats = {}
    for regime in MarketRegime:
        mask = regime_df['regime'] == regime.value
        if mask.sum() > 0:
            stats[regime.value] = {
                'days': mask.sum(),
                'pct_time': mask.mean() * 100,
                'avg_vol': regime_df.loc[mask, 'volatility'].mean(),
                'avg_corr': regime_df.loc[mask, 'correlation'].mean(),
            }
    return stats


def get_regime_colors() -> Dict[str, str]:
    """Color scheme for regime visualization."""
    return {
        MarketRegime.LOW_VOL.value: '#4ecca3',      # Green
        MarketRegime.NORMAL.value: '#3498db',        # Blue
        MarketRegime.HIGH_VOL.value: '#f39c12',      # Orange
        MarketRegime.CRISIS.value: '#e74c3c',        # Red
    }
