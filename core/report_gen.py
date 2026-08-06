"""
PDF report generation using fpdf2.
Generates branded portfolio summary and full analysis reports.
"""

import io
import numpy as np
import pandas as pd
from datetime import datetime


def _safe_str(val):
    """Convert value to string, handling NaN and None."""
    if val is None:
        return "N/A"
    if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
        return "N/A"
    return str(val)


class ReportPDF:
    """Branded PDF report using fpdf2."""

    def __init__(self):
        from fpdf import FPDF
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=20)
        self.pdf.set_font("Helvetica", size=10)
        self._header_color = (56, 126, 209)  # BLUE
        self._alt_row = (245, 247, 250)

    def _add_header(self):
        """Add branded header to current page."""
        self.pdf.set_font("Helvetica", "B", 18)
        self.pdf.set_text_color(*self._header_color)
        self.pdf.cell(0, 12, "hedging platform", new_x="LMARGIN", new_y="NEXT")
        self.pdf.set_font("Helvetica", "", 9)
        self.pdf.set_text_color(140, 140, 140)
        self.pdf.cell(
            0, 6,
            f"Portfolio Risk & Hedging Report  |  {datetime.now().strftime('%B %d, %Y')}",
            new_x="LMARGIN", new_y="NEXT",
        )
        self.pdf.set_draw_color(*self._header_color)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(8)

    def _add_footer_on_pages(self):
        """Set up automatic footer with page numbers."""
        # fpdf2 handles footers through subclass, so we add page numbers after
        pass

    def add_page(self):
        self.pdf.add_page()
        self._add_header()

    def section_title(self, title):
        self.pdf.set_font("Helvetica", "B", 12)
        self.pdf.set_text_color(68, 71, 91)
        self.pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.pdf.set_draw_color(230, 230, 230)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(4)

    def add_key_value(self, key, value):
        self.pdf.set_font("Helvetica", "B", 9)
        self.pdf.set_text_color(140, 140, 140)
        self.pdf.cell(60, 7, key, new_x="RIGHT")
        self.pdf.set_font("Helvetica", "", 10)
        self.pdf.set_text_color(68, 71, 91)
        self.pdf.cell(0, 7, _safe_str(value), new_x="LMARGIN", new_y="NEXT")

    def add_table(self, headers, rows, col_widths=None):
        """Add a styled table.

        Args:
            headers: List of column header strings.
            rows: List of lists, each inner list is a row.
            col_widths: Optional list of column widths. Auto-calculated if None.
        """
        if not headers:
            return

        n_cols = len(headers)
        page_width = 190  # usable width (210 - 10 margin each side)
        if col_widths is None:
            col_widths = [page_width / n_cols] * n_cols

        # Header row
        self.pdf.set_font("Helvetica", "B", 9)
        self.pdf.set_fill_color(*self._header_color)
        self.pdf.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.pdf.cell(col_widths[i], 8, _safe_str(h), border=0, fill=True)
        self.pdf.ln()

        # Data rows
        self.pdf.set_font("Helvetica", "", 9)
        self.pdf.set_text_color(68, 71, 91)
        for row_idx, row in enumerate(rows):
            if row_idx % 2 == 1:
                self.pdf.set_fill_color(*self._alt_row)
                fill = True
            else:
                fill = False
            for i, val in enumerate(row):
                w = col_widths[i] if i < len(col_widths) else col_widths[-1]
                self.pdf.cell(w, 7, _safe_str(val), border=0, fill=fill)
            self.pdf.ln()

        self.pdf.ln(4)

    def add_text(self, text):
        self.pdf.set_font("Helvetica", "", 9)
        self.pdf.set_text_color(68, 71, 91)
        self.pdf.multi_cell(0, 5, text)
        self.pdf.ln(2)

    def get_bytes(self):
        """Return PDF as bytes."""
        # Add page numbers
        total = self.pdf.pages_count
        for i in range(1, total + 1):
            self.pdf.page = i
            self.pdf.set_y(-15)
            self.pdf.set_font("Helvetica", "", 8)
            self.pdf.set_text_color(180, 180, 180)
            self.pdf.cell(0, 10, f"Page {i} of {total}", align="C")

        return self.pdf.output()


