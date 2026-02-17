"""
Shared Zerodha Kite-inspired styling for all pages.
"""

# Zerodha color palette
BLUE = "#387ed1"
GREEN = "#00b386"
RED = "#d43725"
ORANGE = "#f5a623"
PURPLE = "#7c3aed"
CYAN = "#06b6d4"
PINK = "#ec4899"
LIME = "#84cc16"

COLORS = [BLUE, GREEN, RED, ORANGE, PURPLE, CYAN, PINK, LIME]

REGIME_COLORS = {
    "Low Volatility": GREEN,
    "Normal": BLUE,
    "High Volatility": ORANGE,
    "Crisis": RED,
}

# Plotly layout defaults (Zerodha light theme)
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, -apple-system, sans-serif", color="#333", size=12),
    margin=dict(l=50, r=20, t=10, b=40),
    xaxis=dict(gridcolor="#f0f0f0", zerolinecolor="#e0e0e0"),
    yaxis=dict(gridcolor="#f0f0f0", zerolinecolor="#e0e0e0"),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
        font=dict(size=11),
    ),
)


def kite_layout(height=380, **overrides):
    """Return a Plotly layout dict in Zerodha Kite style."""
    layout = {**PLOTLY_LAYOUT, "height": height}
    layout.update(overrides)
    return layout


def heatmap_layout(height=350):
    """Plotly layout for correlation heatmaps."""
    return dict(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#333", size=12),
        margin=dict(l=60, r=60, t=10, b=60),
    )


PAGE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .stApp { background-color: #ffffff; }
    .stApp h1 { display: none; }
    .stApp h2, .stApp h3 {
        color: #44475b; font-weight: 600; font-size: 0.85rem;
        text-transform: uppercase; letter-spacing: 0.05em;
        border-bottom: 1px solid #e8e8e8; padding-bottom: 0.5rem; margin-top: 2rem;
    }
    [data-testid="stMetric"] {
        background: #fff; border: 1px solid #e8e8e8;
        border-radius: 8px; padding: 1rem 1.2rem;
    }
    [data-testid="stMetric"] label {
        color: #8b8b8b !important; font-size: 0.7rem !important;
        text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600 !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #44475b !important; font-size: 1.4rem !important; font-weight: 600 !important;
    }
    .muted { color: #8b8b8b; font-size: 0.8rem; }
    .profit { color: #00b386; font-weight: 600; }
    .loss { color: #eb5b3c; font-weight: 600; }
    .page-header {
        font-size: 0.9rem; font-weight: 600; color: #44475b;
        text-transform: uppercase; letter-spacing: 0.06em;
        border-bottom: 2px solid #5367ff; padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: #ffffff; border-bottom: 1px solid #e8e8e8;
    }

    /* Groww-style sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e8e8e8;
        box-shadow: 2px 0 12px rgba(0,0,0,0.06);
    }

    /* Hamburger button - always visible */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        top: 0.5rem !important; left: 0.5rem !important; z-index: 999 !important;
        display: block !important; visibility: visible !important;
    }
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button,
    button[kind="header"] {
        background: #ffffff !important;
        border: 1px solid #e0e4eb !important;
        border-radius: 10px !important;
        padding: 6px 8px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        visibility: visible !important;
        display: flex !important;
    }
    [data-testid="stSidebarCollapsedControl"] button:hover,
    [data-testid="collapsedControl"] button:hover,
    button[kind="header"]:hover {
        background: #f0f7ff !important;
        border-color: #5367ff !important;
    }
    [data-testid="stSidebarCollapsedControl"] button svg,
    [data-testid="collapsedControl"] button svg,
    button[kind="header"] svg {
        stroke: #5367ff !important;
        width: 20px !important; height: 20px !important;
    }
    [data-testid="stSidebarCollapseButton"] button {
        color: #8b8b8b !important;
        background: transparent !important;
        border: none !important;
    }

    /* Sidebar nav links */
    [data-testid="stSidebarNav"] {
        padding-top: 0.5rem;
        border-bottom: 1px solid #eef0f4;
        padding-bottom: 0.5rem;
    }
    [data-testid="stSidebarNav"] li { margin: 2px 8px; }
    [data-testid="stSidebarNav"] a {
        color: #44475b !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 0.8rem !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stSidebarNav"] a span {
        color: #44475b !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: #f0f7ff !important;
        color: #5367ff !important;
    }
    [data-testid="stSidebarNav"] a:hover span {
        color: #5367ff !important;
    }
    [data-testid="stSidebarNav"] a[aria-selected="true"] {
        background: #f0f7ff !important;
        color: #5367ff !important;
        font-weight: 600 !important;
        border-left: 3px solid #5367ff !important;
    }
    [data-testid="stSidebarNav"] a[aria-selected="true"] span {
        color: #5367ff !important;
    }

    /* Mobile */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }
        .page-header { font-size: 0.8rem; margin-bottom: 1rem; }
        [data-testid="stMetric"] { padding: 0.6rem 0.8rem; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }
        [data-testid="stMetric"] label { font-size: 0.6rem !important; }
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
        [data-testid="stHorizontalBlock"] > div {
            flex: 1 1 100% !important; min-width: 100% !important;
        }
        [data-testid="stDataFrame"] { overflow-x: auto; }
        .stApp h2, .stApp h3 { font-size: 0.75rem; margin-top: 1.5rem; }
        .js-plotly-plot { width: 100% !important; }
        .muted { font-size: 0.7rem; }
    }
    @media (max-width: 480px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        .page-header { font-size: 0.75rem; }
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 0.95rem !important;
        }
    }
</style>
"""


def apply_page_style():
    """Inject page-level CSS."""
    import streamlit as st
    st.markdown(PAGE_CSS, unsafe_allow_html=True)


def page_header(title: str):
    """Render a Kite-style page header."""
    import streamlit as st
    apply_page_style()
    st.markdown(f'<div class="page-header">{title}</div>', unsafe_allow_html=True)
