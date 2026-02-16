"""
Hedge Impact Analysis (Zerodha Kite style).
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from core.portfolio import init_session_state
from core.style import page_header, kite_layout, BLUE, GREEN, RED, COLORS
from risk.hedge_analysis import compare_hedges, optimal_hedge_ratio, var_impact

init_session_state()
page_header("Hedge Impact")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns
port_ret = portfolio.portfolio_returns

if port_ret is None or returns is None:
    st.warning("Portfolio returns not available.")
    st.stop()

candidates = [t for t in portfolio.tickers[1:]]
if not candidates:
    st.warning("Need at least 2 assets to compare hedges.")
    st.stop()

# --- Comparison table ---
st.markdown("### Hedge Candidates")
hedge_df = returns[candidates]
comparison = compare_hedges(port_ret, hedge_df)

st.dataframe(
    comparison.style.format({
        "correlation": "{:.3f}",
        "tail_correlation": "{:.3f}",
        "beta": "{:.3f}",
        "variance_reduction": "{:.1%}",
    }),
    use_container_width=True,
)

# --- Best hedge ---
best_hedge = comparison.index[0]
st.markdown(f"### Best Hedge: {best_hedge}")

opt_ratio = optimal_hedge_ratio(port_ret, returns[best_hedge])
impact = var_impact(port_ret, returns[best_hedge], opt_ratio)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Optimal Ratio", f"{opt_ratio:.3f}")
c2.metric("VaR Before", f"{impact['var_before']:.2%}")
c3.metric("VaR After", f"{impact['var_after']:.2%}")
c4.metric("VaR Reduction", f"{impact['reduction_pct']:.1%}")

# --- Before / After bar chart ---
st.markdown("### Risk Comparison")
fig = go.Figure()
fig.add_trace(go.Bar(
    x=["VaR", "CVaR"],
    y=[impact["var_before"] * 100, impact["cvar_before"] * 100],
    name="Before Hedge",
    marker_color=RED,
    text=[f"{impact['var_before']:.2%}", f"{impact['cvar_before']:.2%}"],
    textposition="auto", textfont=dict(color="#333"),
))
fig.add_trace(go.Bar(
    x=["VaR", "CVaR"],
    y=[impact["var_after"] * 100, impact["cvar_after"] * 100],
    name="After Hedge",
    marker_color=GREEN,
    text=[f"{impact['var_after']:.2%}", f"{impact['cvar_after']:.2%}"],
    textposition="auto", textfont=dict(color="#333"),
))
fig.update_layout(**kite_layout(height=350), barmode="group",
                  yaxis_title="Loss %", yaxis_ticksuffix="%")
st.plotly_chart(fig, use_container_width=True)

# --- Cumulative returns comparison with individual stocks ---
st.markdown("### Performance: Unhedged vs Hedged vs Individual Stocks")
hedged_ret = port_ret + opt_ratio * returns[best_hedge]
common = port_ret.index.intersection(hedged_ret.index)

cum_orig = (1 + port_ret.loc[common]).cumprod() - 1
cum_hedged = (1 + hedged_ret.loc[common]).cumprod() - 1

fig2 = go.Figure()

# Individual stock cumulative returns
cum_individual = (1 + returns).cumprod() - 1
for i, ticker in enumerate(portfolio.tickers):
    fig2.add_trace(go.Scatter(
        x=cum_individual.index, y=cum_individual[ticker] * 100,
        mode="lines", name=ticker,
        line=dict(width=1.5, color=COLORS[i % len(COLORS)]),
        opacity=0.6,
    ))

# Portfolio lines on top
fig2.add_trace(go.Scatter(
    x=cum_orig.index, y=cum_orig.values * 100,
    mode="lines", name="Portfolio (Unhedged)", line=dict(color=RED, width=2.5),
))
fig2.add_trace(go.Scatter(
    x=cum_hedged.index, y=cum_hedged.values * 100,
    mode="lines", name="Portfolio (Hedged)", line=dict(color=GREEN, width=2.5),
))
fig2.update_layout(**kite_layout(height=420),
                   yaxis_title="Return %", yaxis_ticksuffix="%",
                   hovermode="x unified")
st.plotly_chart(fig2, use_container_width=True)
