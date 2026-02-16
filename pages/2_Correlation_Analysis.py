"""
Correlation Analysis (Zerodha Kite style).
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

from core.portfolio import init_session_state
from core.style import page_header, kite_layout, heatmap_layout, BLUE, COLORS
from risk.correlation import (
    calculate_correlation_matrix,
    calculate_tail_correlation,
    calculate_correlation_asymmetry,
    get_correlation_stability,
)

init_session_state()
page_header("Correlation Analysis")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns
tickers = portfolio.tickers

# --- Normal vs Tail ---
normal_corr = calculate_correlation_matrix(returns)
tail_corr = calculate_tail_correlation(returns, quantile=0.05)

st.markdown("### Normal vs Crash Correlations")
col1, col2 = st.columns(2)

for col, corr, label in [(col1, normal_corr, "Normal Days"), (col2, tail_corr, "Crash Days (Worst 5%)")]:
    with col:
        st.markdown(f'<p class="muted">{label}</p>', unsafe_allow_html=True)
        fig = go.Figure(data=go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            colorscale="RdBu_r", zmin=-1, zmax=1,
            text=np.round(corr.values, 2), texttemplate="%{text}",
            textfont={"size": 12, "color": "#333"},
        ))
        fig.update_layout(**heatmap_layout(340))
        st.plotly_chart(fig, use_container_width=True)

# Key insight
if len(tickers) >= 2:
    t1, t2 = tickers[0], tickers[1]
    nv = normal_corr.loc[t1, t2]
    tv = tail_corr.loc[t1, t2]
    spike = tv - nv
    color = "loss" if spike > 0 else "profit"
    st.markdown(
        f'**{t1}** & **{t2}**: normal <span class="muted">{nv:.2f}</span> '
        f'&rarr; crash <span class="{color}">{tv:.2f}</span> '
        f'(<span class="{color}">{spike:+.2f}</span>)',
        unsafe_allow_html=True,
    )

# --- Asymmetry ---
st.markdown("### Correlation Asymmetry")
st.markdown('<p class="muted">Downside correlation minus upside correlation. Positive = worse in crashes.</p>',
            unsafe_allow_html=True)
asym = calculate_correlation_asymmetry(returns)
fig_a = go.Figure(data=go.Heatmap(
    z=asym.values, x=asym.columns, y=asym.index,
    colorscale="RdBu_r", zmin=-1, zmax=1,
    text=np.round(asym.values, 2), texttemplate="%{text}",
    textfont={"size": 12, "color": "#333"},
))
fig_a.update_layout(**heatmap_layout(340))
st.plotly_chart(fig_a, use_container_width=True)

# --- Stability ---
window = 63
st.markdown("### Correlation Stability")
st.markdown('<p class="muted">Higher = more regime-dependent (less reliable diversification).</p>',
            unsafe_allow_html=True)
stability = get_correlation_stability(returns, window=window)
if len(stability) > 0:
    fig_s = go.Figure(data=[go.Bar(
        x=stability.head(10).index.tolist(),
        y=stability.head(10).values,
        marker_color=BLUE,
        text=[f"{v:.3f}" for v in stability.head(10).values],
        textposition="auto",
        textfont=dict(color="#333"),
    )])
    fig_s.update_layout(**kite_layout(height=300), yaxis_title="Instability (Std)")
    st.plotly_chart(fig_s, use_container_width=True)
