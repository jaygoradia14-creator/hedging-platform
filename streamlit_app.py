"""
Hedging Platform - Main Entry Point
====================================
Multi-page Streamlit app for portfolio risk analysis and hedging.
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

# Custom CSS
st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #ffffff; }
    .tagline { font-size: 1.1rem; color: #e94560; margin-bottom: 1rem; }
    .metric-card {
        background: #16213e; border-radius: 8px; padding: 1rem; text-align: center;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
from core.portfolio import init_session_state, update_portfolio, Portfolio
from core.data_fetch import fetch_multi_asset_data, calculate_returns
from core.regime_detector import detect_regime

init_session_state()

# ---------------------------------------------------------------------------
# Sidebar - Portfolio Controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## Portfolio Setup")

    ticker_input = st.text_input(
        "Tickers (comma-separated)",
        value=", ".join(st.session_state.portfolio.tickers),
        help="Enter 2-8 ticker symbols",
    )

    period = st.selectbox(
        "Lookback period",
        options=[1, 2, 3, 5, 10],
        index=2,
        format_func=lambda x: f"{x} year{'s' if x > 1 else ''}",
    )

    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

    if st.button("Load Data", type="primary", use_container_width=True):
        if len(tickers) < 2:
            st.error("Enter at least 2 tickers.")
        else:
            with st.spinner("Fetching market data..."):
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
                    st.success(f"Loaded {len(prices)} days for {len(prices.columns)} assets")
                except Exception as exc:
                    st.error(f"Data fetch failed: {exc}")

    st.markdown("---")

    # ---- Chat interface in sidebar ----
    st.markdown("## Ask the Advisor")

    # Chat history display
    chat_container = st.container(height=300)
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
# Main landing page
# ---------------------------------------------------------------------------
st.markdown('<h1 class="main-title">Hedging Platform</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="tagline">Portfolio risk analysis &amp; hedging effectiveness</p>',
    unsafe_allow_html=True,
)

if not st.session_state.data_loaded:
    st.info("Use the sidebar to enter tickers and load data, then navigate to analysis pages.")
else:
    portfolio = st.session_state.portfolio
    summary = portfolio.summary()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Assets", summary["n_assets"])
    c2.metric("Data Points", summary["data_points"])
    c3.metric("HHI", f"{summary['hhi']:.3f}")
    c4.metric("Effective N", f"{summary['effective_n']:.1f}")

    st.markdown("### Allocation")
    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Pie(
        labels=portfolio.tickers,
        values=portfolio.weights,
        hole=0.4,
        marker=dict(colors=["#e94560", "#3498db", "#4ecca3", "#f39c12", "#9b59b6",
                            "#1abc9c", "#e67e22", "#2ecc71"][:len(portfolio.tickers)]),
    )])
    fig.update_layout(
        template="plotly_dark", height=350,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**Date range:** {summary['date_range']}")
    st.caption("Navigate to pages in the sidebar for detailed analysis.")
