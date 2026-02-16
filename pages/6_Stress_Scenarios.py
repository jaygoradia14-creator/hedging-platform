"""
Stress Scenarios - individual stock stress impact (Groww style).
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from core.portfolio import init_session_state
from core.style import page_header, kite_layout, COLORS

init_session_state()
page_header("Stress Scenarios")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
returns = portfolio.returns
weights = portfolio.weights
tickers = portfolio.tickers


def _stressed_returns(ret, corr_mult=1.0, vol_mult=1.0,
                      liquidity_haircut=0.0):
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
            stressed_corr = (
                corr_matrix + (1 - corr_matrix) * (1 - 1.0 / corr_mult)
            )
            np.fill_diagonal(stressed_corr, 1.0)

        stressed_cov = (
            np.outer(stressed_vols, stressed_vols) * stressed_corr
        )

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

        return pd.DataFrame(
            stressed, index=ret.index, columns=ret.columns
        )
    except Exception:
        return ret


SCENARIOS = {
    "Correlation Shock": {
        "desc": "Correlations spike toward 1 - diversification fails",
        "params": {
            "corr_mult": 3.0, "vol_mult": 1.0,
            "liquidity_haircut": 0.0,
        },
    },
    "Volatility Spike": {
        "desc": "Volatility doubles across all assets",
        "params": {
            "corr_mult": 1.0, "vol_mult": 2.0,
            "liquidity_haircut": 0.0,
        },
    },
    "Liquidity Stress": {
        "desc": "20% annual return haircut from spreads and slippage",
        "params": {
            "corr_mult": 1.0, "vol_mult": 1.2,
            "liquidity_haircut": 0.20,
        },
    },
    "Combined Crisis": {
        "desc": "All three stresses simultaneously",
        "params": {
            "corr_mult": 2.5, "vol_mult": 1.8,
            "liquidity_haircut": 0.15,
        },
    },
}

try:
    # --- Per-stock volatility impact table ---
    st.markdown("### Per-Stock Stress Impact")
    st.markdown(
        '<p class="muted">Annualized volatility: baseline vs each '
        'stress scenario for every stock in your portfolio.</p>',
        unsafe_allow_html=True,
    )

    baseline_vols = returns.std() * np.sqrt(252)
    stock_rows = []
    stressed_data = {}
    for sname, scfg in SCENARIOS.items():
        stressed_data[sname] = _stressed_returns(
            returns, **scfg["params"]
        )

    for ticker in tickers:
        row = {
            "Ticker": ticker,
            "Baseline": f"{baseline_vols[ticker]:.2%}",
        }
        for sname in SCENARIOS:
            sv = float(
                stressed_data[sname][ticker].std() * np.sqrt(252)
            )
            row[sname] = f"{sv:.2%}"
        stock_rows.append(row)

    st.dataframe(
        pd.DataFrame(stock_rows).set_index("Ticker"),
        use_container_width=True,
    )

    # --- Individual stock charts per scenario ---
    st.markdown("### Individual Stock Stress Returns")
    st.markdown(
        '<p class="muted">Cumulative returns for each stock under '
        'baseline vs stressed conditions.</p>',
        unsafe_allow_html=True,
    )

    scenario_tabs = st.tabs(list(SCENARIOS.keys()))

    for tab, (sname, scfg) in zip(scenario_tabs, SCENARIOS.items()):
        with tab:
            st.markdown(
                f'<p class="muted">{scfg["desc"]}</p>',
                unsafe_allow_html=True,
            )

            stressed_ret = stressed_data[sname]

            # Cumulative returns: baseline vs stressed for each stock
            cum_base = (1 + returns).cumprod() - 1
            cum_stress = (1 + stressed_ret).cumprod() - 1

            fig = go.Figure()

            for i, ticker in enumerate(tickers):
                color = COLORS[i % len(COLORS)]

                # Baseline (dashed)
                fig.add_trace(go.Scatter(
                    x=cum_base.index,
                    y=cum_base[ticker] * 100,
                    mode="lines",
                    name=f"{ticker} (baseline)",
                    line=dict(
                        width=1.5, color=color, dash="dash",
                    ),
                    legendgroup=ticker,
                ))

                # Stressed (solid)
                fig.add_trace(go.Scatter(
                    x=cum_stress.index,
                    y=cum_stress[ticker] * 100,
                    mode="lines",
                    name=f"{ticker} (stressed)",
                    line=dict(width=2, color=color),
                    legendgroup=ticker,
                ))

            fig.update_layout(
                **kite_layout(height=450),
                yaxis_title="Cumulative Return %",
                yaxis_ticksuffix="%",
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Per-stock metrics for this scenario
            cols = st.columns(min(len(tickers), 4))
            for i, ticker in enumerate(tickers):
                bv = float(baseline_vols[ticker])
                sv = float(
                    stressed_ret[ticker].std() * np.sqrt(252)
                )
                change = ((sv / bv) - 1) * 100 if bv > 0 else 0
                cols[i % len(cols)].metric(
                    ticker,
                    f"{sv:.1%} vol",
                    f"{change:+.0f}% vs baseline",
                    delta_color="inverse",
                )

    # --- Portfolio-level summary ---
    st.markdown("### Portfolio Impact Summary")

    port_ret = portfolio.portfolio_returns
    port_vol_base = float(port_ret.std() * np.sqrt(252))

    summary_rows = [{"Scenario": "Baseline", "Port Vol": f"{port_vol_base:.2%}",
                     "Change": "-"}]
    for sname in SCENARIOS:
        stressed_port = (stressed_data[sname] * weights).sum(axis=1)
        sv = float(stressed_port.std() * np.sqrt(252))
        change = ((sv / port_vol_base) - 1) * 100
        summary_rows.append({
            "Scenario": sname,
            "Port Vol": f"{sv:.2%}",
            "Change": f"{change:+.1f}%",
        })

    st.dataframe(
        pd.DataFrame(summary_rows).set_index("Scenario"),
        use_container_width=True,
    )

except Exception:
    st.warning(
        "Stress scenario analysis requires at least 2 assets "
        "with sufficient historical data."
    )
