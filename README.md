# Hedging Platform

[![CI](https://github.com/jaygoradia14-creator/hedging-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/jaygoradia14-creator/hedging-platform/actions/workflows/ci.yml)

**[Live App](https://hedging-platform-gy7wnwczncisnsbxeatg4l.streamlit.app/)** | **[GitHub Pages](https://jaygoradia14-creator.github.io/hedging-platform/)**

**Portfolio risk analysis, optimization, and hedging effectiveness platform.**

Analyzes how portfolio correlations spike during market crashes, detects market regimes, computes VaR/CVaR with Monte Carlo simulation, evaluates hedging strategies, and optimizes portfolios using Markowitz efficient frontier - with an AI-powered chat advisor.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Features

### 8 Analysis Pages
1. **Dashboard** - Portfolio overview, live prices, holdings tracker with buy/sell, cumulative returns with S&P 500 benchmark, downloadable CSV reports
2. **Correlation Analysis** - Normal vs crash correlations, asymmetry, stability
3. **Regime Detection** - Per-regime volatility timeline with dropdown, conditional heatmaps
4. **Hedge Impact** - Hedge effectiveness comparison, optimal ratio, VaR reduction
5. **Risk Metrics** - VaR/CVaR gauges, Monte Carlo fan chart, terminal distribution
6. **Stress Scenarios** - Correlation shock, vol spike, liquidity stress, combined crisis
7. **Chat Advisor** - General-purpose AI chat (OpenAI/Gemini) with portfolio context
8. **Efficient Frontier** - Markowitz mean-variance optimization, min variance & max Sharpe portfolios

### Portfolio Tracker
- Add/sell stocks with live price lookup
- P&L tracking with color-coded profit/loss per position
- Total invested, current value, and portfolio-level P&L metrics

### AI Chat Advisor
- Supports OpenAI (`gpt-4o-mini`) and Google Gemini (`gemini-2.0-flash`)
- Function-calling to reference real computed portfolio metrics
- In-app API key input or persistent Streamlit secrets
- Graceful fallback to rules-based responses when no API key is present

### Efficient Frontier
- Random portfolio scatter plot colored by Sharpe ratio
- Efficient frontier curve with min variance and max Sharpe portfolios
- Side-by-side weight comparison (current vs optimal allocations)
- Adjustable risk-free rate parameter

### Real Analytics
- All computations use real market data from Yahoo Finance
- Regime-aware Monte Carlo simulation with transition probabilities
- Historical, parametric, and regime-conditional VaR/CVaR
- S&P 500 benchmark comparison on cumulative returns

## Architecture

```
streamlit_app.py          # Entry point, dashboard, holdings tracker
pages/                    # 7 analysis pages (UI only)
core/                     # Data fetch, regime detection, portfolio state
risk/                     # Correlation, VaR/CVaR, Monte Carlo, hedge analysis, optimizer
chat/                     # LLM chat engine (OpenAI + Gemini) with fallback
tests/                    # 164 tests, 78% coverage, synthetic data, zero network calls
docs/                     # DRIVER, REFLECT, AI Collaboration Log
```

## Testing

```bash
pytest tests/ -v --cov=core --cov=risk --cov=chat --cov-report=term-missing
```

- **164 tests**, **78% code coverage**
- All tests use seeded synthetic data - no network calls, fully deterministic
- CI runs on Python 3.11 and 3.12 via GitHub Actions

## Configuration

- **API Keys** (optional): Paste OpenAI or Gemini key in-app, or set `OPENAI_API_KEY` / `GEMINI_API_KEY` in `.streamlit/secrets.toml`
- **Theme**: Zerodha Kite-inspired light theme in `.streamlit/config.toml`

## Documentation

- [DRIVER Methodology](docs/DRIVER.md) - Problem discovery through review
- [REFLECT Log](docs/REFLECT.md) - Represent -> Implement iterations
- [AI Collaboration Log](docs/AI_COLLAB_LOG.md) - AI usage with prompts and reflections

## Project Evolution

| Phase | Description |
|-------|-------------|
| Initial | Single-page correlation demo |
| Restructure | Multi-page architecture with shared `core/` and `risk/` modules |
| Analytics | VaR/CVaR, Monte Carlo, hedge analysis, stress scenarios |
| Chat | LLM-powered advisor with OpenAI function-calling + Gemini |
| Holdings | Portfolio tracker with buy/sell, live P&L, CSV export |
| Optimization | Markowitz efficient frontier, min variance, max Sharpe |
| CI/CD | GitHub Actions, 78% coverage, flake8 linting |

---

*Built to demonstrate how correlation dynamics undermine portfolio diversification during market crises.*
