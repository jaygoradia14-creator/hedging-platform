"""
Correlation Crash Course
========================
A focused tool showing how diversification fails during market crashes.

Run with: streamlit run app.py
Or directly: streamlit run correlation_crash_course.py
"""

import streamlit as st

st.set_page_config(
    page_title="Correlation Crash Course",
    page_icon="📉",
    layout="wide"
)

# Redirect to main application
st.markdown("""
# Correlation Crash Course

**See how diversification fails when you need it most.**

---

To run the full application:

```bash
streamlit run correlation_crash_course.py
```

Or navigate directly to the correlation analysis.
""")

# Auto-redirect using experimental rerun if we want single entry point
# For simplicity, just run: streamlit run correlation_crash_course.py
