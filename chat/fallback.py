"""
Rules-based fallback chat — general financial advisor + portfolio analytics.
Keyword matching routes to educational content and context-aware portfolio responses.
"""


# ---------------------------------------------------------------------------
# General finance knowledge base (no portfolio data needed)
# ---------------------------------------------------------------------------
GENERAL_KNOWLEDGE = {
    # --- Stocks & Equities ---
    "stock": (
        "**What is a Stock?**\n\n"
        "A stock (or equity/share) represents ownership in a company. When you buy a stock, "
        "you own a fraction of that company and are entitled to a share of its profits (dividends) "
        "and assets.\n\n"
        "- **Common stock**: Voting rights + dividends (variable)\n"
        "- **Preferred stock**: Fixed dividends, no voting, priority in liquidation\n"
        "- Stocks trade on exchanges like NYSE, NASDAQ\n"
        "- Price is driven by supply/demand, earnings, and market sentiment\n"
        "- Long-term average return of the S&P 500: ~10% annually"
    ),
    "bond": (
        "**What is a Bond?**\n\n"
        "A bond is a fixed-income debt instrument. When you buy a bond, you're lending money to "
        "the issuer (government or corporation) in exchange for periodic interest payments (coupon) "
        "and return of principal at maturity.\n\n"
        "- **Government bonds** (Treasuries): Safest, lower yield — TLT, IEF, SHY\n"
        "- **Corporate bonds**: Higher yield, more risk — LQD (investment grade), HYG (high yield)\n"
        "- **Bond prices move inversely to interest rates**\n"
        "- Duration measures sensitivity to rate changes\n"
        "- Bonds typically act as a hedge against equity risk"
    ),
    "etf": (
        "**What is an ETF (Exchange-Traded Fund)?**\n\n"
        "An ETF is a basket of securities that trades on an exchange like a stock. It tracks an "
        "index, sector, commodity, or strategy.\n\n"
        "- **SPY/VOO**: Track the S&P 500\n"
        "- **QQQ**: Tracks NASDAQ-100 (tech-heavy)\n"
        "- **GLD**: Tracks gold prices\n"
        "- **TLT**: Tracks long-term US Treasuries\n"
        "- Lower fees than mutual funds, highly liquid, tax-efficient\n"
        "- Great for diversification — one ETF can hold hundreds of stocks"
    ),
    "mutual fund": (
        "**What is a Mutual Fund?**\n\n"
        "A mutual fund pools money from many investors to buy a diversified portfolio of stocks, "
        "bonds, or other assets, managed by a professional fund manager.\n\n"
        "- **Actively managed**: Manager picks stocks (higher fees, ~0.5-2%)\n"
        "- **Index funds**: Passively track an index (lower fees, ~0.03-0.2%)\n"
        "- Priced once daily at NAV (Net Asset Value)\n"
        "- Minimum investment often required ($1,000-$3,000)\n"
        "- Most active managers underperform the index over 10+ years"
    ),
    "option": (
        "**What are Options?**\n\n"
        "Options are derivatives that give you the right (not obligation) to buy or sell an "
        "asset at a specific price (strike) before a certain date (expiration).\n\n"
        "- **Call option**: Right to BUY at strike price (bullish bet)\n"
        "- **Put option**: Right to SELL at strike price (bearish bet/insurance)\n"
        "- **Premium**: The price you pay for the option\n"
        "- **Greeks**: Delta (price sensitivity), Theta (time decay), "
        "Vega (volatility sensitivity), Gamma (delta acceleration)\n"
        "- Options expire worthless if out of the money — you can lose 100% of premium"
    ),
    "futures": (
        "**What are Futures?**\n\n"
        "Futures are standardized contracts to buy or sell an asset at a predetermined price on a "
        "specific future date. Unlike options, both parties are OBLIGATED to fulfill the contract.\n\n"
        "- Trade on exchanges (CME, NYMEX, ICE)\n"
        "- Used for hedging (farmers, airlines) and speculation\n"
        "- Leveraged: You only post margin (5-15% of contract value)\n"
        "- Mark-to-market daily — gains/losses settled each day\n"
        "- Common futures: S&P 500 (ES), crude oil (CL), gold (GC), Treasury bonds (ZB)"
    ),
    "cryptocurrency": (
        "**Cryptocurrency Overview**\n\n"
        "Cryptocurrencies are digital assets secured by cryptography on decentralized blockchain "
        "networks.\n\n"
        "- **Bitcoin (BTC)**: First and largest crypto, digital gold narrative, 21M supply cap\n"
        "- **Ethereum (ETH)**: Smart contract platform, powers DeFi and NFTs\n"
        "- Extremely volatile (50-80% drawdowns are common)\n"
        "- Not correlated with traditional assets (potential diversifier)\n"
        "- Regulatory landscape evolving rapidly\n"
        "- Consider it a small allocation (1-5%) for risk-tolerant investors"
    ),
    "forex": (
        "**What is Forex (Foreign Exchange)?**\n\n"
        "Forex is the global market for trading currencies. It's the largest financial market "
        "in the world with ~$7.5 trillion daily volume.\n\n"
        "- Currencies trade in pairs: EUR/USD, GBP/JPY, USD/INR\n"
        "- Driven by interest rate differentials, economic data, geopolitics\n"
        "- Highly leveraged (50:1 to 500:1 available)\n"
        "- 24-hour market (Mon-Fri), most active during London/NY overlap\n"
        "- Major pairs: EUR/USD, USD/JPY, GBP/USD, USD/CHF"
    ),
    "ipo": (
        "**What is an IPO (Initial Public Offering)?**\n\n"
        "An IPO is when a private company offers its shares to the public for the first time "
        "on a stock exchange.\n\n"
        "- Companies hire investment banks as underwriters to price and sell shares\n"
        "- **Lock-up period**: Insiders can't sell for 90-180 days after IPO\n"
        "- IPO pop: First-day price surge is common but not guaranteed\n"
        "- High risk: Many IPOs underperform the market in year 1\n"
        "- Recent trend: Direct listings and SPACs as alternatives to traditional IPOs"
    ),
    "dividend": (
        "**What are Dividends?**\n\n"
        "Dividends are a portion of a company's earnings distributed to shareholders, usually "
        "quarterly.\n\n"
        "- **Dividend yield** = Annual dividend / Stock price\n"
        "- **Payout ratio** = Dividends / Earnings (lower is more sustainable)\n"
        "- **Dividend aristocrats**: S&P 500 companies with 25+ years of consecutive increases\n"
        "- Qualified dividends taxed at lower capital gains rates\n"
        "- High-dividend ETFs: VYM, SCHD, DVY, HDV\n"
        "- Dividend reinvestment (DRIP) compounds returns over time"
    ),
    # --- Trading strategies ---
    "day trading": (
        "**Day Trading**\n\n"
        "Day trading involves buying and selling securities within the same trading day, "
        "closing all positions before market close.\n\n"
        "- Requires $25,000+ in account (Pattern Day Trader rule in US)\n"
        "- Uses technical analysis, Level 2 quotes, chart patterns\n"
        "- High frequency of trades, small profit per trade\n"
        "- **Risk**: Studies show 70-90% of day traders lose money\n"
        "- Needs: Fast execution, low commissions, strong risk management\n"
        "- Tax: All gains taxed as short-term (ordinary income rates)"
    ),
    "swing trading": (
        "**Swing Trading**\n\n"
        "Swing trading captures price moves over days to weeks, holding positions longer than "
        "day trades but shorter than investments.\n\n"
        "- Uses technical analysis (support/resistance, moving averages, RSI)\n"
        "- Typically targets 5-15% moves per trade\n"
        "- Less time-intensive than day trading\n"
        "- Works in trending and range-bound markets\n"
        "- Risk management: Stop-losses at 2-5%, position sizing critical"
    ),
    "value investing": (
        "**Value Investing**\n\n"
        "Value investing means buying stocks trading below their intrinsic value, popularized "
        "by Benjamin Graham and Warren Buffett.\n\n"
        "- Look for low P/E, low P/B, high dividend yield\n"
        "- **Margin of safety**: Buy at a significant discount to fair value\n"
        "- Focus on fundamentals: earnings, book value, cash flow, moats\n"
        "- Long-term horizon (years, not months)\n"
        "- Value ETFs: VTV, IWD, VLUE\n"
        "- *\"Price is what you pay. Value is what you get.\"* — Warren Buffett"
    ),
    "growth investing": (
        "**Growth Investing**\n\n"
        "Growth investing focuses on companies with above-average revenue and earnings growth, "
        "even if they appear expensive by traditional metrics.\n\n"
        "- High P/E ratios justified by rapid growth\n"
        "- Focus on revenue growth, TAM (total addressable market), margins\n"
        "- Often reinvest profits rather than paying dividends\n"
        "- Higher volatility but potential for outsized returns\n"
        "- Growth ETFs: VUG, IWF, QQQ, ARKK\n"
        "- Dominated by tech: AAPL, MSFT, GOOGL, AMZN, NVDA"
    ),
    # --- Technical analysis ---
    "technical analysis": (
        "**Technical Analysis**\n\n"
        "Technical analysis studies price patterns and trading volume to forecast future price "
        "movements. It assumes all information is reflected in the price.\n\n"
        "- **Support/Resistance**: Key price levels where buying/selling clusters\n"
        "- **Moving averages**: 50-day and 200-day SMA, golden/death cross\n"
        "- **RSI (Relative Strength Index)**: Overbought (>70) / oversold (<30)\n"
        "- **MACD**: Trend-following momentum indicator\n"
        "- **Bollinger Bands**: Volatility-based price channels\n"
        "- **Volume**: Confirms price moves; divergences signal reversals"
    ),
    "rsi": (
        "**RSI (Relative Strength Index)**\n\n"
        "RSI measures the speed and magnitude of recent price changes to evaluate "
        "overbought or oversold conditions. Range: 0-100.\n\n"
        "- **Above 70**: Overbought — potential pullback/reversal\n"
        "- **Below 30**: Oversold — potential bounce/reversal\n"
        "- **50 level**: Neutral; above 50 = bullish momentum\n"
        "- Divergence (price makes new high but RSI doesn't) = warning signal\n"
        "- Default period: 14 days\n"
        "- Best used with other indicators, not in isolation"
    ),
    "moving average": (
        "**Moving Averages**\n\n"
        "Moving averages smooth out price data to identify trends. They're the most widely "
        "used technical indicator.\n\n"
        "- **SMA (Simple)**: Equal weight to all periods\n"
        "- **EMA (Exponential)**: More weight on recent prices, faster to react\n"
        "- **Golden Cross**: 50-day crosses above 200-day (bullish)\n"
        "- **Death Cross**: 50-day crosses below 200-day (bearish)\n"
        "- Price above 200-day SMA = long-term uptrend\n"
        "- Common periods: 10, 20, 50, 100, 200 days"
    ),
    # --- Economics & Macro ---
    "inflation": (
        "**Inflation**\n\n"
        "Inflation is the rate at which the general price level of goods and services rises, "
        "eroding purchasing power.\n\n"
        "- Measured by CPI (Consumer Price Index) and PCE (Personal Consumption Expenditures)\n"
        "- **Fed target**: 2% annual inflation\n"
        "- **Causes**: Demand-pull, cost-push, monetary expansion\n"
        "- **Inflation hedges**: TIPS, gold (GLD), commodities (DBC), real estate (VNQ)\n"
        "- Central banks fight inflation by raising interest rates\n"
        "- High inflation hurts bonds and cash; moderate inflation is normal"
    ),
    "interest rate": (
        "**Interest Rates & the Federal Reserve**\n\n"
        "The Federal Reserve sets the federal funds rate, which influences all other interest "
        "rates in the economy.\n\n"
        "- **Rate hikes**: Slow economy, fight inflation, hurt stocks & bonds\n"
        "- **Rate cuts**: Stimulate economy, boost stocks, lower borrowing costs\n"
        "- Bond prices move inversely to interest rates\n"
        "- Growth stocks are more sensitive to rate changes (discounted future earnings)\n"
        "- Monitor: FOMC meetings (8 per year), dot plot, Fed minutes\n"
        "- Current tool: Fed Funds Rate target range"
    ),
    "recession": (
        "**Recession**\n\n"
        "A recession is two consecutive quarters of declining GDP (technically defined by NBER "
        "based on multiple economic indicators).\n\n"
        "- **Indicators**: Inverted yield curve, rising unemployment, falling PMI, declining "
        "consumer confidence\n"
        "- Average recession lasts ~11 months\n"
        "- Stocks typically fall 30-40% during recessions\n"
        "- **Defensive sectors** outperform: Utilities, Healthcare, Consumer Staples\n"
        "- Bonds rally as rates are cut\n"
        "- Historically: Great buying opportunity for long-term investors"
    ),
    "gdp": (
        "**GDP (Gross Domestic Product)**\n\n"
        "GDP measures the total value of all goods and services produced in a country. It's "
        "the broadest measure of economic activity.\n\n"
        "- **GDP = C + I + G + (X - M)** (Consumption + Investment + Government + Net Exports)\n"
        "- US GDP: ~$28 trillion (2024)\n"
        "- **Real GDP**: Adjusted for inflation (the one that matters)\n"
        "- Reported quarterly by BEA (Bureau of Economic Analysis)\n"
        "- GDP growth > 2%: Healthy economy\n"
        "- Negative GDP growth for 2 quarters = recession signal"
    ),
    "bull market": (
        "**Bull Market vs Bear Market**\n\n"
        "- **Bull market**: Sustained period of rising prices, typically 20%+ gain from a low. "
        "Driven by optimism, strong economy, low rates.\n"
        "- **Bear market**: Sustained decline of 20%+ from a peak. Driven by fear, recession, "
        "tightening policy.\n\n"
        "Average bull market lasts ~4.4 years with ~150% gain.\n"
        "Average bear market lasts ~11 months with ~36% decline.\n\n"
        "Markets spend about 78% of the time in bull markets historically."
    ),
    # --- Personal finance ---
    "retirement": (
        "**Retirement Planning**\n\n"
        "Key retirement accounts and strategies:\n\n"
        "- **401(k)**: Employer-sponsored, pre-tax contributions, $23,500 limit (2025)\n"
        "- **IRA**: Individual, $7,000 limit. Traditional (pre-tax) or Roth (post-tax, tax-free growth)\n"
        "- **Roth IRA**: Best if you expect higher taxes in retirement\n"
        "- **Rule of 72**: Years to double = 72 / annual return rate\n"
        "- **4% rule**: Withdraw 4% of portfolio annually in retirement\n"
        "- Target: 25x annual expenses saved by retirement\n"
        "- Start early — compounding is most powerful over decades"
    ),
    "tax": (
        "**Investment Taxes (US)**\n\n"
        "- **Short-term capital gains** (held < 1 year): Taxed as ordinary income (up to 37%)\n"
        "- **Long-term capital gains** (held > 1 year): 0%, 15%, or 20% based on income\n"
        "- **Qualified dividends**: Same as long-term capital gains rates\n"
        "- **Tax-loss harvesting**: Sell losers to offset gains (save on taxes)\n"
        "- **Wash sale rule**: Can't rebuy same security within 30 days\n"
        "- **Tax-advantaged accounts**: 401(k), IRA, Roth IRA, HSA\n"
        "- Consider tax implications when rebalancing or selling"
    ),
    "emergency fund": (
        "**Emergency Fund**\n\n"
        "An emergency fund is 3-6 months of living expenses kept in liquid, safe accounts.\n\n"
        "- **Where**: High-yield savings account (5%+ APY currently)\n"
        "- **How much**: 3 months (dual income) to 6 months (single income/freelance)\n"
        "- Build this BEFORE investing in stocks\n"
        "- Don't invest emergency fund in stocks (too volatile)\n"
        "- Purpose: Job loss, medical emergency, car repair, unexpected expenses\n"
        "- Money market funds (like SPAXX, VMFXX) are also good options"
    ),
    # --- Portfolio concepts ---
    "asset allocation": (
        "**Asset Allocation**\n\n"
        "Asset allocation is dividing your portfolio among different asset classes to balance "
        "risk and return based on your goals, timeline, and risk tolerance.\n\n"
        "- **Aggressive (80/20)**: 80% stocks, 20% bonds — younger investors\n"
        "- **Moderate (60/40)**: 60% stocks, 40% bonds — balanced approach\n"
        "- **Conservative (40/60)**: 40% stocks, 60% bonds — near retirement\n"
        "- Add alternatives: 5-15% in gold, REITs, or commodities\n"
        "- **Rebalance** annually or when allocation drifts >5%\n"
        "- Asset allocation explains ~90% of portfolio return variation"
    ),
    "rebalancing": (
        "**Portfolio Rebalancing**\n\n"
        "Rebalancing means adjusting your portfolio back to target allocations when market "
        "moves cause drift.\n\n"
        "- **Calendar rebalancing**: Quarterly or annually\n"
        "- **Threshold rebalancing**: When any asset drifts >5% from target\n"
        "- Forces you to buy low and sell high systematically\n"
        "- Reduces risk by preventing over-concentration\n"
        "- Tax-efficient method: Rebalance using new contributions\n"
        "- In tax-advantaged accounts, rebalance freely without tax consequences"
    ),
    "dollar cost averaging": (
        "**Dollar Cost Averaging (DCA)**\n\n"
        "DCA means investing a fixed amount at regular intervals regardless of price, "
        "reducing the impact of volatility.\n\n"
        "- Example: Invest $500/month in SPY every month\n"
        "- Buy more shares when prices are low, fewer when high\n"
        "- Removes emotion and timing risk from investing\n"
        "- Historically, lump sum beats DCA ~68% of the time (but DCA reduces regret)\n"
        "- Best for: Regular income investors, building positions over time\n"
        "- Most retirement contributions (401k) are DCA by default"
    ),
    "beta": (
        "**Beta**\n\n"
        "Beta measures a stock's volatility relative to the overall market (S&P 500 = beta 1.0).\n\n"
        "- **Beta > 1**: More volatile than market (e.g., TSLA ~1.5, NVDA ~1.7)\n"
        "- **Beta < 1**: Less volatile (e.g., JNJ ~0.5, KO ~0.6)\n"
        "- **Beta = 0**: No correlation to market (e.g., gold)\n"
        "- **Negative beta**: Moves opposite to market (rare — some hedge funds)\n"
        "- High beta = higher risk AND higher potential return\n"
        "- Low beta stocks are defensive; prefer them in bear markets"
    ),
    "p/e ratio": (
        "**P/E Ratio (Price-to-Earnings)**\n\n"
        "The P/E ratio is the most common valuation metric. It tells you how much investors "
        "pay for each dollar of earnings.\n\n"
        "- **P/E = Stock Price / Earnings Per Share**\n"
        "- S&P 500 historical average: ~16-17x\n"
        "- **Low P/E (<15)**: Potentially undervalued or slow growth\n"
        "- **High P/E (>25)**: Expensive or high growth expected\n"
        "- **Forward P/E**: Based on estimated future earnings (more useful)\n"
        "- Compare within same industry — tech has higher P/E than utilities\n"
        "- **PEG ratio** (P/E / Growth rate): PEG < 1 suggests undervalued"
    ),
    "market cap": (
        "**Market Capitalization**\n\n"
        "Market cap = Share price x Total shares outstanding. It classifies company size.\n\n"
        "- **Mega-cap**: >$200B (AAPL, MSFT, GOOGL, AMZN, NVDA)\n"
        "- **Large-cap**: $10B-$200B — stable, lower risk (SPY, VOO)\n"
        "- **Mid-cap**: $2B-$10B — balance of growth and stability\n"
        "- **Small-cap**: $300M-$2B — higher growth potential, more volatile (IWM)\n"
        "- **Micro-cap**: <$300M — very speculative, low liquidity\n"
        "- Diversify across market caps for balanced exposure"
    ),
}

