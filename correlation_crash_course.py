"""
Correlation Crash Course
========================
See how diversification fails when you need it most.

A single-page tool that shows how correlations spike during market crashes -
exactly when you need diversification to work.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import List, Tuple
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Correlation Crash Course",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for clean, focused design
st.markdown("""
<style>
    /* Hide sidebar by default */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Main header styling */
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .tagline {
        font-size: 1.3rem;
        color: #e94560;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }

    .insight-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #e94560;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .insight-title {
        color: #e94560;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .insight-text {
        color: #ffffff;
        font-size: 1rem;
        line-height: 1.6;
    }

    .correlation-high { color: #e74c3c; font-weight: bold; }
    .correlation-low { color: #4ecca3; font-weight: bold; }

    .metric-container {
        background: #16213e;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }

    .metric-label {
        color: #a0a0a0;
        font-size: 0.9rem;
    }

    .metric-value {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: bold;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# DATA FUNCTIONS
# =============================================================================

@st.cache_data(ttl=3600)
def fetch_prices(tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch adjusted close prices for multiple assets."""
    import yfinance as yf

    data = yf.download(tickers, start=start_date, end=end_date, progress=False)

    if isinstance(data.columns, pd.MultiIndex):
        prices = data['Adj Close'] if 'Adj Close' in data.columns.get_level_values(0) else data['Close']
    else:
        prices = data[['Adj Close']] if 'Adj Close' in data.columns else data[['Close']]
        prices.columns = tickers

    if prices.index.tz is not None:
        prices.index = prices.index.tz_localize(None)

    return prices.dropna()


def calculate_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate log returns from prices."""
    return np.log(prices / prices.shift(1)).dropna()


def calculate_normal_correlation(returns: pd.DataFrame) -> pd.DataFrame:
    """Standard Pearson correlation."""
    return returns.corr()


def calculate_tail_correlation(returns: pd.DataFrame, quantile: float = 0.05) -> pd.DataFrame:
    """
    Correlation during the worst market days (bottom 5%).
    This is when diversification matters most - and usually fails.
    """
    market_col = returns.columns[0]  # Use first ticker as market proxy
    threshold = returns[market_col].quantile(quantile)
    tail_mask = returns[market_col] <= threshold

    tail_returns = returns[tail_mask]
    if len(tail_returns) < 10:
        return calculate_normal_correlation(returns)

    return tail_returns.corr()


def calculate_rolling_correlation(returns: pd.DataFrame, window: int = 63) -> pd.Series:
    """Calculate rolling average pairwise correlation."""
    rolling_corr = returns.rolling(window=window).corr()
    avg_corr = []
    dates = returns.index[window-1:]

    for date in dates:
        try:
            corr_matrix = rolling_corr.loc[date]
            if isinstance(corr_matrix, pd.DataFrame):
                mask = np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
                upper_triangle = corr_matrix.values[mask]
                avg_corr.append(np.nanmean(upper_triangle))
            else:
                avg_corr.append(np.nan)
        except:
            avg_corr.append(np.nan)

    return pd.Series(avg_corr, index=dates, name='avg_correlation')


def detect_stress_periods(returns: pd.DataFrame, vol_window: int = 21) -> pd.Series:
    """Identify stress periods based on volatility spikes."""
    rolling_vol = returns.rolling(window=vol_window).std() * np.sqrt(252)
    avg_vol = rolling_vol.mean(axis=1)

    # Stress = top 20% volatility days
    threshold = avg_vol.quantile(0.80)
    is_stress = avg_vol > threshold

    return is_stress


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    # Header
    st.markdown('<h1 class="main-title">Correlation Crash Course</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">See how diversification fails when you need it most.</p>', unsafe_allow_html=True)

    # Input section
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        # Ticker input
        default_tickers = "SPY, TLT, GLD"
        ticker_input = st.text_input(
            "Enter 2-5 tickers (comma-separated)",
            value=default_tickers,
            help="Example: SPY, TLT, GLD, QQQ"
        )

        tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

        if len(tickers) < 2:
            st.error("Please enter at least 2 tickers.")
            return
        if len(tickers) > 5:
            st.warning("Using first 5 tickers only.")
            tickers = tickers[:5]

    with col2:
        # Time period
        lookback_years = st.selectbox(
            "Historical period",
            options=[3, 5, 10],
            index=0,
            format_func=lambda x: f"{x} years"
        )

    with col3:
        st.write("")  # Spacer
        st.write("")
        analyze_button = st.button("Analyze", type="primary", use_container_width=True)

    # Default: auto-analyze on load
    if not analyze_button and 'analyzed' not in st.session_state:
        st.session_state.analyzed = True
        analyze_button = True

    if not analyze_button:
        return

    # Fetch data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * lookback_years)

    with st.spinner(f"Fetching data for {', '.join(tickers)}..."):
        try:
            prices = fetch_prices(tickers, str(start_date.date()), str(end_date.date()))
            returns = calculate_returns(prices)

            # Check we have enough data
            if len(returns) < 100:
                st.error("Not enough historical data. Try different tickers or a shorter period.")
                return

        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return

    # ==========================================================================
    # THE KEY INSIGHT
    # ==========================================================================

    st.markdown("---")

    # Calculate correlations
    normal_corr = calculate_normal_correlation(returns)
    tail_corr = calculate_tail_correlation(returns, quantile=0.05)

    # Get the comparison (using first two tickers as primary example)
    t1, t2 = tickers[0], tickers[1]
    normal_val = normal_corr.loc[t1, t2]
    tail_val = tail_corr.loc[t1, t2]
    correlation_spike = tail_val - normal_val

    # Key insight box
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">The Key Insight</div>
        <div class="insight-text">
            During normal markets, <strong>{t1}</strong> and <strong>{t2}</strong> have a correlation of
            <span class="correlation-low">{normal_val:.2f}</span>.
            But during the <em>worst 5% of market days</em>, that correlation jumps to
            <span class="correlation-high">{tail_val:.2f}</span>.
            <br><br>
            <strong>That's a {abs(correlation_spike):.0%} spike in correlation - exactly when you needed diversification to protect you.</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================================================
    # CORRELATION COMPARISON
    # ==========================================================================

    st.markdown("### Normal vs Crash Correlations")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Normal Market Days**")
        st.markdown("*How assets move together on typical days*")

        # Heatmap for normal correlation
        fig_normal = go.Figure(data=go.Heatmap(
            z=normal_corr.values,
            x=normal_corr.columns,
            y=normal_corr.index,
            colorscale='RdBu_r',
            zmin=-1, zmax=1,
            text=np.round(normal_corr.values, 2),
            texttemplate="%{text}",
            textfont={"size": 14},
            hovertemplate="<b>%{x}</b> & <b>%{y}</b><br>Correlation: %{z:.2f}<extra></extra>"
        ))

        fig_normal.update_layout(
            height=300,
            template='plotly_dark',
            margin=dict(l=50, r=50, t=30, b=50),
            xaxis_title="",
            yaxis_title=""
        )

        st.plotly_chart(fig_normal, use_container_width=True)

    with col2:
        st.markdown("**During Crashes (Worst 5% of Days)**")
        st.markdown("*How assets move together when markets plunge*")

        # Heatmap for tail correlation
        fig_tail = go.Figure(data=go.Heatmap(
            z=tail_corr.values,
            x=tail_corr.columns,
            y=tail_corr.index,
            colorscale='RdBu_r',
            zmin=-1, zmax=1,
            text=np.round(tail_corr.values, 2),
            texttemplate="%{text}",
            textfont={"size": 14},
            hovertemplate="<b>%{x}</b> & <b>%{y}</b><br>Tail Correlation: %{z:.2f}<extra></extra>"
        ))

        fig_tail.update_layout(
            height=300,
            template='plotly_dark',
            margin=dict(l=50, r=50, t=30, b=50),
            xaxis_title="",
            yaxis_title=""
        )

        st.plotly_chart(fig_tail, use_container_width=True)

    # ==========================================================================
    # CORRELATION TIMELINE
    # ==========================================================================

    st.markdown("### Correlation Over Time")
    st.markdown("*Watch correlations spike during stress periods (shaded red)*")

    # Calculate rolling correlation and stress periods
    rolling_corr = calculate_rolling_correlation(returns, window=63)
    is_stress = detect_stress_periods(returns, vol_window=21)

    # Align indices
    common_idx = rolling_corr.index.intersection(is_stress.index)
    rolling_corr = rolling_corr.loc[common_idx]
    is_stress = is_stress.loc[common_idx]

    # Create timeline figure
    fig_timeline = go.Figure()

    # Add stress period shading
    stress_starts = []
    stress_ends = []
    in_stress = False

    for i, (date, stressed) in enumerate(is_stress.items()):
        if stressed and not in_stress:
            stress_starts.append(date)
            in_stress = True
        elif not stressed and in_stress:
            stress_ends.append(date)
            in_stress = False

    if in_stress:
        stress_ends.append(is_stress.index[-1])

    for start, end in zip(stress_starts, stress_ends):
        fig_timeline.add_vrect(
            x0=start, x1=end,
            fillcolor="rgba(231, 76, 60, 0.2)",
            layer="below",
            line_width=0
        )

    # Add correlation line
    fig_timeline.add_trace(go.Scatter(
        x=rolling_corr.index,
        y=rolling_corr.values,
        mode='lines',
        name='Average Correlation',
        line=dict(color='#3498db', width=2),
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Correlation: %{y:.2f}<extra></extra>"
    ))

    # Add threshold line
    fig_timeline.add_hline(
        y=0.6,
        line_dash="dash",
        line_color="#e94560",
        annotation_text="Stress Threshold (0.6)",
        annotation_position="top right"
    )

    fig_timeline.update_layout(
        height=400,
        template='plotly_dark',
        showlegend=False,
        margin=dict(l=50, r=50, t=30, b=50),
        xaxis_title="",
        yaxis_title="Average Pairwise Correlation",
        yaxis=dict(range=[-0.2, 1.0])
    )

    st.plotly_chart(fig_timeline, use_container_width=True)

    # ==========================================================================
    # THE TAKEAWAY
    # ==========================================================================

    st.markdown("---")

    # Calculate summary stats
    avg_normal_corr = np.mean([normal_corr.iloc[i, j]
                               for i in range(len(tickers))
                               for j in range(i+1, len(tickers))])

    avg_tail_corr = np.mean([tail_corr.iloc[i, j]
                             for i in range(len(tickers))
                             for j in range(i+1, len(tickers))])

    spike_pct = (avg_tail_corr - avg_normal_corr) / max(abs(avg_normal_corr), 0.01) * 100

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">Normal Correlation</div>
            <div class="metric-value" style="color: #4ecca3;">{:.2f}</div>
        </div>
        """.format(avg_normal_corr), unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">Crash Correlation</div>
            <div class="metric-value" style="color: #e74c3c;">{:.2f}</div>
        </div>
        """.format(avg_tail_corr), unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">Correlation Spike</div>
            <div class="metric-value" style="color: #f39c12;">+{:.0f}%</div>
        </div>
        """.format(abs(spike_pct)), unsafe_allow_html=True)

    st.markdown("")

    st.markdown("""
    <div class="insight-box">
        <div class="insight-title">Why This Matters</div>
        <div class="insight-text">
            Most investors believe that spreading money across different assets protects them from big losses.
            But this data shows the uncomfortable truth: <strong>correlations spike during crashes</strong>.
            <br><br>
            When stocks fall hard, most "diversifying" assets fall with them. The protection you thought you had
            disappears exactly when you need it most.
            <br><br>
            <em>This is why understanding tail correlation - not just normal correlation -
            is essential for anyone serious about risk management.</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p><strong>Correlation Crash Course</strong></p>
        <p>Built to demonstrate one counterintuitive truth about markets.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
