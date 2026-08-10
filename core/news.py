"""
News fetching and keyword-based sentiment scoring.
Uses yfinance for news + optional Finnhub API for additional coverage.
"""

import os
from datetime import datetime, timezone

POSITIVE_KEYWORDS = [
    "surge", "soar", "rally", "gain", "jump", "rise", "boost", "record",
    "beat", "exceed", "upgrade", "outperform", "bullish", "profit", "growth",
    "strong", "positive", "optimistic", "recover", "breakthrough", "momentum",
    "expand", "upbeat", "dividend", "buyback", "innovation", "milestone",
    "approval", "partnership", "deal",
]

NEGATIVE_KEYWORDS = [
    "crash", "plunge", "drop", "fall", "decline", "loss", "miss", "cut",
    "downgrade", "underperform", "bearish", "warning", "risk", "weak",
    "negative", "pessimistic", "recession", "layoff", "lawsuit", "fraud",
    "investigation", "default", "bankruptcy", "sell-off", "selloff", "concern",
    "fear", "inflation", "tariff", "sanction",
]


def score_sentiment(title):
    """Score sentiment of a news title using keyword matching.

    Returns:
        Tuple of (label, score) where label is Positive/Negative/Neutral
        and score is in range [-1.0, 1.0].
    """
    lower = title.lower()
    pos = sum(1 for kw in POSITIVE_KEYWORDS if kw in lower)
    neg = sum(1 for kw in NEGATIVE_KEYWORDS if kw in lower)
    total = pos + neg

    if total == 0:
        return "Neutral", 0.0

    score = (pos - neg) / total
    if score > 0.1:
        return "Positive", round(score, 2)
    elif score < -0.1:
        return "Negative", round(score, 2)
    return "Neutral", round(score, 2)


# Ticker-to-company-name mapping for relevance filtering
_TICKER_NAMES = {
    "SPY": "s&p 500", "QQQ": "nasdaq", "IWM": "russell",
    "TLT": "treasury", "IEF": "treasury", "SHY": "treasury",
    "GLD": "gold", "SLV": "silver", "USO": "oil",
    "VNQ": "real estate", "DBC": "commodit",
    "AAPL": "apple", "MSFT": "microsoft", "GOOGL": "google",
    "AMZN": "amazon", "META": "meta", "NVDA": "nvidia",
    "TSLA": "tesla", "JPM": "jpmorgan", "V": "visa",
    "JNJ": "johnson", "WMT": "walmart", "PG": "procter",
    "XOM": "exxon", "CVX": "chevron", "BAC": "bank of america",
    "NFLX": "netflix", "AMD": "amd", "DIS": "disney",
    "BTC-USD": "bitcoin", "ETH-USD": "ethereum",
    "AGG": "bond", "BND": "bond", "HYG": "high yield",
    "EFA": "international", "EEM": "emerging",
}


def _is_relevant(title, ticker):
    """Check if a news title is relevant to the given ticker."""
    lower = title.lower()
    # Direct ticker mention
    if ticker.lower() in lower:
        return True
    # Company/asset name mention
    name = _TICKER_NAMES.get(ticker.upper(), "")
    if name and name in lower:
        return True
    return False


def fetch_yfinance_news(ticker, max_items=10):
    """Fetch news for a ticker using yfinance.

    Returns:
        List of normalized news dicts, filtered to be relevant to the ticker.
    """
    try:
        import yfinance as yf
        tk = yf.Ticker(ticker)
        raw = tk.news or []
    except Exception:
        return []

    items = []
    for article in raw[:max_items * 2]:  # Fetch more to compensate for filtering
        # Handle both old and new yfinance news API formats
        content = article.get("content", {})
        if content and isinstance(content, dict):
            # New format: nested under "content"
            title = content.get("title", "")
            provider = content.get("provider", {})
            source = provider.get("displayName", "Unknown") if isinstance(provider, dict) else "Unknown"
            pub_date = content.get("pubDate", "") or content.get("displayTime", "")
            click_url = content.get("clickThroughUrl", {})
            link = click_url.get("url", "") if isinstance(click_url, dict) else ""
            if not link:
                canonical = content.get("canonicalUrl", {})
                link = canonical.get("url", "") if isinstance(canonical, dict) else ""
        else:
            # Old format: flat keys
            title = article.get("title", "")
            source = article.get("publisher", "Unknown")
            pub_date = ""
            link = article.get("link", "")

        if not title:
            continue

        # Filter out general news not relevant to this ticker
        if not _is_relevant(title, ticker):
            continue

        label, sc = score_sentiment(title)

        # Parse publish time
        pub = ""
        if pub_date and isinstance(pub_date, str) and pub_date:
            try:
                # ISO format: "2026-08-06T03:58:32Z"
                pub = pub_date[:16].replace("T", " ")
            except Exception:
                pub = ""
        elif not pub_date:
            # Legacy: epoch timestamp
            pub_ts = article.get("providerPublishTime", 0)
            if pub_ts:
                try:
                    pub = datetime.fromtimestamp(pub_ts, tz=timezone.utc).strftime(
                        "%Y-%m-%d %H:%M"
                    )
                except Exception:
                    pass

        items.append({
            "title": title,
            "link": link,
            "source": source,
            "published": pub,
            "ticker": ticker,
            "sentiment": label,
            "sentiment_score": sc,
        })

        if len(items) >= max_items:
            break

    return items


