"""
Dashboard - Portfolio overview and key metrics.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.portfolio import init_session_state
from risk.correlation import calculate_diversification_ratio

init_session_state()

st.header("Portfolio Dashboard")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns

# --- Key Metrics ---
div_ratio = calculate_diversification_ratio(returns, portfolio.weights)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Assets", portfolio.n_assets)
c2.metric("HHI Concentration", f"{portfolio.hhi_concentration():.3f}")
c3.metric("Effective N", f"{portfolio.effective_n():.1f}")
c4.metric("Diversification Ratio", f"{div_ratio:.2f}")

st.markdown("---")

# --- Allocation pie + weight bar ---
col_pie, col_bar = st.columns(2)

with col_pie:
    st.subheader("Allocation")
    colors = ["#e94560", "#3498db", "#4ecca3", "#f39c12", "#9b59b6",
              "#1abc9c", "#e67e22", "#2ecc71"]
    fig_pie = go.Figure(data=[go.Pie(
        labels=portfolio.tickers,
        values=portfolio.weights,
        hole=0.4,
        marker=dict(colors=colors[:portfolio.n_assets]),
    )])
    fig_pie.update_layout(template="plotly_dark", height=320,
                          margin=dict(l=20, r=20, t=10, b=20))
    st.plotly_chart(fig_pie, use_container_width=True)

with col_bar:
    st.subheader("Weight Distribution")
    fig_bar = go.Figure(data=[go.Bar(
        x=portfolio.tickers,
        y=portfolio.weights * 100,
        marker_color=colors[:portfolio.n_assets],
        text=[f"{w:.1f}%" for w in portfolio.weights * 100],
        textposition="auto",
    )])
    fig_bar.update_layout(template="plotly_dark", height=320,
                          yaxis_title="Weight (%)",
                          margin=dict(l=40, r=20, t=10, b=40))
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Cumulative returns ---
st.subheader("Cumulative Returns")
cum_ret = (1 + returns).cumprod() - 1
port_cum = (1 + portfolio.portfolio_returns).cumprod() - 1

fig_cum = go.Figure()
for ticker in portfolio.tickers:
    fig_cum.add_trace(go.Scatter(
        x=cum_ret.index, y=cum_ret[ticker],
        mode="lines", name=ticker, opacity=0.6,
    ))
fig_cum.add_trace(go.Scatter(
    x=port_cum.index, y=port_cum.values,
    mode="lines", name="Portfolio",
    line=dict(color="#e94560", width=3),
))
fig_cum.update_layout(template="plotly_dark", height=400,
                      yaxis_title="Cumulative Return",
                      yaxis_tickformat=".0%",
                      margin=dict(l=50, r=20, t=10, b=40))
st.plotly_chart(fig_cum, use_container_width=True)

# --- Summary table ---
st.subheader("Asset Statistics (Annualized)")
ann_ret = returns.mean() * 252
ann_vol = returns.std() * np.sqrt(252)
sharpe = ann_ret / ann_vol

import pandas as pd
stats_df = pd.DataFrame({
    "Ann. Return": ann_ret.apply(lambda x: f"{x:.2%}"),
    "Ann. Volatility": ann_vol.apply(lambda x: f"{x:.2%}"),
    "Sharpe Ratio": sharpe.apply(lambda x: f"{x:.2f}"),
    "Weight": [f"{w:.1%}" for w in portfolio.weights],
})
st.dataframe(stats_df, use_container_width=True)
