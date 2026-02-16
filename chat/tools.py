"""
OpenAI function-calling tool definitions and executor.
"""

import json

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_correlation_matrix",
            "description": "Get the current correlation matrix for portfolio assets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tail": {
                        "type": "boolean",
                        "description": "If true, return tail (crash) correlation instead of normal.",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_var_metrics",
            "description": "Get VaR and CVaR metrics for the portfolio.",
            "parameters": {
                "type": "object",
                "properties": {
                    "confidence": {
                        "type": "number",
                        "description": "Confidence level (e.g. 0.95).",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_hedges",
            "description": "Compare hedge effectiveness of portfolio assets.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_regime_status",
            "description": "Get the current market regime and recent regime statistics.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def execute_tool(name: str, arguments: dict, session_state) -> str:
    """Route tool calls to computation functions and return JSON string."""
    portfolio = getattr(session_state, "portfolio", None)
    regime_df = getattr(session_state, "regime_df", None)

    if portfolio is None or portfolio.returns is None:
        return json.dumps({"error": "No portfolio data loaded."})

    returns = portfolio.returns
    weights = portfolio.weights

    if name == "get_correlation_matrix":
        from risk.correlation import calculate_correlation_matrix, calculate_tail_correlation
        tail = arguments.get("tail", False)
        if tail:
            corr = calculate_tail_correlation(returns)
        else:
            corr = calculate_correlation_matrix(returns)
        return corr.round(3).to_json()

    elif name == "get_var_metrics":
        from risk.var_cvar import var_cvar_summary
        conf = arguments.get("confidence", 0.95)
        s = var_cvar_summary(returns, weights, conf)
        return json.dumps({k: round(v, 6) if isinstance(v, float) else v for k, v in s.items()})

    elif name == "compare_hedges":
        from risk.hedge_analysis import compare_hedges as _compare
        port_ret = portfolio.portfolio_returns
        candidates = [t for t in portfolio.tickers[1:]]
        if not candidates:
            return json.dumps({"error": "Need >1 asset for hedge comparison."})
        hedge_df = returns[candidates]
        result = _compare(port_ret, hedge_df)
        return result.round(4).to_json()

    elif name == "get_regime_status":
        if regime_df is None:
            return json.dumps({"error": "Regime data not computed."})
        from core.regime_detector import get_regime_statistics
        current = regime_df["regime"].iloc[-1]
        stats = get_regime_statistics(regime_df)
        return json.dumps({"current_regime": current, "statistics": stats})

    return json.dumps({"error": f"Unknown tool: {name}"})
