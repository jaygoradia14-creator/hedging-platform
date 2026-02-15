"""
Hedge Impact - compare hedging candidates, optimal ratio, before/after VaR.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from core.portfolio import init_session_state
from risk.hedge_analysis import compare_hedges, optimal_hedge_ratio, var_impact

init_session_state()

st.header("Hedge Impact Analysis")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns
port_ret = portfolio.portfolio_returns

if port_ret is None or returns is None:
    st.warning("Portfolio returns not available.")
    st.stop()

# --- Hedge candidate selection ---
st.subheader("Hedge Candidate Comparison")

# Use all non-first assets as potential hedges
candidates = [t for t in portfolio.tickers[1:]]
if not candidates:
    st.warning("Need at least 2 assets to compare hedges.")
    st.stop()

hedge_df = returns[candidates]
comparison = compare_hedges(port_ret, hedge_df)

# Display comparison table
st.dataframe(
    comparison.style.format({
        "correlation": "{:.3f}",
        "tail_correlation": "{:.3f}",
        "beta": "{:.3f}",
        "variance_reduction": "{:.1%}",
    }),
    use_container_width=True,
)

# --- Best hedge details ---
best_hedge = comparison.index[0]
st.subheader(f"Best Hedge: {best_hedge}")

opt_ratio = optimal_hedge_ratio(port_ret, returns[best_hedge])
st.metric("Optimal Hedge Ratio", f"{opt_ratio:.3f}")

impact = var_impact(port_ret, returns[best_hedge], opt_ratio)

c1, c2, c3 = st.columns(3)
c1.metric("VaR Before", f"{impact['var_before']:.2%}")
c2.metric("VaR After", f"{impact['var_after']:.2%}")
c3.metric("VaR Reduction", f"{impact['reduction_pct']:.1%}")

# --- Before/after VaR bar chart ---
st.subheader("VaR & CVaR: Before vs After Hedge")

fig = go.Figure()
fig.add_trace(go.Bar(
    x=["VaR", "CVaR"],
    y=[impact["var_before"], impact["cvar_before"]],
    name="Before Hedge",
    marker_color="#e74c3c",
))
fig.add_trace(go.Bar(
    x=["VaR", "CVaR"],
    y=[impact["var_after"], impact["cvar_after"]],
    name="After Hedge",
    marker_color="#4ecca3",
))
fig.update_layout(
    template="plotly_dark", height=350, barmode="group",
    yaxis_title="Loss (positive = worse)",
    yaxis_tickformat=".2%",
    margin=dict(l=50, r=20, t=10, b=40),
)
st.plotly_chart(fig, use_container_width=True)

# --- Hedged vs unhedged cumulative returns ---
st.subheader("Cumulative Returns: Unhedged vs Hedged")

hedged_ret = port_ret + opt_ratio * returns[best_hedge]
common = port_ret.index.intersection(hedged_ret.index)

cum_orig = (1 + port_ret.loc[common]).cumprod() - 1
cum_hedged = (1 + hedged_ret.loc[common]).cumprod() - 1

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=cum_orig.index, y=cum_orig.values,
    mode="lines", name="Unhedged", line=dict(color="#e74c3c", width=2),
))
fig2.add_trace(go.Scatter(
    x=cum_hedged.index, y=cum_hedged.values,
    mode="lines", name="Hedged", line=dict(color="#4ecca3", width=2),
))
fig2.update_layout(
    template="plotly_dark", height=380,
    yaxis_title="Cumulative Return", yaxis_tickformat=".0%",
    margin=dict(l=50, r=20, t=10, b=40),
)
st.plotly_chart(fig2, use_container_width=True)
