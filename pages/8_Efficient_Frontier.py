"""
Efficient Frontier - Markowitz Mean-Variance Optimization.
Uses holdings-derived weights as 'Current Portfolio' when available.
"""

import streamlit as st
import numpy as np
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

# --- Compute current weights from holdings if available ---
holdings = st.session_state.holdings
current_weights = portfolio.weights
current_label = "Current (Equal-Weight)"

if holdings:
    active = {t: h for t, h in holdings.items()
              if t in portfolio.tickers and h.get("shares", 0) > 0}
    total_value = sum(
        h["shares"] * h["buy_price"] for h in active.values()
    )
    if active and total_value > 0:
        # Build full-length weight vector (0 for unheld tickers)
        hw = np.array([
            active[t]["shares"] * active[t]["buy_price"] / total_value
            if t in active else 0.0
            for t in portfolio.tickers
        ])
        current_weights = hw
        current_label = "Current (Holdings)"

with st.spinner("Computing efficient frontier..."):
    mv = min_variance_portfolio(returns)
    ms = max_sharpe_portfolio(returns, risk_free)
    ef = efficient_frontier(returns, n_points=50, risk_free=risk_free)
    rp = random_portfolios(returns, n_portfolios=2000, risk_free=risk_free)

    # Current portfolio position
    mean_ret = returns.mean().values
    cov = returns.cov().values
    cur_ret, cur_vol, cur_sharpe = portfolio_performance(
        current_weights, mean_ret, cov, risk_free
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
    mode="markers", name=current_label,
    marker=dict(size=15, color=COLORS[0], symbol="diamond",
                line=dict(width=2, color="#fff")),
    hovertemplate=f"{current_label}<br>Vol: %{{x:.1f}}%<br>Ret: %{{y:.1f}}%<extra></extra>",
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
    "Portfolio": [current_label, "Min Variance", "Max Sharpe"],
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
        "Current": [f"{w:.1%}" for w in current_weights],
        "Optimal": [f"{w:.1%}" for w in mv["weights"]],
        "Change": [f"{o - c:+.1%}" for c, o in zip(current_weights, mv["weights"])],
    })
    st.dataframe(mv_weights.set_index("Ticker"), use_container_width=True)

with w_col2:
    st.markdown("**Max Sharpe**")
    ms_weights = pd.DataFrame({
        "Ticker": portfolio.tickers,
        "Current": [f"{w:.1%}" for w in current_weights],
        "Optimal": [f"{w:.1%}" for w in ms["weights"]],
        "Change": [f"{o - c:+.1%}" for c, o in zip(current_weights, ms["weights"])],
    })
    st.dataframe(ms_weights.set_index("Ticker"), use_container_width=True)

# --- Weight comparison bar chart ---
st.markdown("### Weight Comparison")

fig_w = go.Figure()
x = portfolio.tickers
fig_w.add_trace(go.Bar(
    name=current_label, x=x, y=current_weights * 100, marker_color=COLORS[0],
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

# --- Rebalancing Suggestions ---
st.markdown("### Rebalancing Suggestions")

rebal_target = st.radio(
    "Optimization Target",
    ["Min Variance", "Max Sharpe"],
    horizontal=True,
    key="rebal_target",
)

optimal_weights = mv["weights"] if rebal_target == "Min Variance" else ms["weights"]

# Compute deltas
deltas = optimal_weights - current_weights

# Build rebalancing table (filter noise < 0.5%)
rebal_rows = []
for i, t in enumerate(portfolio.tickers):
    if abs(deltas[i]) < 0.005:
        continue
    action = "BUY" if deltas[i] > 0 else "SELL"
    rebal_rows.append({
        "Ticker": t,
        "Current %": round(current_weights[i] * 100, 1),
        "Optimal %": round(optimal_weights[i] * 100, 1),
        "Change %": round(deltas[i] * 100, 1),
        "Action": action,
    })

if rebal_rows:
    rebal_df = pd.DataFrame(rebal_rows)

    # Add dollar amounts if holdings exist
    total_value = 0.0
    if holdings:
        active = {t: h for t, h in holdings.items()
                  if t in portfolio.tickers and h.get("shares", 0) > 0}
        total_value = sum(
            h["shares"] * h["buy_price"] for h in active.values()
        )

    if total_value > 0:
        rebal_df["Est. $ Amount"] = rebal_df["Change %"].apply(
            lambda x: f"${abs(x / 100) * total_value:,.0f}"
        )
        total_txn = sum(abs(r["Change %"] / 100) * total_value
                        for r in rebal_rows)
        st.metric("Total Estimated Transaction Value",
                  f"${total_txn:,.0f}")

    # Color-code with styled dataframe
    def _color_action(val):
        if val == "BUY":
            return f"color: {COLORS[1]}"  # GREEN
        elif val == "SELL":
            return f"color: {COLORS[2]}"  # RED
        return ""

    def _color_change(val):
        if isinstance(val, (int, float)):
            if val > 0:
                return f"color: {COLORS[1]}"
            elif val < 0:
                return f"color: {COLORS[2]}"
        return ""

    styled = (
        rebal_df.style
        .map(_color_action, subset=["Action"])
        .map(_color_change, subset=["Change %"])
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)
else:
    st.info("Your portfolio is already close to the optimal allocation.")
