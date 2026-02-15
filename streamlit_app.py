"""
Hedging Platform - Main Entry Point
Zerodha Kite-inspired UI
"""

import streamlit as st
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Hedging Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Zerodha Kite-inspired CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* === GLOBAL === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .stApp {
        background-color: #ffffff;
    }

    /* === SIDEBAR (Zerodha dark nav) === */
    [data-testid="stSidebar"] {
        background-color: #1a1a2e;
        color: #ffffff;
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSelectbox label {
        color: #9b9baf !important;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #ffffff !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        border-bottom: 1px solid #2d2d44;
        padding-bottom: 0.5rem;
    }
    [data-testid="stSidebar"] hr {
        border-color: #2d2d44;
    }

    /* === TOP BAR === */
    .kite-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #e8e8e8;
        padding: 0.6rem 0;
        margin-bottom: 1.5rem;
    }
    .kite-logo {
        font-size: 1.4rem;
        font-weight: 700;
        color: #387ed1;
        letter-spacing: -0.02em;
    }
    .kite-logo span { color: #999; font-weight: 400; font-size: 0.85rem; margin-left: 0.5rem; }

    /* === METRIC CARDS (Zerodha style) === */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e8e8e8;
        border-radius: 4px;
        padding: 1rem 1.2rem;
    }
    [data-testid="stMetric"] label {
        color: #999999 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600 !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #333333 !important;
        font-size: 1.4rem !important;
        font-weight: 600 !important;
    }

    /* === SECTION HEADERS === */
    .stApp h1 {
        display: none;
    }
    .stApp h2, .stApp h3 {
        color: #333333;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 1px solid #e8e8e8;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }

    /* === TABLES === */
    .stDataFrame {
        border: 1px solid #e8e8e8;
        border-radius: 4px;
    }
    .stDataFrame thead th {
        background: #f8f9fa !important;
        color: #999 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-weight: 600 !important;
        border-bottom: 1px solid #e8e8e8 !important;
    }

    /* === BUTTONS (Zerodha blue) === */
    .stButton > button[kind="primary"] {
        background-color: #387ed1;
        border: none;
        border-radius: 3px;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #2c6ab8;
    }

    /* === INFO/WARNING BOXES === */
    .stAlert {
        border-radius: 4px;
        border-left: 3px solid #387ed1;
        background: #f0f6ff;
    }

    /* === ZERODHA COLORS === */
    .profit { color: #00b386; font-weight: 600; }
    .loss { color: #d43725; font-weight: 600; }
    .muted { color: #999999; font-size: 0.8rem; }

    /* === HIDE STREAMLIT CHROME === */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] { background: #ffffff; border-bottom: 1px solid #e8e8e8; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
from core.portfolio import init_session_state, Portfolio
from core.data_fetch import fetch_multi_asset_data, calculate_returns
from core.regime_detector import detect_regime

init_session_state()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Portfolio")

    ticker_input = st.text_input(
        "INSTRUMENTS",
        value=", ".join(st.session_state.portfolio.tickers),
        help="Enter 2-8 ticker symbols",
    )

    period = st.selectbox(
        "PERIOD",
        options=[1, 2, 3, 5, 10],
        index=2,
        format_func=lambda x: f"{x}Y",
    )

    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

    if st.button("Load Data", type="primary", use_container_width=True):
        if len(tickers) < 2:
            st.error("Enter at least 2 tickers.")
        else:
            with st.spinner("Fetching..."):
                end = datetime.now()
                start = end - timedelta(days=365 * period)
                try:
                    prices = fetch_multi_asset_data(
                        tickers, str(start.date()), str(end.date())
                    )
                    returns = calculate_returns(prices)
                    regime_df = detect_regime(returns)

                    portfolio = Portfolio(
                        tickers=list(prices.columns),
                        weights=np.ones(len(prices.columns)) / len(prices.columns),
                        prices=prices,
                    )
                    portfolio.returns = returns
                    st.session_state.portfolio = portfolio
                    st.session_state.regime_df = regime_df
                    st.session_state.data_loaded = True
                    st.success(f"{len(prices.columns)} instruments loaded")
                except Exception as exc:
                    st.error(f"Failed: {exc}")

    st.markdown("---")

    # Chat
    st.markdown("## Advisor")

    chat_container = st.container(height=280)
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
    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem; color: #999;">
        <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">No instruments loaded</p>
        <p style="font-size: 0.85rem;">Enter tickers in the sidebar and click <strong>Load Data</strong> to begin.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    portfolio = st.session_state.portfolio
    summary = portfolio.summary()

    # Metrics row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Instruments", summary["n_assets"])
    c2.metric("Data Points", summary["data_points"])
    c3.metric("HHI", f"{summary['hhi']:.3f}")
    c4.metric("Effective N", f"{summary['effective_n']:.1f}")

    st.markdown("### Allocation")

    col_chart, col_table = st.columns([1, 1])

    with col_chart:
        import plotly.graph_objects as go
        kite_colors = ["#387ed1", "#00b386", "#d43725", "#f5a623",
                       "#7c3aed", "#06b6d4", "#ec4899", "#84cc16"]
        fig = go.Figure(data=[go.Pie(
            labels=portfolio.tickers,
            values=portfolio.weights,
            hole=0.55,
            marker=dict(colors=kite_colors[:portfolio.n_assets],
                        line=dict(color="#ffffff", width=2)),
            textinfo="label+percent",
            textfont=dict(size=12, color="#333"),
        )])
        fig.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=10, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            font=dict(family="Inter, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        import pandas as pd
        ann_ret = portfolio.returns.mean() * 252
        ann_vol = portfolio.returns.std() * np.sqrt(252)

        stats_df = pd.DataFrame({
            "Weight": [f"{w:.1%}" for w in portfolio.weights],
            "Return (Ann.)": ann_ret.apply(lambda x: f"{x:+.2%}"),
            "Volatility": ann_vol.apply(lambda x: f"{x:.2%}"),
            "Sharpe": (ann_ret / ann_vol).apply(lambda x: f"{x:.2f}"),
        }, index=portfolio.tickers)
        stats_df.index.name = "Instrument"
        st.dataframe(stats_df, use_container_width=True, height=280)

    # Cumulative returns
    st.markdown("### Performance")
    returns = portfolio.returns
    cum_ret = (1 + returns).cumprod() - 1
    port_cum = (1 + portfolio.portfolio_returns).cumprod() - 1

    fig_perf = go.Figure()
    for i, ticker in enumerate(portfolio.tickers):
        fig_perf.add_trace(go.Scatter(
            x=cum_ret.index, y=cum_ret[ticker] * 100,
            mode="lines", name=ticker, opacity=0.5,
            line=dict(width=1.5, color=kite_colors[i % len(kite_colors)]),
        ))
    fig_perf.add_trace(go.Scatter(
        x=port_cum.index, y=port_cum.values * 100,
        mode="lines", name="Portfolio",
        line=dict(color="#387ed1", width=2.5),
    ))
    fig_perf.update_layout(
        height=380,
        margin=dict(l=50, r=20, t=10, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="Return %", gridcolor="#f0f0f0", zerolinecolor="#e0e0e0",
                   ticksuffix="%"),
        xaxis=dict(gridcolor="#f0f0f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
                    font=dict(size=11)),
        font=dict(family="Inter, sans-serif", color="#333"),
    )
    st.plotly_chart(fig_perf, use_container_width=True)

    st.markdown(f'<p class="muted">Data: {summary["date_range"]} &middot; Navigate to pages in sidebar for detailed analysis</p>',
                unsafe_allow_html=True)
