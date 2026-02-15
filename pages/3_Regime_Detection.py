"""
Regime Detection - timeline, statistics, and regime-conditional heatmaps.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from core.portfolio import init_session_state
from core.regime_detector import (
    MarketRegime,
    detect_regime,
    get_regime_statistics,
    get_regime_colors,
)
from risk.correlation import calculate_correlation_heatmap_data

init_session_state()

st.header("Regime Detection")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns
regime_df = st.session_state.regime_df

if regime_df is None:
    regime_df = detect_regime(returns)
    st.session_state.regime_df = regime_df

colors = get_regime_colors()

# --- Regime timeline ---
st.subheader("Regime Timeline")

fig = go.Figure()

for regime in MarketRegime:
    mask = regime_df["regime"] == regime.value
    if mask.any():
        fig.add_trace(go.Scatter(
            x=regime_df.index[mask],
            y=regime_df["volatility"][mask],
            mode="markers",
            name=regime.value,
            marker=dict(color=colors[regime.value], size=4),
        ))

fig.update_layout(
    template="plotly_dark", height=400,
    yaxis_title="Average Annualized Volatility",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    margin=dict(l=50, r=20, t=10, b=40),
)
st.plotly_chart(fig, use_container_width=True)

# --- Regime statistics table ---
st.subheader("Regime Statistics")
stats = get_regime_statistics(regime_df)

if stats:
    rows = []
    for regime_name, s in stats.items():
        rows.append({
            "Regime": regime_name,
            "Days": s["days"],
            "% Time": f"{s['pct_time']:.1f}%",
            "Avg Volatility": f"{s['avg_vol']:.2%}",
            "Avg Correlation": f"{s['avg_corr']:.2f}",
        })
    st.dataframe(pd.DataFrame(rows).set_index("Regime"), use_container_width=True)

# --- Regime-conditional correlation heatmaps ---
st.subheader("Correlation by Regime")

regime_tabs = st.tabs([r.value for r in MarketRegime])

for tab, regime in zip(regime_tabs, MarketRegime):
    with tab:
        corr = calculate_correlation_heatmap_data(returns, regime_df, regime.value)
        if corr.empty or corr.shape[0] < 2:
            st.warning(f"Not enough data for {regime.value} regime.")
            continue
        fig_h = go.Figure(data=go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            colorscale="RdBu_r", zmin=-1, zmax=1,
            text=np.round(corr.values, 2), texttemplate="%{text}",
            textfont={"size": 13},
        ))
        fig_h.update_layout(template="plotly_dark", height=350,
                            margin=dict(l=50, r=50, t=10, b=50))
        st.plotly_chart(fig_h, use_container_width=True)

# --- Regime distribution bar chart ---
st.subheader("Regime Distribution")
if stats:
    fig_bar = go.Figure(data=[go.Bar(
        x=list(stats.keys()),
        y=[s["pct_time"] for s in stats.values()],
        marker_color=[colors.get(k, "#888") for k in stats.keys()],
        text=[f"{s['pct_time']:.1f}%" for s in stats.values()],
        textposition="auto",
    )])
    fig_bar.update_layout(template="plotly_dark", height=300,
                          yaxis_title="% of Time",
                          margin=dict(l=50, r=20, t=10, b=40))
    st.plotly_chart(fig_bar, use_container_width=True)
