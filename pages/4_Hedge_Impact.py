"""
Hedge Impact Analysis (Zerodha Kite style).
Uses actual holdings weights when available; falls back to equal-weight.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from core.portfolio import init_session_state
from core.style import page_header, kite_layout, GREEN, RED, COLORS
from risk.hedge_analysis import compare_hedges, optimal_hedge_ratio, var_impact

init_session_state()
page_header("Hedge Impact")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns

if returns is None:
    st.warning("Portfolio returns not available.")
    st.stop()

# --- Compute portfolio returns using holdings weights if available ---
holdings = st.session_state.holdings
using_holdings = False

if holdings:
    active = {t: h for t, h in holdings.items()
              if t in portfolio.tickers and h.get("shares", 0) > 0}
    total_value = sum(
        h["shares"] * h["buy_price"] for h in active.values()
    )
    if active and total_value > 0:
        held_tickers = [t for t in portfolio.tickers if t in active]
        held_weights = np.array([
            active[t]["shares"] * active[t]["buy_price"] / total_value
            for t in held_tickers
        ])
        port_ret = (returns[held_tickers] * held_weights).sum(axis=1)
        using_holdings = True

if not using_holdings:
    port_ret = portfolio.portfolio_returns

if port_ret is None:
    st.warning("Portfolio returns not available.")
    st.stop()

if using_holdings:
    st.info("Using actual holdings weights for portfolio returns.")
else:
    st.info("Using equal weights (no holdings). Add holdings on the main page for weighted analysis.")

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

# =========================================================================
# Protective Put Pricing (Black-Scholes)
# =========================================================================
st.markdown("### Protective Put Pricing")
st.markdown(
    '<p class="muted">Black-Scholes put option pricing for downside '
    'protection. Uses historical volatility as the sigma input.</p>',
    unsafe_allow_html=True,
)

try:
    from risk.black_scholes import black_scholes_put, protective_put_cost, put_greeks
    from core.data_fetch import fetch_latest_prices

    live_df = fetch_latest_prices(portfolio.tickers)
    price_map = {}
    if not live_df.empty:
        for _, row in live_df.iterrows():
            if pd.notna(row.get("Price")):
                price_map[row["Ticker"]] = float(row["Price"])

    # Strike and expiry selectors
    strike_options = [
        "10% ITM", "5% ITM", "2% ITM",
        "ATM",
        "2% OTM", "5% OTM", "10% OTM", "15% OTM", "20% OTM",
    ]
    strike_opt = st.selectbox(
        "Strike", strike_options, index=3, key="put_strike"
    )
    expiry_options = ["1 month", "2 months", "3 months", "6 months", "9 months", "1 year"]
    expiry_opt = st.selectbox(
        "Expiry", expiry_options, key="put_expiry"
    )

    strike_pct = {
        "10% ITM": 1.10, "5% ITM": 1.05, "2% ITM": 1.02,
        "ATM": 1.0,
        "2% OTM": 0.98, "5% OTM": 0.95, "10% OTM": 0.90,
        "15% OTM": 0.85, "20% OTM": 0.80,
    }[strike_opt]
    T = {
        "1 month": 1 / 12, "2 months": 2 / 12, "3 months": 3 / 12,
        "6 months": 6 / 12, "9 months": 9 / 12, "1 year": 1.0,
    }[expiry_opt]
    r = 0.05  # risk-free rate assumption

    ann_vols = returns.std() * np.sqrt(252)

    put_rows = []
    for ticker in portfolio.tickers:
        S = price_map.get(ticker)
        if S is None or S <= 0:
            continue

        sigma = float(ann_vols[ticker])
        K = S * strike_pct

        put_price = black_scholes_put(S, K, T, r, sigma)
        greeks = put_greeks(S, K, T, r, sigma)

        # Shares from holdings or default to 100
        shares = 100.0
        if holdings and ticker in holdings:
            shares = holdings[ticker].get("shares", 100.0)

        total_cost = protective_put_cost(S, K, T, r, sigma, shares)
        position_value = S * shares
        cost_pct = (total_cost / position_value * 100) if position_value > 0 else 0.0

        put_rows.append({
            "Ticker": ticker,
            "Spot": f"${S:,.2f}",
            "Strike": f"${K:,.2f}",
            "Put Premium": f"${put_price:,.2f}",
            "Shares": f"{shares:.0f}",
            "Total Hedge Cost": f"${total_cost:,.2f}",
            "Cost % of Position": f"{cost_pct:.2f}%",
            "Delta": f"{greeks['delta']:.3f}",
            "Gamma": f"{greeks['gamma']:.4f}",
            "Theta": f"{greeks['theta']:.4f}",
            "Vega": f"{greeks['vega']:.4f}",
        })

    if put_rows:
        st.dataframe(
            pd.DataFrame(put_rows).set_index("Ticker"),
            use_container_width=True,
        )
    else:
        st.warning("No live prices available for put pricing.")

except Exception as exc:
    st.warning(f"Protective put pricing unavailable: {exc}")
