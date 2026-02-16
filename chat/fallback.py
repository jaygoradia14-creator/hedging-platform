"""
Rules-based fallback chat when no OpenAI API key is available.
Keyword matching routes to context-aware responses grounded in portfolio analytics.
"""


def fallback_response(user_message: str, session_state) -> str:
    """Generate a rules-based response using keyword matching and portfolio context."""
    msg = user_message.lower().strip()

    portfolio = getattr(session_state, "portfolio", None)
    regime_df = getattr(session_state, "regime_df", None)
    data_loaded = getattr(session_state, "data_loaded", False)

    if not data_loaded or portfolio is None:
        return (
            "Please load portfolio data first using the sidebar controls. "
            "Enter your tickers and click **Load Data** to get started."
        )

    returns = portfolio.returns
    weights = portfolio.weights
    tickers = portfolio.tickers

    # --- Correlation queries ---
    if any(kw in msg for kw in ["correlation", "corr", "diversif", "how correlated", "move together"]):
        try:
            from risk.correlation import (
                calculate_correlation_matrix,
                calculate_tail_correlation,
                calculate_diversification_ratio,
            )
            normal = calculate_correlation_matrix(returns)
            tail = calculate_tail_correlation(returns)
            dr = calculate_diversification_ratio(returns, weights)

            if len(tickers) >= 2:
                t1, t2 = tickers[0], tickers[1]
                nv = normal.loc[t1, t2]
                tv = tail.loc[t1, t2]
                spike = tv - nv

                return (
                    f"**Correlation Analysis:**\n\n"
                    f"- **{t1}-{t2} normal correlation:** {nv:.2f}\n"
                    f"- **{t1}-{t2} crash correlation:** {tv:.2f} ({spike:+.2f} spike)\n"
                    f"- **Diversification ratio:** {dr:.2f}\n\n"
                    f"{'Correlations spike significantly during crashes - your diversification benefit erodes under stress.' if spike > 0.1 else 'Correlations are relatively stable across regimes.'} "
                    f"A diversification ratio of {dr:.2f} means {'good diversification benefit' if dr > 1.3 else 'moderate diversification' if dr > 1.1 else 'limited diversification benefit'}.\n\n"
                    f"Visit the **Correlation Analysis** page for heatmaps and rolling timeline."
                )
            return f"Your portfolio diversification ratio is {dr:.2f}. Visit the Correlation Analysis page for details."
        except Exception:
            return "Visit the **Correlation Analysis** page to see how your assets correlate during normal and crash periods."

    # --- VaR queries ---
    if any(kw in msg for kw in ["var", "value at risk", "cvar", "expected shortfall",
                                 "risk metric", "how much can i lose", "worst case", "downside risk"]):
        try:
            from risk.var_cvar import var_cvar_summary, regime_conditional_var
            s = var_cvar_summary(returns, weights, 0.95)

            response = (
                f"**Risk Metrics (95% confidence):**\n\n"
                f"- **Historical VaR:** {s['historical_var']:.2%} daily\n"
                f"- **CVaR (Expected Shortfall):** {s['historical_cvar']:.2%} daily\n"
                f"- **Parametric VaR:** {s['parametric_var']:.2%} daily\n\n"
                f"This means on the worst 5% of trading days, you can expect to lose at least "
                f"**{s['historical_var']:.2%}** of portfolio value. The average loss on those worst days is "
                f"**{s['historical_cvar']:.2%}** (CVaR)."
            )

            if regime_df is not None:
                rv = regime_conditional_var(returns, weights, regime_df, 0.95)
                if rv:
                    regime_lines = [f"  - {k}: {v:.2%}" for k, v in rv.items() if not (isinstance(v, float) and v != v)]
                    if regime_lines:
                        response += f"\n\n**VaR by regime:**\n" + "\n".join(regime_lines)

            response += "\n\nVisit the **Risk Metrics** page for Monte Carlo projections and regime-conditional analysis."
            return response
        except Exception:
            return "Visit the **Risk Metrics** page for VaR, CVaR, and Monte Carlo analysis."

    # --- Regime queries ---
    if any(kw in msg for kw in ["regime", "volatility", "crisis", "market state", "market condition",
                                 "what phase", "which regime"]):
        if regime_df is not None and len(regime_df) > 0:
            current = regime_df["regime"].iloc[-1]
            from core.regime_detector import get_regime_statistics
            stats = get_regime_statistics(regime_df)

            response = f"**Current Market Regime: {current}**\n\n"

            regime_descriptions = {
                "Low Volatility": "Markets are calm with below-average volatility. Correlations tend to be lower, meaning diversification is working well.",
                "Normal": "Standard market conditions with typical volatility and correlation levels.",
                "High Volatility": "Elevated volatility but not yet at crisis levels. Watch for correlation spikes that could reduce diversification benefit.",
                "Crisis": "Extreme volatility and/or high correlations. Diversification is likely failing - hedging instruments are critical.",
            }
            response += regime_descriptions.get(current, "") + "\n\n"

            response += "**Historical distribution:**\n"
            for name, s in stats.items():
                response += f"- {name}: {s['pct_time']:.1f}% of time (avg vol: {s['avg_vol']:.2%}, avg corr: {s['avg_corr']:.2f})\n"

            response += "\nVisit the **Regime Detection** page for timeline and regime-conditional correlations."
            return response
        return "Visit the **Regime Detection** page to see current market regime analysis."

    # --- Hedge queries ---
    if any(kw in msg for kw in ["hedge", "protect", "insurance", "downside", "reduce risk",
                                 "best hedge", "hedge ratio", "which asset"]):
        if len(tickers) > 1:
            try:
                from risk.hedge_analysis import compare_hedges, optimal_hedge_ratio, var_impact
                port_ret = portfolio.portfolio_returns
                candidates = tickers[1:]
                hedge_df = returns[candidates]
                comparison = compare_hedges(port_ret, hedge_df)

                best = comparison.index[0]
                best_metrics = comparison.iloc[0]
                opt_ratio = optimal_hedge_ratio(port_ret, returns[best])
                impact = var_impact(port_ret, returns[best], opt_ratio)

                response = (
                    f"**Hedge Analysis:**\n\n"
                    f"**Best hedge candidate: {best}**\n"
                    f"- Correlation with portfolio: {best_metrics['correlation']:.3f}\n"
                    f"- Tail correlation: {best_metrics['tail_correlation']:.3f}\n"
                    f"- Variance reduction: {best_metrics['variance_reduction']:.1%}\n"
                    f"- Optimal hedge ratio: {opt_ratio:.3f}\n\n"
                    f"**VaR impact at optimal ratio:**\n"
                    f"- Before: {impact['var_before']:.2%} → After: {impact['var_after']:.2%}\n"
                    f"- **VaR reduction: {impact['reduction_pct']:.1%}**\n\n"
                )
                if len(comparison) > 1:
                    response += "**Other candidates:**\n"
                    for ticker in comparison.index[1:]:
                        row = comparison.loc[ticker]
                        response += f"- {ticker}: variance reduction {row['variance_reduction']:.1%}, corr {row['correlation']:.3f}\n"

                response += "\nVisit the **Hedge Impact** page for detailed comparison charts."
                return response
            except Exception:
                pass
        return "Add more assets to your portfolio to analyze hedging opportunities. Visit the **Hedge Impact** page."

    # --- Stress scenario queries ---
    if any(kw in msg for kw in ["stress", "scenario", "crash", "what if", "worst case scenario",
                                 "black swan", "tail risk"]):
        return (
            "**Stress Scenarios** test your portfolio against 4 extreme events:\n\n"
            "1. **Correlation Shock** - All correlations spike toward 1 (diversification fails)\n"
            "2. **Volatility Spike** - Vol doubles across all assets\n"
            "3. **Liquidity Stress** - 20% return haircut from widened spreads\n"
            "4. **Combined Crisis** - All three simultaneously\n\n"
            "Each scenario uses Monte Carlo simulation with your portfolio's actual covariance structure, "
            "modified to reflect the stress conditions.\n\n"
            "Visit the **Stress Scenarios** page to see projected outcomes under each scenario."
        )

    # --- Explain / educational queries ---
    if any(kw in msg for kw in ["explain", "what is", "what does", "how does", "define", "meaning"]):
        if "hhi" in msg:
            hhi = portfolio.hhi_concentration()
            return (
                f"**HHI (Herfindahl-Hirschman Index)** measures portfolio concentration.\n\n"
                f"- Ranges from 1/n (perfectly diversified) to 1 (single asset)\n"
                f"- Your HHI: **{hhi:.4f}** (effective {portfolio.effective_n():.1f} assets)\n"
                f"- {'Well diversified' if hhi < 0.3 else 'Moderately concentrated' if hhi < 0.5 else 'Highly concentrated'}"
            )
        if "sharpe" in msg:
            ann_ret = returns.mean() * 252
            ann_vol = returns.std() * 252**0.5
            port_sharpe = float((ann_ret * weights).sum() / (portfolio.portfolio_returns.std() * 252**0.5))
            return (
                f"**Sharpe Ratio** = (Return - Risk-Free Rate) / Volatility\n\n"
                f"It measures risk-adjusted return. Higher is better.\n"
                f"- Your portfolio Sharpe: **{port_sharpe:.2f}**\n"
                f"- Above 1.0 = good, above 2.0 = excellent"
            )
        if "monte carlo" in msg or "simulation" in msg:
            return (
                "**Monte Carlo Simulation** generates thousands of possible future return paths "
                "using your portfolio's historical mean returns and covariance structure.\n\n"
                "- **Standard MC** uses Cholesky decomposition to generate correlated random returns\n"
                "- **Regime-Aware MC** uses different parameters per regime with transition probabilities\n\n"
                "Visit the **Risk Metrics** page to run simulations."
            )
        return (
            "I can explain concepts like VaR, CVaR, correlation, regime detection, HHI, "
            "Sharpe ratio, and Monte Carlo simulation. Try asking *'What is VaR?'* or *'Explain HHI'*."
        )

    # --- Help / general ---
    if any(kw in msg for kw in ["help", "what can", "how do", "menu", "options", "capabilities"]):
        return (
            "I can help you understand your portfolio analytics. Try asking:\n\n"
            "- **Correlation**: *How correlated are my assets?*\n"
            "- **VaR/CVaR**: *What is my Value-at-Risk?*\n"
            "- **Regime**: *What market regime are we in?*\n"
            "- **Hedging**: *Which asset is the best hedge?*\n"
            "- **Stress**: *What happens under a crisis scenario?*\n"
            "- **Explain**: *What is HHI?* / *Explain Monte Carlo*\n\n"
            "All responses reference your actual portfolio data and computed metrics."
        )

    # --- Default: portfolio summary ---
    summary = portfolio.summary()
    port_ret = portfolio.portfolio_returns
    import numpy as np
    ann_ret = float(port_ret.mean() * 252)
    ann_vol = float(port_ret.std() * np.sqrt(252))

    return (
        f"**Your Portfolio:**\n\n"
        f"- **Assets:** {', '.join(summary['tickers'])} ({summary['n_assets']} instruments)\n"
        f"- **Effective diversification:** {summary['effective_n']:.1f} assets\n"
        f"- **Annualized return:** {ann_ret:+.2%}\n"
        f"- **Annualized volatility:** {ann_vol:.2%}\n"
        f"- **Data:** {summary.get('date_range', 'N/A')}\n\n"
        f"Ask me about **correlation**, **VaR**, **regimes**, **hedging**, or **stress scenarios** "
        f"for specific insights."
    )
