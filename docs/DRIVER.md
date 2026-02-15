# DRIVER Methodology - Hedging Platform

## Discover

### Problem Statement
Portfolio diversification breaks down during market crises. Standard correlation analysis gives investors a false sense of security because it measures average behavior, not crisis behavior. When stocks crash, correlations spike - and the "diversified" portfolio that looked safe loses money across all positions simultaneously.

### Key Questions
- How much do correlations increase during market crashes vs normal periods?
- Can we detect regime shifts before they cause portfolio damage?
- Which hedging instruments actually provide protection during crises?
- How can we quantify the gap between perceived and actual portfolio risk?

### Stakeholders
- Individual investors building multi-asset portfolios
- Risk managers evaluating hedging strategies
- Finance students learning about tail risk and correlation dynamics

---

## Represent

### Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend | Streamlit multi-page | Rapid prototyping, interactive widgets, free cloud hosting |
| Data source | yfinance API | Free, reliable, covers all major ETFs and equities |
| Risk engine | Custom Python modules | Full control over VaR, CVaR, Monte Carlo implementations |
| Chat interface | OpenAI gpt-4o-mini + fallback | Cost-efficient, graceful degradation without API key |
| Deployment | Streamlit Cloud | Auto-deploys from GitHub main branch |

### Data Flow
```
yfinance API
  -> core/data_fetch.py (prices, returns)
    -> core/regime_detector.py (regime classification)
    -> risk/correlation.py (normal, tail, asymmetric correlations)
    -> risk/var_cvar.py (VaR, CVaR, regime-conditional)
    -> risk/monte_carlo.py (standard + regime-aware simulations)
    -> risk/hedge_analysis.py (effectiveness, optimal ratio, VaR impact)
      -> Streamlit pages (visualization)
      -> chat/ module (LLM-powered explanations)
```

### Module Separation
- **core/**: Data fetching, regime detection, portfolio state management
- **risk/**: All analytics (correlation, VaR, Monte Carlo, hedging)
- **chat/**: LLM integration with graceful fallback
- **pages/**: UI only - no computation logic, imports from core/ and risk/

---

## Implement

### Phase 1: Foundation
- Created `core/portfolio.py` with Portfolio dataclass and session state management
- Built `streamlit_app.py` as multi-page entry point with sidebar chat
- Migrated correlation analysis from single-page app to `pages/2_Correlation_Analysis.py`
- Added regime detection page with timeline and conditional heatmaps
- Established test infrastructure with synthetic data fixtures (seeded, deterministic)

### Phase 2: New Analytics
- Implemented VaR/CVaR module with historical, parametric, and regime-conditional methods
- Built Monte Carlo engine with standard (Cholesky) and regime-aware simulation
- Created hedge analysis module: effectiveness metrics, optimal ratio (OLS), VaR impact
- Added stress scenario page with 4 scenarios: correlation shock, vol spike, liquidity, combined

### Phase 3: Chat Interface
- Designed system prompt with portfolio and analysis context injection
- Implemented OpenAI function-calling tools (4 tools routing to real computations)
- Built rules-based fallback for operation without API key
- Integrated chat into sidebar for persistence across all pages

### Phase 4: CI/CD + Documentation
- GitHub Actions CI: Python 3.11+3.12 matrix, flake8 lint, pytest with 70% coverage threshold
- DRIVER, REFLECT, and AI Collaboration Log documentation

---

## Validate

### Test Strategy
- **52+ test cases** across 8 test files
- **Zero network calls**: all tests use seeded synthetic data (504 trading days, 5 assets)
- **Deterministic**: `np.random.seed(42)` ensures reproducibility
- **Coverage target**: >70% across core/, risk/, and chat/ modules

### Acceptance Criteria
1. All 6 pages render without errors when data is loaded
2. Chat responds meaningfully in both API and fallback modes
3. VaR properties hold: CVaR >= VaR, higher confidence -> higher VaR
4. Monte Carlo simulations are deterministic with seed
5. Hedge analysis correctly identifies negative-correlation assets as better hedges
6. CI pipeline passes on push/PR to main

---

## Evolve

### Future Enhancements
- **Options pricing**: Add Black-Scholes for put option hedging cost analysis
- **Real-time data**: WebSocket integration for intraday regime detection
- **Portfolio optimization**: Mean-variance efficient frontier with regime constraints
- **Custom scenarios**: User-defined stress parameter inputs
- **Historical backtesting**: Walk-forward validation of hedge recommendations

---

## Review

### Lessons Learned
1. **Tail correlation > normal correlation** for risk management decisions
2. **Regime detection** provides actionable context that static metrics miss
3. **Sidebar chat** is better UX than a separate chat page (preserves analysis context)
4. **Synthetic test data** eliminates flaky tests while preserving statistical properties
5. **Function-calling** enables LLM to surface real computations, not hallucinated numbers
