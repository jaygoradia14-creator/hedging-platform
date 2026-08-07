"""
Investment Growth Simulator — "Growth of $X" visualization (Zerodha Kite style).

Two modes:
  - Single Stock: pick any ticker, date, and amount to see hypothetical growth vs SPY
  - Portfolio: uses the loaded portfolio weights to show weighted growth
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

from core.portfolio import init_session_state
from core.style import page_header, kite_layout, COLORS, BLUE, GREEN, RED
from core.data_fetch import fetch_multi_asset_data, POPULAR_TICKERS

init_session_state()
page_header("Investment Growth")

mode = st.radio("Mode", ["Single Stock", "Portfolio"], horizontal=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _calc_stats(growth: pd.Series, daily_returns: pd.Series, years: float):
    """Compute summary statistics for a growth series."""
    total_return_pct = (growth.iloc[-1] / growth.iloc[0]) - 1
    ann_return = (1 + total_return_pct) ** (1 / years) - 1 if years > 0 else 0.0
    ann_vol = float(daily_returns.std() * np.sqrt(252))
    sharpe = ann_return / ann_vol if ann_vol > 0 else 0.0
    cummax = growth.cummax()
    drawdown = (growth - cummax) / cummax
    max_dd = float(drawdown.min())
    best_day = float(daily_returns.max())
    worst_day = float(daily_returns.min())
    return {
        "total_return_pct": total_return_pct,
        "ann_return": ann_return,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_dd": max_dd,
        "best_day": best_day,
        "worst_day": worst_day,
    }


# ---------------------------------------------------------------------------
# Single Stock Mode
# ---------------------------------------------------------------------------

if mode == "Single Stock":
    c_ticker, c_date, c_amount = st.columns(3)
    with c_ticker:
        ticker = st.selectbox("Ticker", options=POPULAR_TICKERS,
                              index=POPULAR_TICKERS.index("SPY")
                              if "SPY" in POPULAR_TICKERS else 0)
    with c_date:
        invest_date = st.date_input("Investment Date",
                                    value=date(2024, 1, 1),
                                    min_value=date.today() - timedelta(days=365 * 10),
                                    max_value=date.today())
    with c_amount:
        amount = st.number_input("Amount ($)", value=10_000, min_value=100,
                                 step=1000, format="%d")

    if invest_date >= date.today():
        st.error("Investment date must be in the past.")
        st.stop()

    # Fetch data — include SPY as benchmark if not already the ticker
    fetch_tickers = [ticker]
    include_spy = ticker.upper() != "SPY"
    if include_spy:
        fetch_tickers.append("SPY")

    with st.spinner("Fetching price data..."):
        prices = fetch_multi_asset_data(
            fetch_tickers,
            start_date=invest_date.strftime("%Y-%m-%d"),
            end_date=date.today().strftime("%Y-%m-%d"),
        )

    if prices.empty or ticker not in prices.columns:
        st.warning(f"No price data available for **{ticker}** in the selected range.")
        st.stop()

    # Growth calculation
    growth = amount * (prices[ticker] / prices[ticker].iloc[0])
    current_value = float(growth.iloc[-1])
    total_gain = current_value - amount

    # Metrics row
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Initial Investment", f"${amount:,.0f}")
    mc2.metric("Current Value", f"${current_value:,.2f}")
    pnl_color = "profit" if total_gain >= 0 else "loss"
    mc3.metric("Total Return", f"${total_gain:+,.2f}")
    total_pct = (current_value / amount - 1) * 100
    mc4.metric("Total Return %", f"{total_pct:+.2f}%")

    # Growth chart
    st.markdown("### Growth of Investment")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=growth.index, y=growth.values,
        mode="lines", name=ticker,
        line=dict(color=BLUE, width=2.5),
    ))

    if include_spy and "SPY" in prices.columns:
        spy_growth = amount * (prices["SPY"] / prices["SPY"].iloc[0])
        fig.add_trace(go.Scatter(
            x=spy_growth.index, y=spy_growth.values,
            mode="lines", name="SPY (Benchmark)",
            line=dict(color="#999999", width=1.5, dash="dot"),
        ))

    fig.add_hline(y=amount, line_dash="dash", line_color="#cccccc",
                  annotation_text=f"${amount:,.0f} invested",
                  annotation_position="bottom left",
                  annotation_font_color="#999999")
    fig.update_layout(
        **kite_layout(height=420),
        yaxis_title="Portfolio Value ($)",
        yaxis_tickprefix="$",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Stats
    daily_ret = prices[ticker].pct_change().dropna()
    n_days = (prices.index[-1] - prices.index[0]).days
    years = max(n_days / 365.25, 1 / 365.25)
    stats = _calc_stats(growth, daily_ret, years)

    st.markdown("### Statistics")
    s1, s2, s3 = st.columns(3)
    s1.metric("Annualized Return", f"{stats['ann_return']:.2%}")
    s2.metric("Annualized Volatility", f"{stats['ann_vol']:.2%}")
    s3.metric("Sharpe Ratio", f"{stats['sharpe']:.2f}")

    s4, s5, s6 = st.columns(3)
    s4.metric("Max Drawdown", f"{stats['max_dd']:.2%}")
    s5.metric("Best Day", f"{stats['best_day']:+.2%}")
    s6.metric("Worst Day", f"{stats['worst_day']:+.2%}")


# ---------------------------------------------------------------------------
# Portfolio Mode
# ---------------------------------------------------------------------------

else:
    if not st.session_state.data_loaded:
        st.info("Load data from the sidebar first.")
        st.stop()

    portfolio = st.session_state.portfolio
    prices = portfolio.prices
    returns = portfolio.returns

    if prices is None or returns is None:
        st.warning("Portfolio price data is not available.")
        st.stop()

    # Inputs
    pc_date, pc_amount = st.columns(2)
    with pc_date:
        default_start = prices.index[0].date()
        invest_date = st.date_input(
            "Investment Date",
            value=default_start,
            min_value=default_start,
            max_value=prices.index[-1].date(),
        )
    with pc_amount:
        amount = st.number_input("Amount ($)", value=10_000, min_value=100,
                                 step=1000, format="%d")

    # Slice data from chosen date
    start_ts = pd.Timestamp(invest_date)
    price_slice = prices[prices.index >= start_ts]

    if len(price_slice) < 2:
        st.warning("Not enough data from the selected date.")
        st.stop()

    # Portfolio growth via weighted returns
    simple_ret = price_slice.pct_change().dropna()
    weights = portfolio.weights
    port_returns = (simple_ret * weights).sum(axis=1)
    port_growth = amount * (1 + port_returns).cumprod()
    # Prepend the initial investment
    first_date = price_slice.index[0]
    port_growth = pd.concat([pd.Series([amount], index=[first_date]), port_growth])

    current_value = float(port_growth.iloc[-1])
    total_gain = current_value - amount

    # Metrics
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Initial Investment", f"${amount:,.0f}")
    mc2.metric("Current Value", f"${current_value:,.2f}")
    mc3.metric("Total Return", f"${total_gain:+,.2f}")
    total_pct = (current_value / amount - 1) * 100
    mc4.metric("Total Return %", f"{total_pct:+.2f}%")

    # Growth chart: per-ticker lines (transparent) + bold portfolio line
    st.markdown("### Growth of Investment")
    fig = go.Figure()

    for i, ticker in enumerate(portfolio.tickers):
        tk_growth = amount * (price_slice[ticker] / price_slice[ticker].iloc[0])
        fig.add_trace(go.Scatter(
            x=tk_growth.index, y=tk_growth.values,
            mode="lines", name=ticker, opacity=0.4,
            line=dict(width=1.5, color=COLORS[i % len(COLORS)]),
        ))

    fig.add_trace(go.Scatter(
        x=port_growth.index, y=port_growth.values,
        mode="lines", name="Portfolio",
        line=dict(color=BLUE, width=2.5),
    ))

    fig.add_hline(y=amount, line_dash="dash", line_color="#cccccc",
                  annotation_text=f"${amount:,.0f} invested",
                  annotation_position="bottom left",
                  annotation_font_color="#999999")
    fig.update_layout(
        **kite_layout(height=420),
        yaxis_title="Portfolio Value ($)",
        yaxis_tickprefix="$",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Portfolio stats
    n_days = (port_growth.index[-1] - port_growth.index[0]).days
    years = max(n_days / 365.25, 1 / 365.25)
    stats = _calc_stats(port_growth, port_returns, years)

    st.markdown("### Statistics")
    s1, s2, s3 = st.columns(3)
    s1.metric("Annualized Return", f"{stats['ann_return']:.2%}")
    s2.metric("Annualized Volatility", f"{stats['ann_vol']:.2%}")
    s3.metric("Sharpe Ratio", f"{stats['sharpe']:.2f}")

    s4, s5, s6 = st.columns(3)
    s4.metric("Max Drawdown", f"{stats['max_dd']:.2%}")
    s5.metric("Best Day", f"{stats['best_day']:+.2%}")
    s6.metric("Worst Day", f"{stats['worst_day']:+.2%}")

    # Breakdown table
    st.markdown("### Per-Ticker Breakdown")
    breakdown_rows = []
    for i, ticker in enumerate(portfolio.tickers):
        w = float(weights[i])
        allocated = amount * w
        end_price = float(price_slice[ticker].iloc[-1])
        start_price = float(price_slice[ticker].iloc[0])
        ticker_value = allocated * (end_price / start_price)
        ticker_gain = ticker_value - allocated
        ticker_pct = (end_price / start_price - 1) * 100
        breakdown_rows.append({
            "Ticker": ticker,
            "Weight": f"{w:.1%}",
            "Allocated": f"${allocated:,.2f}",
            "Current Value": f"${ticker_value:,.2f}",
            "Gain/Loss": f"${ticker_gain:+,.2f}",
            "Return %": f"{ticker_pct:+.2f}%",
        })

    breakdown_df = pd.DataFrame(breakdown_rows)
    st.dataframe(breakdown_df.set_index("Ticker"), use_container_width=True)
