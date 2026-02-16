"""
System prompt templates and context builders for the chat interface.
"""

SYSTEM_PROMPT = """You are a financial advisor and portfolio analyst embedded in a hedging platform.
You interpret computed analytics in plain language and provide actionable buy/sell opinions
based on the user's portfolio data, holdings, and current market regime.

Current portfolio context:
{portfolio_context}

Current analysis context:
{analysis_context}

Current holdings:
{holdings_context}

Guidelines:
- Be concise (2-4 sentences per response).
- Reference specific numbers from the portfolio and holdings context.
- Give buy/sell opinions based on P&L, diversification, and regime data.
- Suggest diversification opportunities when sector exposure is unbalanced.
- If asked about something not computed, suggest which page to visit.
- Consider the current market regime when making recommendations.
"""


def build_portfolio_context(session_state) -> str:
    """Summarize portfolio state into a concise string for the system prompt."""
    portfolio = getattr(session_state, "portfolio", None)
    if portfolio is None or not getattr(session_state, "data_loaded", False):
        return "No portfolio loaded yet."

    summary = portfolio.summary()
    lines = [
        f"Assets: {', '.join(summary['tickers'])}",
        f"Weights: {summary['weights']}",
        f"HHI: {summary['hhi']:.4f}, Effective N: {summary['effective_n']:.1f}",
    ]
    if "data_points" in summary:
        lines.append(f"Data: {summary['data_points']} days, {summary['date_range']}")
    return "\n".join(lines)


def build_analysis_context(session_state) -> str:
    """Summarize available analysis results."""
    parts = []
    regime_df = getattr(session_state, "regime_df", None)
    if regime_df is not None:
        current = regime_df["regime"].iloc[-1] if len(regime_df) > 0 else "Unknown"
        parts.append(f"Current regime: {current}")

    portfolio = getattr(session_state, "portfolio", None)
    if portfolio is not None and portfolio.returns is not None:
        from risk.var_cvar import var_cvar_summary
        try:
            s = var_cvar_summary(portfolio.returns, portfolio.weights, 0.95)
            parts.append(
                f"95% VaR: {s['historical_var']:.2%}, CVaR: {s['historical_cvar']:.2%}"
            )
        except Exception:
            pass

        from risk.correlation import calculate_diversification_ratio
        try:
            dr = calculate_diversification_ratio(portfolio.returns, portfolio.weights)
            parts.append(f"Diversification ratio: {dr:.2f}")
        except Exception:
            pass

    return "\n".join(parts) if parts else "No analysis computed yet."


def build_holdings_context(session_state) -> str:
    """Summarize current holdings with P&L for the system prompt."""
    holdings = getattr(session_state, "holdings", {})
    if not holdings:
        return "No holdings tracked."

    lines = []
    for ticker, info in holdings.items():
        lines.append(
            f"{ticker}: {info['shares']:.2f} shares @ ${info['buy_price']:.2f}"
        )
    return "\n".join(lines)


def build_system_message(session_state) -> str:
    """Build the full system message."""
    return SYSTEM_PROMPT.format(
        portfolio_context=build_portfolio_context(session_state),
        analysis_context=build_analysis_context(session_state),
        holdings_context=build_holdings_context(session_state),
    )
