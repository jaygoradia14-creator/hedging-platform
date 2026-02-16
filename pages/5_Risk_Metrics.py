"""
Risk Metrics (Zerodha Kite style).
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from core.portfolio import init_session_state
from core.style import page_header, kite_layout, BLUE, RED, GREEN, ORANGE, REGIME_COLORS, COLORS
from risk.var_cvar import var_cvar_summary, regime_conditional_var, historical_var, historical_cvar

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

# --- Per-stock VaR table ---
st.markdown("### Individual Stock Risk")
stock_risk_rows = []
for ticker in portfolio.tickers:
    stock_ret = returns[ticker]
    s_var = historical_var(stock_ret, confidence)
    s_cvar = historical_cvar(stock_ret, confidence)
    ann_vol = float(stock_ret.std() * np.sqrt(252))
    stock_risk_rows.append({
        "Ticker": ticker,
        "VaR": f"{s_var:.2%}",
        "CVaR": f"{s_cvar:.2%}",
        "Ann. Volatility": f"{ann_vol:.2%}",
    })
st.dataframe(pd.DataFrame(stock_risk_rows).set_index("Ticker"), use_container_width=True)

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

# --- Individual stock cumulative returns ---
st.markdown("### Historical Context: Individual Stock Returns")
cum_ret = (1 + returns).cumprod() - 1
port_cum = (1 + portfolio.portfolio_returns).cumprod() - 1

fig_ctx = go.Figure()
for i, ticker in enumerate(portfolio.tickers):
    fig_ctx.add_trace(go.Scatter(
        x=cum_ret.index, y=cum_ret[ticker] * 100,
        mode="lines", name=ticker,
        line=dict(width=1.5, color=COLORS[i % len(COLORS)]),
    ))
fig_ctx.add_trace(go.Scatter(
    x=port_cum.index, y=port_cum.values * 100,
    mode="lines", name="Portfolio",
    line=dict(color="#1a1a2e", width=2.5),
))
fig_ctx.update_layout(**kite_layout(height=380),
                      yaxis_title="Cumulative Return %", yaxis_ticksuffix="%",
                      hovermode="x unified")
st.plotly_chart(fig_ctx, use_container_width=True)
