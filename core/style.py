"""
Shared Wolf & Wright-inspired styling for all pages.
"""

# Color palette — Bloomberg-inspired on dark
NAVY = "#011f24"
NAVY_LIGHT = "#032b32"
CHART_BG = "#131722"
CHART_BG_CARD = "#1c2333"
BLUE = "#4d65ff"
GREEN = "#00b386"
RED = "#eb5b3c"
ORANGE = "#ff9f0a"
PURPLE = "#bf5af2"
CYAN = "#64d2ff"
PINK = "#ff6482"
LIME = "#30d158"
INDIGO = "#5e5ce6"
TEAL = "#40c8e0"

COLORS = [ORANGE, CYAN, LIME, PINK, PURPLE, TEAL, BLUE, GREEN, RED, INDIGO]

REGIME_COLORS = {
    "Low Volatility": GREEN,
    "Normal": BLUE,
    "High Volatility": ORANGE,
    "Crisis": RED,
}

# Plotly layout defaults (Bloomberg dark, clean)
PLOTLY_LAYOUT = dict(
    paper_bgcolor=CHART_BG,
    plot_bgcolor=CHART_BG,
    font=dict(family="Inter, -apple-system, sans-serif", color="#d1d4dc", size=12),
    margin=dict(l=50, r=16, t=10, b=30),
    xaxis=dict(
        showgrid=False,
        showline=False,
        zeroline=False,
        tickfont=dict(size=10, color="#6b7a8d"),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.06)",
        showline=False,
        zeroline=False,
        tickfont=dict(size=10, color="#6b7a8d"),
    ),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
        font=dict(size=11, family="Inter, sans-serif", color="#d1d4dc"),
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)",
    ),
    hoverlabel=dict(
        bgcolor="#1c2333",
        bordercolor="#2d3548",
        font=dict(size=11, color="#ffffff", family="Inter, sans-serif"),
    ),
)


