"""
News - Portfolio news feed with per-ticker filtering and sentiment badges.
"""

import streamlit as st
from datetime import datetime, timedelta

from core.portfolio import init_session_state
from core.style import page_header, GREEN, RED

init_session_state()
page_header("News")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio

# --- Fetch news with 5-minute TTL cache ---
cache_time = st.session_state.get("news_cache_time")
cache_valid = (
    cache_time is not None
    and (datetime.now() - cache_time) < timedelta(minutes=5)
)

if not cache_valid:
    with st.spinner("Fetching latest news..."):
        from core.news import fetch_portfolio_news
        news_items = fetch_portfolio_news(portfolio.tickers, max_per_ticker=5)
        st.session_state.news_cache = news_items
        st.session_state.news_cache_time = datetime.now()
else:
    news_items = st.session_state.news_cache

# --- Ticker filter ---
filter_options = ["All Holdings"] + portfolio.tickers
selected = st.selectbox("Filter by ticker", options=filter_options)

if selected != "All Holdings":
    news_items = [n for n in news_items if n["ticker"] == selected]

# --- Metrics row ---
total = len(news_items)
pos = sum(1 for n in news_items if n["sentiment"] == "Positive")
neg = sum(1 for n in news_items if n["sentiment"] == "Negative")
neu = total - pos - neg

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Articles", total)
c2.metric("Positive", pos)
c3.metric("Negative", neg)
c4.metric("Neutral", neu)

# --- News cards ---
if not news_items:
    st.info("No news articles found for the selected filter.")
else:
    for item in news_items:
        sentiment = item["sentiment"]
        if sentiment == "Positive":
            badge_color = GREEN
        elif sentiment == "Negative":
            badge_color = RED
        else:
            badge_color = "#8b8b8b"

        title_html = item["title"]
        if item.get("link"):
            title_html = (
                f'<a href="{item["link"]}" target="_blank" '
                f'style="color:#44475b;text-decoration:none;font-weight:600;">'
                f'{item["title"]}</a>'
            )

        card_html = f"""
        <div style="border:1px solid #e8e8e8;border-radius:8px;padding:12px 16px;
                    margin-bottom:10px;background:#fff;">
            <div style="font-size:0.95rem;margin-bottom:6px;">
                {title_html}
            </div>
            <div style="font-size:0.75rem;color:#8b8b8b;">
                {item.get("source", "")}
                {" | " + item["published"] if item.get("published") else ""}
                &nbsp;&nbsp;
                <span style="background:#f0f7ff;color:#44475b;padding:2px 8px;
                             border-radius:4px;font-weight:500;">
                    {item["ticker"]}
                </span>
                &nbsp;
                <span style="background:{badge_color};color:#fff;padding:2px 8px;
                             border-radius:4px;font-weight:500;">
                    {sentiment}
                </span>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
