"""
Rules-based signal engine for buy/sell/hold recommendations.
Generates signals from regime, technicals, portfolio composition, and holdings.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class SignalType(Enum):
    OPPORTUNITY = "Opportunity"
    CAUTION = "Caution"
    ACTION_NEEDED = "Action Needed"


@dataclass
class Signal:
    ticker: str
    signal_type: SignalType
    title: str
    description: str
    source: str
    indicator_value: Optional[float] = None
    action: str = ""
    priority: int = 5
    reasoning: str = ""  # Plain-English explanation for common investor


def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index."""
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_sma(prices, window):
    """Calculate simple moving average."""
    return prices.rolling(window=window, min_periods=window).mean()


def regime_signals(regime_df):
    """Generate signals based on market regime.

    Args:
        regime_df: DataFrame with 'regime' column from regime detector.

    Returns:
        List of Signal objects.
    """
    signals = []
    if regime_df is None or regime_df.empty:
        return signals

    current = regime_df["regime"].iloc[-1]

    if current == "Crisis":
        signals.append(Signal(
            ticker="PORTFOLIO",
            signal_type=SignalType.ACTION_NEEDED,
            title="Crisis Regime Detected",
            description=(
                "Market is in crisis mode with extreme volatility and high correlations. "
                "Diversification benefits are reduced. Consider defensive positioning."
            ),
            source="Regime",
            action="Increase defensive allocation (bonds, gold). Reduce equity exposure.",
            priority=9,
            reasoning=(
                "Markets are showing signs of extreme stress — prices are swinging wildly "
                "and stocks that normally move independently are all dropping together. "
                "During times like these, safer assets (bonds, gold) tend to protect your money better."
            ),
        ))
    elif current == "High Volatility":
        signals.append(Signal(
            ticker="PORTFOLIO",
            signal_type=SignalType.CAUTION,
            title="High Volatility Regime",
            description=(
                "Market volatility is elevated. Correlations may spike. "
                "Risk management is more important than usual."
            ),
            source="Regime",
            action="Tighten stop-losses. Monitor positions closely.",
            priority=6,
            reasoning=(
                "The market is experiencing bigger-than-usual price swings right now. "
                "Think of it like choppy waters — it's not a crisis, but you should be more "
                "careful. Keep a closer eye on your investments and avoid making big new bets "
                "until things calm down."
            ),
        ))
    elif current == "Low Volatility":
        signals.append(Signal(
            ticker="PORTFOLIO",
            signal_type=SignalType.OPPORTUNITY,
            title="Low Volatility Environment",
            description=(
                "Markets are calm with low volatility. Good conditions for "
                "building positions via dollar-cost averaging."
            ),
            source="Regime",
            action="Consider adding equity exposure. Good time to DCA.",
            priority=3,
            reasoning=(
                "Markets are calm and steady right now — prices aren't swinging much. "
                "This is often a good time to invest gradually (buying a little each week or month) "
                "because you're less likely to buy at a wild peak or valley."
            ),
        ))
    else:
        signals.append(Signal(
            ticker="PORTFOLIO",
            signal_type=SignalType.OPPORTUNITY,
            title="Normal Market Conditions",
            description="Markets operating in normal volatility range.",
            source="Regime",
            action="Maintain current allocations. Rebalance if needed.",
            priority=2,
            reasoning=(
                "Markets are behaving normally — nothing unusual happening. "
                "This is a good time to review your portfolio and make sure your investments "
                "are still aligned with your goals."
            ),
        ))

    return signals


