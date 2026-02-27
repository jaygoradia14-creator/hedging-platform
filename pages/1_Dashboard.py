"""
Dashboard - Portfolio overview and key metrics (Zerodha Kite style).
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from core.portfolio import init_session_state
from core.style import page_header, kite_layout, COLORS, BLUE
from risk.correlation import calculate_diversification_ratio

init_session_state()
page_header("Dashboard")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns

# --- Key Metrics ---
div_ratio = calculate_diversification_ratio(returns, portfolio.weights)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Instruments", portfolio.n_assets)
c2.metric("HHI Concentration", f"{portfolio.hhi_concentration():.3f}")
c3.metric("Effective N", f"{portfolio.effective_n():.1f}")
c4.metric("Diversification Ratio", f"{div_ratio:.2f}")

# --- Allocation + Stats ---
st.markdown("### Allocation")
col_pie, col_bar = st.columns(2)

with col_pie:
    fig_pie = go.Figure(data=[go.Pie(
        labels=portfolio.tickers,
        values=portfolio.weights,
        hole=0.55,
        marker=dict(colors=COLORS[:portfolio.n_assets],
                    line=dict(color="#ffffff", width=2)),
        textinfo="label+percent",
        textfont=dict(size=12, color="#333"),
    )])
    fig_pie.update_layout(**kite_layout(height=320), showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_bar:
    fig_bar = go.Figure(data=[go.Bar(
        x=portfolio.tickers,
        y=portfolio.weights * 100,
        marker_color=COLORS[:portfolio.n_assets],
        text=[f"{w:.1f}%" for w in portfolio.weights * 100],
        textposition="auto",
        textfont=dict(color="#333"),
    )])
    fig_bar.update_layout(**kite_layout(height=320),
                          yaxis_title="Weight %", yaxis_ticksuffix="%")
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Sector Exposure ---
st.markdown("### Sector Exposure")

from core.data_fetch import get_sectors  # noqa: E402

_sectors = get_sectors(portfolio.tickers)

# Compute weights from holdings if available
_holdings = st.session_state.holdings
_sec_wts = portfolio.weights.copy()

if _holdings:
    _active = {t: h for t, h in _holdings.items()
               if t in portfolio.tickers and h.get("shares", 0) > 0}
    _total_val = sum(
        h["shares"] * h["buy_price"] for h in _active.values()
    )
    if _active and _total_val > 0:
        _sec_wts = np.array([
            _active[t]["shares"] * _active[t]["buy_price"] / _total_val
            if t in _active else 0.0
            for t in portfolio.tickers
        ])

# Aggregate by sector
_sector_agg = {}
for i, t in enumerate(portfolio.tickers):
    sec = _sectors[t]
    _sector_agg.setdefault(sec, {"weight": 0.0, "count": 0})
    _sector_agg[sec]["weight"] += _sec_wts[i]
    _sector_agg[sec]["count"] += 1

_sec_names = list(_sector_agg.keys())
_sec_weights = [_sector_agg[s]["weight"] for s in _sec_names]
_sec_counts = [_sector_agg[s]["count"] for s in _sec_names]

sec_c1, sec_c2 = st.columns([1, 1])

with sec_c1:
    fig_sec = go.Figure(data=[go.Pie(
        labels=_sec_names,
        values=_sec_weights,
        hole=0.55,
        marker=dict(colors=COLORS[:len(_sec_names)],
                    line=dict(color="#ffffff", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#333"),
    )])
    fig_sec.update_layout(**kite_layout(height=320), showlegend=False)
    st.plotly_chart(fig_sec, use_container_width=True)

with sec_c2:
    sec_df = pd.DataFrame({
        "Sector": _sec_names,
        "Weight %": [f"{w:.1%}" for w in _sec_weights],
        "# Tickers": _sec_counts,
    })
    st.dataframe(sec_df.set_index("Sector"), use_container_width=True)

    sec_hhi = sum(w ** 2 for w in _sec_weights)
    st.metric("Sector HHI", f"{sec_hhi:.3f}")

# Concentration warnings
for _sec, _data in _sector_agg.items():
    _pct = _data["weight"] * 100
    if _pct > 60:
        st.error(f"Sector '{_sec}' has {_pct:.1f}% concentration — "
                 "extremely high risk from single-sector exposure.")
    elif _pct > 40:
        st.warning(f"Sector '{_sec}' has {_pct:.1f}% concentration — "
                   "consider diversifying across sectors.")

# --- Cumulative returns ---
st.markdown("### Performance")
cum_ret = (1 + returns).cumprod() - 1
port_cum = (1 + portfolio.portfolio_returns).cumprod() - 1

fig_cum = go.Figure()
for i, ticker in enumerate(portfolio.tickers):
    fig_cum.add_trace(go.Scatter(
        x=cum_ret.index, y=cum_ret[ticker] * 100,
        mode="lines", name=ticker, opacity=0.5,
        line=dict(width=1.5, color=COLORS[i % len(COLORS)]),
    ))
fig_cum.add_trace(go.Scatter(
    x=port_cum.index, y=port_cum.values * 100,
    mode="lines", name="Portfolio",
    line=dict(color=BLUE, width=2.5),
))
fig_cum.update_layout(**kite_layout(height=400),
                      yaxis_title="Return %", yaxis_ticksuffix="%")
st.plotly_chart(fig_cum, use_container_width=True)

# --- Stats table ---
st.markdown("### Statistics (Annualized)")
ann_ret = returns.mean() * 252
ann_vol = returns.std() * np.sqrt(252)
sharpe = ann_ret / ann_vol

stats_df = pd.DataFrame({
    "Weight": [f"{w:.1%}" for w in portfolio.weights],
    "Return": ann_ret.apply(lambda x: f"{x:+.2%}"),
    "Volatility": ann_vol.apply(lambda x: f"{x:.2%}"),
    "Sharpe": sharpe.apply(lambda x: f"{x:.2f}"),
}, index=portfolio.tickers)
stats_df.index.name = "Instrument"
st.dataframe(stats_df, use_container_width=True)
