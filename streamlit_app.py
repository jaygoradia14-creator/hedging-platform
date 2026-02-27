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

    user_msg = st.chat_input("Ask anything about finance...", key="sidebar_chat")
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

# --- Sector Exposure ---
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
                    line=dict(color="#ffffff", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#333"),
    )])
    fig_sec.update_layout(**kite_layout(height=340), showlegend=False)
    st.plotly_chart(fig_sec, use_container_width=True)

with sec_col2:
    sec_table = pd.DataFrame({
        "Sector": _sec_names,
        "Weight %": [f"{w:.1%}" for w in _sec_weights],
        "# Tickers": _sec_counts,
    })
    st.dataframe(sec_table.set_index("Sector"),
                 use_container_width=True, height=300)

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

# --- My Holdings ---
st.markdown("### My Holdings")

# Add Stock form — at the top so it's always visible
st.markdown("#### Add Stock")
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
        # Build price options in steps of 15, centered around current price
        center = round(default_price / 15) * 15
        options = sorted(set(
            max(15, center + i * 15) for i in range(-5, 6)
        ))
        # Pick the closest option to actual price as default
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
    st.info("No holdings yet. Add stocks above.")

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

# --- Individual cumulative returns with benchmark ---
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

# Benchmark: S&P 500 (SPY) — if not already in portfolio
if "SPY" not in portfolio.tickers:
    try:
        bench_prices = fetch_multi_asset_data(
            ["SPY"],
            str(portfolio.prices.index[0].date()),
            str(portfolio.prices.index[-1].date()),
        )
        if not bench_prices.empty:
            bench_ret = calculate_returns(bench_prices)
            bench_cum = (1 + bench_ret["SPY"]).cumprod() - 1
            fig_cum.add_trace(go.Scatter(
                x=bench_cum.index, y=bench_cum.values * 100,
                mode="lines", name="S&P 500 (Benchmark)",
                line=dict(color="#999", width=2, dash="dash"),
            ))
    except Exception:
        pass

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

# --- Download Report ---
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

dl1, dl2 = st.columns(2)
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

st.markdown(
    f'<p class="muted">Data: {summary["date_range"]} &middot; Navigate to pages in sidebar for detailed analysis</p>',
    unsafe_allow_html=True,
)
