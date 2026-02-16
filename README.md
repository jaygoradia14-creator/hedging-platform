# Hedging Platform

[![CI](https://github.com/jaygoradia14-creator/hedging-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/jaygoradia14-creator/hedging-platform/actions/workflows/ci.yml)

**[Live App](https://jaygoradia14-creator-hedging-platform.streamlit.app)** | **[GitHub Pages](https://jaygoradia14-creator.github.io/hedging-platform/)**

**Portfolio risk analysis and hedging effectiveness platform.**

Analyzes how portfolio correlations spike during market crashes, detects market regimes, computes VaR/CVaR with Monte Carlo simulation, and evaluates hedging strategies - with an AI-powered chat advisor.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Features

### 7 Analysis Pages
1. **Dashboard** - Portfolio overview, HHI concentration, cumulative returns
2. **Correlation Analysis** - Normal vs crash correlations, asymmetry, stability
3. **Regime Detection** - Volatility-based regime timeline, conditional heatmaps
4. **Hedge Impact** - Hedge effectiveness comparison, optimal ratio, VaR reduction
5. **Risk Metrics** - VaR/CVaR gauges, Monte Carlo fan chart, terminal distribution
6. **Stress Scenarios** - Correlation shock, vol spike, liquidity stress, combined crisis
7. **Chat Advisor** - Full-page AI chat with portfolio context panel and suggested questions

### AI Chat Advisor
- Sidebar chat that persists across all pages
- Uses OpenAI `gpt-4o-mini` with function-calling to reference real computed metrics
- Graceful fallback to rules-based responses when no API key is present

### Real Analytics
- All computations use real market data from Yahoo Finance
- Regime-aware Monte Carlo simulation with transition probabilities
- Historical, parametric, and regime-conditional VaR/CVaR

## Project Evolution

| Commit | R->I Moment |
|--------|-------------|
| Initial | Single-page correlation demo (`correlation_crash_course.py`) |
| Restructure | Multi-page architecture with shared `core/` and `risk/` modules |
| Analytics | VaR/CVaR, Monte Carlo, hedge analysis modules |
| Chat | LLM-powered sidebar advisor with function-calling |
| CI/CD | GitHub Actions, 70% coverage threshold, documentation |

## Architecture

```
streamlit_app.py          # Entry point + sidebar chat
pages/                    # 6 analysis pages (UI only)
core/                     # Data fetch, regime detection, portfolio state
risk/                     # Correlation, VaR/CVaR, Monte Carlo, hedge analysis
chat/                     # LLM chat engine with fallback
tests/                    # 69 tests, synthetic data, zero network calls
docs/                     # DRIVER, REFLECT, AI Collaboration Log
```

## Testing

```bash
pytest tests/ -v --cov=core --cov=risk --cov=chat --cov-report=term-missing
```

All tests use seeded synthetic data - no network calls, fully deterministic.

## Configuration

- **OpenAI API key** (optional): Set `OPENAI_API_KEY` in environment or `.streamlit/secrets.toml`
- **Theme**: Zerodha Kite-inspired light theme in `.streamlit/config.toml`

## Documentation

- [DRIVER Methodology](docs/DRIVER.md) - Problem discovery through review
- [REFLECT Log](docs/REFLECT.md) - Represent -> Implement iterations
- [AI Collaboration Log](docs/AI_COLLAB_LOG.md) - AI usage with prompts and reflections

## Legacy

- `correlation_crash_course.py` - Original single-page app (deprecated, kept for reference)
- `app.py` - Original entry point (deprecated, replaced by `streamlit_app.py`)
- `index.html` - GitHub Pages visualization (separate, untouched)

---

*Built to demonstrate how correlation dynamics undermine portfolio diversification during market crises.*