def generate_summary_report(portfolio, regime_df, holdings=None,
                            current_prices=None, sectors=None):
    """Generate a 2-3 page portfolio summary PDF.

    Returns:
        PDF bytes.
    """
    report = ReportPDF()
    returns = portfolio.returns

    # Page 1: Portfolio Overview
    report.add_page()
    report.section_title("Portfolio Overview")

    report.add_key_value("Instruments", ", ".join(portfolio.tickers))
    report.add_key_value("Number of Assets", str(portfolio.n_assets))

    if returns is not None:
        ann_ret = float(portfolio.portfolio_returns.mean() * 252)
        ann_vol = float(portfolio.portfolio_returns.std() * np.sqrt(252))
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
        report.add_key_value("Annualized Return", f"{ann_ret:+.2%}")
        report.add_key_value("Annualized Volatility", f"{ann_vol:.2%}")
        report.add_key_value("Sharpe Ratio", f"{sharpe:.2f}")

    hhi = portfolio.hhi_concentration()
    report.add_key_value("HHI Concentration", f"{hhi:.4f}")
    report.add_key_value("Effective # Assets", f"{portfolio.effective_n():.1f}")

    # Asset details table
    report.section_title("Asset Breakdown")
    headers = ["Ticker", "Sector", "Weight", "Return", "Volatility", "Sharpe"]
    rows = []
    if returns is not None:
        ann_ret_s = returns.mean() * 252
        ann_vol_s = returns.std() * np.sqrt(252)
        for i, t in enumerate(portfolio.tickers):
            sec = sectors.get(t, "Other") if sectors else "N/A"
            ret = float(ann_ret_s[t]) if t in ann_ret_s.index else 0
            vol = float(ann_vol_s[t]) if t in ann_vol_s.index else 0
            sh = ret / vol if vol > 0 else 0
            rows.append([
                t, sec, f"{portfolio.weights[i]:.1%}",
                f"{ret:+.2%}", f"{vol:.2%}", f"{sh:.2f}",
            ])
    report.add_table(headers, rows, col_widths=[25, 40, 25, 30, 35, 35])

    # Sector breakdown
    if sectors:
        report.section_title("Sector Breakdown")
        sector_weights = {}
        for i, t in enumerate(portfolio.tickers):
            sec = sectors.get(t, "Other")
            sector_weights[sec] = sector_weights.get(sec, 0) + portfolio.weights[i]
        sec_rows = [[sec, f"{w:.1%}"] for sec, w in sorted(
            sector_weights.items(), key=lambda x: -x[1]
        )]
        report.add_table(["Sector", "Weight"], sec_rows, col_widths=[100, 90])

    # Page 2: Risk Snapshot
    report.add_page()
    report.section_title("Risk Snapshot")

    if returns is not None:
        try:
            from risk.var_cvar import var_cvar_summary
            var_s = var_cvar_summary(returns, portfolio.weights, 0.95)
            report.add_key_value("95% Historical VaR",
                                 f"{var_s.get('historical_var', 0):.2%}")
            report.add_key_value("95% Historical CVaR",
                                 f"{var_s.get('historical_cvar', 0):.2%}")
            report.add_key_value("95% Parametric VaR",
                                 f"{var_s.get('parametric_var', 0):.2%}")
        except Exception:
            pass

        try:
            from risk.correlation import calculate_diversification_ratio
            div_ratio = calculate_diversification_ratio(returns, portfolio.weights)
            report.add_key_value("Diversification Ratio", f"{div_ratio:.2f}")
        except Exception:
            pass

    report.add_key_value("HHI", f"{hhi:.4f}")

    # Regime info
    if regime_df is not None and not regime_df.empty:
        current_regime = regime_df["regime"].iloc[-1]
        report.add_key_value("Current Regime", current_regime)
        try:
            from core.regime_detector import get_regime_statistics
            stats = get_regime_statistics(regime_df)
            report.section_title("Regime Statistics")
            regime_rows = []
            for name, s in stats.items():
                regime_rows.append([
                    name,
                    f"{s['pct_time']:.1f}%",
                    f"{s['avg_vol']:.2%}",
                    f"{s['avg_corr']:.2f}",
                ])
            report.add_table(
                ["Regime", "% Time", "Avg Vol", "Avg Corr"],
                regime_rows,
                col_widths=[50, 45, 45, 50],
            )
        except Exception:
            pass

    # Page 3 (conditional): Holdings P&L
    if holdings and current_prices:
        report.add_page()
        report.section_title("Holdings P&L")
        from core.portfolio import get_holdings_summary
        rows_data = get_holdings_summary(current_prices)
        if rows_data:
            total_invested = sum(r["Shares"] * r["Buy Price"] for r in rows_data)
            total_value = sum(r["Value"] for r in rows_data)
            total_pnl = total_value - total_invested
            report.add_key_value("Total Invested", f"${total_invested:,.2f}")
            report.add_key_value("Current Value", f"${total_value:,.2f}")
            report.add_key_value("Total P&L", f"${total_pnl:+,.2f}")

            hold_rows = []
            for r in rows_data:
                hold_rows.append([
                    r["Ticker"],
                    f"{r['Shares']:.1f}",
                    f"${r['Buy Price']:,.2f}",
                    f"${r['Current Price']:,.2f}",
                    f"${r['P&L']:+,.2f}",
                    f"{r['P&L %']:+.1f}%",
                ])
            report.add_table(
                ["Ticker", "Shares", "Buy Price", "Current", "P&L", "P&L %"],
                hold_rows,
                col_widths=[28, 25, 35, 35, 35, 32],
            )

    return report.get_bytes()


