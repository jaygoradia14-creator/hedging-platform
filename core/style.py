"""
Shared Wolf & Wright-inspired styling for all pages.
"""

# Wolf & Wright color palette
NAVY = "#011f24"
NAVY_LIGHT = "#032b32"
BLUE = "#4d65ff"
GREEN = "#00b386"
RED = "#eb5b3c"
ORANGE = "#f59e0b"
PURPLE = "#8b5cf6"
CYAN = "#06b6d4"
PINK = "#ec4899"
LIME = "#22c55e"
INDIGO = "#6366f1"
TEAL = "#14b8a6"

COLORS = [BLUE, GREEN, RED, ORANGE, PURPLE, CYAN, PINK, LIME, INDIGO, TEAL]

REGIME_COLORS = {
    "Low Volatility": GREEN,
    "Normal": BLUE,
    "High Volatility": ORANGE,
    "Crisis": RED,
}

# Plotly layout defaults (clean, modern light theme with Inconsolata)
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inconsolata, monospace", color="#011f24", size=12),
    margin=dict(l=55, r=25, t=15, b=45),
    xaxis=dict(
        gridcolor="rgba(1,31,36,0.06)",
        zerolinecolor="#e0e0e0",
        showgrid=True,
        tickfont=dict(size=10, color="#6b7280"),
        linecolor="#e2e5ea",
        linewidth=1,
    ),
    yaxis=dict(
        gridcolor="rgba(1,31,36,0.06)",
        zerolinecolor="#e0e0e0",
        showgrid=True,
        tickfont=dict(size=10, color="#6b7280"),
        linecolor="#e2e5ea",
        linewidth=1,
    ),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
        font=dict(size=11, color="#011f24"),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="rgba(0,0,0,0)",
    ),
    hoverlabel=dict(
        bgcolor="#ffffff",
        bordercolor="#e2e5ea",
        font=dict(size=12, color="#011f24", family="Inconsolata, monospace"),
    ),
)


def kite_layout(height=380, **overrides):
    """Return a Plotly layout dict in Wolf & Wright style."""
    layout = {**PLOTLY_LAYOUT, "height": height}
    layout.update(overrides)
    return layout


def heatmap_layout(height=350):
    """Plotly layout for correlation heatmaps."""
    return dict(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inconsolata, monospace", color="#011f24", size=12),
        margin=dict(l=60, r=60, t=15, b=60),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor="#e2e5ea",
            font=dict(size=12, color="#011f24"),
        ),
    )


PAGE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inconsolata:wght@400;500;600;700&family=Cardo:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .stApp { background-color: #ffffff; }
    .stApp h1 { display: none; }
    .stApp h2, .stApp h3 {
        font-family: 'Inconsolata', monospace;
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
        font-family: 'Inconsolata', monospace;
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
        font-family: 'Inconsolata', monospace;
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
        font-family: 'Inconsolata', monospace;
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
    .page-header {
        font-family: 'Inconsolata', monospace;
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
