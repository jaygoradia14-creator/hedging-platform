"""
Hedging Platform - Main Entry Point
Auto-loads data, shows live prices with sectors, Wolf & Wright UI.
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
# Wolf & Wright CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .stApp { background-color: #ffffff; }

    /* ========== DARK NAVY SIDEBAR ========== */
    [data-testid="stSidebar"] {
        background-color: #011f24;
        border-right: 1px solid rgba(255,255,255,0.08);
        box-shadow: 2px 0 12px rgba(0,0,0,0.15);
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    /* Sidebar text defaults - light on dark */
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSelectbox label {
        color: rgba(255,255,255,0.7) !important; font-size: 0.7rem;
        text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600;
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        font-family: 'Inter', sans-serif;
        color: #ffffff !important; font-size: 0.75rem; text-transform: uppercase;
        letter-spacing: 0.08em; font-weight: 700;
        border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.5rem;
    }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08); }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] small {
        color: rgba(255,255,255,0.7) !important;
    }

    /* Sidebar page navigation - dark theme */
    [data-testid="stSidebarNav"] {
        padding-top: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        padding-bottom: 0.5rem;
        margin-bottom: 0.5rem;
    }
    [data-testid="stSidebarNav"] li {
        margin: 2px 8px;
    }
    [data-testid="stSidebarNav"] a {
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 0.8rem !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
        display: flex !important;
        align-items: center !important;
    }
    [data-testid="stSidebarNav"] a span {
        color: rgba(255,255,255,0.7) !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(255,255,255,0.08) !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebarNav"] a:hover span {
        color: #ffffff !important;
    }
    [data-testid="stSidebarNav"] a[aria-selected="true"] {
        background: rgba(77,101,255,0.15) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-left: 3px solid #4d65ff !important;
    }
    [data-testid="stSidebarNav"] a[aria-selected="true"] span {
        color: #ffffff !important;
    }

    /* Hamburger button - dark navy style */
    button[kind="header"] {
        color: #ffffff !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        top: 0.5rem;
        left: 0.5rem;
        z-index: 999;
    }
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button {
        background: #011f24 !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        padding: 6px 8px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        transition: all 0.2s;
    }
    [data-testid="stSidebarCollapsedControl"] button:hover,
    [data-testid="collapsedControl"] button:hover {
        background: #032b32 !important;
        border-color: #4d65ff !important;
        box-shadow: 0 2px 12px rgba(77,101,255,0.15);
    }
    [data-testid="stSidebarCollapsedControl"] button svg,
    [data-testid="collapsedControl"] button svg {
        stroke: #ffffff !important;
        width: 20px !important;
        height: 20px !important;
    }
    /* Close button inside sidebar */
    [data-testid="stSidebarCollapseButton"] button {
        color: rgba(255,255,255,0.7) !important;
        background: transparent !important;
        border: none !important;
    }
    [data-testid="stSidebarCollapseButton"] button:hover {
        color: #ffffff !important;
    }

    /* ========== TOPBAR ========== */
    .ww-topbar {
        display: flex; align-items: center; justify-content: space-between;
        background: #011f24; color: #ffffff;
        padding: 0.8rem 1.2rem; margin: -1rem -1rem 1.5rem -1rem;
        border-radius: 0 0 10px 10px;
    }
    .ww-logo {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem; font-weight: 700; color: #ffffff;
        letter-spacing: -0.02em;
    }
    .ww-logo span {
        color: rgba(255,255,255,0.5); font-weight: 400; font-size: 0.85rem; margin-left: 0.5rem;
    }
    .ww-tagline {
        font-family: 'Inter', sans-serif;
        font-style: normal;
        color: rgba(255,255,255,0.6);
        font-size: 0.8rem;
        font-weight: 400;
        letter-spacing: 0.02em;
    }

    /* ========== METRICS ========== */
    [data-testid="stMetric"] {
        background: #fff; border: 1px solid #e2e5ea;
        border-radius: 10px; padding: 1.2rem 1rem;
        text-align: center;
        transition: border-color 0.4s ease, box-shadow 0.4s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: #4d65ff;
        box-shadow: 0 2px 12px rgba(77,101,255,0.10);
    }
    [data-testid="stMetric"] > div {
        display: flex; flex-direction: column; align-items: center;
    }
    [data-testid="stMetric"] label {
        font-family: 'Inter', sans-serif;
        color: #6b7280 !important; font-size: 0.68rem !important;
        text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600 !important;
        text-align: center !important; width: 100%;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #011f24 !important; font-size: 1.5rem !important; font-weight: 700 !important;
        text-align: center !important; width: 100%;
    }

    /* ========== HEADINGS ========== */
    .stApp h1 { display: none; }
    .stApp h2, .stApp h3 {
        font-family: 'Inter', sans-serif;
        color: #011f24; font-weight: 600; font-size: 0.85rem; text-transform: uppercase;
        letter-spacing: 0.05em; border-bottom: 1px solid #e2e5ea;
        padding-bottom: 0.5rem; margin-top: 2rem;
    }

    /* ========== STYLED TABLES ========== */
    .styled-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border: 1px solid #e2e5ea;
        border-radius: 10px;
        overflow: hidden;
        font-size: 0.82rem;
    }
    .styled-table thead th {
        background: #f4f5f7;
        color: #6b7280;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 10px 12px;
        text-align: center;
        border-bottom: 2px solid #e2e5ea;
        white-space: nowrap;
    }
    .styled-table tbody td {
        padding: 9px 12px;
        text-align: center;
        color: #011f24;
        border-bottom: 1px solid #f0f0f0;
        white-space: nowrap;
    }
    .styled-table tbody tr:last-child td {
        border-bottom: none;
    }
    .styled-table tbody tr:hover {
        background: #f0f4f8;
    }
    .styled-table .ticker-cell {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #4d65ff;
        text-align: left;
    }
    .styled-table .sector-cell {
        text-align: left;
        color: #6b7280;
        font-size: 0.75rem;
    }
    .styled-table .positive { color: #00b386; font-weight: 600; }
    .styled-table .negative { color: #eb5b3c; font-weight: 600; }
    .styled-table .na-cell { color: #c0c0c0; }

    /* ========== DATAFRAME OVERRIDES ========== */
    [data-testid="stDataFrame"] {
        border: 1px solid #e2e5ea;
        border-radius: 10px;
        overflow: hidden;
    }

    /* ========== CHART CARDS ========== */
    .chart-card {
        background: #131722;
        border: 1px solid #2d3548;
        border-radius: 10px;
        padding: 1rem 1rem 0.5rem 1rem;
        margin-bottom: 1rem;
    }
    .chart-card h4 {
        font-family: 'Inter', sans-serif;
        color: #d1d4dc;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin: 0 0 0.5rem 0;
    }

    /* ========== UTILITY ========== */
    .profit { color: #00b386; font-weight: 600; }
    .loss { color: #eb5b3c; font-weight: 600; }
    .muted { color: #6b7280; font-size: 0.8rem; }

    /* ========== HEADER ========== */
    footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: #ffffff;
        border-bottom: 1px solid #e2e5ea;
    }

    /* ========== MOBILE ========== */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }
        .ww-topbar {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.3rem;
        }
        .ww-logo { font-size: 1.1rem; }
        .ww-logo span { font-size: 0.7rem; }
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
        .ww-logo { font-size: 1rem; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 0.95rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
from core.portfolio import (  # noqa: E402
    init_session_state, Portfolio, add_holding, sell_holding,
    get_holdings_summary, save_holdings,
)
from core.data_fetch import (  # noqa: E402
    fetch_multi_asset_data, calculate_returns, fetch_latest_prices, get_sectors, POPULAR_TICKERS,
)
from core.regime_detector import detect_regime  # noqa: E402

init_session_state()

# ---------------------------------------------------------------------------
# Sidebar (Advisor chat only)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Advisor")

    from chat.engine import get_active_provider  # noqa: E402
    _provider = get_active_provider()
    if "Fallback" not in _provider:
        st.caption(f"Powered by {_provider}")
    else:
        st.caption("Rules-based mode")

    chat_container = st.container(height=250)
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_msg = st.chat_input("Ask anything about finance...", key="sidebar_chat")
    if user_msg:
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        from chat.engine import get_response
        _hist = [
            m for m in st.session_state.chat_history
            if m["role"] in ("user", "assistant")
        ][:-1]  # Exclude the message we just appended
        reply = get_response(user_msg, st.session_state, history=_hist)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

# --- 1. Topbar ---
st.markdown("""
<div class="ww-topbar">
    <div class="ww-logo">hedging<span>platform</span></div>
    <div class="ww-tagline">Portfolio Risk & Hedging Analysis</div>