def generate_full_report(portfolio, regime_df, holdings=None,
                         current_prices=None, sectors=None,
                         signals=None, news_items=None):
    """Generate a 5-6 page full analysis PDF.

    Includes everything from summary report plus correlation matrix,
    recommendations, and news digest.

    Returns:
        PDF bytes.
    """
    report = ReportPDF()
    returns = portfolio.returns

    # --- Page 1: Portfolio Overview (same as summary) ---
    report.add_page()
    report.section_title("Portfolio Overview")

    report.add_key_value("Instruments", ", ".join(portfolio.tickers))
    report.add_key_value("Number of Assets", str(portfolio.n_assets))

    if returns is not None:
        ann_ret = float(portfolio.portfolio_returns.mean() * 252)
        ann_vol = float(portfolio.portfolio_returns.std() * np.sqrt(252))
        sharpe = ann_ret / ann_vol if ann_vol > 0 else 0
        report.add_key_value("Annualized Return", f"{ann_ret:+.2%}")
        report.add_key_value("Annualized Volatility", f"{ann_vol:.2%}")
        report.add_key_value("Sharpe Ratio", f"{sharpe:.2f}")

    hhi = portfolio.hhi_concentration()
    report.add_key_value("HHI Concentration", f"{hhi:.4f}")

    # Asset table
    report.section_title("Asset Breakdown")
    headers = ["Ticker", "Sector", "Weight", "Return", "Volatility", "Sharpe"]
    rows = []
    if returns is not None:
        ann_ret_s = returns.mean() * 252
        ann_vol_s = returns.std() * np.sqrt(252)
        for i, t in enumerate(portfolio.tickers):
            sec = sectors.get(t, "Other") if sectors else "N/A"
            ret = float(ann_ret_s[t]) if t in ann_ret_s.index else 0
            vol = float(ann_vol_s[t]) if t in ann_vol_s.index else 0
            sh = ret / vol if vol > 0 else 0
            rows.append([
                t, sec, f"{portfolio.weights[i]:.1%}",
                f"{ret:+.2%}", f"{vol:.2%}", f"{sh:.2f}",
            ])
    report.add_table(headers, rows, col_widths=[25, 40, 25, 30, 35, 35])

    # --- Page 2: Risk Snapshot ---
    report.add_page()
    report.section_title("Risk Snapshot")

    if returns is not None:
        try:
            from risk.var_cvar import var_cvar_summary
            var_s = var_cvar_summary(returns, portfolio.weights, 0.95)
            report.add_key_value("95% Historical VaR",
                                 f"{var_s.get('historical_var', 0):.2%}")
            report.add_key_value("95% Historical CVaR",
                                 f"{var_s.get('historical_cvar', 0):.2%}")
        except Exception:
            pass

        try:
            from risk.correlation import calculate_diversification_ratio
            div_ratio = calculate_diversification_ratio(returns, portfolio.weights)
            report.add_key_value("Diversification Ratio", f"{div_ratio:.2f}")
        except Exception:
            pass

    report.add_key_value("HHI", f"{hhi:.4f}")

    if regime_df is not None and not regime_df.empty:
        current_regime = regime_df["regime"].iloc[-1]
        report.add_key_value("Current Regime", current_regime)
        try:
            from core.regime_detector import get_regime_statistics
            stats = get_regime_statistics(regime_df)
            report.section_title("Regime Statistics")
            regime_rows = []
            for name, s in stats.items():
                regime_rows.append([
                    name, f"{s['pct_time']:.1f}%",
                    f"{s['avg_vol']:.2%}", f"{s['avg_corr']:.2f}",
                ])
            report.add_table(
                ["Regime", "% Time", "Avg Vol", "Avg Corr"],
                regime_rows,
                col_widths=[50, 45, 45, 50],
            )
        except Exception:
            pass

    # --- Correlation Matrix ---
    if returns is not None and len(portfolio.tickers) >= 2:
        report.section_title("Correlation Matrix")
        try:
            from risk.correlation import calculate_correlation_matrix
            corr = calculate_correlation_matrix(returns)
            corr_headers = [""] + list(corr.columns)
            corr_rows = []
            n = len(corr.columns)
            col_w = min(30, 190 // (n + 1))
            for t in corr.index:
                row = [t] + [f"{corr.loc[t, c]:.2f}" for c in corr.columns]
                corr_rows.append(row)
            report.add_table(
                corr_headers, corr_rows,
                col_widths=[col_w] * (n + 1),
            )
        except Exception:
            pass

    # --- Page 3: Holdings ---
    if holdings and current_prices:
        report.add_page()
        report.section_title("Holdings P&L")
        from core.portfolio import get_holdings_summary
        rows_data = get_holdings_summary(current_prices)
        if rows_data:
            total_invested = sum(r["Shares"] * r["Buy Price"] for r in rows_data)
            total_value = sum(r["Value"] for r in rows_data)
            total_pnl = total_value - total_invested
            report.add_key_value("Total Invested", f"${total_invested:,.2f}")
            report.add_key_value("Current Value", f"${total_value:,.2f}")
            report.add_key_value("Total P&L", f"${total_pnl:+,.2f}")

            hold_rows = []
            for r in rows_data:
                hold_rows.append([
                    r["Ticker"], f"{r['Shares']:.1f}",
                    f"${r['Buy Price']:,.2f}", f"${r['Current Price']:,.2f}",
                    f"${r['P&L']:+,.2f}", f"{r['P&L %']:+.1f}%",
                ])
            report.add_table(
                ["Ticker", "Shares", "Buy Price", "Current", "P&L", "P&L %"],
                hold_rows,
                col_widths=[28, 25, 35, 35, 35, 32],
            )

    # --- Page 4: Recommendations ---
    if signals:
        report.add_page()
        report.section_title("Recommendations")
        from core.signals import calculate_portfolio_health_score
        health = calculate_portfolio_health_score(signals)
        report.add_key_value("Portfolio Health Score", f"{health}/100")
        report.add_text(
            "Disclaimer: These recommendations are for educational purposes only "
            "and do not constitute financial advice."
        )

        sig_rows = []
        for s in signals[:15]:
            sig_rows.append([
                s.ticker,
                s.signal_type.value,
                s.title,
                s.action,
                s.source,
            ])
        report.add_table(
            ["Ticker", "Type", "Signal", "Action", "Source"],
            sig_rows,
            col_widths=[25, 30, 50, 55, 30],
        )

    # --- Page 5: News Digest ---
    if news_items:
        report.add_page()
        report.section_title("News Digest")
        news_rows = []
        for item in news_items[:20]:
            news_rows.append([
                item.get("ticker", ""),
                item.get("title", "")[:60],
                item.get("sentiment", ""),
                item.get("source", ""),
                item.get("published", "")[:10],
            ])
        report.add_table(
            ["Ticker", "Headline", "Sentiment", "Source", "Date"],
            news_rows,
            col_widths=[25, 70, 30, 35, 30],
        )

    return report.get_bytes()
