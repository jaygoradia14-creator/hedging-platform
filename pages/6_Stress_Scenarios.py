"""
Stress Scenarios (Zerodha Kite style).
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from core.portfolio import init_session_state
from core.style import page_header, kite_layout, BLUE, RED, ORANGE, PURPLE, COLORS
from risk.monte_carlo import simulate_paths, simulation_statistics, percentile_bands

init_session_state()
page_header("Stress Scenarios")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns
weights = portfolio.weights

N_SIMS = 1000
N_DAYS = 252


def _stressed_returns(ret, corr_mult=1.0, vol_mult=1.0, liquidity_haircut=0.0):
    """Create stressed return distribution."""
    try:
        mu = ret.mean().values
        cov = ret.cov().values
        n = len(mu)

        vols = np.sqrt(np.diag(cov))
        corr_matrix = cov / np.outer(vols, vols)

        stressed_vols = vols * vol_mult

        stressed_corr = corr_matrix.copy()
        if corr_mult > 1.0:
            stressed_corr = corr_matrix + (1 - corr_matrix) * (1 - 1.0 / corr_mult)
            np.fill_diagonal(stressed_corr, 1.0)

        stressed_cov = np.outer(stressed_vols, stressed_vols) * stressed_corr

        eigvals = np.linalg.eigvalsh(stressed_cov)
        if eigvals.min() <= 0:
            stressed_cov += np.eye(n) * (abs(eigvals.min()) + 1e-8)

        stressed_mu = mu - liquidity_haircut / 252
        L = np.linalg.cholesky(stressed_cov)

        stressed = np.zeros((len(ret), n))
        np.random.seed(99)
        for t in range(len(ret)):
            z = np.random.randn(n)
            stressed[t] = stressed_mu + L @ z

        return pd.DataFrame(stressed, index=ret.index, columns=ret.columns)
    except Exception:
        return ret


SCENARIOS = {
    "Correlation Shock": {
        "desc": "Correlations spike toward 1 - diversification fails",
        "params": {"corr_mult": 3.0, "vol_mult": 1.0, "liquidity_haircut": 0.0},
        "color": RED,
    },
    "Volatility Spike": {
        "desc": "Volatility doubles across all assets",
        "params": {"corr_mult": 1.0, "vol_mult": 2.0, "liquidity_haircut": 0.0},
        "color": ORANGE,
    },
    "Liquidity Stress": {
        "desc": "20% annual return haircut from spreads and slippage",
        "params": {"corr_mult": 1.0, "vol_mult": 1.2, "liquidity_haircut": 0.20},
        "color": PURPLE,
    },
    "Combined Crisis": {
        "desc": "Corr shock + vol spike + liquidity stress simultaneously",
        "params": {"corr_mult": 2.5, "vol_mult": 1.8, "liquidity_haircut": 0.15},
        "color": "#1a1a2e",
    },
}

try:
    # Baseline
    baseline_sims = simulate_paths(returns, weights, N_SIMS, N_DAYS, seed=42)
    baseline_stats = simulation_statistics(baseline_sims)

    results = {"Baseline": baseline_stats}
    all_sims = {"Baseline": baseline_sims}

    for name, cfg in SCENARIOS.items():
        stressed = _stressed_returns(returns, **cfg["params"])
        sims = simulate_paths(stressed, weights, N_SIMS, N_DAYS, seed=42)
        results[name] = simulation_statistics(sims)
        all_sims[name] = sims

    # --- Per-stock stress impact table ---
    st.markdown("### Per-Stock Stress Impact")
    st.markdown('<p class="muted">Annualized volatility under each scenario vs baseline.</p>',
                unsafe_allow_html=True)

    stock_stress_rows = []
    baseline_vols = returns.std() * np.sqrt(252)
    for ticker in portfolio.tickers:
        row = {"Ticker": ticker, "Baseline Vol": f"{baseline_vols[ticker]:.2%}"}
        for sname, scfg in SCENARIOS.items():
            stressed = _stressed_returns(returns, **scfg["params"])
            stressed_vol = float(stressed[ticker].std() * np.sqrt(252))
            row[sname] = f"{stressed_vol:.2%}"
        stock_stress_rows.append(row)
    st.dataframe(pd.DataFrame(stock_stress_rows).set_index("Ticker"), use_container_width=True)

    # --- Summary table ---
    st.markdown("### Scenario Comparison")
    rows = []
    for name, s in results.items():
        rows.append({
            "Scenario": name,
            "Median": f"{s['p50']:.1%}",
            "Mean": f"{s['mean']:.1%}",
            "5th Pctl": f"{s['p5']:.1%}",
            "Prob Loss": f"{s['prob_loss']:.1%}",
            "Std Dev": f"{s['std']:.1%}",
        })
    st.dataframe(pd.DataFrame(rows).set_index("Scenario"), use_container_width=True)

    # --- Tabs for each scenario ---
    st.markdown("### Projections")
    scenario_tabs = st.tabs(list(SCENARIOS.keys()))

    for tab, (name, cfg) in zip(scenario_tabs, SCENARIOS.items()):
        with tab:
            st.markdown(f'<p class="muted">{cfg["desc"]}</p>', unsafe_allow_html=True)

            bands_base = percentile_bands(baseline_sims)
            bands_stress = percentile_bands(all_sims[name])
            days = np.arange(1, N_DAYS + 1)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=days, y=bands_base["p50"] * 100, mode="lines",
                name="Baseline", line=dict(color=BLUE, width=2, dash="dash"),
            ))
            fig.add_trace(go.Scatter(
                x=days, y=bands_stress["p95"] * 100, mode="lines",
                line=dict(width=0), showlegend=False,
            ))
            fig.add_trace(go.Scatter(
                x=days, y=bands_stress["p5"] * 100, mode="lines",
                line=dict(width=0), fill="tonexty",
                fillcolor="rgba(212,55,37,0.1)", name=f"{name} 5-95th",
            ))
            fig.add_trace(go.Scatter(
                x=days, y=bands_stress["p50"] * 100, mode="lines",
                name=f"{name}", line=dict(color=cfg["color"], width=2),
            ))
            fig.update_layout(**kite_layout(height=400),
                              xaxis_title="Trading Days",
                              yaxis_title="Return %", yaxis_ticksuffix="%")
            st.plotly_chart(fig, use_container_width=True)

except Exception:
    st.warning("Stress scenario analysis requires at least 2 assets with sufficient historical data.")