</div>
""", unsafe_allow_html=True)

# --- 2. Portfolio Controls (inline in dashboard) ---
_ctrl_left, _ctrl_mid, _ctrl_right = st.columns([4, 1, 1])
with _ctrl_left:
    tickers = st.multiselect(
        "INSTRUMENTS",
        options=POPULAR_TICKERS,
        default=st.session_state.portfolio.tickers,
        help="Search and select 2-8 ticker symbols",
    )
with _ctrl_mid:
    period = st.selectbox(
        "PERIOD",
        options=[1, 2, 3, 5, 10],
        index=2,
        format_func=lambda x: f"{x}Y",
    )
with _ctrl_right:
    st.markdown("<br>", unsafe_allow_html=True)
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

if not st.session_state.data_loaded:
    st.info("Loading default portfolio (SPY, TLT, GLD)...")
    st.stop()

portfolio = st.session_state.portfolio
summary = portfolio.summary()
returns = portfolio.returns

import plotly.graph_objects as go  # noqa: E402
from core.style import COLORS, BLUE, kite_layout, color_with_alpha  # noqa: E402

# Per-ticker returns summary next to controls
_ann_ret_quick = returns.mean() * 252
_ret_cols = st.columns(len(portfolio.tickers))
for _rc, _t in zip(_ret_cols, portfolio.tickers):
    _rv = _ann_ret_quick[_t]
    _rc.metric(_t, f"{_rv:+.2%}")

# Fetch live prices early (needed by Add Stock + signals + later sections)
with st.spinner("Fetching latest prices..."):
    live_df = fetch_latest_prices(portfolio.tickers)

# --- 3. Add Stock ---
st.markdown("### Add Stock")
add_col1, add_col2, add_col3, add_col4 = st.columns([2, 1.5, 1.5, 1])
with add_col1:
    add_ticker = st.selectbox(
        "Ticker", options=portfolio.tickers, key="add_ticker_select",
        label_visibility="collapsed",
    )
with add_col2:
    add_shares = st.number_input(
        "Shares", min_value=0.01, value=1.0, step=1.0, key="add_shares",
    )
with add_col3:
    default_price = 0.0
    if live_df is not None and not live_df.empty:
        match = live_df[live_df["Ticker"] == add_ticker]
        if not match.empty and pd.notna(match.iloc[0]["Price"]):
            default_price = float(match.iloc[0]["Price"])
    if default_price > 0:
        center = round(default_price / 15) * 15
        options = sorted(set(
            max(15, center + i * 15) for i in range(-5, 6)
        ))
        closest = min(options, key=lambda x: abs(x - default_price))
        add_price = st.selectbox(
            "Buy Price", options=[float(o) for o in options],
            index=options.index(closest), key="add_price_select",
            format_func=lambda x: f"${x:,.0f}",
        )
    else:
        add_price = st.number_input(
            "Buy Price", min_value=0.01, value=0.01,
            step=0.01, key="add_price",
        )
with add_col4:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Add", type="primary", key="add_holding_btn", use_container_width=True):
        add_holding(add_ticker, add_shares, add_price)
        save_holdings()
        st.rerun()

# --- 4. TradingView Ticker Tape ---
from core.tradingview import ticker_tape_html  # noqa: E402
st.components.v1.html(ticker_tape_html(portfolio.tickers), height=50)

# --- 3. Metrics row (Instruments, Data Points, HHI) ---
c1, c2, c3 = st.columns(3)
c1.metric("Instruments", summary["n_assets"])
c2.metric("Data Points", summary["data_points"])
c3.metric("HHI", f"{summary['hhi']:.3f}")

# --- 5. Key Signals ---
st.markdown("### Key Signals")
from core.signals import generate_all_signals, get_signal_color  # noqa: E402

st.markdown("### Live Prices & Sectors")

_held = st.session_state.holdings
_cur_prices = {}
if _held and live_df is not None and not live_df.empty:
    for _, _r in live_df.iterrows():
        if pd.notna(_r.get("Price")):
            _cur_prices[_r["Ticker"]] = _r["Price"]

_signals = generate_all_signals(
    portfolio, st.session_state.regime_df, _held, _cur_prices
)
_top_sigs = _signals[:3]
if _top_sigs:
    _sig_cols = st.columns(len(_top_sigs))
    for _col, _sig in zip(_sig_cols, _top_sigs):
        _color = get_signal_color(_sig.signal_type)
        _col.markdown(
            f'<div style="border-left:3px solid {_color};padding:8px 12px;'
            f'background:#fff;border:1px solid #e2e5ea;border-left:3px solid {_color};'
            f'border-radius:6px;font-size:0.8rem;">'
            f'<span style="color:{_color};font-weight:600;font-size:0.7rem;">'
            f'{_sig.signal_type.value.upper()}</span><br>'
            f'<span style="color:#011f24;font-weight:500;">{_sig.title}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.caption("View all recommendations on the Recommendations page.")

# --- 6. Live Prices table ---
if not live_df.empty and live_df["Price"].notna().any():
    # Build styled HTML table for live prices
    def _fmt_val(val, fmt, prefix="", suffix=""):
        if pd.isna(val) or val is None:
            return '<span class="na-cell">N/A</span>'
        return f"{prefix}{fmt.format(val)}{suffix}"

    def _fmt_change(val, fmt="{:+.2f}", suffix=""):
        if pd.isna(val) or val is None:
            return '<span class="na-cell">N/A</span>'
        cls = "positive" if val >= 0 else "negative"
        return f'<span class="{cls}">{fmt.format(val)}{suffix}</span>'

    _cols = ["Sector", "Price", "Change", "Chg %", "Volume",
             "Mkt Cap", "P/E", "EPS", "Div Yield", "Beta", "52W High", "52W Low"]
    _header = "".join(f"<th>{c}</th>" for c in ["Ticker"] + _cols)
    _na_span = '<span class="na-cell">N/A</span>'
    _rows_html = ""
    for _, r in live_df.iterrows():
        vol_val = r["Volume"]
        vol_cell = _fmt_val(vol_val, "{:,.0f}") if pd.notna(vol_val) and vol_val > 0 else _na_span
        mktcap_val = r.get("Mkt Cap")
        mktcap_cell = mktcap_val if pd.notna(mktcap_val) else _na_span
        _rows_html += "<tr>"
        _rows_html += f'<td class="ticker-cell">{r["Ticker"]}</td>'
        _rows_html += f'<td class="sector-cell">{r["Sector"]}</td>'
        _rows_html += f'<td>{_fmt_val(r["Price"], "{:,.2f}", prefix="$")}</td>'
        _rows_html += f'<td>{_fmt_change(r["Change"])}</td>'
        _rows_html += f'<td>{_fmt_change(r["Change %"], suffix="%")}</td>'
        _rows_html += f'<td>{vol_cell}</td>'
        _rows_html += f'<td>{mktcap_cell}</td>'
        _rows_html += f'<td>{_fmt_val(r.get("P/E"), "{:.1f}")}</td>'
        _rows_html += f'<td>{_fmt_val(r.get("EPS"), "{:.2f}", prefix="$")}</td>'
        _rows_html += f'<td>{_fmt_val(r.get("Div Yield"), "{:.2f}", suffix="%")}</td>'
        _rows_html += f'<td>{_fmt_val(r.get("Beta"), "{:.2f}")}</td>'
        _rows_html += f'<td>{_fmt_val(r.get("52W High"), "{:,.2f}", prefix="$")}</td>'
        _rows_html += f'<td>{_fmt_val(r.get("52W Low"), "{:,.2f}", prefix="$")}</td>'
        _rows_html += "</tr>"

    st.markdown(
        f'<div style="overflow-x:auto;">'
        f'<table class="styled-table"><thead><tr>{_header}</tr></thead>'
        f'<tbody>{_rows_html}</tbody></table></div>',
        unsafe_allow_html=True,
    )

# --- 7. Top Headlines ---
st.markdown("### Top Headlines")
from core.news import fetch_portfolio_news  # noqa: E402
from datetime import datetime as _dt  # noqa: E402

_news_cache_time = st.session_state.get("news_cache_time")
_news_valid = (
    _news_cache_time is not None
    and (_dt.now() - _news_cache_time).seconds < 300
)
if not _news_valid:
    _top_news = fetch_portfolio_news(portfolio.tickers, max_per_ticker=2)
    st.session_state.news_cache = _top_news
    st.session_state.news_cache_time = _dt.now()
else:
    _top_news = st.session_state.news_cache

for _item in _top_news[:5]:
    _sent = _item["sentiment"]
    _sc = "#00b386" if _sent == "Positive" else "#d43725" if _sent == "Negative" else "#6b7280"
    _link = _item.get("link", "")
    _title_disp = _item["title"]
    if _link:
        _title_disp = f'<a href="{_link}" target="_blank" style="color:#011f24;text-decoration:none;">{_item["title"]}</a>'
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0;'
        f'border-bottom:1px solid #f0f0f0;font-size:0.85rem;">'
        f'<span style="background:#f0f4f8;color:#011f24;padding:1px 6px;'
        f'border-radius:3px;font-size:0.7rem;font-weight:500;">{_item["ticker"]}</span>'
        f'{_title_disp}'
        f'<span style="color:{_sc};font-size:0.7rem;font-weight:600;margin-left:auto;">'
        f'{_sent}</span></div>',
        unsafe_allow_html=True,
    )
if _top_news:
    st.caption("View all news on the News page in the sidebar.")

# --- 8. Allocation ---
st.markdown("### Allocation")

sectors = get_sectors(portfolio.tickers)

col_pie, col_table = st.columns([1, 1])

with col_pie:
    fig = go.Figure(data=[go.Pie(
        labels=[f"{t} ({sectors[t]})" for t in portfolio.tickers],
        values=portfolio.weights,
        hole=0.55,
        marker=dict(colors=COLORS[:portfolio.n_assets],
                    line=dict(color="#131722", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#d1d4dc"),
    )])
    fig.update_layout(**kite_layout(height=340), showlegend=False)
    st.markdown('<div class="chart-card"><h4>Allocation</h4>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_table:
    ann_ret = returns.mean() * 252
    ann_vol = returns.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol

    _alloc_header = "".join(f"<th>{c}</th>" for c in
                            ["Instrument", "Sector", "Weight", "Return", "Volatility", "Sharpe"])
    _alloc_rows = ""
    for t in portfolio.tickers:
        i = portfolio.tickers.index(t)
        _ret_val = ann_ret[t]
        _ret_cls = "positive" if _ret_val >= 0 else "negative"
        _alloc_rows += (
            f'<tr>'
            f'<td class="ticker-cell">{t}</td>'
            f'<td class="sector-cell">{sectors[t]}</td>'
            f'<td>{portfolio.weights[i]:.1%}</td>'
            f'<td><span class="{_ret_cls}">{_ret_val:+.2%}</span></td>'
            f'<td>{ann_vol[t]:.2%}</td>'
            f'<td>{sharpe[t]:.2f}</td>'
            f'</tr>'
        )
    st.markdown(
        f'<div style="overflow-x:auto;">'
        f'<table class="styled-table"><thead><tr>{_alloc_header}</tr></thead>'
        f'<tbody>{_alloc_rows}</tbody></table></div>',
        unsafe_allow_html=True,
    )

# --- 9. Sector Exposure ---
st.markdown("### Sector Exposure")

# Compute weights from holdings if available
_holdings = st.session_state.holdings
_sector_weights = portfolio.weights.copy()

if _holdings:
    _active = {t: h for t, h in _holdings.items()
               if t in portfolio.tickers and h.get("shares", 0) > 0}
    _total_val = sum(
        h["shares"] * h["buy_price"] for h in _active.values()
    )
    if _active and _total_val > 0:
        _sector_weights = np.array([
            _active[t]["shares"] * _active[t]["buy_price"] / _total_val
            if t in _active else 0.0
            for t in portfolio.tickers
        ])

# Aggregate by sector
_sector_agg = {}
for i, t in enumerate(portfolio.tickers):
    sec = sectors[t]
    _sector_agg.setdefault(sec, {"weight": 0.0, "count": 0})
    _sector_agg[sec]["weight"] += _sector_weights[i]
    _sector_agg[sec]["count"] += 1

_sec_names = list(_sector_agg.keys())
_sec_weights = [_sector_agg[s]["weight"] for s in _sec_names]
_sec_counts = [_sector_agg[s]["count"] for s in _sec_names]

sec_col1, sec_col2 = st.columns([1, 1])

with sec_col1:
    fig_sec = go.Figure(data=[go.Pie(
        labels=_sec_names,
        values=_sec_weights,
        hole=0.55,
        marker=dict(colors=COLORS[:len(_sec_names)],
                    line=dict(color="#131722", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#d1d4dc"),
    )])
    fig_sec.update_layout(**kite_layout(height=340), showlegend=False)
    st.markdown('<div class="chart-card"><h4>Sector Breakdown</h4>', unsafe_allow_html=True)
    st.plotly_chart(fig_sec, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with sec_col2:
    _sec_header = "".join(f"<th>{c}</th>" for c in ["Sector", "Weight", "# Tickers"])
    _sec_rows = ""
    for sn, sw, sc in zip(_sec_names, _sec_weights, _sec_counts):
        _sec_rows += (
            f'<tr>'
            f'<td class="ticker-cell">{sn}</td>'
            f'<td>{sw:.1%}</td>'
            f'<td>{sc}</td>'
            f'</tr>'
        )
    st.markdown(
        f'<div style="overflow-x:auto;">'
        f'<table class="styled-table"><thead><tr>{_sec_header}</tr></thead>'
        f'<tbody>{_sec_rows}</tbody></table></div>',
        unsafe_allow_html=True,
    )

    # Sector HHI
    sec_hhi = sum(w ** 2 for w in _sec_weights)
    st.metric("Sector HHI", f"{sec_hhi:.3f}")

# Concentration warnings
for sec, data in _sector_agg.items():
    pct = data["weight"] * 100
    if pct > 60:
        st.error(f"Sector '{sec}' has {pct:.1f}% concentration — "
                 "extremely high risk from single-sector exposure.")
    elif pct > 40:
        st.warning(f"Sector '{sec}' has {pct:.1f}% concentration — "
                   "consider diversifying across sectors.")

# --- 10. My Holdings ---
st.markdown("### My Holdings")

# Holdings with integrated sell buttons
holdings = st.session_state.holdings
if holdings:
    held_tickers = list(holdings.keys())
    current_price_map = {}
    if live_df is not None and not live_df.empty:
        for _, row in live_df.iterrows():
            if pd.notna(row.get("Price")):
                current_price_map[row["Ticker"]] = row["Price"]
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

        # Each holding: info + sell in one row
        for r in rows:
            pnl_color = "profit" if r["P&L"] >= 0 else "loss"
            st.markdown(
                f'**{r["Ticker"]}** &mdash; {r["Shares"]:.2f} shares @ '
                f'${r["Buy Price"]:,.2f} &rarr; ${r["Current Price"]:,.2f} '
                f'&nbsp;&nbsp; <span class="{pnl_color}">'
                f'P&L: ${r["P&L"]:+,.2f} ({r["P&L %"]:+.2f}%)</span>',
                unsafe_allow_html=True,
            )
            sc1, sc2 = st.columns([3, 1])
            with sc1:
                sell_qty = st.number_input(
                    "Shares to sell", min_value=0.0, max_value=float(r["Shares"]),
                    value=0.0, step=1.0, key=f"sell_{r['Ticker']}",
                    label_visibility="collapsed",
                    placeholder="Shares to sell",
                )
            with sc2:
                if st.button(
                    f"Sell {r['Ticker']}", key=f"sell_btn_{r['Ticker']}",
                    type="primary", use_container_width=True,
                ):
                    if sell_qty > 0:
                        sell_holding(r["Ticker"], sell_qty)
                        save_holdings()
                        st.rerun()
                    else:
                        st.warning("Enter shares to sell")
else:
    st.info("No holdings yet. Use Add Stock at the top of the page.")

# --- 11. Individual stock price charts ---
st.markdown("### Individual Price History")

fig_prices = go.Figure()
for i, ticker in enumerate(portfolio.tickers):
    # Normalize to 100 for comparison
    _clr = COLORS[i % len(COLORS)]
    normalized = (portfolio.prices[ticker] / portfolio.prices[ticker].iloc[0]) * 100
    fig_prices.add_trace(go.Scatter(
        x=normalized.index, y=normalized.values,
        mode="lines", name=f"{ticker} ({sectors[ticker]})",
        line=dict(width=3, color=_clr, shape="spline", smoothing=0.5),
        fill="tozeroy",
        fillcolor=color_with_alpha(_clr, 0.06),
    ))
fig_prices.update_layout(
    **kite_layout(height=420),
    yaxis_title="Normalized Price (Base = 100)",
    hovermode="x unified",
)

st.markdown('<div class="chart-card"><h4>Price History</h4>', unsafe_allow_html=True)
st.plotly_chart(fig_prices, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 12. TradingView Analysis ---
st.markdown("### TradingView Analysis")
from core.tradingview import advanced_chart_html, technical_analysis_html  # noqa: E402

_tv_ticker = st.selectbox(
    "Select instrument for TradingView analysis",
    options=portfolio.tickers,
    key="tv_ticker_select",
)
_tv_chart_col, _tv_ta_col = st.columns([2, 1])
with _tv_chart_col:
    st.components.v1.html(advanced_chart_html(_tv_ticker, height=450), height=460)
with _tv_ta_col:
    st.components.v1.html(technical_analysis_html(_tv_ticker, height=400), height=410)

# --- 13. Download Report ---
st.markdown("### Download Report")

from risk.var_cvar import var_cvar_summary  # noqa: E402
from risk.correlation import calculate_diversification_ratio  # noqa: E402

try:
    var_s = var_cvar_summary(returns, portfolio.weights, 0.95)
    div_ratio = calculate_diversification_ratio(returns, portfolio.weights)
except Exception:
    var_s = {}
    div_ratio = None

report_rows = []
for i, t in enumerate(portfolio.tickers):
    report_rows.append({
        "Ticker": t,
        "Sector": sectors[t],
        "Weight": f"{portfolio.weights[i]:.2%}",
        "Ann Return": f"{(returns[t].mean() * 252):.2%}",
        "Ann Vol": f"{(returns[t].std() * np.sqrt(252)):.2%}",
        "Sharpe": f"{(returns[t].mean() * 252) / (returns[t].std() * np.sqrt(252)):.2f}",
    })
report_df = pd.DataFrame(report_rows)

# Add summary row
summary_row = {
    "Ticker": "PORTFOLIO",
    "Sector": "",
    "Weight": "100%",
    "Ann Return": f"{(portfolio.portfolio_returns.mean() * 252):.2%}",
    "Ann Vol": f"{(portfolio.portfolio_returns.std() * np.sqrt(252)):.2%}",
    "Sharpe": f"{(portfolio.portfolio_returns.mean() * 252) / (portfolio.portfolio_returns.std() * np.sqrt(252)):.2f}",
}
report_df = pd.concat([report_df, pd.DataFrame([summary_row])], ignore_index=True)

# Add risk metrics as extra rows
risk_rows = []
if var_s:
    risk_rows.append({"Ticker": "95% VaR", "Sector": f"{var_s.get('historical_var', 0):.2%}"})
    risk_rows.append({"Ticker": "95% CVaR", "Sector": f"{var_s.get('historical_cvar', 0):.2%}"})
if div_ratio:
    risk_rows.append({"Ticker": "Div Ratio", "Sector": f"{div_ratio:.2f}"})
risk_rows.append({"Ticker": "HHI", "Sector": f"{summary['hhi']:.4f}"})
if risk_rows:
    report_df = pd.concat([report_df, pd.DataFrame(risk_rows)], ignore_index=True)

dl1, dl2, dl3 = st.columns(3)
with dl1:
    import io
    buf1 = io.BytesIO()
    report_df.to_excel(buf1, index=False, engine="openpyxl")
    st.download_button(
        "Download Portfolio Report",
        buf1.getvalue(),
        file_name="portfolio_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
with dl2:
    buf2 = io.BytesIO()
    returns.to_excel(buf2, engine="openpyxl")
    st.download_button(
        "Download Returns Data",
        buf2.getvalue(),
        file_name="returns_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
with dl3:
    if st.button("Generate PDF Report", use_container_width=True):
        with st.spinner("Generating PDF..."):
            from core.report_gen import generate_summary_report  # noqa: E402
            _pdf_bytes = generate_summary_report(
                portfolio, st.session_state.regime_df,
                st.session_state.holdings, _cur_prices, sectors,
            )
        st.session_state["_main_pdf"] = bytes(_pdf_bytes)
    if st.session_state.get("_main_pdf"):
        st.download_button(
            "Download PDF",
            st.session_state["_main_pdf"],
            file_name="portfolio_summary.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

st.markdown(
    f'<p class="muted">Data: {summary["date_range"]} &middot; Navigate to pages in sidebar for detailed analysis</p>',
    unsafe_allow_html=True,
)