# Mapping keywords to knowledge base keys
KEYWORD_TO_TOPIC = {
    "stock": "stock", "equity": "stock", "equities": "stock", "share": "stock",
    "bond": "bond", "fixed income": "bond", "treasury": "bond", "treasuries": "bond",
    "debt": "bond",
    "etf": "etf", "exchange traded": "etf", "index fund": "etf",
    "mutual fund": "mutual fund",
    "option": "option", "call option": "option", "put option": "option",
    "options trading": "option", "greeks": "option", "delta": "option",
    "theta": "option", "strike price": "option",
    "futures": "futures", "futures contract": "futures",
    "crypto": "cryptocurrency", "bitcoin": "cryptocurrency",
    "btc": "cryptocurrency", "ethereum": "cryptocurrency", "eth": "cryptocurrency",
    "blockchain": "cryptocurrency",
    "forex": "forex", "currency": "forex", "exchange rate": "forex", "fx": "forex",
    "ipo": "ipo", "initial public offering": "ipo", "going public": "ipo",
    "dividend": "dividend", "yield": "dividend", "payout": "dividend",
    "day trad": "day trading", "day-trad": "day trading", "scalping": "day trading",
    "swing trad": "swing trading", "swing-trad": "swing trading",
    "value invest": "value investing", "warren buffett": "value investing",
    "benjamin graham": "value investing", "undervalued": "value investing",
    "growth invest": "growth investing",
    "technical analysis": "technical analysis", "chart pattern": "technical analysis",
    "candlestick": "technical analysis", "support and resistance": "technical analysis",
    "rsi": "rsi", "relative strength": "rsi", "overbought": "rsi", "oversold": "rsi",
    "moving average": "moving average", "sma": "moving average", "ema": "moving average",
    "golden cross": "moving average", "death cross": "moving average", "macd": "moving average",
    "inflation": "inflation", "cpi": "inflation", "purchasing power": "inflation",
    "interest rate": "interest rate", "fed": "interest rate",
    "federal reserve": "interest rate", "rate hike": "interest rate",
    "rate cut": "interest rate", "monetary policy": "interest rate", "fomc": "interest rate",
    "recession": "recession", "economic downturn": "recession",
    "gdp": "gdp", "gross domestic product": "gdp", "economic growth": "gdp",
    "bull market": "bull market", "bear market": "bull market",
    "bull": "bull market", "bear": "bull market",
    "retirement": "retirement", "401k": "retirement", "401(k)": "retirement",
    "ira": "retirement", "roth": "retirement", "pension": "retirement",
    "retire": "retirement",
    "tax": "tax", "capital gains": "tax", "tax loss": "tax", "wash sale": "tax",
    "emergency fund": "emergency fund", "savings": "emergency fund",
    "rainy day": "emergency fund",
    "asset allocation": "asset allocation", "portfolio allocation": "asset allocation",
    "60/40": "asset allocation", "80/20": "asset allocation",
    "rebalance": "rebalancing", "rebalancing": "rebalancing",
    "dca": "dollar cost averaging", "dollar cost": "dollar cost averaging",
    "lump sum": "dollar cost averaging",
    "beta": "beta", "high beta": "beta", "low beta": "beta",
    "p/e": "p/e ratio", "pe ratio": "p/e ratio", "price to earnings": "p/e ratio",
    "price-to-earnings": "p/e ratio", "peg ratio": "p/e ratio",
    "valuation": "p/e ratio",
    "market cap": "market cap", "large cap": "market cap", "small cap": "market cap",
    "mid cap": "market cap", "mega cap": "market cap", "micro cap": "market cap",
}


