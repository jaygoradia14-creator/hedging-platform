"""
News - Portfolio news feed with per-ticker filtering and sentiment badges.
Global sentiment gauge, institutional holders, and market movers.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from core.portfolio import init_session_state
from core.style import page_header, GREEN, RED

init_session_state()
page_header("News")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio

# --- Fetch news with 5-minute TTL cache (invalidates when tickers change) ---
cache_time = st.session_state.get("news_cache_time")
cache_tickers = st.session_state.get("news_cache_tickers", [])
cache_valid = (
    cache_time is not None
    and (datetime.now() - cache_time) < timedelta(minutes=5)
    and set(cache_tickers) == set(portfolio.tickers)
)

if not cache_valid:
    with st.spinner("Fetching latest news..."):
        from core.news import fetch_portfolio_news
        news_items = fetch_portfolio_news(portfolio.tickers, max_per_ticker=5)
        st.session_state.news_cache = news_items
        st.session_state.news_cache_time = datetime.now()
        st.session_state.news_cache_tickers = list(portfolio.tickers)
else:
    news_items = st.session_state.news_cache

# --- Global Sentiment Gauge ---
from core.news import aggregate_sentiment, match_news_to_movers

agg = aggregate_sentiment(news_items)
sent_color = GREEN if agg["label"] == "Bullish" else RED if agg["label"] == "Bearish" else "#8b8b8b"
st.markdown(
    f'<div style="text-align:center;padding:16px;margin-bottom:16px;'
    f'border:1px solid #e8e8e8;border-radius:10px;background:#fff;">'
    f'<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;'
    f'color:#6b7280;font-weight:600;margin-bottom:4px;">Portfolio Sentiment</div>'
    f'<div style="font-size:1.8rem;font-weight:700;color:{sent_color};">{agg["label"]}</div>'
    f'<div style="font-size:0.85rem;color:#6b7280;">Score: {agg["score"]:+.3f}</div>'
    f'<div style="display:flex;justify-content:center;gap:16px;margin-top:8px;font-size:0.8rem;">'
    f'<span style="color:{GREEN};">Positive: {agg["positive"]}</span>'
    f'<span style="color:#8b8b8b;">Neutral: {agg["neutral"]}</span>'
    f'<span style="color:{RED};">Negative: {agg["negative"]}</span>'
    f'</div></div>',
    unsafe_allow_html=True,
)

# --- Market Movers ---
from core.data_fetch import fetch_latest_prices

live_df = fetch_latest_prices(portfolio.tickers)
price_changes = {}
if live_df is not None and not live_df.empty:
    for _, r in live_df.iterrows():
        if pd.notna(r.get("Change %")):
            price_changes[r["Ticker"]] = r["Change %"]

movers = match_news_to_movers(news_items, price_changes)
if movers:
    st.markdown("### Market Movers")
    st.caption("Stocks with >1% daily move and matching news headlines.")
    for mv_ticker, mv_data in movers.items():
        mv_chg = mv_data["change"]
        mv_border = GREEN if mv_chg >= 0 else RED
        mv_cls = "color:" + GREEN if mv_chg >= 0 else "color:" + RED
        reasons_html = ""
        for reason in mv_data["reasons"]:
            r_link = reason.get("link", "")
            r_title = reason["headline"]
            if r_link:
                r_title = (
                    f'<a href="{r_link}" target="_blank" '
                    f'style="color:#44475b;text-decoration:none;">{reason["headline"]}</a>'
                )
            reasons_html += (
                f'<div style="font-size:0.82rem;padding:3px 0;">'
                f'<span style="background:#f0f4f8;padding:1px 6px;border-radius:3px;'
                f'font-size:0.7rem;font-weight:500;color:#6b7280;">{reason["category"]}</span> '
                f'{r_title}</div>'
            )
        st.markdown(
            f'<div style="border-left:4px solid {mv_border};border:1px solid #e8e8e8;'
            f'border-left:4px solid {mv_border};border-radius:8px;padding:12px 16px;'
            f'margin-bottom:10px;background:#fff;">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
            f'<span style="font-weight:700;font-size:0.95rem;">{mv_ticker}</span>'
            f'<span style="{mv_cls};font-size:0.85rem;font-weight:600;">{mv_chg:+.2f}%</span>'
            f'</div>{reasons_html}</div>',
            unsafe_allow_html=True,
        )

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

# --- Who Owns Your Stocks? (Institutional Holders) ---
st.markdown("### Who Owns Your Stocks?")
st.caption(
    "These are big investment firms that also own shares in your stocks. "
    "Seeing major institutions hold the same stocks can be a sign of confidence."
)

inst_cache_time = st.session_state.get("inst_cache_time")
inst_valid = (
    inst_cache_time is not None
    and (datetime.now() - inst_cache_time) < timedelta(minutes=10)
)

if not inst_valid:
    from core.data_fetch import fetch_institutional_holders
    inst_data = {}
    for ticker in portfolio.tickers:
        holders = fetch_institutional_holders(ticker, top_n=5)
        if holders:
            inst_data[ticker] = holders
    st.session_state.inst_cache = inst_data
    st.session_state.inst_cache_time = datetime.now()
else:
    inst_data = st.session_state.inst_cache

if inst_data:
    for ticker, holders in inst_data.items():
        with st.expander(f"{ticker} - Top Institutional Holders"):
            holder_rows = []
            for h in holders:
                holder_rows.append({
                    "Holder": h.get("Holder", h.get("holder", "Unknown")),
                    "Shares": f'{h.get("Shares", h.get("shares", 0)):,.0f}',
                    "% Out": f'{h.get("% Out", h.get("pctHeld", 0)):.2%}' if isinstance(h.get("% Out", h.get("pctHeld", 0)), float) else str(h.get("% Out", h.get("pctHeld", "N/A"))),
                })
            if holder_rows:
                st.dataframe(
                    pd.DataFrame(holder_rows),
                    use_container_width=True,
                    hide_index=True,
                )
else:
    st.info("No institutional holder data available.")
