"""
Chat Advisor - OpenAI-powered chat interface grounded in portfolio analytics.
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
    .provider-badge {
        display: inline-block; background: #e8f5e9; border: 1px solid #00b386;
        border-radius: 16px; padding: 0.25rem 0.8rem; font-size: 0.75rem;
        color: #00b386; font-weight: 600; margin-bottom: 1rem;
    }
    .provider-badge-fallback {
        display: inline-block; background: #fff3e0; border: 1px solid #f5a623;
        border-radius: 16px; padding: 0.25rem 0.8rem; font-size: 0.75rem;
        color: #f5a623; font-weight: 600; margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="chat-header">Portfolio Advisor</div>', unsafe_allow_html=True)

# --- Provider status badge ---
from chat.engine import get_active_provider  # noqa: E402

provider = get_active_provider()
if "Fallback" in provider:
    st.markdown(
        f'<div class="provider-badge-fallback">Powered by: {provider}</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="provider-badge">Powered by: {provider}</div>',
        unsafe_allow_html=True,
    )

# --- Portfolio context panel ---
if st.session_state.data_loaded:
    portfolio = st.session_state.portfolio
    summary = portfolio.summary()
    regime_df = st.session_state.regime_df
    current_regime = (
        regime_df["regime"].iloc[-1]
        if regime_df is not None and len(regime_df) > 0
        else "Unknown"
    )

    from risk.var_cvar import var_cvar_summary  # noqa: E402
    from risk.correlation import calculate_diversification_ratio  # noqa: E402
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
        ctx_parts.append(
            f"<strong>95% VaR:</strong> {var_s['historical_var']:.2%} "
            f"| <strong>CVaR:</strong> {var_s['historical_cvar']:.2%}"
        )
    if div_ratio:
        ctx_parts.append(f"<strong>Diversification Ratio:</strong> {div_ratio:.2f}")

    st.markdown(
        f'<div class="chat-context">{"&nbsp;&nbsp;·&nbsp;&nbsp;".join(ctx_parts)}</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<div class="chat-context">No portfolio loaded. '
        'Load data from the sidebar to enable context-aware responses.</div>',
        unsafe_allow_html=True,
    )

# --- Initialize chat history for this page ---
if "page_chat_history" not in st.session_state:
    st.session_state.page_chat_history = [
        {"role": "assistant", "content": (
            "Hey! I'm your financial advisor. Ask me **anything** about finance!\n\n"
            "**Investment Advice:**\n"
            "- *What stocks should I invest in?*\n"
            "- *Where should I put my money?*\n"
            "- *Should I sell my holdings?*\n\n"
            "**General Finance:**\n"
            "- *What is a stock / bond / ETF / option?*\n"
            "- *Explain inflation / interest rates / P/E ratio*\n"
            "- *Tell me about value investing / technical analysis*\n\n"
            "**Your Portfolio:**\n"
            "- *What is my Value-at-Risk?*\n"
            "- *How correlated are my assets?*\n"
            "- *What market regime are we in?*"
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
        "What stocks should I invest in?",
        "What is my Value-at-Risk?",
        "Explain options trading",
        "What market regime are we in?",
        "Tell me about value investing",
        "Should I sell my holdings?",
    ]
    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        if cols[i % 3].button(suggestion, key=f"suggest_{i}", use_container_width=True):
            st.session_state.page_chat_history.append(
                {"role": "user", "content": suggestion}
            )
            try:
                from chat.engine import get_response
                chat_hist = [
                    m for m in st.session_state.page_chat_history[1:]
                    if m["role"] in ("user", "assistant")
                ]
                reply = get_response(suggestion, st.session_state, history=chat_hist)
            except Exception as e:
                reply = f"**Error:** {e}"
            st.session_state.page_chat_history.append(
                {"role": "assistant", "content": reply}
            )
            st.rerun()

# --- Chat input ---
user_input = st.chat_input("Ask anything about finance, investing, or your portfolio...")

if user_input:
    st.session_state.page_chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                from chat.engine import get_response
                # Pass conversation history (exclude welcome message and current input)
                chat_hist = [
                    m for m in st.session_state.page_chat_history[1:-1]
                    if m["role"] in ("user", "assistant")
                ]
                reply = get_response(user_input, st.session_state, history=chat_hist)
            except Exception as e:
                reply = f"**Error:** {e}"

        st.markdown(reply)

    st.session_state.page_chat_history.append({"role": "assistant", "content": reply})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    st.rerun()