def technical_signals(portfolio):
    """Generate technical analysis signals per ticker.

    Checks SMA crossovers (50/200 golden/death cross) and RSI levels.

    Args:
        portfolio: Portfolio object with prices and tickers.

    Returns:
        List of Signal objects.
    """
    signals = []
    if portfolio.prices is None:
        return signals

    for ticker in portfolio.tickers:
        if ticker not in portfolio.prices.columns:
            continue
        prices = portfolio.prices[ticker].dropna()
        if len(prices) < 200:
            continue

        # SMA crossover signals
        sma50 = calculate_sma(prices, 50)
        sma200 = calculate_sma(prices, 200)

        if sma50.iloc[-1] is not None and sma200.iloc[-1] is not None:
            # Check for golden/death cross in last 5 trading days
            recent_50 = sma50.iloc[-5:]
            recent_200 = sma200.iloc[-5:]
            cross_diff = recent_50 - recent_200

            if len(cross_diff.dropna()) >= 2:
                prev_diff = cross_diff.dropna().iloc[0]
                curr_diff = cross_diff.dropna().iloc[-1]

                if prev_diff <= 0 and curr_diff > 0:
                    signals.append(Signal(
                        ticker=ticker,
                        signal_type=SignalType.OPPORTUNITY,
                        title=f"{ticker}: Golden Cross",
                        description=(
                            f"50-day SMA crossed above 200-day SMA. "
                            f"Historically bullish signal."
                        ),
                        source="Technical",
                        indicator_value=float(prices.iloc[-1]),
                        action="Bullish trend confirmed. Consider adding.",
                        priority=7,
                        reasoning=(
                            f"The short-term trend for {ticker} just crossed above its long-term trend "
                            f"— this pattern (called a 'golden cross') has historically meant prices "
                            f"continue rising. It could be a good time to consider buying."
                        ),
                    ))
                elif prev_diff >= 0 and curr_diff < 0:
                    signals.append(Signal(
                        ticker=ticker,
                        signal_type=SignalType.CAUTION,
                        title=f"{ticker}: Death Cross",
                        description=(
                            f"50-day SMA crossed below 200-day SMA. "
                            f"Historically bearish signal."
                        ),
                        source="Technical",
                        indicator_value=float(prices.iloc[-1]),
                        action="Bearish trend signal. Consider reducing.",
                        priority=7,
                        reasoning=(
                            f"The short-term trend for {ticker} just dropped below its long-term trend "
                            f"— this pattern (called a 'death cross') has historically meant prices "
                            f"may keep falling. Consider reducing your position or waiting before buying more."
                        ),
                    ))

        # RSI signals
        rsi = calculate_rsi(prices)
        if rsi.iloc[-1] is not None and not np.isnan(rsi.iloc[-1]):
            rsi_val = float(rsi.iloc[-1])
            if rsi_val > 70:
                signals.append(Signal(
                    ticker=ticker,
                    signal_type=SignalType.CAUTION,
                    title=f"{ticker}: RSI Overbought ({rsi_val:.0f})",
                    description=(
                        f"RSI at {rsi_val:.1f} indicates overbought conditions. "
                        f"May see a pullback."
                    ),
                    source="Technical",
                    indicator_value=rsi_val,
                    action="Consider taking partial profits.",
                    priority=5,
                    reasoning=(
                        f"Traders are buying {ticker} aggressively right now (RSI is {rsi_val:.0f}, "
                        f"above the 70 'overheated' level). When everyone rushes to buy, prices often "
                        f"pull back. It might be wise to wait before buying more or take some profit."
                    ),
                ))
            elif rsi_val < 30:
                signals.append(Signal(
                    ticker=ticker,
                    signal_type=SignalType.OPPORTUNITY,
                    title=f"{ticker}: RSI Oversold ({rsi_val:.0f})",
                    description=(
                        f"RSI at {rsi_val:.1f} indicates oversold conditions. "
                        f"May be a buying opportunity."
                    ),
                    source="Technical",
                    indicator_value=rsi_val,
                    action="Potential buying opportunity on recovery.",
                    priority=5,
                    reasoning=(
                        f"Traders have been selling {ticker} heavily (RSI is {rsi_val:.0f}, "
                        f"below the 30 'oversold' level). When selling gets this extreme, prices "
                        f"often bounce back. If you believe in this company long-term, this could "
                        f"be a chance to buy at a discount."
                    ),
                ))

    return signals


