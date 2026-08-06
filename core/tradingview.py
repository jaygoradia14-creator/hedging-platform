"""
TradingView widget HTML generators for Streamlit embedding.
Uses official TradingView embed scripts for ticker tape, charts, and technical analysis.
"""

import json

# Common exchange mappings for yfinance tickers -> TradingView format
_EXCHANGE_MAP = {
    # Major US stocks
    "AAPL": "NASDAQ:AAPL", "MSFT": "NASDAQ:MSFT", "GOOGL": "NASDAQ:GOOGL",
    "AMZN": "NASDAQ:AMZN", "META": "NASDAQ:META", "NVDA": "NASDAQ:NVDA",
    "TSLA": "NASDAQ:TSLA", "NFLX": "NASDAQ:NFLX", "AMD": "NASDAQ:AMD",
    "INTC": "NASDAQ:INTC", "CRM": "NYSE:CRM", "ORCL": "NYSE:ORCL",
    "ADBE": "NASDAQ:ADBE", "PYPL": "NASDAQ:PYPL", "SQ": "NYSE:SQ",
    "SHOP": "NYSE:SHOP", "UBER": "NYSE:UBER", "ABNB": "NASDAQ:ABNB",
    "COIN": "NASDAQ:COIN", "PLTR": "NYSE:PLTR", "SNAP": "NYSE:SNAP",
    "PINS": "NYSE:PINS", "DIS": "NYSE:DIS", "NKE": "NYSE:NKE",
    "MCD": "NYSE:MCD", "SBUX": "NASDAQ:SBUX", "KO": "NYSE:KO",
    "PEP": "NASDAQ:PEP", "COST": "NASDAQ:COST", "HD": "NYSE:HD",
    "LOW": "NYSE:LOW", "TGT": "NYSE:TGT", "WMT": "NYSE:WMT",
    "PG": "NYSE:PG", "JNJ": "NYSE:JNJ", "UNH": "NYSE:UNH",
    "ABBV": "NYSE:ABBV", "PFE": "NYSE:PFE", "MRK": "NYSE:MRK",
    "LLY": "NYSE:LLY", "TMO": "NYSE:TMO", "JPM": "NYSE:JPM",
    "V": "NYSE:V", "GS": "NYSE:GS", "MS": "NYSE:MS",
    "C": "NYSE:C", "WFC": "NYSE:WFC", "BAC": "NYSE:BAC",
    "AXP": "NYSE:AXP", "SCHW": "NYSE:SCHW", "XOM": "NYSE:XOM",
    "CVX": "NYSE:CVX", "BA": "NYSE:BA", "CAT": "NYSE:CAT",
    "DE": "NYSE:DE", "LMT": "NYSE:LMT", "RTX": "NYSE:RTX",
    "GE": "NYSE:GE", "HON": "NASDAQ:HON", "NEE": "NYSE:NEE",
    "SO": "NYSE:SO", "DUK": "NYSE:DUK", "AEP": "NASDAQ:AEP",
    "AMT": "NYSE:AMT", "PLD": "NYSE:PLD", "CCI": "NYSE:CCI",
    # ETFs (AMEX / ARCA)
    "SPY": "AMEX:SPY", "QQQ": "NASDAQ:QQQ", "IWM": "AMEX:IWM",
    "DIA": "AMEX:DIA", "VOO": "AMEX:VOO", "VTI": "AMEX:VTI",
    "EFA": "AMEX:EFA", "EEM": "AMEX:EEM", "VEA": "AMEX:VEA",
    "VWO": "AMEX:VWO", "IEFA": "AMEX:IEFA",
    "TLT": "NASDAQ:TLT", "IEF": "NASDAQ:IEF", "SHY": "NASDAQ:SHY",
    "LQD": "AMEX:LQD", "HYG": "AMEX:HYG", "TIP": "AMEX:TIP",
    "AGG": "AMEX:AGG", "BND": "NASDAQ:BND",
    "GLD": "AMEX:GLD", "SLV": "AMEX:SLV", "USO": "AMEX:USO",
    "VNQ": "AMEX:VNQ", "DBC": "AMEX:DBC", "PDBC": "AMEX:PDBC",
    "VXX": "AMEX:VXX", "UVXY": "AMEX:UVXY",
    "XLF": "AMEX:XLF", "XLK": "AMEX:XLK", "XLE": "AMEX:XLE",
    "XLV": "AMEX:XLV", "XLI": "AMEX:XLI", "XLP": "AMEX:XLP",
    "XLY": "AMEX:XLY", "XLU": "AMEX:XLU", "XLRE": "AMEX:XLRE",
    "XLC": "AMEX:XLC",
    "VUG": "AMEX:VUG", "VTV": "AMEX:VTV", "VXUS": "NASDAQ:VXUS",
    "SCHD": "AMEX:SCHD", "DVY": "AMEX:DVY", "HDV": "AMEX:HDV",
    # Crypto
    "BTC-USD": "BITSTAMP:BTCUSD", "ETH-USD": "BITSTAMP:ETHUSD",
    # International
    "BABA": "NYSE:BABA", "TSM": "NYSE:TSM", "ASML": "NASDAQ:ASML",
    "BRK-B": "NYSE:BRK.B",
}


def _map_ticker_to_tradingview(ticker):
    """Map a yfinance ticker to TradingView format."""
    return _EXCHANGE_MAP.get(ticker, ticker)


def ticker_tape_html(tickers, height=46):
    """Generate scrolling TradingView ticker tape HTML.

    Args:
        tickers: List of yfinance ticker symbols.
        height: Widget height in pixels.

    Returns:
        HTML string for st.components.v1.html().
    """
    symbols = []
    for t in tickers:
        tv = _map_ticker_to_tradingview(t)
        symbols.append({"proName": tv, "title": t})

    config = {
        "symbols": symbols,
        "showSymbolLogo": True,
        "isTransparent": True,
        "displayMode": "adaptive",
        "colorTheme": "light",
        "locale": "en",
    }

    return f"""
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript"
        src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js"
        async>
        {json.dumps(config)}
      </script>
    </div>
    """


def advanced_chart_html(ticker, height=500):
    """Generate a full interactive TradingView chart HTML.

    Args:
        ticker: yfinance ticker symbol.
        height: Widget height in pixels.

    Returns:
        HTML string for st.components.v1.html().
    """
    tv_symbol = _map_ticker_to_tradingview(ticker)

    config = {
        "autosize": True,
        "symbol": tv_symbol,
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "1",
        "locale": "en",
        "allow_symbol_change": False,
        "support_host": "https://www.tradingview.com",
    }

    return f"""
    <div class="tradingview-widget-container" style="height:{height}px;width:100%">
      <div class="tradingview-widget-container__widget"
           style="height:calc(100% - 32px);width:100%"></div>
      <script type="text/javascript"
        src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js"
        async>
        {json.dumps(config)}
      </script>
    </div>
    """


def technical_analysis_html(ticker, height=425):
    """Generate TradingView technical analysis gauge HTML.

    Shows Buy/Sell/Neutral gauge with interval tabs.

    Args:
        ticker: yfinance ticker symbol.
        height: Widget height in pixels.

    Returns:
        HTML string for st.components.v1.html().
    """
    tv_symbol = _map_ticker_to_tradingview(ticker)

    config = {
        "interval": "1D",
        "width": "100%",
        "isTransparent": True,
        "height": height,
        "symbol": tv_symbol,
        "showIntervalTabs": True,
        "displayMode": "single",
        "locale": "en",
        "colorTheme": "light",
    }

    return f"""
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript"
        src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js"
        async>
        {json.dumps(config)}
      </script>
    </div>
    """
