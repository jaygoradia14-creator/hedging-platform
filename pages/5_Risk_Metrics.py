"""
Risk Metrics - VaR/CVaR gauges, Monte Carlo fan chart, terminal distribution.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

from core.portfolio import init_session_state
from risk.var_cvar import var_cvar_summary, regime_conditional_var
from risk.monte_carlo import (
    simulate_paths,
    regime_aware_simulation,
    simulation_statistics,
    percentile_bands,
)

init_session_state()

st.header("Risk Metrics")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns
weights = portfolio.weights
regime_df = st.session_state.regime_df

# --- VaR / CVaR Summary ---
st.subheader("Value-at-Risk & Expected Shortfall")
confidence = st.selectbox("Confidence Level", [0.90, 0.95, 0.99], index=1,
                          format_func=lambda x: f"{x:.0%}")

summary = var_cvar_summary(returns, weights, confidence)

c1, c2, c3 = st.columns(3)
c1.metric("Historical VaR", f"{summary['historical_var']:.2%}")
c2.metric("Historical CVaR", f"{summary['historical_cvar']:.2%}")
c3.metric("Parametric VaR", f"{summary['parametric_var']:.2%}")

# --- Regime-conditional VaR ---
if regime_df is not None:
    st.subheader("VaR by Regime")
    regime_var = regime_conditional_var(returns, weights, regime_df, confidence)

    regime_colors = {"Low Volatility": "#4ecca3", "Normal": "#3498db",
                     "High Volatility": "#f39c12", "Crisis": "#e74c3c"}

    if regime_var:
        fig_rv = go.Figure(data=[go.Bar(
            x=list(regime_var.keys()),
            y=list(regime_var.values()),
            marker_color=[regime_colors.get(k, "#888") for k in regime_var.keys()],
            text=[f"{v:.2%}" if not np.isnan(v) else "N/A" for v in regime_var.values()],
            textposition="auto",
        )])
        fig_rv.update_layout(template="plotly_dark", height=300,
                             yaxis_title=f"VaR ({confidence:.0%})",
                             yaxis_tickformat=".2%",
                             margin=dict(l=50, r=20, t=10, b=40))
        st.plotly_chart(fig_rv, use_container_width=True)

# --- Monte Carlo Simulation ---
st.subheader("Monte Carlo Simulation")

sim_type = st.radio("Simulation Type", ["Standard", "Regime-Aware"], horizontal=True)
n_sims = st.slider("Simulations", 100, 5000, 1000, step=100)
n_days = st.slider("Horizon (trading days)", 21, 504, 252, step=21)

with st.spinner("Running simulation..."):
    if sim_type == "Standard":
        sims = simulate_paths(returns, weights, n_sims, n_days, seed=42)
    else:
        sims = regime_aware_simulation(returns, weights, regime_df, n_sims, n_days, seed=42)

bands = percentile_bands(sims)
stats = simulation_statistics(sims)

# Fan chart
st.subheader("Projection Fan Chart")
days = np.arange(1, n_days + 1)

fig_fan = go.Figure()
fig_fan.add_trace(go.Scatter(
    x=days, y=bands["p95"], mode="lines", line=dict(width=0),
    showlegend=False,
))
fig_fan.add_trace(go.Scatter(
    x=days, y=bands["p5"], mode="lines", line=dict(width=0),
    fill="tonexty", fillcolor="rgba(52,152,219,0.15)",
    name="5th-95th",
))
fig_fan.add_trace(go.Scatter(
    x=days, y=bands["p75"], mode="lines", line=dict(width=0),
    showlegend=False,
))
fig_fan.add_trace(go.Scatter(
    x=days, y=bands["p25"], mode="lines", line=dict(width=0),
    fill="tonexty", fillcolor="rgba(52,152,219,0.3)",
    name="25th-75th",
))
fig_fan.add_trace(go.Scatter(
    x=days, y=bands["p50"], mode="lines",
    line=dict(color="#e94560", width=2), name="Median",
))
fig_fan.update_layout(
    template="plotly_dark", height=400,
    xaxis_title="Trading Days", yaxis_title="Cumulative Return",
    yaxis_tickformat=".0%",
    margin=dict(l=50, r=20, t=10, b=40),
)
st.plotly_chart(fig_fan, use_container_width=True)

# Terminal distribution
st.subheader("Terminal Distribution")
terminal = sims[:, -1]

fig_hist = go.Figure(data=[go.Histogram(
    x=terminal, nbinsx=50, marker_color="#3498db",
)])
fig_hist.add_vline(x=0, line_dash="dash", line_color="#e94560")
fig_hist.update_layout(
    template="plotly_dark", height=300,
    xaxis_title="Terminal Return", yaxis_title="Count",
    xaxis_tickformat=".0%",
    margin=dict(l=50, r=20, t=10, b=40),
)
st.plotly_chart(fig_hist, use_container_width=True)

# Summary stats
c1, c2, c3, c4 = st.columns(4)
c1.metric("Median Return", f"{stats['p50']:.1%}")
c2.metric("Mean Return", f"{stats['mean']:.1%}")
c3.metric("Prob. of Loss", f"{stats['prob_loss']:.1%}")
c4.metric("Std Dev", f"{stats['std']:.1%}")
