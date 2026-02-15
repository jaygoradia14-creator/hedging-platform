"""
Rules-based fallback chat when no OpenAI API key is available.
Keyword matching routes to context-aware responses.
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
            "Enter your tickers and click 'Load Data' to get started."
        )

    # --- Correlation queries ---
    if any(kw in msg for kw in ["correlation", "corr", "diversif"]):
        try:
            from risk.correlation import calculate_diversification_ratio
            dr = calculate_diversification_ratio(portfolio.returns, portfolio.weights)
            return (
                f"Your portfolio's diversification ratio is {dr:.2f}. "
                f"A ratio above 1 means diversification is providing benefit. "
                f"Visit the Correlation Analysis page for normal vs crash correlation heatmaps."
            )
        except Exception:
            return "Visit the Correlation Analysis page to see how your assets correlate."

    # --- VaR queries ---
    if any(kw in msg for kw in ["var", "value at risk", "cvar", "expected shortfall", "risk metric"]):
        try:
            from risk.var_cvar import var_cvar_summary
            s = var_cvar_summary(portfolio.returns, portfolio.weights, 0.95)
            return (
                f"At 95% confidence: Historical VaR = {s['historical_var']:.2%}, "
                f"CVaR (Expected Shortfall) = {s['historical_cvar']:.2%}. "
                f"This means on the worst 5% of days, you can expect to lose at least "
                f"{s['historical_var']:.2%} of portfolio value."
            )
        except Exception:
            return "Visit the Risk Metrics page for VaR and CVaR analysis."

    # --- Regime queries ---
    if any(kw in msg for kw in ["regime", "volatility", "crisis", "market state"]):
        if regime_df is not None and len(regime_df) > 0:
            current = regime_df["regime"].iloc[-1]
            from core.regime_detector import get_regime_statistics
            stats = get_regime_statistics(regime_df)
            regime_info = ", ".join(
                f"{k}: {v['pct_time']:.0f}% of time" for k, v in stats.items()
            )
            return (
                f"The current market regime is **{current}**. "
                f"Regime distribution: {regime_info}. "
                f"Visit the Regime Detection page for timeline and conditional analysis."
            )
        return "Visit the Regime Detection page to see current market regime analysis."

    # --- Hedge queries ---
    if any(kw in msg for kw in ["hedge", "protect", "insurance", "downside"]):
        tickers = portfolio.tickers
        if len(tickers) > 1:
            return (
                f"Your portfolio includes {', '.join(tickers)}. "
                f"Visit the Hedge Impact page to see which assets best reduce portfolio risk "
                f"and the optimal hedge ratio."
            )
        return "Add more assets to your portfolio to analyze hedging opportunities."

    # --- Help / general ---
    if any(kw in msg for kw in ["help", "what can", "how do", "explain"]):
        return (
            "I can help you understand your portfolio analytics. Try asking about:\n"
            "- **Correlation**: How are your assets correlated?\n"
            "- **VaR**: What's your Value-at-Risk?\n"
            "- **Regime**: What's the current market regime?\n"
            "- **Hedging**: How can you reduce portfolio risk?\n\n"
            "Use the sidebar pages for detailed analysis."
        )

    # Default
    summary = portfolio.summary()
    return (
        f"Your portfolio has {summary['n_assets']} assets "
        f"({', '.join(summary['tickers'])}), "
        f"with an effective diversification of {summary['effective_n']:.1f} assets. "
        f"Try asking about correlation, VaR, regimes, or hedging for specific insights."
    )