def _match_general_topic(msg: str):
    """Try to match user message to a general knowledge topic."""
    for keyword, topic in KEYWORD_TO_TOPIC.items():
        if keyword in msg:
            return GENERAL_KNOWLEDGE.get(topic)
    return None


def fallback_response(user_message: str, session_state) -> str:
    """Generate a rules-based response using keyword matching and portfolio context."""
    msg = user_message.lower().strip()

    portfolio = getattr(session_state, "portfolio", None)
    regime_df = getattr(session_state, "regime_df", None)
    data_loaded = getattr(session_state, "data_loaded", False)

    # --- General finance knowledge (works even without portfolio) ---
    general = _match_general_topic(msg)
    if general and not _is_portfolio_specific(msg):
        return general

    if not data_loaded or portfolio is None:
        # Still try general knowledge
        if general:
            return general
        return (
            "I can answer any finance question! Try asking about stocks, bonds, ETFs, "
            "options, crypto, inflation, interest rates, or trading strategies.\n\n"
            "For portfolio-specific analysis, load data using the sidebar controls."
        )

    returns = portfolio.returns
    weights = portfolio.weights
    tickers = portfolio.tickers

    # --- Buy advice ---
    if any(kw in msg for kw in ["best stocks", "should i buy", "recommend", "invest in",
                                "good stocks", "what to buy", "buy recommendation"]):
        try:
            from core.data_fetch import get_sectors
            sector_counts = {}
            for t in tickers:
                sec = get_sectors([t])[t]
                sector_counts[sec] = sector_counts.get(sec, 0) + 1

            held = getattr(session_state, "holdings", {})
            held_sectors = {}
            for ht in held:
                sec = get_sectors([ht])[ht]
                held_sectors[sec] = held_sectors.get(sec, 0) + 1

            regime_text = ""
            if regime_df is not None and len(regime_df) > 0:
                current = regime_df["regime"].iloc[-1]
                regime_text = f"We are in a **{current}** regime. "

            missing_sectors = [s for s in ["Technology", "Healthcare", "Energy", "Financials",
                                           "Consumer Staples", "Gold", "Long-Term Treasury"]
                               if s not in sector_counts and s not in held_sectors]

            response = f"**Buy Suggestions based on your portfolio:**\n\n{regime_text}"
            response += f"Your portfolio covers: {', '.join(sorted(sector_counts.keys()))}.\n\n"
            if missing_sectors:
                response += f"Consider diversifying into: **{', '.join(missing_sectors[:4])}**.\n\n"
            if regime_df is not None and len(regime_df) > 0:
                current = regime_df["regime"].iloc[-1]
                if current in ("Crisis", "High Volatility"):
                    response += ("In elevated-volatility regimes, consider defensive assets like "
                                 "**TLT** (treasuries), **GLD** (gold), or **XLU** (utilities).\n")
                else:
                    response += ("In the current low-to-normal volatility environment, growth-oriented "
                                 "assets like **QQQ** or sector ETFs may offer upside.\n")
            return response
        except Exception:
            return "Load your portfolio first to get personalized buy suggestions."

    # --- Sell advice ---
    if any(kw in msg for kw in ["should i sell", "take profit", "cut losses", "exit position",
                                "sell advice", "time to sell"]):
        try:
            held = getattr(session_state, "holdings", {})
            if not held:
                return ("You don't have any holdings tracked yet. "
                        "Add stocks in the **My Holdings** section to get sell advice.")

            import pandas as _pd
            from core.data_fetch import fetch_latest_prices as _flp
            held_tickers = list(held.keys())
            live = _flp(held_tickers)
            price_map = {}
            for _, row in live.iterrows():
                if _pd.notna(row.get("Price")):
                    price_map[row["Ticker"]] = row["Price"]

            from core.portfolio import get_holdings_summary
            rows = get_holdings_summary(price_map)

            regime_text = ""
            if regime_df is not None and len(regime_df) > 0:
                current = regime_df["regime"].iloc[-1]
                regime_text = f"Current regime: **{current}**. "

            response = f"**Sell Analysis for your holdings:**\n\n{regime_text}\n"
            for r in rows:
                pnl_label = "profit" if r["P&L"] >= 0 else "loss"
                response += (f"- **{r['Ticker']}**: {r['Shares']:.1f} shares, "
                             f"P&L ${r['P&L']:+,.2f} ({r['P&L %']:+.1f}%) — ")
                if r["P&L %"] > 20:
                    response += "Consider taking partial profit.\n"
                elif r["P&L %"] < -15:
                    response += "Significant {}, review your thesis.\n".format(pnl_label)
                else:
                    response += "Hold for now.\n"

            if regime_df is not None and len(regime_df) > 0:
                current = regime_df["regime"].iloc[-1]
                if current == "Crisis":
                    response += ("\nIn **Crisis** regime, consider reducing high-beta positions "
                                 "and increasing defensive allocations.")
                elif current == "High Volatility":
                    response += "\nIn **High Volatility**, tighten stop-losses and watch for breakdowns."
            return response
        except Exception:
            return "Add holdings in the **My Holdings** section to get personalized sell advice."

    # --- Market outlook ---
    if any(kw in msg for kw in ["market outlook", "sector performance", "market trend",
                                "market forecast", "market direction"]):
        try:
            response = "**Market Outlook:**\n\n"
            if regime_df is not None and len(regime_df) > 0:
                current = regime_df["regime"].iloc[-1]
                from core.regime_detector import get_regime_statistics
                stats = get_regime_statistics(regime_df)
                response += f"Current regime: **{current}**\n\n"
                for name, s in stats.items():
                    response += (f"- {name}: {s['pct_time']:.1f}% of time "
                                 f"(vol: {s['avg_vol']:.2%}, corr: {s['avg_corr']:.2f})\n")
                response += "\n"

            import numpy as np
            port_ret = portfolio.portfolio_returns
            ann_ret = float(port_ret.mean() * 252)
            ann_vol = float(port_ret.std() * np.sqrt(252))
            response += (f"Portfolio annualized return: **{ann_ret:+.2%}**, "
                         f"volatility: **{ann_vol:.2%}**.\n\n")
            response += "Visit **Regime Detection** and **Risk Metrics** pages for deeper analysis."
            return response
        except Exception:
            return "Load portfolio data to see market outlook analysis."

    # --- Correlation queries ---
    if any(kw in msg for kw in ["correlation", "corr", "diversif", "how correlated", "move together"]):
        try:
            from risk.correlation import (
                calculate_correlation_matrix,
                calculate_tail_correlation,
                calculate_diversification_ratio,
            )
            normal = calculate_correlation_matrix(returns)
            tail = calculate_tail_correlation(returns)
            dr = calculate_diversification_ratio(returns, weights)

            if len(tickers) >= 2:
                t1, t2 = tickers[0], tickers[1]
                nv = normal.loc[t1, t2]
                tv = tail.loc[t1, t2]
                spike = tv - nv

                return (
                    f"**Correlation Analysis:**\n\n"
                    f"- **{t1}-{t2} normal correlation:** {nv:.2f}\n"
                    f"- **{t1}-{t2} crash correlation:** {tv:.2f} ({spike:+.2f} spike)\n"
                    f"- **Diversification ratio:** {dr:.2f}\n\n"
                    f"{'Corr spike in crashes.' if spike > 0.1 else 'Corr stable across regimes.'} "
                    f"Diversification ratio of {dr:.2f} means "
                    f"{'good' if dr > 1.3 else 'moderate' if dr > 1.1 else 'limited'} diversification.\n\n"
                    f"Visit the **Correlation Analysis** page for heatmaps."
                )
            return (
                f"Your portfolio diversification ratio is {dr:.2f}. "
                f"Visit the Correlation Analysis page for details."
            )
        except Exception:
            return ("Visit the **Correlation Analysis** page to see how "
                    "your assets correlate during normal and crash periods.")

    # --- VaR queries ---
    if any(kw in msg for kw in ["value at risk", "cvar", "expected shortfall",
                                "risk metric", "how much can i lose", "worst case",
                                "downside risk"]):
        try:
            from risk.var_cvar import var_cvar_summary, regime_conditional_var
            s = var_cvar_summary(returns, weights, 0.95)

            response = (
                f"**Risk Metrics (95% confidence):**\n\n"
                f"- **Historical VaR:** {s['historical_var']:.2%} daily\n"
                f"- **CVaR (Expected Shortfall):** {s['historical_cvar']:.2%} daily\n"
                f"- **Parametric VaR:** {s['parametric_var']:.2%} daily\n\n"
                f"This means on the worst 5% of trading days, you can expect to lose at least "
                f"**{s['historical_var']:.2%}** of portfolio value. The average loss on those worst days is "
                f"**{s['historical_cvar']:.2%}** (CVaR)."
            )

            if regime_df is not None:
                rv = regime_conditional_var(returns, weights, regime_df, 0.95)
                if rv:
                    regime_lines = [
                        f"  - {k}: {v:.2%}" for k, v in rv.items()
                        if not (isinstance(v, float) and v != v)
                    ]
                    if regime_lines:
                        response += "\n\n**VaR by regime:**\n" + "\n".join(regime_lines)

            response += "\n\nVisit the **Risk Metrics** page for regime-conditional analysis."
            return response
        except Exception:
            return "Visit the **Risk Metrics** page for VaR, CVaR, and Monte Carlo analysis."

    # --- Regime queries ---
    if any(kw in msg for kw in ["regime", "crisis", "market state", "market condition",
                                "what phase", "which regime"]):
        if regime_df is not None and len(regime_df) > 0:
            current = regime_df["regime"].iloc[-1]
            from core.regime_detector import get_regime_statistics
            stats = get_regime_statistics(regime_df)

            response = f"**Current Market Regime: {current}**\n\n"

            regime_descriptions = {
                "Low Volatility": (
                    "Markets are calm with below-average volatility. "
                    "Correlations tend to be lower, diversification works well."
                ),
                "Normal": (
                    "Standard market conditions with typical volatility "
                    "and correlation levels."
                ),
                "High Volatility": (
                    "Elevated volatility but not at crisis levels. "
                    "Watch for correlation spikes reducing diversification."
                ),
                "Crisis": (
                    "Extreme volatility and high correlations. "
                    "Diversification is likely failing - hedging is critical."
                ),
            }
            response += regime_descriptions.get(current, "") + "\n\n"

            response += "**Historical distribution:**\n"
            for name, s in stats.items():
                response += (
                    f"- {name}: {s['pct_time']:.1f}% of time "
                    f"(avg vol: {s['avg_vol']:.2%}, "
                    f"avg corr: {s['avg_corr']:.2f})\n"
                )

            response += "\nVisit the **Regime Detection** page for timeline."
            return response
        return "Visit the **Regime Detection** page to see current market regime analysis."

    # --- Hedge queries ---
    if any(kw in msg for kw in ["hedge", "protect", "insurance", "reduce risk",
                                "best hedge", "hedge ratio", "which asset"]):
        if len(tickers) > 1:
            try:
                from risk.hedge_analysis import compare_hedges, optimal_hedge_ratio, var_impact
                port_ret = portfolio.portfolio_returns
                candidates = tickers[1:]
                hedge_df = returns[candidates]
                comparison = compare_hedges(port_ret, hedge_df)

                best = comparison.index[0]
                best_metrics = comparison.iloc[0]
                opt_ratio = optimal_hedge_ratio(port_ret, returns[best])
                impact = var_impact(port_ret, returns[best], opt_ratio)

                response = (
                    f"**Hedge Analysis:**\n\n"
                    f"**Best hedge candidate: {best}**\n"
                    f"- Correlation with portfolio: {best_metrics['correlation']:.3f}\n"
                    f"- Tail correlation: {best_metrics['tail_correlation']:.3f}\n"
                    f"- Variance reduction: {best_metrics['variance_reduction']:.1%}\n"
                    f"- Optimal hedge ratio: {opt_ratio:.3f}\n\n"
                    f"**VaR impact at optimal ratio:**\n"
                    f"- Before: {impact['var_before']:.2%} -> After: {impact['var_after']:.2%}\n"
                    f"- **VaR reduction: {impact['reduction_pct']:.1%}**\n\n"
                )
                if len(comparison) > 1:
                    response += "**Other candidates:**\n"
                    for ticker in comparison.index[1:]:
                        row = comparison.loc[ticker]
                        response += (
                            f"- {ticker}: var reduction "
                            f"{row['variance_reduction']:.1%}, "
                            f"corr {row['correlation']:.3f}\n"
                        )

                response += "\nVisit the **Hedge Impact** page for detailed charts."
                return response
            except Exception:
                pass
        return "Add more assets to analyze hedging. Visit the **Hedge Impact** page."

    # --- Stress scenario queries ---
    if any(kw in msg for kw in ["stress", "scenario", "what if", "worst case scenario",
                                "black swan", "tail risk"]):
        return (
            "**Stress Scenarios** test your portfolio against 4 extreme events:\n\n"
            "1. **Correlation Shock** - All correlations spike toward 1\n"
            "2. **Volatility Spike** - Vol doubles across all assets\n"
            "3. **Liquidity Stress** - 20% return haircut from spreads\n"
            "4. **Combined Crisis** - All three simultaneously\n\n"
            "Visit the **Stress Scenarios** page to see projected outcomes."
        )

    # --- Explain / educational queries ---
    if any(kw in msg for kw in ["explain", "what is", "what does", "how does",
                                "define", "meaning", "what are"]):
        # Check general knowledge first
        if general:
            return general
        if "hhi" in msg:
            hhi = portfolio.hhi_concentration()
            return (
                f"**HHI (Herfindahl-Hirschman Index)** measures portfolio concentration.\n\n"
                f"- Ranges from 1/n (perfectly diversified) to 1 (single asset)\n"
                f"- Your HHI: **{hhi:.4f}** "
                f"(effective {portfolio.effective_n():.1f} assets)\n"
                f"- {'Well diversified' if hhi < 0.3 else 'Moderate' if hhi < 0.5 else 'Concentrated'}"
            )
        if "sharpe" in msg:
            ann_ret = returns.mean() * 252
            ann_vol = returns.std() * 252**0.5
            port_sharpe = float(
                (ann_ret * weights).sum() / (portfolio.portfolio_returns.std() * 252**0.5)
            )
            return (
                f"**Sharpe Ratio** = (Return - Risk-Free Rate) / Volatility\n\n"
                f"It measures risk-adjusted return. Higher is better.\n"
                f"- Your portfolio Sharpe: **{port_sharpe:.2f}**\n"
                f"- Above 1.0 = good, above 2.0 = excellent"
            )
        if "monte carlo" in msg or "simulation" in msg:
            return (
                "**Monte Carlo Simulation** generates thousands of possible future return paths "
                "using your portfolio's historical mean returns and covariance.\n\n"
                "- **Standard MC** uses Cholesky decomposition for correlated random returns\n"
                "- **Regime-Aware MC** uses per-regime parameters + transition probabilities\n\n"
                "Visit the **Risk Metrics** page to run simulations."
            )
        if "var" in msg:
            return (
                "**Value at Risk (VaR)** estimates the maximum expected loss over a given "
                "time period at a certain confidence level.\n\n"
                "- **95% daily VaR of 2%** means: on 95% of days, you lose less than 2%\n"
                "- **Historical VaR**: Based on actual past returns\n"
                "- **Parametric VaR**: Assumes normal distribution\n"
                "- **CVaR (Expected Shortfall)**: Average loss beyond VaR threshold\n"
                "- CVaR is considered a better risk measure as it captures tail risk"
            )
        return (
            "I can explain many finance concepts! Try asking about:\n"
            "stocks, bonds, ETFs, options, futures, crypto, forex, inflation, "
            "interest rates, P/E ratio, beta, Sharpe ratio, VaR, "
            "technical analysis, RSI, moving averages, and more."
        )

    # --- Help / general ---
    if any(kw in msg for kw in ["help", "what can", "how do", "menu",
                                "options", "capabilities"]):
        return (
            "I'm your financial advisor! I can help with:\n\n"
            "**General Finance:**\n"
            "- *What is a stock/bond/ETF/option?*\n"
            "- *Explain P/E ratio / beta / Sharpe ratio*\n"
            "- *How does inflation affect investments?*\n"
            "- *What is dollar cost averaging?*\n"
            "- *Tell me about value investing*\n\n"
            "**Your Portfolio:**\n"
            "- *How correlated are my assets?*\n"
            "- *What is my Value-at-Risk?*\n"
            "- *What market regime are we in?*\n"
            "- *Which asset is the best hedge?*\n"
            "- *Should I buy/sell?*\n\n"
            "**Trading & Strategies:**\n"
            "- *Explain technical analysis / RSI / MACD*\n"
            "- *What is swing trading?*\n"
            "- *How do options work?*\n\n"
            "Ask me anything about finance!"
        )

    # --- Greetings ---
    if any(kw in msg for kw in ["hello", "hi", "hey", "good morning", "good evening",
                                "what's up", "howdy", "greetings"]):
        return (
            "Hey! I'm your financial advisor. Ask me anything about:\n\n"
            "- **Investing**: Stocks, bonds, ETFs, crypto, options\n"
            "- **Your portfolio**: Risk, correlations, hedging, P&L\n"
            "- **Finance concepts**: P/E ratio, Sharpe, inflation, interest rates\n"
            "- **Strategies**: Value investing, swing trading, DCA\n\n"
            "What would you like to know?"
        )

    # --- Thank you ---
    if any(kw in msg for kw in ["thank", "thanks", "appreciate", "great answer"]):
        return "You're welcome! Feel free to ask anything else about finance or your portfolio."

    # --- Try general knowledge as last resort before default ---
    if general:
        return general

    # --- Default: intelligent catch-all ---
    summary = portfolio.summary()
    port_ret = portfolio.portfolio_returns
    import numpy as np
    ann_ret = float(port_ret.mean() * 252)
    ann_vol = float(port_ret.std() * np.sqrt(252))

    return (
        f"I'm not sure I understood that, but I can help with a lot! Here's a quick summary:\n\n"
        f"**Your Portfolio:** {', '.join(summary['tickers'][:5])} "
        f"({summary['n_assets']} instruments)\n"
        f"**Return:** {ann_ret:+.2%} | **Vol:** {ann_vol:.2%}\n\n"
        f"Try asking me about:\n"
        f"- General finance: *What is an ETF?*, *Explain inflation*, *How do options work?*\n"
        f"- Your portfolio: *What's my VaR?*, *Should I sell?*, *Market outlook*\n"
        f"- Strategies: *Value investing*, *Dollar cost averaging*, *Technical analysis*"
    )


def _is_portfolio_specific(msg: str) -> bool:
    """Check if the message is specifically about the user's portfolio."""
    portfolio_keywords = [
        "my portfolio", "my holdings", "my assets", "my stocks",
        "my position", "my risk", "my return", "my var",
        "should i buy", "should i sell", "my allocation",
    ]
    return any(kw in msg for kw in portfolio_keywords)
