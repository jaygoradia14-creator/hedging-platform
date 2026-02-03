"""
Data fetching module for the hedging platform.
Reuses patterns from the existing codebase with enhancements for multi-asset support.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta


def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch stock data from yfinance with proper error handling.

    Args:
        ticker: Stock symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        DataFrame with OHLCV data
    """
    import yfinance as yf

    data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    # Handle MultiIndex columns (yfinance quirk)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Remove timezone info for consistency
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    return data


def fetch_multi_asset_data(
    tickers: List[str],
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch adjusted close prices for multiple assets.

    Returns:
        DataFrame with adjusted close prices, columns = tickers
    """
    import yfinance as yf

    data = yf.download(tickers, start=start_date, end=end_date, progress=False)

    # Extract adjusted close
    if isinstance(data.columns, pd.MultiIndex):
        prices = data['Adj Close'] if 'Adj Close' in data.columns.get_level_values(0) else data['Close']
    else:
        prices = data[['Adj Close']] if 'Adj Close' in data.columns else data[['Close']]
        prices.columns = tickers

    # Remove timezone
    if prices.index.tz is not None:
        prices.index = prices.index.tz_localize(None)

    return prices.dropna()


def calculate_returns(prices: pd.DataFrame, method: str = 'log') -> pd.DataFrame:
    """
    Calculate returns from price data.

    Args:
        prices: DataFrame of prices
        method: 'log' for log returns, 'simple' for arithmetic returns

    Returns:
        DataFrame of returns
    """
    if method == 'log':
        return np.log(prices / prices.shift(1)).dropna()
    else:
        return prices.pct_change().dropna()


# Default asset universe for multi-asset hedging
ASSET_UNIVERSE = {
    'equities': ['SPY', 'QQQ', 'IWM', 'EFA', 'EEM'],
    'bonds': ['TLT', 'IEF', 'LQD', 'HYG', 'TIP'],
    'alternatives': ['GLD', 'SLV', 'USO', 'VNQ', 'DBC'],
    'volatility': ['VXX'],
}

def get_default_tickers() -> List[str]:
    """Get flattened list of all default tickers."""
    tickers = []
    for category in ASSET_UNIVERSE.values():
        tickers.extend(category)
    return tickers
