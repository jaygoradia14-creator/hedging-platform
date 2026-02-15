# REFLECT Log - Represent -> Implement Iterations

## Iteration 1: Single-Page to Multi-Page Architecture

### Represent
The initial `correlation_crash_course.py` was a single-page Streamlit app focused solely on correlation spikes. The HTML `index.html` had 5 pages of richer analysis (stress scenarios, portfolio management, regime detection) but used simulated data and Chart.js.

**Gap identified**: The Streamlit app needed to match the HTML version's breadth while using real computed analytics instead of simulated data.

### Implement
- Created `streamlit_app.py` as a multi-page entry point
- Built 6 separate page files under `pages/`
- Each page imports from shared `core/` and `risk/` modules

### Pivot
Changed from mirroring the HTML's page structure exactly to organizing by analytical concept (Dashboard, Correlation, Regime, Hedge Impact, Risk Metrics, Stress Scenarios) - better for progressive disclosure.

---

## Iteration 2: Duplicated Functions to Shared Modules

### Represent
`correlation_crash_course.py` duplicated functions already in `core/data_fetch.py` and `risk/correlation.py` (e.g., `fetch_prices`, `calculate_returns`, `calculate_tail_correlation`). This violated DRY and made maintenance harder.

### Implement
- `pages/2_Correlation_Analysis.py` imports exclusively from `core/` and `risk/`
- Removed all inline data functions from page files
- Original `correlation_crash_course.py` kept as deprecated reference

### Result
Zero function duplication across pages. Single source of truth for all analytics.

---

## Iteration 3: Page Chat to Sidebar Chat

### Represent
Initially considered a dedicated chat page (`pages/7_Chat.py`). Problem: navigating to the chat page loses context of which analysis the user was viewing.

### Implement
- Embedded chat in sidebar using `st.chat_input` + `st.chat_message`
- Chat persists across all page navigations via `st.session_state.chat_history`
- Context builders inject current portfolio state and analysis results into system prompt

### Result
Users can ask questions about any visualization without leaving the page. The LLM always has access to the most recent analysis context.

---

## Iteration 4: Simulated Data (HTML) to Real Analytics (Streamlit)

### Represent
The HTML version used hardcoded/simulated data for all visualizations. Looked impressive but couldn't respond to user inputs or real market conditions.

### Implement
- All analytics computed from real yfinance data
- Monte Carlo uses actual portfolio covariance structure
- Stress scenarios modify the real covariance matrix (correlation shock, vol spike, etc.)
- Regime detection runs on actual rolling volatility and correlation

### Result
Every number in the app is computed from real market data. Stress scenarios use the actual portfolio's statistical properties as the baseline.

---

## Iteration 5: Test Infrastructure

### Represent
No tests existed. Needed comprehensive coverage without network dependencies for CI reliability.

### Implement
- Created `tests/conftest.py` with seeded synthetic price data (5 assets, 504 days)
- Synthetic data preserves realistic properties: correlated returns via Cholesky decomposition, realistic drift and volatility
- 52+ test cases across 8 files covering all core, risk, and chat modules

### Result
All tests deterministic, zero network calls, CI-ready. Coverage exceeds 70% threshold.