def fetch_finnhub_news(ticker, max_items=10):
    """Fetch news using Finnhub API (optional).

    Returns empty list if no API key is available.
    """
    api_key = None
    try:
        import streamlit as st
        api_key = st.secrets.get("FINNHUB_API_KEY")
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("FINNHUB_API_KEY")
    if not api_key:
        return []

    try:
        import finnhub
        client = finnhub.Client(api_key=api_key)
        today = datetime.now().strftime("%Y-%m-%d")
        from_date = (
            datetime.now().replace(day=max(1, datetime.now().day - 7))
        ).strftime("%Y-%m-%d")
        raw = client.company_news(ticker, _from=from_date, to=today)
    except Exception:
        return []

    items = []
    for article in (raw or [])[:max_items]:
        title = article.get("headline", "")
        if not title:
            continue
        label, sc = score_sentiment(title)
        pub = ""
        if article.get("datetime"):
            try:
                pub = datetime.fromtimestamp(
                    article["datetime"], tz=timezone.utc
                ).strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass
        items.append({
            "title": title,
            "link": article.get("url", ""),
            "source": article.get("source", "Finnhub"),
            "published": pub,
            "ticker": ticker,
            "sentiment": label,
            "sentiment_score": sc,
        })

    return items


def fetch_portfolio_news(tickers, max_per_ticker=5, use_finnhub=True):
    """Fetch and aggregate news across all portfolio tickers.

    Deduplicates by title and sorts by recency.

    Returns:
        List of normalized news dicts.
    """
    all_items = []
    seen_titles = set()

    for ticker in tickers:
        yf_news = fetch_yfinance_news(ticker, max_items=max_per_ticker)
        for item in yf_news:
            key = item["title"].lower().strip()
            if key not in seen_titles:
                seen_titles.add(key)
                all_items.append(item)

        if use_finnhub:
            fh_news = fetch_finnhub_news(ticker, max_items=max_per_ticker)
            for item in fh_news:
                key = item["title"].lower().strip()
                if key not in seen_titles:
                    seen_titles.add(key)
                    all_items.append(item)

    # Sort by published date descending (most recent first)
    all_items.sort(key=lambda x: x.get("published", ""), reverse=True)
    return all_items


def aggregate_sentiment(news_items):
    """Compute overall portfolio sentiment summary."""
    if not news_items:
        return {"label": "Neutral", "score": 0.0, "positive": 0, "negative": 0, "neutral": 0, "total": 0}
    pos = sum(1 for n in news_items if n["sentiment"] == "Positive")
    neg = sum(1 for n in news_items if n["sentiment"] == "Negative")
    neu = len(news_items) - pos - neg
    avg_score = sum(n["sentiment_score"] for n in news_items) / len(news_items)
    if avg_score > 0.05:
        label = "Bullish"
    elif avg_score < -0.05:
        label = "Bearish"
    else:
        label = "Neutral"
    return {"label": label, "score": round(avg_score, 3), "positive": pos, "negative": neg, "neutral": neu, "total": len(news_items)}


MOVEMENT_KEYWORDS = {
    "earnings": "Earnings Report", "revenue": "Revenue Results",
    "budget": "Government Budget", "fed": "Federal Reserve",
    "rate": "Interest Rate Change", "dividend": "Dividend News",
    "merger": "Merger/Acquisition", "acquisition": "Merger/Acquisition",
    "regulation": "Regulation Change", "tariff": "Trade Policy",
    "layoff": "Workforce Changes", "launch": "Product Launch",
    "partnership": "Partnership Deal", "upgrade": "Analyst Upgrade",
    "downgrade": "Analyst Downgrade", "guidance": "Company Guidance",
    "inflation": "Inflation Data", "gdp": "Economic Data",
    "jobs": "Employment Data", "oil": "Oil/Energy Prices",
}


def match_news_to_movers(news_items, price_changes):
    """Match significant price movers with relevant news headlines.

    Args:
        news_items: List of news dicts from fetch_portfolio_news()
        price_changes: Dict of {ticker: change_pct} from live prices

    Returns:
        Dict of {ticker: {"change": pct, "reasons": [{"headline": str, "category": str}]}}
    """
    movers = {}
    for ticker, change in price_changes.items():
        if abs(change) < 1.0:  # Only flag moves > 1%
            continue
        ticker_news = [n for n in news_items if n["ticker"] == ticker]
        reasons = []
        for item in ticker_news[:3]:
            title_lower = item["title"].lower()
            categories = [cat for kw, cat in MOVEMENT_KEYWORDS.items() if kw in title_lower]
            reasons.append({
                "headline": item["title"],
                "category": categories[0] if categories else "Market News",
                "link": item.get("link", ""),
            })
        if reasons:
            movers[ticker] = {"change": change, "reasons": reasons}
    return movers
