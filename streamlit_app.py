"""
Hedging Platform - Main Entry Point
Auto-loads data, shows live prices with sectors, Zerodha Kite UI.
"""

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Hedging Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Zerodha Kite CSS (same as before)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .stApp { background-color: #ffffff; }

    /* ========== GROWW-STYLE SIDEBAR ========== */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e8e8e8;
        box-shadow: 2px 0 12px rgba(0,0,0,0.06);
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    /* Sidebar text defaults */
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSelectbox label {
        color: #8b8b8b !important; font-size: 0.7rem;
        text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600;
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #44475b !important; font-size: 0.75rem; text-transform: uppercase;
        letter-spacing: 0.08em; font-weight: 700;
        border-bottom: 1px solid #eef0f4; padding-bottom: 0.5rem;
    }
    [data-testid="stSidebar"] hr { border-color: #eef0f4; }

    /* Sidebar page navigation - Groww style */
    [data-testid="stSidebarNav"] {
        padding-top: 0.5rem;
        border-bottom: 1px solid #eef0f4;
        padding-bottom: 0.5rem;
        margin-bottom: 0.5rem;
    }
    [data-testid="stSidebarNav"] li {
        margin: 2px 8px;
    }
    [data-testid="stSidebarNav"] a {
        color: #44475b !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 0.8rem !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
        display: flex !important;
        align-items: center !important;
    }
    [data-testid="stSidebarNav"] a span {
        color: #44475b !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: #f0f7ff !important;
        color: #5367ff !important;
    }
    [data-testid="stSidebarNav"] a:hover span {
        color: #5367ff !important;
    }
    [data-testid="stSidebarNav"] a[aria-selected="true"] {
        background: #f0f7ff !important;
        color: #5367ff !important;
        font-weight: 600 !important;
        border-left: 3px solid #5367ff !important;
    }
    [data-testid="stSidebarNav"] a[aria-selected="true"] span {
        color: #5367ff !important;
    }

    /* Hamburger button - Groww style (top left) */
    button[kind="header"] {
        color: #44475b !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        top: 0.5rem;
        left: 0.5rem;
        z-index: 999;
    }
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button {
        background: #ffffff !important;
        border: 1px solid #e0e4eb !important;
        border-radius: 10px !important;
        padding: 6px 8px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.2s;
    }
    [data-testid="stSidebarCollapsedControl"] button:hover,
    [data-testid="collapsedControl"] button:hover {
        background: #f0f7ff !important;
        border-color: #5367ff !important;
        box-shadow: 0 2px 12px rgba(83,103,255,0.15);
    }
    [data-testid="stSidebarCollapsedControl"] button svg,
    [data-testid="collapsedControl"] button svg {
        stroke: #5367ff !important;
        width: 20px !important;
        height: 20px !important;
    }
    /* Close button inside sidebar */
    [data-testid="stSidebarCollapseButton"] button {
        color: #8b8b8b !important;
        background: transparent !important;
        border: none !important;
    }
    [data-testid="stSidebarCollapseButton"] button:hover {
        color: #44475b !important;
    }

    /* ========== TOPBAR ========== */
    .kite-topbar {
        display: flex; align-items: center; justify-content: space-between;
        border-bottom: 1px solid #e8e8e8; padding: 0.6rem 0; margin-bottom: 1.5rem;
    }
    .kite-logo {
        font-size: 1.4rem; font-weight: 700; color: #5367ff;
        letter-spacing: -0.02em;
    }
    .kite-logo span {
        color: #999; font-weight: 400; font-size: 0.85rem; margin-left: 0.5rem;
    }

    /* ========== METRICS ========== */
    [data-testid="stMetric"] {
        background: #fff; border: 1px solid #e8e8e8;
        border-radius: 8px; padding: 1rem 1.2rem;
    }
    [data-testid="stMetric"] label {
        color: #8b8b8b !important; font-size: 0.7rem !important;
        text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600 !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #44475b !important; font-size: 1.4rem !important; font-weight: 600 !important;
    }

    /* ========== HEADINGS ========== */
    .stApp h1 { display: none; }
    .stApp h2, .stApp h3 {
        color: #44475b; font-weight: 600; font-size: 0.85rem; text-transform: uppercase;
        letter-spacing: 0.05em; border-bottom: 1px solid #e8e8e8;
        padding-bottom: 0.5rem; margin-top: 2rem;
    }

    /* ========== UTILITY ========== */
    .profit { color: #00b386; font-weight: 600; }
    .loss { color: #eb5b3c; font-weight: 600; }
    .muted { color: #8b8b8b; font-size: 0.8rem; }

    /* ========== HEADER ========== */
    footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: #ffffff;
        border-bottom: 1px solid #e8e8e8;
    }

    /* ========== MOBILE ========== */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }
        .kite-topbar {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.3rem;
        }
        .kite-logo { font-size: 1.1rem; }
        .kite-logo span { font-size: 0.7rem; }
        [data-testid="stMetric"] { padding: 0.6rem 0.8rem; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }
        [data-testid="stMetric"] label { font-size: 0.6rem !important; }
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
        [data-testid="stHorizontalBlock"] > div {
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        [data-testid="stDataFrame"] { overflow-x: auto; }
        .stApp h2, .stApp h3 { font-size: 0.75rem; margin-top: 1.5rem; }
        .js-plotly-plot { width: 100% !important; }
        .muted { font-size: 0.7rem; }
    }
    @media (max-width: 480px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        .kite-logo { font-size: 1rem; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 0.95rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
from core.portfolio import init_session_state, Portfolio, add_holding, sell_holding, get_holdings_summary  # noqa: E402
from core.data_fetch import (  # noqa: E402
    fetch_multi_asset_data, calculate_returns, fetch_latest_prices, get_sectors, POPULAR_TICKERS,
)
from core.regime_detector import detect_regime  # noqa: E402

init_session_state()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Portfolio")

    tickers = st.multiselect(
        "INSTRUMENTS",
        options=POPULAR_TICKERS,
        default=st.session_state.portfolio.tickers,
        help="Search and select 2-8 ticker symbols",
    )

    period = st.selectbox(
        "PERIOD",
        options=[1, 2, 3, 5, 10],
        index=2,
        format_func=lambda x: f"{x}Y",
    )

    load_clicked = st.button("Load Data", type="primary", use_container_width=True)

    # Auto-load on first visit
    if not st.session_state.data_loaded and not load_clicked:
        load_clicked = True

    if load_clicked and len(tickers) >= 2:
        with st.spinner("Fetching market data..."):
            end = datetime.now()
            start = end - timedelta(days=365 * period)
            try:
                prices = fetch_multi_asset_data(
                    tickers, str(start.date()), str(end.date())
                )
                if prices.empty or prices.shape[1] < 2:
                    st.error("Could not fetch data for these tickers. Check symbols.")
                else:
                    returns = calculate_returns(prices)
                    regime_df = detect_regime(returns)

                    actual_tickers = list(prices.columns)
                    portfolio = Portfolio(
                        tickers=actual_tickers,
                        weights=np.ones(len(actual_tickers)) / len(actual_tickers),
                        prices=prices,
                    )
                    portfolio.returns = returns
                    st.session_state.portfolio = portfolio
                    st.session_state.regime_df = regime_df
                    st.session_state.data_loaded = True
                    st.success(f"{len(actual_tickers)} instruments loaded")
            except Exception as exc:
                st.error(f"Failed: {exc}")
    elif load_clicked and len(tickers) < 2:
        st.error("Enter at least 2 tickers.")

    st.markdown("---")

    # Chat
    st.markdown("## Advisor")
    chat_container = st.container(height=250)
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_msg = st.chat_input("Ask about your portfolio...", key="sidebar_chat")
    if user_msg:
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        try:
            from chat.engine import get_response
            reply = get_response(user_msg, st.session_state)
        except Exception:
            from chat.fallback import fallback_response
            reply = fallback_response(user_msg, st.session_state)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.markdown("""
<div class="kite-topbar">
    <div class="kite-logo">hedging<span>platform</span></div>
    <div class="muted">Portfolio Risk & Hedging Analysis</div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.data_loaded:
    st.info("Loading default portfolio (SPY, TLT, GLD)...")
    st.stop()

portfolio = st.session_state.portfolio
summary = portfolio.summary()
returns = portfolio.returns

import plotly.graph_objects as go  # noqa: E402
from core.style import COLORS, kite_layout  # noqa: E402

# --- Metrics row ---
c1, c2, c3 = st.columns(3)
c1.metric("Instruments", summary["n_assets"])
c2.metric("Data Points", summary["data_points"])
c3.metric("HHI", f"{summary['hhi']:.3f}")

# --- Live Prices & Sectors ---
st.markdown("### Live Prices & Sectors")

with st.spinner("Fetching latest prices..."):
    live_df = fetch_latest_prices(portfolio.tickers)

if not live_df.empty and live_df["Price"].notna().any():
    # Format for display
    display_df = live_df.copy()
    display_df["Price"] = display_df["Price"].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    display_df["Change"] = display_df["Change"].apply(
        lambda x: f"{x:+.2f}" if pd.notna(x) else "N/A"
    )
    display_df["Change %"] = display_df["Change %"].apply(
        lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A"
    )
    display_df["Volume"] = display_df["Volume"].apply(
        lambda x: f"{x:,.0f}" if pd.notna(x) and x > 0 else "N/A"
    )
    st.dataframe(display_df.set_index("Ticker"), use_container_width=True)

# --- Allocation ---
st.markdown("### Allocation")

col_pie, col_table = st.columns([1, 1])

sectors = get_sectors(portfolio.tickers)

with col_pie:
    fig = go.Figure(data=[go.Pie(
        labels=[f"{t} ({sectors[t]})" for t in portfolio.tickers],
        values=portfolio.weights,
        hole=0.55,
        marker=dict(colors=COLORS[:portfolio.n_assets],
                    line=dict(color="#ffffff", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#333"),
    )])
    fig.update_layout(**kite_layout(height=340), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col_table:
    ann_ret = returns.mean() * 252
    ann_vol = returns.std() * np.sqrt(252)

    stats_df = pd.DataFrame({
        "Sector": [sectors[t] for t in portfolio.tickers],
        "Weight": [f"{w:.1%}" for w in portfolio.weights],
        "Return": ann_ret.apply(lambda x: f"{x:+.2%}"),
        "Volatility": ann_vol.apply(lambda x: f"{x:.2%}"),
        "Sharpe": (ann_ret / ann_vol).apply(lambda x: f"{x:.2f}"),
    }, index=portfolio.tickers)
    stats_df.index.name = "Instrument"
    st.dataframe(stats_df, use_container_width=True, height=300)

# --- My Holdings ---
st.markdown("### My Holdings")

# Summary metrics (top of holdings)
holdings = st.session_state.holdings
if holdings:
    # Gather current prices for held tickers
    held_tickers = list(holdings.keys())
    current_price_map = {}
    if live_df is not None and not live_df.empty:
        for _, row in live_df.iterrows():
            if pd.notna(row.get("Price")):
                current_price_map[row["Ticker"]] = row["Price"]
    # Fetch prices for tickers not in live_df
    missing = [t for t in held_tickers if t not in current_price_map]
    if missing:
        extra = fetch_latest_prices(missing)
        for _, row in extra.iterrows():
            if pd.notna(row.get("Price")):
                current_price_map[row["Ticker"]] = row["Price"]

    rows = get_holdings_summary(current_price_map)
    if rows:
        total_invested = sum(r["Shares"] * r["Buy Price"] for r in rows)
        total_value = sum(r["Value"] for r in rows)
        total_pnl = total_value - total_invested
        total_pnl_pct = (total_pnl / total_invested * 100) if total_invested else 0.0

        hc1, hc2, hc3, hc4 = st.columns(4)
        hc1.metric("Total Invested", f"${total_invested:,.2f}")
        hc2.metric("Current Value", f"${total_value:,.2f}")
        hc3.metric("Total P&L", f"${total_pnl:+,.2f}")
        hc4.metric("P&L %", f"{total_pnl_pct:+.2f}%")

        # Holdings table with color-coded P&L
        styled_rows = []
        for r in rows:
            styled_rows.append({
                "Ticker": r["Ticker"],
                "Shares": f"{r['Shares']:.2f}",
                "Buy Price": f"${r['Buy Price']:,.2f}",
                "Current Price": f"${r['Current Price']:,.2f}",
                "Value": f"${r['Value']:,.2f}",
                "P&L": f"${r['P&L']:+,.2f}",
                "P&L %": f"{r['P&L %']:+.2f}%",
            })
        st.dataframe(pd.DataFrame(styled_rows).set_index("Ticker"), use_container_width=True)

        # Sell per stock
        for r in rows:
            with st.expander(f"Sell {r['Ticker']}"):
                max_shares = r["Shares"]
                sell_qty = st.number_input(
                    f"Shares to sell ({r['Ticker']})",
                    min_value=0.0, max_value=float(max_shares),
                    value=0.0, step=1.0, key=f"sell_{r['Ticker']}",
                )
                if st.button(f"Sell {r['Ticker']}", key=f"sell_btn_{r['Ticker']}"):
                    if sell_qty > 0:
                        sell_holding(r["Ticker"], sell_qty)
                        st.success(f"Sold {sell_qty:.2f} shares of {r['Ticker']}")
                        st.rerun()
    else:
        st.info("No holdings yet. Use the form below to add stocks.")
else:
    st.info("No holdings yet. Use the form below to add stocks.")

# Add Stock form
with st.expander("Add Stock to Holdings", expanded=not bool(holdings)):
    add_col1, add_col2, add_col3 = st.columns(3)
    with add_col1:
        add_ticker = st.selectbox(
            "Ticker", options=portfolio.tickers, key="add_ticker_select",
        )
    with add_col2:
        add_shares = st.number_input("Shares", min_value=0.01, value=1.0, step=1.0, key="add_shares")
    with add_col3:
        # Default buy price = current price if available
        default_price = 0.0
        if live_df is not None and not live_df.empty:
            match = live_df[live_df["Ticker"] == add_ticker]
            if not match.empty and pd.notna(match.iloc[0]["Price"]):
                default_price = float(match.iloc[0]["Price"])
        add_price = st.number_input(
            "Buy Price", min_value=0.01, value=max(default_price, 0.01), step=0.01, key="add_price",
        )
    if st.button("Add to Holdings", type="primary", key="add_holding_btn"):
        add_holding(add_ticker, add_shares, add_price)
        st.success(f"Added {add_shares:.2f} shares of {add_ticker} at ${add_price:,.2f}")
        st.rerun()

# --- Individual stock price charts ---
st.markdown("### Individual Price History")

fig_prices = go.Figure()
for i, ticker in enumerate(portfolio.tickers):
    # Normalize to 100 for comparison
    normalized = (portfolio.prices[ticker] / portfolio.prices[ticker].iloc[0]) * 100
    fig_prices.add_trace(go.Scatter(
        x=normalized.index, y=normalized.values,
        mode="lines", name=f"{ticker} ({sectors[ticker]})",
        line=dict(width=2, color=COLORS[i % len(COLORS)]),
    ))
fig_prices.update_layout(
    **kite_layout(height=420),
    yaxis_title="Normalized Price (Base = 100)",
    hovermode="x unified",
)
st.plotly_chart(fig_prices, use_container_width=True)

# --- Individual cumulative returns ---
st.markdown("### Cumulative Returns")

cum_ret = (1 + returns).cumprod() - 1
port_cum = (1 + portfolio.portfolio_returns).cumprod() - 1

fig_cum = go.Figure()
for i, ticker in enumerate(portfolio.tickers):
    fig_cum.add_trace(go.Scatter(
        x=cum_ret.index, y=cum_ret[ticker] * 100,
        mode="lines", name=f"{ticker}",
        line=dict(width=1.8, color=COLORS[i % len(COLORS)]),
    ))
fig_cum.add_trace(go.Scatter(
    x=port_cum.index, y=port_cum.values * 100,
    mode="lines", name="Portfolio",
    line=dict(color="#1a1a2e", width=3),
))
fig_cum.update_layout(
    **kite_layout(height=420),
    yaxis_title="Return %", yaxis_ticksuffix="%",
    hovermode="x unified",
)
st.plotly_chart(fig_cum, use_container_width=True)

# --- Individual daily returns ---
st.markdown("### Daily Returns")

fig_daily = go.Figure()
for i, ticker in enumerate(portfolio.tickers):
    fig_daily.add_trace(go.Scatter(
        x=returns.index, y=returns[ticker] * 100,
        mode="lines", name=ticker,
        line=dict(width=1, color=COLORS[i % len(COLORS)]),
        opacity=0.7,
    ))
fig_daily.add_hline(y=0, line_color="#e8e8e8")
fig_daily.update_layout(
    **kite_layout(height=350),
    yaxis_title="Daily Return %", yaxis_ticksuffix="%",
    hovermode="x unified",
)
st.plotly_chart(fig_daily, use_container_width=True)

# --- Individual rolling volatility ---
st.markdown("### Rolling Volatility (21-Day)")

from core.regime_detector import calculate_rolling_volatility  # noqa: E402
rolling_vol = calculate_rolling_volatility(returns, window=21)

fig_vol = go.Figure()
for i, ticker in enumerate(portfolio.tickers):
    fig_vol.add_trace(go.Scatter(
        x=rolling_vol.index, y=rolling_vol[ticker] * 100,
        mode="lines", name=ticker,
        line=dict(width=1.5, color=COLORS[i % len(COLORS)]),
    ))
fig_vol.update_layout(
    **kite_layout(height=380),
    yaxis_title="Annualized Volatility %", yaxis_ticksuffix="%",
    hovermode="x unified",
)
st.plotly_chart(fig_vol, use_container_width=True)

st.markdown(
    f'<p class="muted">Data: {summary["date_range"]} &middot; Navigate to pages in sidebar for detailed analysis</p>',
    unsafe_allow_html=True,
)
