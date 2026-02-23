"""
Stress Scenarios - historical crisis replay + parametric stress (Groww style).
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

# =========================================================================
# Section 1 - Historical Crisis Replay (real data via yfinance)
# =========================================================================
st.markdown("### Historical Crisis Replay")
st.markdown(
    '<p class="muted">Actual portfolio performance during major market '
    'crises. Data fetched from Yahoo Finance for your selected tickers.</p>',
    unsafe_allow_html=True,
)

CRISES = {
    "2008 GFC": {
        "start": "2008-09-01",
        "end": "2009-03-31",
        "desc": "Global Financial Crisis - Lehman collapse, credit freeze",
    },
    "2020 COVID": {
        "start": "2020-02-15",
        "end": "2020-04-15",
        "desc": "COVID-19 pandemic crash - fastest 30% drawdown in history",
    },
    "2022 Rate Hike": {
        "start": "2022-01-01",
        "end": "2022-10-31",
        "desc": "Fed rate hiking cycle - bonds and equities fell together",
    },
}

try:
    from core.data_fetch import fetch_multi_asset_data, calculate_returns

    crisis_tabs = st.tabs(list(CRISES.keys()))

    for tab, (crisis_name, crisis_cfg) in zip(crisis_tabs, CRISES.items()):
        with tab:
            st.markdown(
                f'<p class="muted">{crisis_cfg["desc"]}</p>',
                unsafe_allow_html=True,
            )

            with st.spinner(f"Fetching {crisis_name} data..."):
                crisis_prices = fetch_multi_asset_data(
                    tickers, crisis_cfg["start"], crisis_cfg["end"]
                )

            if crisis_prices.empty or crisis_prices.shape[1] == 0:
                st.warning(
                    f"No data available for {crisis_name} period. "
                    "Some tickers may not have existed yet."
                )
                continue

            available = list(crisis_prices.columns)
            crisis_ret = calculate_returns(crisis_prices)

            if crisis_ret.empty:
                st.warning(f"Insufficient return data for {crisis_name}.")
                continue

            # --- Cumulative drawdown chart ---
            cum = (1 + crisis_ret).cumprod()
            running_max = cum.cummax()
            drawdown = (cum - running_max) / running_max

            fig_dd = go.Figure()
            for i, tkr in enumerate(available):
                fig_dd.add_trace(go.Scatter(
                    x=drawdown.index,
                    y=drawdown[tkr] * 100,
                    mode="lines",
                    name=tkr,
                    line=dict(width=2, color=COLORS[i % len(COLORS)]),
                ))
            fig_dd.update_layout(
                **kite_layout(height=380),
                yaxis_title="Drawdown %",
                yaxis_ticksuffix="%",
                hovermode="x unified",
            )
            st.plotly_chart(fig_dd, use_container_width=True)

            # --- Volatility comparison: crisis vs current baseline ---
            st.markdown("#### Volatility: Crisis vs Current")
            baseline_vols = returns.std() * np.sqrt(252)
            crisis_vols = crisis_ret.std() * np.sqrt(252)

            vol_rows = []
            for tkr in available:
                bv = float(baseline_vols[tkr]) if tkr in baseline_vols.index else None
                cv = float(crisis_vols[tkr])
                row = {"Ticker": tkr, "Crisis Vol": f"{cv:.2%}"}
                if bv is not None:
                    row["Current Baseline Vol"] = f"{bv:.2%}"
                    row["Change"] = f"{((cv / bv) - 1) * 100:+.0f}%" if bv > 0 else "N/A"
                else:
                    row["Current Baseline Vol"] = "N/A"
                    row["Change"] = "N/A"
                vol_rows.append(row)

            st.dataframe(
                pd.DataFrame(vol_rows).set_index("Ticker"),
                use_container_width=True,
            )

            # --- Correlation matrix during the crisis ---
            if len(available) >= 2:
                st.markdown("#### Crisis Correlation Matrix")
                crisis_corr = crisis_ret[available].corr()
                fig_corr = go.Figure(data=go.Heatmap(
                    z=crisis_corr.values,
                    x=available,
                    y=available,
                    colorscale="RdBu_r",
                    zmin=-1, zmax=1,
                    text=crisis_corr.values.round(2),
                    texttemplate="%{text}",
                    textfont=dict(size=11),
                ))
                fig_corr.update_layout(
                    height=350,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter, sans-serif", color="#333", size=12),
                    margin=dict(l=60, r=60, t=10, b=60),
                )
                st.plotly_chart(fig_corr, use_container_width=True)

            # --- Max drawdown metrics ---
            max_dd = drawdown.min()
            cols = st.columns(min(len(available), 4))
            for i, tkr in enumerate(available):
                cols[i % len(cols)].metric(
                    tkr,
                    f"{max_dd[tkr]:.1%}",
                    "max drawdown",
                    delta_color="inverse",
                )

except Exception as exc:
    st.warning(f"Could not load historical crisis data: {exc}")


# =========================================================================
# Section 2 - Parametric Stress Scenarios (existing)
# =========================================================================
st.markdown("---")
st.markdown("### Parametric Stress Scenarios")
st.markdown(
    '<p class="muted">Synthetic what-if analysis: stressed covariance '
    'matrices to model hypothetical extreme conditions.</p>',
    unsafe_allow_html=True,
)


def _stressed_returns(ret, corr_mult=1.0, vol_mult=1.0,
                      liquidity_haircut=0.0):
    """Create stressed return distribution using a local RNG."""
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

        rng = np.random.default_rng(99)
        stressed = np.zeros((len(ret), n))
        for t in range(len(ret)):
            z = rng.standard_normal(n)
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
