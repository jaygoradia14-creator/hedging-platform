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


def fetch_yfinance_news(ticker, max_items=10):
    """Fetch news for a ticker using yfinance.

    Returns:
        List of normalized news dicts.
    """
    try:
        import yfinance as yf
        tk = yf.Ticker(ticker)
        raw = tk.news or []
    except Exception:
        return []

    items = []
    for article in raw[:max_items]:
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