def color_with_alpha(hex_color, alpha=0.10):
    """Convert a hex color to rgba string with the given alpha."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return f"rgba({r},{g},{b},{alpha})"


def kite_layout(height=380, **overrides):
    """Return a Plotly layout dict in Wolf & Wright style."""
    layout = {**PLOTLY_LAYOUT, "height": height}
    layout.update(overrides)
    return layout


def heatmap_layout(height=350):
    """Plotly layout for correlation heatmaps."""
    return dict(
        height=height,
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        font=dict(family="Inter, -apple-system, sans-serif", color="#d1d4dc", size=12),
        margin=dict(l=60, r=60, t=15, b=60),
        hoverlabel=dict(
            bgcolor="#1c2333",
            bordercolor="#2d3548",
            font=dict(size=11, color="#ffffff", family="Inter, sans-serif"),
        ),
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
        font-family: 'Inter', sans-serif;
        color: #011f24; font-weight: 600; font-size: 0.85rem;
        text-transform: uppercase; letter-spacing: 0.05em;
        border-bottom: 1px solid #e2e5ea; padding-bottom: 0.5rem; margin-top: 2rem;
    }
    [data-testid="stMetric"] {
        background: #fff; border: 1px solid #e2e5ea;
        border-radius: 10px; padding: 1.2rem 1rem;
        text-align: center;
        transition: border-color 0.4s ease, box-shadow 0.4s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: #4d65ff;
        box-shadow: 0 2px 12px rgba(77,101,255,0.10);
    }
    [data-testid="stMetric"] > div {
        display: flex; flex-direction: column; align-items: center;
    }
    [data-testid="stMetric"] label {
        font-family: 'Inter', sans-serif;
        color: #6b7280 !important; font-size: 0.68rem !important;
        text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600 !important;
        text-align: center !important; width: 100%;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #011f24 !important; font-size: 1.5rem !important; font-weight: 700 !important;
        text-align: center !important; width: 100%;
    }

    /* Styled tables */
    .styled-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border: 1px solid #e2e5ea;
        border-radius: 10px;
        overflow: hidden;
        font-size: 0.82rem;
    }
    .styled-table thead th {
        background: #f4f5f7;
        color: #6b7280;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 10px 12px;
        text-align: center;
        border-bottom: 2px solid #e2e5ea;
        white-space: nowrap;
    }
    .styled-table tbody td {
        padding: 9px 12px;
        text-align: center;
        color: #011f24;
        border-bottom: 1px solid #f0f0f0;
        white-space: nowrap;
    }
    .styled-table tbody tr:last-child td {
        border-bottom: none;
    }
    .styled-table tbody tr:hover {
        background: #f0f4f8;
    }
    .styled-table .ticker-cell {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #4d65ff;
        text-align: left;
    }
    .styled-table .sector-cell {
        text-align: left;
        color: #6b7280;
        font-size: 0.75rem;
    }
    .styled-table .positive { color: #00b386; font-weight: 600; }
    .styled-table .negative { color: #eb5b3c; font-weight: 600; }
    .styled-table .na-cell { color: #c0c0c0; }

    /* Dataframe overrides */
    [data-testid="stDataFrame"] {
        border: 1px solid #e2e5ea;
        border-radius: 10px;
        overflow: hidden;
    }

    .muted { color: #6b7280; font-size: 0.8rem; }
    .profit { color: #00b386; font-weight: 600; }
    .loss { color: #eb5b3c; font-weight: 600; }
    .chart-card {
        background: #131722;
        border: 1px solid #2d3548;
        border-radius: 10px;
        padding: 1rem 1rem 0.5rem 1rem;
        margin-bottom: 1rem;
    }
    .chart-card h4 {
        font-family: 'Inter', sans-serif;
        color: #d1d4dc;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin: 0 0 0.5rem 0;
    }
    .page-header {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem; font-weight: 600; color: #011f24;
        text-transform: uppercase; letter-spacing: 0.06em;
        border-bottom: 2px solid #4d65ff; padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: #ffffff; border-bottom: 1px solid #e2e5ea;
    }

    /* Dark navy sidebar */
    [data-testid="stSidebar"] {
        background-color: #011f24;
        border-right: 1px solid rgba(255,255,255,0.08);
        box-shadow: 2px 0 12px rgba(0,0,0,0.15);
    }

    /* Hamburger button - dark navy style */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        top: 0.5rem !important; left: 0.5rem !important; z-index: 999 !important;
        display: block !important; visibility: visible !important;
    }
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button,
    button[kind="header"] {
        background: #011f24 !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
        padding: 6px 8px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        visibility: visible !important;
        display: flex !important;
    }
    [data-testid="stSidebarCollapsedControl"] button:hover,
    [data-testid="collapsedControl"] button:hover,
    button[kind="header"]:hover {
        background: #032b32 !important;
        border-color: #4d65ff !important;
    }
    [data-testid="stSidebarCollapsedControl"] button svg,
    [data-testid="collapsedControl"] button svg,
    button[kind="header"] svg {
        stroke: #ffffff !important;
        width: 20px !important; height: 20px !important;
    }
    [data-testid="stSidebarCollapseButton"] button {
        color: rgba(255,255,255,0.7) !important;
        background: transparent !important;
        border: none !important;
    }

    /* Sidebar nav links - dark theme */
    [data-testid="stSidebarNav"] {
        padding-top: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        padding-bottom: 0.5rem;
    }
    [data-testid="stSidebarNav"] li { margin: 2px 8px; }
    [data-testid="stSidebarNav"] a {
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        padding: 0.55rem 0.8rem !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stSidebarNav"] a span {
        color: rgba(255,255,255,0.7) !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: rgba(255,255,255,0.08) !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebarNav"] a:hover span {
        color: #ffffff !important;
    }
    [data-testid="stSidebarNav"] a[aria-selected="true"] {
        background: rgba(77,101,255,0.15) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-left: 3px solid #4d65ff !important;
    }
    [data-testid="stSidebarNav"] a[aria-selected="true"] span {
        color: #ffffff !important;
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
    """Render a Wolf & Wright-style page header."""
    import streamlit as st
    apply_page_style()
    st.markdown(f'<div class="page-header">{title}</div>', unsafe_allow_html=True)
