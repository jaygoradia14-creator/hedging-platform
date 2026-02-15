"""
Correlation Analysis - migrated from correlation_crash_course.py.
Uses shared core/ and risk/ modules instead of duplicated functions.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

from core.portfolio import init_session_state
from core.regime_detector import calculate_rolling_correlation as rolling_corr_regime
from risk.correlation import (
    calculate_correlation_matrix,
    calculate_tail_correlation,
    calculate_correlation_asymmetry,
    calculate_diversification_ratio,
    get_correlation_stability,
)

init_session_state()

st.header("Correlation Analysis")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns
tickers = portfolio.tickers

# --- Normal vs Tail Correlation ---
normal_corr = calculate_correlation_matrix(returns)
tail_corr = calculate_tail_correlation(returns, quantile=0.05)

st.subheader("Normal vs Crash Correlations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Normal Market Days**")
    fig_n = go.Figure(data=go.Heatmap(
        z=normal_corr.values, x=normal_corr.columns, y=normal_corr.index,
        colorscale="RdBu_r", zmin=-1, zmax=1,
        text=np.round(normal_corr.values, 2), texttemplate="%{text}",
        textfont={"size": 13},
    ))
    fig_n.update_layout(template="plotly_dark", height=350,
                        margin=dict(l=50, r=50, t=10, b=50))
    st.plotly_chart(fig_n, use_container_width=True)

with col2:
    st.markdown("**During Crashes (Worst 5%)**")
    fig_t = go.Figure(data=go.Heatmap(
        z=tail_corr.values, x=tail_corr.columns, y=tail_corr.index,
        colorscale="RdBu_r", zmin=-1, zmax=1,
        text=np.round(tail_corr.values, 2), texttemplate="%{text}",
        textfont={"size": 13},
    ))
    fig_t.update_layout(template="plotly_dark", height=350,
                        margin=dict(l=50, r=50, t=10, b=50))
    st.plotly_chart(fig_t, use_container_width=True)

# --- Key insight ---
if len(tickers) >= 2:
    t1, t2 = tickers[0], tickers[1]
    nv = normal_corr.loc[t1, t2]
    tv = tail_corr.loc[t1, t2]
    spike = tv - nv
    st.info(
        f"**{t1}** & **{t2}**: normal correlation {nv:.2f} -> crash correlation "
        f"{tv:.2f} (spike of {spike:+.2f})"
    )

# --- Correlation asymmetry ---
st.subheader("Correlation Asymmetry (Down - Up)")
asym = calculate_correlation_asymmetry(returns)
fig_a = go.Figure(data=go.Heatmap(
    z=asym.values, x=asym.columns, y=asym.index,
    colorscale="RdBu_r", zmin=-1, zmax=1,
    text=np.round(asym.values, 2), texttemplate="%{text}",
    textfont={"size": 13},
))
fig_a.update_layout(template="plotly_dark", height=350,
                    margin=dict(l=50, r=50, t=10, b=50))
st.plotly_chart(fig_a, use_container_width=True)
st.caption("Positive = higher correlation on down days (bad for hedging).")

# --- Rolling correlation timeline ---
st.subheader("Rolling Correlation Timeline")
window = st.slider("Window (trading days)", 21, 126, 63, step=21)
rolling_corr = rolling_corr_regime(returns, window=window)

fig_rc = go.Figure()
fig_rc.add_trace(go.Scatter(
    x=rolling_corr.index, y=rolling_corr.values,
    mode="lines", line=dict(color="#3498db", width=2),
    name="Avg Pairwise Corr",
))
fig_rc.add_hline(y=0.6, line_dash="dash", line_color="#e94560",
                 annotation_text="Stress Threshold")
fig_rc.update_layout(template="plotly_dark", height=380,
                     yaxis_title="Average Pairwise Correlation",
                     yaxis=dict(range=[-0.3, 1.0]),
                     margin=dict(l=50, r=20, t=10, b=40))
st.plotly_chart(fig_rc, use_container_width=True)

# --- Stability ---
st.subheader("Correlation Stability")
stability = get_correlation_stability(returns, window=window)
if len(stability) > 0:
    st.bar_chart(stability.head(10))
    st.caption("Higher values = more regime-dependent correlations.")
