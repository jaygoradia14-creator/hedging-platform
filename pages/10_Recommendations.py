"""
Recommendations - Portfolio health score, action cards, and signal table.
"""

import streamlit as st
import pandas as pd

from core.portfolio import init_session_state
from core.style import page_header

init_session_state()
page_header("Recommendations")

# Disclaimer banner
st.markdown(
    '<div style="background:#fff8e1;border:1px solid #f5a623;border-radius:8px;'
    'padding:10px 16px;margin-bottom:16px;font-size:0.85rem;color:#8b6914;">'
    'For educational purposes only. This is not financial advice. '
    'Always do your own research before making investment decisions.'
    '</div>',
    unsafe_allow_html=True,
)

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
regime_df = st.session_state.regime_df
holdings = st.session_state.holdings

# Get current prices for holdings
current_prices = {}
if holdings:
    from core.data_fetch import fetch_latest_prices
    live = fetch_latest_prices(list(holdings.keys()))
    for _, row in live.iterrows():
        if pd.notna(row.get("Price")):
            current_prices[row["Ticker"]] = row["Price"]

# Generate signals
from core.signals import (
    generate_all_signals,
    calculate_portfolio_health_score,
    get_signal_color,
    SignalType,
)

signals = generate_all_signals(portfolio, regime_df, holdings, current_prices)
health_score = calculate_portfolio_health_score(signals)

# --- Health Score ---
st.metric("Portfolio Health Score", f"{health_score}/100")

# --- Top Action Cards ---
st.markdown("### Top Signals")

top_signals = signals[:5]
if not top_signals:
    st.info("No signals generated. Your portfolio looks stable.")
else:
    for sig in top_signals:
        color = get_signal_color(sig.signal_type)
        type_label = sig.signal_type.value
        card_html = f"""
        <div style="border-left:4px solid {color};border:1px solid #e8e8e8;
                    border-left:4px solid {color};border-radius:8px;
                    padding:12px 16px;margin-bottom:10px;background:#fff;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <span style="background:{color};color:#fff;padding:2px 10px;
                             border-radius:4px;font-size:0.75rem;font-weight:600;">
                    {type_label}
                </span>
                <span style="font-weight:600;color:#44475b;font-size:0.9rem;">
                    {sig.title}
                </span>
            </div>
            <div style="font-size:0.85rem;color:#666;margin-bottom:4px;">
                {sig.description}
            </div>
            <div style="font-size:0.8rem;color:#44475b;font-weight:500;">
                Action: {sig.action}
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

# --- Full Signal Table ---
st.markdown("### All Signals")

if signals:
    table_data = []
    for s in signals:
        table_data.append({
            "Ticker": s.ticker,
            "Signal": s.title,
            "Type": s.signal_type.value,
            "Indicator": (
                f"{s.indicator_value:.1f}" if s.indicator_value is not None
                else "-"
            ),
            "Action": s.action,
            "Source": s.source,
        })
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No signals to display.")

# --- Expandable sections by source ---
st.markdown("### Signals by Source")

sources = ["Regime", "Technical", "Portfolio", "Holdings"]
for source in sources:
    source_signals = [s for s in signals if s.source == source]
    with st.expander(f"{source} ({len(source_signals)} signals)"):
        if source_signals:
            for s in source_signals:
                color = get_signal_color(s.signal_type)
                st.markdown(
                    f'<span style="color:{color};font-weight:600;">'
                    f'{s.signal_type.value}</span> — '
                    f'**{s.title}**: {s.description}',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No signals from this source.")
