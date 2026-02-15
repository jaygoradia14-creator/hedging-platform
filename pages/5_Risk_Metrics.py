"""
Risk Metrics (Zerodha Kite style).
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

from core.portfolio import init_session_state
from core.style import page_header, kite_layout, BLUE, RED, GREEN, ORANGE, REGIME_COLORS
from risk.var_cvar import var_cvar_summary, regime_conditional_var
from risk.monte_carlo import (
    simulate_paths,
    regime_aware_simulation,
    simulation_statistics,
    percentile_bands,
)

init_session_state()
page_header("Risk Metrics")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns
weights = portfolio.weights
regime_df = st.session_state.regime_df

# --- VaR / CVaR ---
st.markdown("### Value-at-Risk & Expected Shortfall")
confidence = st.selectbox("Confidence", [0.90, 0.95, 0.99], index=1,
                          format_func=lambda x: f"{x:.0%}")

summary = var_cvar_summary(returns, weights, confidence)

c1, c2, c3 = st.columns(3)
c1.metric("Historical VaR", f"{summary['historical_var']:.2%}")
c2.metric("Historical CVaR", f"{summary['historical_cvar']:.2%}")
c3.metric("Parametric VaR", f"{summary['parametric_var']:.2%}")

# --- Regime VaR ---
if regime_df is not None:
    st.markdown("### VaR by Regime")
    regime_var = regime_conditional_var(returns, weights, regime_df, confidence)
    if regime_var:
        fig_rv = go.Figure(data=[go.Bar(
            x=list(regime_var.keys()),
            y=[v * 100 for v in regime_var.values()],
            marker_color=[REGIME_COLORS.get(k, "#ccc") for k in regime_var.keys()],
            text=[f"{v:.2%}" if not np.isnan(v) else "N/A" for v in regime_var.values()],
            textposition="auto", textfont=dict(color="#333"),
        )])
        fig_rv.update_layout(**kite_layout(height=300),
                             yaxis_title=f"VaR ({confidence:.0%})", yaxis_ticksuffix="%")
        st.plotly_chart(fig_rv, use_container_width=True)

# --- Monte Carlo ---
st.markdown("### Monte Carlo Simulation")
sim_type = st.radio("Type", ["Standard", "Regime-Aware"], horizontal=True)
n_sims = st.slider("Simulations", 100, 5000, 1000, step=100)
n_days = st.slider("Horizon (days)", 21, 504, 252, step=21)

with st.spinner("Simulating..."):
    if sim_type == "Standard":
        sims = simulate_paths(returns, weights, n_sims, n_days, seed=42)
    else:
        sims = regime_aware_simulation(returns, weights, regime_df, n_sims, n_days, seed=42)

bands = percentile_bands(sims)
stats = simulation_statistics(sims)

# Fan chart
st.markdown("### Projection")
days = np.arange(1, n_days + 1)

fig_fan = go.Figure()
fig_fan.add_trace(go.Scatter(
    x=days, y=bands["p95"] * 100, mode="lines", line=dict(width=0), showlegend=False,
))
fig_fan.add_trace(go.Scatter(
    x=days, y=bands["p5"] * 100, mode="lines", line=dict(width=0),
    fill="tonexty", fillcolor="rgba(56,126,209,0.1)", name="5th-95th",
))
fig_fan.add_trace(go.Scatter(
    x=days, y=bands["p75"] * 100, mode="lines", line=dict(width=0), showlegend=False,
))
fig_fan.add_trace(go.Scatter(
    x=days, y=bands["p25"] * 100, mode="lines", line=dict(width=0),
    fill="tonexty", fillcolor="rgba(56,126,209,0.25)", name="25th-75th",
))
fig_fan.add_trace(go.Scatter(
    x=days, y=bands["p50"] * 100, mode="lines",
    line=dict(color=BLUE, width=2), name="Median",
))
fig_fan.update_layout(**kite_layout(height=400),
                      xaxis_title="Trading Days",
                      yaxis_title="Return %", yaxis_ticksuffix="%")
st.plotly_chart(fig_fan, use_container_width=True)

# Terminal distribution
st.markdown("### Terminal Distribution")
terminal = sims[:, -1]

fig_hist = go.Figure(data=[go.Histogram(
    x=terminal * 100, nbinsx=50, marker_color=BLUE,
    marker_line=dict(color="#fff", width=0.5),
)])
fig_hist.add_vline(x=0, line_dash="dash", line_color=RED)
fig_hist.update_layout(**kite_layout(height=300),
                       xaxis_title="Terminal Return %", xaxis_ticksuffix="%",
                       yaxis_title="Count")
st.plotly_chart(fig_hist, use_container_width=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Median", f"{stats['p50']:.1%}")
c2.metric("Mean", f"{stats['mean']:.1%}")
c3.metric("Prob Loss", f"{stats['prob_loss']:.1%}")
c4.metric("Std Dev", f"{stats['std']:.1%}")
