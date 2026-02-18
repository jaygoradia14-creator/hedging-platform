"""
Efficient Frontier - Markowitz Mean-Variance Optimization.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.portfolio import init_session_state
from core.style import page_header, kite_layout, COLORS

init_session_state()
page_header("Efficient Frontier")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns

from risk.optimizer import (  # noqa: E402
    portfolio_performance,
    min_variance_portfolio,
    max_sharpe_portfolio,
    efficient_frontier,
    random_portfolios,
)

risk_free = st.slider("Risk-Free Rate (%)", 0.0, 8.0, 2.0, 0.5) / 100

with st.spinner("Computing efficient frontier..."):
    mv = min_variance_portfolio(returns)
    ms = max_sharpe_portfolio(returns, risk_free)
    ef = efficient_frontier(returns, n_points=50, risk_free=risk_free)
    rp = random_portfolios(returns, n_portfolios=2000, risk_free=risk_free)

    # Current portfolio position
    mean_ret = returns.mean().values
    cov = returns.cov().values
    cur_ret, cur_vol, cur_sharpe = portfolio_performance(
        portfolio.weights, mean_ret, cov, risk_free
    )

# --- Efficient Frontier Chart ---
st.markdown("### Frontier")

fig = go.Figure()

# Random portfolios scatter
fig.add_trace(go.Scatter(
    x=rp["volatilities"] * 100, y=rp["returns"] * 100,
    mode="markers",
    marker=dict(size=3, color=rp["sharpes"], colorscale="Viridis",
                showscale=True, colorbar=dict(title="Sharpe")),
    name="Random Portfolios",
    hovertemplate="Vol: %{x:.1f}%<br>Ret: %{y:.1f}%<extra></extra>",
))

# Efficient frontier curve
fig.add_trace(go.Scatter(
    x=ef["volatilities"] * 100, y=ef["returns"] * 100,
    mode="lines", name="Efficient Frontier",
    line=dict(color="#1a1a2e", width=3),
))

# Current portfolio
fig.add_trace(go.Scatter(
    x=[cur_vol * 100], y=[cur_ret * 100],
    mode="markers", name="Current Portfolio",
    marker=dict(size=15, color=COLORS[0], symbol="diamond",
                line=dict(width=2, color="#fff")),
    hovertemplate="Current<br>Vol: %{x:.1f}%<br>Ret: %{y:.1f}%<extra></extra>",
))

# Min variance
fig.add_trace(go.Scatter(
    x=[mv["volatility"] * 100], y=[mv["return"] * 100],
    mode="markers", name="Min Variance",
    marker=dict(size=15, color=COLORS[1], symbol="star",
                line=dict(width=2, color="#fff")),
    hovertemplate="Min Var<br>Vol: %{x:.1f}%<br>Ret: %{y:.1f}%<extra></extra>",
))

# Max Sharpe
fig.add_trace(go.Scatter(
    x=[ms["volatility"] * 100], y=[ms["return"] * 100],
    mode="markers", name="Max Sharpe",
    marker=dict(size=15, color=COLORS[3], symbol="star",
                line=dict(width=2, color="#fff")),
    hovertemplate="Max Sharpe<br>Vol: %{x:.1f}%<br>Ret: %{y:.1f}%<extra></extra>",
))

fig.update_layout(
    **kite_layout(height=520),
    xaxis_title="Annualized Volatility %",
    yaxis_title="Annualized Return %",
    xaxis_ticksuffix="%",
    yaxis_ticksuffix="%",
    hovermode="closest",
)
st.plotly_chart(fig, use_container_width=True)

# --- Metrics comparison ---
st.markdown("### Portfolio Comparison")

comp_df = pd.DataFrame({
    "Portfolio": ["Current (Equal-Weight)", "Min Variance", "Max Sharpe"],
    "Return": [f"{cur_ret:.2%}", f"{mv['return']:.2%}", f"{ms['return']:.2%}"],
    "Volatility": [f"{cur_vol:.2%}", f"{mv['volatility']:.2%}", f"{ms['volatility']:.2%}"],
    "Sharpe": [f"{cur_sharpe:.2f}", f"{mv['sharpe']:.2f}", f"{ms['sharpe']:.2f}"],
})
st.dataframe(comp_df.set_index("Portfolio"), use_container_width=True)

# --- Optimal weights ---
st.markdown("### Optimal Weights")

w_col1, w_col2 = st.columns(2)

with w_col1:
    st.markdown("**Min Variance**")
    mv_weights = pd.DataFrame({
        "Ticker": portfolio.tickers,
        "Current": [f"{w:.1%}" for w in portfolio.weights],
        "Optimal": [f"{w:.1%}" for w in mv["weights"]],
        "Change": [f"{o - c:+.1%}" for c, o in zip(portfolio.weights, mv["weights"])],
    })
    st.dataframe(mv_weights.set_index("Ticker"), use_container_width=True)

with w_col2:
    st.markdown("**Max Sharpe**")
    ms_weights = pd.DataFrame({
        "Ticker": portfolio.tickers,
        "Current": [f"{w:.1%}" for w in portfolio.weights],
        "Optimal": [f"{w:.1%}" for w in ms["weights"]],
        "Change": [f"{o - c:+.1%}" for c, o in zip(portfolio.weights, ms["weights"])],
    })
    st.dataframe(ms_weights.set_index("Ticker"), use_container_width=True)

# --- Weight comparison bar chart ---
st.markdown("### Weight Comparison")

fig_w = go.Figure()
x = portfolio.tickers
fig_w.add_trace(go.Bar(
    name="Current", x=x, y=portfolio.weights * 100, marker_color=COLORS[0],
))
fig_w.add_trace(go.Bar(
    name="Min Variance", x=x, y=mv["weights"] * 100, marker_color=COLORS[1],
))
fig_w.add_trace(go.Bar(
    name="Max Sharpe", x=x, y=ms["weights"] * 100, marker_color=COLORS[3],
))
fig_w.update_layout(**kite_layout(height=350), barmode="group",
                    yaxis_title="Weight %", yaxis_ticksuffix="%")
st.plotly_chart(fig_w, use_container_width=True)
