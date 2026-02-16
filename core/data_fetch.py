"""
Data fetching module for the hedging platform.
Fetches live prices, sector info, and computes returns.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta


# Sector mapping for common ETFs and stocks
SECTOR_MAP = {
    # US Equity ETFs
    "SPY": "US Large Cap", "QQQ": "US Tech", "IWM": "US Small Cap",
    "DIA": "US Large Cap", "VOO": "US Large Cap", "VTI": "US Total Market",
    # International
    "EFA": "Intl Developed", "EEM": "Emerging Markets", "VEA": "Intl Developed",
    "VWO": "Emerging Markets", "IEFA": "Intl Developed",
    # Fixed Income
    "TLT": "Long-Term Treasury", "IEF": "Mid-Term Treasury", "SHY": "Short-Term Treasury",
    "LQD": "Investment Grade", "HYG": "High Yield", "TIP": "TIPS",
    "AGG": "Aggregate Bond", "BND": "Aggregate Bond",
    # Alternatives
    "GLD": "Gold", "SLV": "Silver", "USO": "Oil",
    "VNQ": "Real Estate", "DBC": "Commodities", "PDBC": "Commodities",
    # Volatility
    "VXX": "Volatility", "UVXY": "Volatility",
    # Sector ETFs
    "XLF": "Financials", "XLK": "Technology", "XLE": "Energy",
    "XLV": "Healthcare", "XLI": "Industrials", "XLP": "Consumer Staples",
    "XLY": "Consumer Discretionary", "XLU": "Utilities", "XLRE": "Real Estate",
    "XLC": "Communication",
    # Popular stocks
    "AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Technology",
    "AMZN": "Consumer Discretionary", "META": "Technology", "NVDA": "Technology",
    "TSLA": "Consumer Discretionary", "JPM": "Financials", "V": "Financials",
    "JNJ": "Healthcare", "WMT": "Consumer Staples", "PG": "Consumer Staples",
    "XOM": "Energy", "CVX": "Energy", "BAC": "Financials",
}


def get_sector(ticker: str) -> str:
    """Get sector/category for a ticker."""
    return SECTOR_MAP.get(ticker.upper(), "Other")


def get_sectors(tickers: List[str]) -> Dict[str, str]:
    """Get sectors for multiple tickers."""
    return {t: get_sector(t) for t in tickers}


def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch stock data from yfinance."""
    import yfinance as yf
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)
    return data


def fetch_multi_asset_data(
    tickers: List[str],
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """Fetch adjusted close prices for multiple assets."""
    import yfinance as yf
    data = yf.download(tickers, start=start_date, end=end_date, progress=False)

    if isinstance(data.columns, pd.MultiIndex):
        if 'Adj Close' in data.columns.get_level_values(0):
            prices = data['Adj Close']
        elif 'Close' in data.columns.get_level_values(0):
            prices = data['Close']
        else:
            prices = data.iloc[:, :len(tickers)]
    else:
        if 'Adj Close' in data.columns:
            prices = data[['Adj Close']]
        elif 'Close' in data.columns:
            prices = data[['Close']]
        else:
            prices = data
        if len(tickers) == 1:
            prices.columns = tickers

    if prices.index.tz is not None:
        prices.index = prices.index.tz_localize(None)

    # Ensure columns are the tickers we asked for (in order)
    available = [t for t in tickers if t in prices.columns]
    prices = prices[available]

    return prices.dropna()


def fetch_latest_prices(tickers: List[str]) -> pd.DataFrame:
    """Fetch the latest price data for display (last 5 days)."""
    import yfinance as yf

    records = []
    for ticker in tickers:
        try:
            tk = yf.Ticker(ticker)
            info = tk.fast_info
            hist = tk.history(period="5d")
            if len(hist) < 2:
                continue
            current = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2])
            change = current - prev
            change_pct = (change / prev) * 100
            records.append({
                "Ticker": ticker,
                "Sector": get_sector(ticker),
                "Price": current,
                "Change": change,
                "Change %": change_pct,
                "Volume": int(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else 0,
            })
        except Exception:
            records.append({
                "Ticker": ticker,
                "Sector": get_sector(ticker),
                "Price": None, "Change": None, "Change %": None, "Volume": None,
            })

    return pd.DataFrame(records)


def calculate_returns(prices: pd.DataFrame, method: str = 'log') -> pd.DataFrame:
    """Calculate returns from price data."""
    if method == 'log':
        return np.log(prices / prices.shift(1)).dropna()
    else:
        return prices.pct_change().dropna()


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
