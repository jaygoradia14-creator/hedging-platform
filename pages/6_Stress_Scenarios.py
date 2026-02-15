"""
Stress Scenarios - 4 stress scenarios using Monte Carlo simulation.
Scenarios: correlation shock, volatility spike, liquidity stress, combined.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from core.portfolio import init_session_state
from risk.monte_carlo import simulate_paths, simulation_statistics, percentile_bands

init_session_state()

st.header("Stress Scenarios")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns
weights = portfolio.weights

N_SIMS = 1000
N_DAYS = 252


def _stressed_returns(returns, corr_mult=1.0, vol_mult=1.0, liquidity_haircut=0.0):
    """Create stressed return distribution by modifying covariance structure."""
    mu = returns.mean().values
    cov = returns.cov().values
    n = len(mu)

    # Decompose into vol and corr
    vols = np.sqrt(np.diag(cov))
    corr_matrix = cov / np.outer(vols, vols)

    # Apply stress multipliers
    stressed_vols = vols * vol_mult

    # Shift correlations toward 1
    stressed_corr = corr_matrix.copy()
    if corr_mult > 1.0:
        stressed_corr = corr_matrix + (1 - corr_matrix) * (1 - 1.0 / corr_mult)
        np.fill_diagonal(stressed_corr, 1.0)

    # Reconstruct covariance
    stressed_cov = np.outer(stressed_vols, stressed_vols) * stressed_corr

    # Ensure positive definite
    eigvals = np.linalg.eigvalsh(stressed_cov)
    if eigvals.min() <= 0:
        stressed_cov += np.eye(n) * (abs(eigvals.min()) + 1e-8)

    # Apply liquidity haircut to drift
    stressed_mu = mu - liquidity_haircut / 252

    # Generate synthetic returns
    L = np.linalg.cholesky(stressed_cov)
    stressed = np.zeros((len(returns), n))
    np.random.seed(99)
    for t in range(len(returns)):
        z = np.random.randn(n)
        stressed[t] = stressed_mu + L @ z

    return pd.DataFrame(stressed, index=returns.index, columns=returns.columns)


SCENARIOS = {
    "Correlation Shock": {
        "desc": "Correlations spike toward 1 - diversification fails",
        "params": {"corr_mult": 3.0, "vol_mult": 1.0, "liquidity_haircut": 0.0},
        "color": "#e74c3c",
    },
    "Volatility Spike": {
        "desc": "Volatility doubles across all assets",
        "params": {"corr_mult": 1.0, "vol_mult": 2.0, "liquidity_haircut": 0.0},
        "color": "#f39c12",
    },
    "Liquidity Stress": {
        "desc": "20% annual return haircut from widened spreads and slippage",
        "params": {"corr_mult": 1.0, "vol_mult": 1.2, "liquidity_haircut": 0.20},
        "color": "#9b59b6",
    },
    "Combined Crisis": {
        "desc": "Corr shock + vol spike + liquidity stress simultaneously",
        "params": {"corr_mult": 2.5, "vol_mult": 1.8, "liquidity_haircut": 0.15},
        "color": "#e94560",
    },
}

# --- Baseline ---
baseline_sims = simulate_paths(returns, weights, N_SIMS, N_DAYS, seed=42)
baseline_stats = simulation_statistics(baseline_sims)

# --- Run scenarios ---
st.subheader("Scenario Comparison")

results = {"Baseline": baseline_stats}
all_sims = {"Baseline": baseline_sims}

for name, cfg in SCENARIOS.items():
    stressed = _stressed_returns(returns, **cfg["params"])
    sims = simulate_paths(stressed, weights, N_SIMS, N_DAYS, seed=42)
    results[name] = simulation_statistics(sims)
    all_sims[name] = sims

# Summary table
rows = []
for name, s in results.items():
    rows.append({
        "Scenario": name,
        "Median Return": f"{s['p50']:.1%}",
        "Mean Return": f"{s['mean']:.1%}",
        "5th Pctl": f"{s['p5']:.1%}",
        "Prob Loss": f"{s['prob_loss']:.1%}",
        "Std Dev": f"{s['std']:.1%}",
    })
st.dataframe(pd.DataFrame(rows).set_index("Scenario"), use_container_width=True)

# --- Fan chart comparison ---
st.subheader("Projection Comparison")

scenario_tabs = st.tabs(list(SCENARIOS.keys()))

for tab, (name, cfg) in zip(scenario_tabs, SCENARIOS.items()):
    with tab:
        st.markdown(f"*{cfg['desc']}*")

        bands_base = percentile_bands(baseline_sims)
        bands_stress = percentile_bands(all_sims[name])
        days = np.arange(1, N_DAYS + 1)

        fig = go.Figure()
        # Baseline median
        fig.add_trace(go.Scatter(
            x=days, y=bands_base["p50"], mode="lines",
            name="Baseline Median", line=dict(color="#3498db", width=2, dash="dash"),
        ))
        # Stressed band
        fig.add_trace(go.Scatter(
            x=days, y=bands_stress["p95"], mode="lines", line=dict(width=0),
            showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=days, y=bands_stress["p5"], mode="lines", line=dict(width=0),
            fill="tonexty", fillcolor=f"rgba(231,76,60,0.15)",
            name=f"{name} 5th-95th",
        ))
        fig.add_trace(go.Scatter(
            x=days, y=bands_stress["p50"], mode="lines",
            name=f"{name} Median", line=dict(color=cfg["color"], width=2),
        ))
        fig.update_layout(
            template="plotly_dark", height=400,
            xaxis_title="Trading Days", yaxis_title="Cumulative Return",
            yaxis_tickformat=".0%",
            margin=dict(l=50, r=20, t=10, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)
