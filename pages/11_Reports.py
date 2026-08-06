"""
Reports - PDF report generation and download.
"""

import streamlit as st
import pandas as pd

from core.portfolio import init_session_state
from core.style import page_header

init_session_state()
page_header("Reports")

if not st.session_state.data_loaded:
    st.info("Load data from the sidebar first.")
    st.stop()

portfolio = st.session_state.portfolio
regime_df = st.session_state.regime_df
holdings = st.session_state.holdings

# --- Report type selection ---
report_type = st.radio(
    "Report Type",
    options=["Portfolio Summary (2-3 pages)", "Full Analysis (5-6 pages)"],
    horizontal=True,
)

if report_type == "Portfolio Summary (2-3 pages)":
    st.markdown(
        "**Includes:** Portfolio overview, asset breakdown, sector exposure, "
        "risk metrics (VaR/CVaR), current regime, and holdings P&L (if any)."
    )
else:
    st.markdown(
        "**Includes:** Everything in the summary, plus correlation matrix, "
        "buy/sell recommendations with health score, and a news digest."
    )

# --- Generate button ---
if st.button("Generate PDF Report", type="primary", use_container_width=True):
    with st.spinner("Generating report..."):
        from core.data_fetch import get_sectors, fetch_latest_prices
        from core.report_gen import generate_summary_report, generate_full_report

        sectors = get_sectors(portfolio.tickers)

        # Get current prices for holdings
        current_prices = {}
        if holdings:
            live = fetch_latest_prices(list(holdings.keys()))
            for _, row in live.iterrows():
                if pd.notna(row.get("Price")):
                    current_prices[row["Ticker"]] = row["Price"]

        if "Summary" in report_type:
            pdf_bytes = generate_summary_report(
                portfolio, regime_df, holdings, current_prices, sectors,
            )
            filename = "portfolio_summary.pdf"
        else:
            # Full report needs signals and news
            from core.signals import generate_all_signals
            from core.news import fetch_portfolio_news

            signals = generate_all_signals(
                portfolio, regime_df, holdings, current_prices,
            )
            news_items = fetch_portfolio_news(
                portfolio.tickers, max_per_ticker=3,
            )
            pdf_bytes = generate_full_report(
                portfolio, regime_df, holdings, current_prices,
                sectors, signals, news_items,
            )
            filename = "portfolio_full_report.pdf"

    st.download_button(
        f"Download {filename}",
        pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        use_container_width=True,
    )
    st.success("Report generated successfully.")

# --- Existing Excel exports ---
st.markdown("### Excel Exports")

import numpy as np
from core.data_fetch import get_sectors
from core.style import COLORS

returns = portfolio.returns
sectors = get_sectors(portfolio.tickers)

report_rows = []
for i, t in enumerate(portfolio.tickers):
    report_rows.append({
        "Ticker": t,
        "Sector": sectors[t],
        "Weight": f"{portfolio.weights[i]:.2%}",
        "Ann Return": f"{(returns[t].mean() * 252):.2%}",
        "Ann Vol": f"{(returns[t].std() * np.sqrt(252)):.2%}",
        "Sharpe": f"{(returns[t].mean() * 252) / (returns[t].std() * np.sqrt(252)):.2f}",
    })
report_df = pd.DataFrame(report_rows)

import io

dl1, dl2 = st.columns(2)
with dl1:
    buf1 = io.BytesIO()
    report_df.to_excel(buf1, index=False, engine="openpyxl")
    st.download_button(
        "Download Portfolio Report (Excel)",
        buf1.getvalue(),
        file_name="portfolio_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
with dl2:
    buf2 = io.BytesIO()
    returns.to_excel(buf2, engine="openpyxl")
    st.download_button(
        "Download Returns Data (Excel)",
        buf2.getvalue(),
        file_name="returns_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