def portfolio_signals(portfolio, regime_df):
    """Generate portfolio-level signals (concentration, risk).

    Args:
        portfolio: Portfolio object.
        regime_df: Regime detection DataFrame.

    Returns:
        List of Signal objects.
    """
    signals = []
    if portfolio.returns is None:
        return signals

    returns = portfolio.returns
    weights = portfolio.weights
    tickers = portfolio.tickers

    # Sector concentration
    try:
        from core.data_fetch import get_sectors
        sectors = get_sectors(tickers)
        sector_weights = {}
        for i, t in enumerate(tickers):
            sec = sectors[t]
            sector_weights[sec] = sector_weights.get(sec, 0) + weights[i]

        for sec, w in sector_weights.items():
            pct = w * 100
            if pct > 60:
                signals.append(Signal(
                    ticker="PORTFOLIO",
                    signal_type=SignalType.ACTION_NEEDED,
                    title=f"Extreme Sector Concentration: {sec}",
                    description=(
                        f"{sec} accounts for {pct:.0f}% of portfolio. "
                        f"Extremely high single-sector risk."
                    ),
                    source="Portfolio",
                    indicator_value=pct,
                    action=f"Diversify away from {sec}. Target <40%.",
                    priority=8,
                    reasoning=(
                        f"Over {pct:.0f}% of your money is in {sec} stocks. If something bad "
                        f"happens to that industry (regulation, recession, etc.), most of your "
                        f"portfolio would be hurt at once. Spreading your money across different "
                        f"sectors helps protect you."
                    ),
                ))
            elif pct > 40:
                signals.append(Signal(
                    ticker="PORTFOLIO",
                    signal_type=SignalType.CAUTION,
                    title=f"High Sector Concentration: {sec}",
                    description=(
                        f"{sec} accounts for {pct:.0f}% of portfolio."
                    ),
                    source="Portfolio",
                    indicator_value=pct,
                    action=f"Consider reducing {sec} exposure.",
                    priority=5,
                    reasoning=(
                        f"About {pct:.0f}% of your money is in {sec} stocks. That's a lot of eggs "
                        f"in one basket. Consider adding stocks from other industries so a downturn "
                        f"in {sec} doesn't hurt your whole portfolio."
                    ),
                ))
    except Exception:
        pass

    # HHI concentration
    hhi = float(np.sum(weights ** 2))
    if hhi > 0.5:
        signals.append(Signal(
            ticker="PORTFOLIO",
            signal_type=SignalType.ACTION_NEEDED,
            title=f"High Portfolio Concentration (HHI: {hhi:.2f})",
            description="Portfolio is highly concentrated in few assets.",
            source="Portfolio",
            indicator_value=hhi,
            action="Add more assets to improve diversification.",
            priority=7,
            reasoning=(
                "Most of your money is concentrated in just a few investments. "
                "If one of them drops sharply, your whole portfolio takes a big hit. "
                "Adding more different stocks or funds spreads your risk so no single "
                "bad event can wipe out your gains."
            ),
        ))

    # VaR check
    try:
        from risk.var_cvar import var_cvar_summary
        var_s = var_cvar_summary(returns, weights, 0.95)
        var_pct = abs(var_s.get("historical_var", 0)) * 100
        if var_pct > 5:
            signals.append(Signal(
                ticker="PORTFOLIO",
                signal_type=SignalType.ACTION_NEEDED,
                title=f"Very High VaR: {var_pct:.1f}%",
                description=(
                    f"95% daily VaR is {var_pct:.1f}%. Portfolio could lose "
                    f"this much in a single bad day."
                ),
                source="Portfolio",
                indicator_value=var_pct,
                action="Reduce risk or add hedging instruments.",
                priority=8,
                reasoning=(
                    f"Based on historical data, your portfolio could lose as much as "
                    f"{var_pct:.1f}% in a single bad day. That's higher than average. "
                    f"Consider adding safer investments like bonds or gold to cushion "
                    f"against big drops."
                ),
            ))
        elif var_pct > 3:
            signals.append(Signal(
                ticker="PORTFOLIO",
                signal_type=SignalType.CAUTION,
                title=f"Elevated VaR: {var_pct:.1f}%",
                description=f"95% daily VaR at {var_pct:.1f}% is above average.",
                source="Portfolio",
                indicator_value=var_pct,
                action="Monitor closely. Consider hedging.",
                priority=5,
                reasoning=(
                    f"Your portfolio's risk level is moderately high — it could lose "
                    f"about {var_pct:.1f}% on a bad day. That's not alarming, but worth "
                    f"keeping an eye on. Adding some bonds or gold could help smooth out "
                    f"the bumps."
                ),
            ))
    except Exception:
        pass

    # Correlation spike check
    try:
        from risk.correlation import calculate_correlation_matrix, calculate_tail_correlation
        normal_corr = calculate_correlation_matrix(returns)
        tail_corr = calculate_tail_correlation(returns)
        if len(tickers) >= 2:
            avg_normal = normal_corr.values[np.triu_indices_from(
                normal_corr.values, k=1
            )].mean()
            avg_tail = tail_corr.values[np.triu_indices_from(
                tail_corr.values, k=1
            )].mean()
            spike = avg_tail - avg_normal
            if spike > 0.2:
                signals.append(Signal(
                    ticker="PORTFOLIO",
                    signal_type=SignalType.CAUTION,
                    title="Correlation Spike in Crashes",
                    description=(
                        f"Tail correlations are {spike:.2f} higher than normal. "
                        f"Diversification weakens in crashes."
                    ),
                    source="Portfolio",
                    indicator_value=spike,
                    action="True diversifiers (gold, treasuries) may help.",
                    priority=6,
                    reasoning=(
                        "Your stocks tend to all drop together during market crashes — the "
                        "diversification you think you have disappears when you need it most. "
                        "Adding truly different assets like government bonds or gold can help "
                        "because they often go up when stocks go down."
                    ),
                ))
    except Exception:
        pass

    return signals


