# Correlation Crash Course

**See how diversification fails when you need it most.**

Most investors believe spreading money across different assets protects them from big losses. This tool shows the uncomfortable truth: correlations spike during crashes, exactly when you need diversification to work.

## Quick Start

```bash
# Install dependencies
pip install streamlit pandas numpy yfinance plotly

# Run the app
streamlit run correlation_crash_course.py
```

## What This Shows

Enter 2-5 stock tickers and see:

1. **Normal Correlation** - How assets move together on typical days
2. **Crash Correlation** - How assets move together during the worst 5% of market days
3. **Timeline** - Watch correlations spike during stress periods

## The Key Insight

During normal markets, a diversified portfolio of SPY (stocks), TLT (bonds), and GLD (gold) shows low correlations between assets. But during market crashes, those correlations spike toward 1.0.

This means the protection you thought you had disappears exactly when you need it most.

## Why This Matters

- **For investors**: Understanding tail correlation is essential for real risk management
- **For students**: This concept isn't taught in intro finance courses - knowing it signals depth
- **For interviews**: "Correlations spike during crashes" is a counterintuitive insight that demonstrates real market understanding

## Technical Details

- **Tail correlation**: Measured during the bottom 5% of market returns (quantile = 0.05)
- **Stress detection**: Based on rolling volatility exceeding the 80th percentile
- **Data source**: Yahoo Finance (yfinance)

## Files

```
correlation_crash_course.py  # Main application (run this)
app.py                       # Simple entry point
core/                        # Data fetching and regime detection
risk/                        # Correlation calculations
```

---

*Built to demonstrate one counterintuitive truth about markets.*
