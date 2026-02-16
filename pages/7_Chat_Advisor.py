"""
Chat Advisor - LLM-powered chat interface grounded in portfolio analytics.
This is the primary intelligent interface for the hedging platform.
"""

import streamlit as st
from core.portfolio import init_session_state
from core.style import apply_page_style

apply_page_style()
init_session_state()

# Custom chat CSS
st.markdown("""
<style>
    .chat-header {
        font-size: 1.1rem; font-weight: 600; color: #333;
        text-transform: uppercase; letter-spacing: 0.06em;
        border-bottom: 2px solid #387ed1; padding-bottom: 0.6rem;
        margin-bottom: 1rem;
    }
    .chat-context {
        background: #f8f9fa; border: 1px solid #e8e8e8; border-radius: 6px;
        padding: 1rem 1.2rem; margin-bottom: 1.5rem; font-size: 0.85rem; color: #555;
    }
    .chat-context strong { color: #333; }
    .suggestion-btn {
        display: inline-block; background: #f0f6ff; border: 1px solid #387ed1;
        border-radius: 20px; padding: 0.4rem 1rem; margin: 0.3rem;
        font-size: 0.8rem; color: #387ed1; cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-header">Portfolio Advisor</div>', unsafe_allow_html=True)

# --- Portfolio context panel ---
if st.session_state.data_loaded:
    portfolio = st.session_state.portfolio
    summary = portfolio.summary()
    regime_df = st.session_state.regime_df
    current_regime = regime_df["regime"].iloc[-1] if regime_df is not None and len(regime_df) > 0 else "Unknown"

    # Quick stats context
    from risk.var_cvar import var_cvar_summary
    from risk.correlation import calculate_diversification_ratio
    try:
        var_s = var_cvar_summary(portfolio.returns, portfolio.weights, 0.95)
        div_ratio = calculate_diversification_ratio(portfolio.returns, portfolio.weights)
    except Exception:
        var_s = None
        div_ratio = None

    ctx_parts = [
        f"<strong>Portfolio:</strong> {', '.join(summary['tickers'])} ({summary['n_assets']} assets)",
        f"<strong>Period:</strong> {summary.get('date_range', 'N/A')}",
        f"<strong>Regime:</strong> {current_regime}",
    ]
    if var_s:
        ctx_parts.append(f"<strong>95% VaR:</strong> {var_s['historical_var']:.2%} | <strong>CVaR:</strong> {var_s['historical_cvar']:.2%}")
    if div_ratio:
        ctx_parts.append(f"<strong>Diversification Ratio:</strong> {div_ratio:.2f}")

    st.markdown(
        f'<div class="chat-context">{"&nbsp;&nbsp;·&nbsp;&nbsp;".join(ctx_parts)}</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="chat-context">No portfolio loaded. Load data from the sidebar to enable context-aware responses.</div>',
        unsafe_allow_html=True,
    )

# --- Initialize chat history for this page ---
if "page_chat_history" not in st.session_state:
    st.session_state.page_chat_history = [
        {"role": "assistant", "content": (
            "Welcome to the Portfolio Advisor. I can help you understand your portfolio's "
            "risk metrics, correlations, regime analysis, and hedging strategies.\n\n"
            "Try asking:\n"
            "- *What is my current Value-at-Risk?*\n"
            "- *How correlated are my assets?*\n"
            "- *What regime are we in?*\n"
            "- *How can I hedge my portfolio?*\n"
            "- *Explain my diversification ratio*"
        )}
    ]

# --- Display chat messages ---
for msg in st.session_state.page_chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Suggested questions ---
if len(st.session_state.page_chat_history) <= 1 and st.session_state.data_loaded:
    st.markdown("**Quick questions:**")
    suggestions = [
        "What is my portfolio's Value-at-Risk?",
        "How do correlations change during crashes?",
        "What market regime are we in?",
        "Which asset is the best hedge?",
        "How diversified is my portfolio?",
        "What happens under stress scenarios?",
    ]
    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        if cols[i % 3].button(suggestion, key=f"suggest_{i}", use_container_width=True):
            st.session_state.page_chat_history.append({"role": "user", "content": suggestion})
            try:
                from chat.engine import get_response
                reply = get_response(suggestion, st.session_state)
            except Exception:
                from chat.fallback import fallback_response
                reply = fallback_response(suggestion, st.session_state)
            st.session_state.page_chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

# --- Chat input ---
user_input = st.chat_input("Ask about your portfolio...")

if user_input:
    st.session_state.page_chat_history.append({"role": "user", "content": user_input})

    # Also add to sidebar chat history for cross-page persistence
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                from chat.engine import get_response
                reply = get_response(user_input, st.session_state)
            except Exception:
                from chat.fallback import fallback_response
                reply = fallback_response(user_input, st.session_state)

        st.markdown(reply)

    st.session_state.page_chat_history.append({"role": "assistant", "content": reply})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    st.rerun()