def holdings_signals(holdings, current_prices):
    """Generate signals based on P&L of current holdings.

    Args:
        holdings: Dict of {ticker: {"shares": float, "buy_price": float}}.
        current_prices: Dict of {ticker: current_price}.

    Returns:
        List of Signal objects.
    """
    signals = []
    if not holdings:
        return signals

    for ticker, info in holdings.items():
        cur = current_prices.get(ticker)
        if cur is None:
            continue
        cost = info["buy_price"]
        if cost <= 0:
            continue
        pnl_pct = ((cur - cost) / cost) * 100

        if pnl_pct > 50:
            signals.append(Signal(
                ticker=ticker,
                signal_type=SignalType.ACTION_NEEDED,
                title=f"{ticker}: Large Gain ({pnl_pct:+.0f}%)",
                description=(
                    f"Position up {pnl_pct:.1f}% from buy price. "
                    f"Consider locking in some profits."
                ),
                source="Holdings",
                indicator_value=pnl_pct,
                action="Take partial profit. Sell 25-50% of position.",
                priority=7,
                reasoning=(
                    f"Your {ticker} stock has grown by {pnl_pct:.0f}% since you bought it. "
                    f"That's a great return! But big gains can disappear quickly if the market "
                    f"turns. Consider selling some shares to lock in your profit — you can "
                    f"always buy back later."
                ),
            ))
        elif pnl_pct > 20:
            signals.append(Signal(
                ticker=ticker,
                signal_type=SignalType.OPPORTUNITY,
                title=f"{ticker}: Take Profit ({pnl_pct:+.0f}%)",
                description=(
                    f"Position up {pnl_pct:.1f}% — solid gain. "
                    f"Good opportunity to secure profits."
                ),
                source="Holdings",
                indicator_value=pnl_pct,
                action="Consider selling 20-30% to lock in gains.",
                priority=4,
                reasoning=(
                    f"Your {ticker} stock is up {pnl_pct:.0f}% — that's a solid gain. "
                    f"You might want to sell a portion (say 20-30%) to secure some profit "
                    f"while keeping the rest invested in case it keeps going up."
                ),
            ))
        elif pnl_pct < -15:
            signals.append(Signal(
                ticker=ticker,
                signal_type=SignalType.ACTION_NEEDED,
                title=f"{ticker}: Cut Losses ({pnl_pct:+.0f}%)",
                description=(
                    f"Position down {abs(pnl_pct):.1f}%. "
                    f"Review your thesis. Consider cutting losses."
                ),
                source="Holdings",
                indicator_value=pnl_pct,
                action="Re-evaluate thesis. Cut if fundamentals changed.",
                priority=8,
                reasoning=(
                    f"Your {ticker} stock has dropped {abs(pnl_pct):.0f}% from what you paid. "
                    f"Ask yourself: has something changed about this company? If the reason you "
                    f"bought it no longer holds, it may be better to sell now and invest elsewhere "
                    f"rather than hope for recovery."
                ),
            ))
        elif pnl_pct < -10:
            signals.append(Signal(
                ticker=ticker,
                signal_type=SignalType.CAUTION,
                title=f"{ticker}: Underwater ({pnl_pct:+.0f}%)",
                description=(
                    f"Position down {abs(pnl_pct):.1f}% from buy price."
                ),
                source="Holdings",
                indicator_value=pnl_pct,
                action="Monitor closely. Set stop-loss if not already.",
                priority=5,
                reasoning=(
                    f"Your {ticker} stock is down {abs(pnl_pct):.0f}% from your buy price. "
                    f"It's not a huge loss yet, but keep watching. Consider setting a 'stop-loss' "
                    f"— a price at which you'd automatically sell to prevent further losses."
                ),
            ))

    return signals


def generate_all_signals(portfolio, regime_df, holdings=None, current_prices=None):
    """Generate all signals and sort by priority descending.

    Args:
        portfolio: Portfolio object.
        regime_df: Regime detection DataFrame.
        holdings: Dict of holdings (optional).
        current_prices: Dict of current prices (optional).

    Returns:
        List of Signal objects sorted by priority (highest first).
    """
    all_signals = []
    all_signals.extend(regime_signals(regime_df))
    all_signals.extend(technical_signals(portfolio))
    all_signals.extend(portfolio_signals(portfolio, regime_df))
    if holdings and current_prices:
        all_signals.extend(holdings_signals(holdings, current_prices))
    all_signals.sort(key=lambda s: s.priority, reverse=True)
    return all_signals


def calculate_portfolio_health_score(signals):
    """Calculate a 0-100 portfolio health score based on signals.

    Starts at 100, deducts for negative signals, adds for positive.
    """
    score = 100
    for s in signals:
        if s.signal_type == SignalType.ACTION_NEEDED:
            score -= 15
        elif s.signal_type == SignalType.CAUTION:
            score -= 5
        elif s.signal_type == SignalType.OPPORTUNITY:
            score += 2
    return max(0, min(100, score))


def get_signal_color(signal_type):
    """Map signal type to Kite color."""
    from core.style import GREEN, ORANGE, RED
    if signal_type == SignalType.OPPORTUNITY:
        return GREEN
    elif signal_type == SignalType.CAUTION:
        return ORANGE
    elif signal_type == SignalType.ACTION_NEEDED:
        return RED
    return "#8b8b8b"
