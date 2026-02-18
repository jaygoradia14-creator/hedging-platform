"""
Regime Detection (Zerodha Kite style).
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from core.portfolio import init_session_state
from core.style import page_header, kite_layout, heatmap_layout, REGIME_COLORS, COLORS
from core.regime_detector import (
    MarketRegime,
    detect_regime,
    get_regime_statistics,
    calculate_rolling_volatility,
)
from risk.correlation import calculate_correlation_heatmap_data

init_session_state()
page_header("Regime Detection")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns
regime_df = st.session_state.regime_df

if regime_df is None:
    regime_df = detect_regime(returns)
    st.session_state.regime_df = regime_df

# --- Current regime ---
current = regime_df["regime"].iloc[-1]
st.metric("Current Regime", current)

# --- Timeline: per-regime stock volatility ---
st.markdown("### Regime Timeline")

regime_names = [r.value for r in MarketRegime]
selected_regime = st.selectbox("Select Regime", options=regime_names, key="regime_select")

rolling_vol = calculate_rolling_volatility(returns, window=21)
mask = regime_df["regime"] == selected_regime
regime_dates = regime_df.index[mask]

if len(regime_dates) > 0:
    # Filter rolling vol to only dates in this regime
    vol_filtered = rolling_vol.loc[rolling_vol.index.isin(regime_dates)]

    regime_color = REGIME_COLORS.get(selected_regime, "#999")
    st.markdown(
        f'<span style="color:{regime_color}; font-weight:600; font-size:0.9rem;">'
        f'{selected_regime} — {len(regime_dates)} days '
        f'({len(regime_dates) / len(regime_df) * 100:.1f}% of total)</span>',
        unsafe_allow_html=True,
    )

    fig = go.Figure()
    for i, ticker in enumerate(portfolio.tickers):
        if ticker in vol_filtered.columns:
            fig.add_trace(go.Scatter(
                x=vol_filtered.index, y=vol_filtered[ticker],
                mode="lines", name=ticker,
                line=dict(width=2, color=COLORS[i % len(COLORS)]),
            ))

    fig.update_layout(
        **kite_layout(height=420),
        yaxis_title="Annualized Volatility",
        yaxis_tickformat=".0%",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"No data available for {selected_regime} regime.")

# --- Stats table ---
st.markdown("### Regime Statistics")
stats = get_regime_statistics(regime_df)

if stats:
    rows = []
    for name, s in stats.items():
        rows.append({
            "Regime": name,
            "Days": s["days"],
            "% Time": f"{s['pct_time']:.1f}%",
            "Avg Vol": f"{s['avg_vol']:.2%}",
            "Avg Corr": f"{s['avg_corr']:.2f}",
        })
    st.dataframe(pd.DataFrame(rows).set_index("Regime"), use_container_width=True)

# --- Distribution ---
st.markdown("### Distribution")
if stats:
    fig_bar = go.Figure(data=[go.Bar(
        x=list(stats.keys()),
        y=[s["pct_time"] for s in stats.values()],
        marker_color=[REGIME_COLORS.get(k, "#ccc") for k in stats.keys()],
        text=[f"{s['pct_time']:.1f}%" for s in stats.values()],
        textposition="auto",
        textfont=dict(color="#333"),
    )])
    fig_bar.update_layout(**kite_layout(height=300), yaxis_title="% of Time",
                          yaxis_ticksuffix="%")
    st.plotly_chart(fig_bar, use_container_width=True)

# --- Conditional heatmaps ---
st.markdown("### Correlation by Regime")
regime_tabs = st.tabs([r.value for r in MarketRegime])

for tab, regime in zip(regime_tabs, MarketRegime):
    with tab:
        corr = calculate_correlation_heatmap_data(returns, regime_df, regime.value)
        if corr.empty or corr.shape[0] < 2:
            st.markdown('<p class="muted">Not enough data for this regime.</p>',
                        unsafe_allow_html=True)
            continue
        fig_h = go.Figure(data=go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            colorscale="RdBu_r", zmin=-1, zmax=1,
            text=np.round(corr.values, 2), texttemplate="%{text}",
            textfont={"size": 12, "color": "#333"},
        ))
        fig_h.update_layout(**heatmap_layout(340))
        st.plotly_chart(fig_h, use_container_width=True)
