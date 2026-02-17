"""
Rules-based fallback chat — general financial advisor + portfolio analytics.
Intent-first routing: action intents (buy/sell/invest) checked BEFORE
educational keyword matching to avoid "what stocks to invest in" -> "What is a Stock?"
"""


# ---------------------------------------------------------------------------
# General finance knowledge base (no portfolio data needed)
# ---------------------------------------------------------------------------
GENERAL_KNOWLEDGE = {
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
        '- *"Price is what you pay. Value is what you get."* — Warren Buffett'
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
    "retirement": (
        "**Retirement Planning**\n\n"
        "Key retirement accounts and strategies:\n\n"
        "- **401(k)**: Employer-sponsored, pre-tax contributions, $23,500 limit (2025)\n"
        "- **IRA**: Individual, $7,000 limit. Traditional (pre-tax) or Roth (post-tax, "
        "tax-free growth)\n"
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
    "short selling": (
        "**Short Selling**\n\n"
        "Short selling means borrowing shares and selling them, hoping to buy back at a "
        "lower price for profit.\n\n"
        "- **How it works**: Borrow shares → sell high → buy back low → return shares\n"
        "- **Unlimited loss potential** (price can go to infinity)\n"
        "- Requires a margin account\n"
        "- Short interest: % of shares sold short (high = bearish sentiment)\n"
        "- **Short squeeze**: Shorts forced to buy back, spiking the price (e.g., GME 2021)\n"
        "- Most retail investors should avoid short selling due to risk"
    ),
    "risk management": (
        "**Risk Management in Investing**\n\n"
        "Risk management is about protecting your capital while pursuing returns.\n\n"
        "- **Position sizing**: Never risk more than 1-2% of portfolio on a single trade\n"
        "- **Stop-loss orders**: Automatically sell when price drops to a set level\n"
        "- **Diversification**: Don't put all eggs in one basket\n"
        "- **Asset allocation**: Match risk level to your time horizon\n"
        "- **Hedging**: Use bonds, gold, or options to offset equity risk\n"
        "- **Rebalancing**: Maintain target allocations as markets move\n"
        "- **Risk metrics**: VaR, CVaR, Sharpe ratio, max drawdown"
    ),
    "index investing": (
        "**Index Investing**\n\n"
        "Index investing means buying funds that track a market index instead of picking "
        "individual stocks.\n\n"
        "- **S&P 500 funds**: SPY, VOO, IVV — track the 500 largest US companies\n"
        "- **Total market**: VTI, ITOT — entire US stock market\n"
        "- **International**: VXUS, IXUS — non-US developed + emerging markets\n"
        "- **Fees**: Ultra-low (0.03-0.1% vs 1-2% for active funds)\n"
        "- Warren Buffett recommends index funds for most investors\n"
        "- Beats ~90% of active managers over 15+ years"
    ),
    "sector": (
        "**Stock Market Sectors**\n\n"
        "The market is divided into 11 GICS sectors:\n\n"
        "- **Technology** (XLK): AAPL, MSFT, NVDA — growth, high beta\n"
        "- **Healthcare** (XLV): UNH, JNJ, LLY — defensive + growth\n"
        "- **Financials** (XLF): JPM, BRK-B, GS — rate-sensitive\n"
        "- **Consumer Discretionary** (XLY): AMZN, TSLA — cyclical\n"
        "- **Consumer Staples** (XLP): PG, KO, PEP — defensive\n"
        "- **Energy** (XLE): XOM, CVX — commodity-linked\n"
        "- **Utilities** (XLU): NEE, DUK — bond-like, defensive\n"
        "- **Industrials** (XLI): CAT, HON — economic bellwether\n"
        "- **Materials** (XLB), **Real Estate** (XLRE), **Communication** (XLC)"
    ),
}

# Keywords that ONLY match for educational queries (prefixed with "what is", "explain", etc.)
KEYWORD_TO_TOPIC = {
    "stock": "stock", "equity": "stock", "equities": "stock", "shares": "stock",
    "bond": "bond", "fixed income": "bond", "treasury": "bond", "treasuries": "bond",
    "debt instrument": "bond",
    "etf": "etf", "exchange traded": "etf", "index fund": "index investing",
    "mutual fund": "mutual fund",
    "option": "option", "call option": "option", "put option": "option",
    "options trading": "option", "greeks": "option",
    "strike price": "option",
    "futures": "futures", "futures contract": "futures",
    "crypto": "cryptocurrency", "bitcoin": "cryptocurrency",
    "btc": "cryptocurrency", "ethereum": "cryptocurrency",
    "blockchain": "cryptocurrency",
    "forex": "forex", "foreign exchange": "forex", "exchange rate": "forex",
    "ipo": "ipo", "initial public offering": "ipo", "going public": "ipo",
    "dividend": "dividend",
    "day trad": "day trading", "day-trad": "day trading", "scalping": "day trading",
    "swing trad": "swing trading", "swing-trad": "swing trading",
    "value invest": "value investing", "warren buffett": "value investing",
    "benjamin graham": "value investing",
    "growth invest": "growth investing",
    "technical analysis": "technical analysis", "chart pattern": "technical analysis",
    "candlestick": "technical analysis", "support and resistance": "technical analysis",
    "rsi": "rsi", "relative strength": "rsi", "overbought": "rsi", "oversold": "rsi",
    "moving average": "moving average", "sma": "moving average", "ema": "moving average",
    "golden cross": "moving average", "death cross": "moving average", "macd": "moving average",
    "inflation": "inflation", "cpi": "inflation", "purchasing power": "inflation",
    "interest rate": "interest rate", "fed fund": "interest rate",
    "federal reserve": "interest rate", "rate hike": "interest rate",
    "rate cut": "interest rate", "monetary policy": "interest rate", "fomc": "interest rate",
    "recession": "recession", "economic downturn": "recession",
    "gdp": "gdp", "gross domestic product": "gdp",
    "bull market": "bull market", "bear market": "bull market",
    "retirement": "retirement", "401k": "retirement", "401(k)": "retirement",
    "ira": "retirement", "roth": "retirement", "pension": "retirement",
    "retire": "retirement",
    "capital gains": "tax", "tax loss": "tax", "wash sale": "tax",
    "emergency fund": "emergency fund", "rainy day": "emergency fund",
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
    "short sell": "short selling", "shorting": "short selling",
    "short squeeze": "short selling",
    "risk manage": "risk management", "position sizing": "risk management",
    "stop loss": "risk management", "stop-loss": "risk management",
    "index invest": "index investing", "passive invest": "index investing",
    "bogle": "index investing",
    "sector": "sector", "gics": "sector",
}


def _match_general_topic(msg: str):
    """Match message to a general knowledge topic. Longer keywords first."""
    # Sort by length descending so "futures contract" matches before "futures"
    for keyword in sorted(KEYWORD_TO_TOPIC, key=len, reverse=True):
        if keyword in msg:
            topic = KEYWORD_TO_TOPIC[keyword]
            return GENERAL_KNOWLEDGE.get(topic)
    return None


def _has_action_intent(msg: str) -> bool:
    """Check if the user wants investment advice (buy/sell/invest) vs. education."""
    action_phrases = [
        "invest in", "should i buy", "should i sell", "what to buy", "what to sell",
        "best stocks", "good stocks", "recommend", "buy recommendation",
        "where to invest", "where should i", "what should i invest",
        "stocks to invest", "stocks to buy", "which stock",
        "take profit", "cut losses", "exit position", "sell advice",
        "time to sell", "time to buy", "worth buying", "worth investing",
        "start investing", "how to invest", "where to put money",
        "best investment", "good investment", "safe investment",
        "how much to invest", "invest my money", "grow my money",
        "market outlook", "market trend", "market forecast", "market direction",
        "sector performance", "how is the market",
    ]
    return any(phrase in msg for phrase in action_phrases)


def _has_educational_intent(msg: str) -> bool:
    """Check if the user is asking an educational / definitional question."""
    prefixes = [
        "what is ", "what are ", "what does ", "what do ",
        "explain ", "define ", "meaning of ", "tell me about ",
        "how does ", "how do ", "describe ", "teach me ",
    ]
    return any(msg.startswith(p) for p in prefixes)


def fallback_response(user_message: str, session_state) -> str:
    """Generate a rules-based response — intent-first routing."""
    msg = user_message.lower().strip()

    portfolio = getattr(session_state, "portfolio", None)
    data_loaded = getattr(session_state, "data_loaded", False)

    # ---------------------------------------------------------------
    # 1. Greetings (quick, always works)
    # ---------------------------------------------------------------
    if any(kw in msg for kw in ["hello", "hi ", "hey", "good morning",
                                "good evening", "howdy", "greetings"]):
        if msg.strip() in ("hi", "hey", "hello", "howdy", "greetings"):
            return (
                "Hey! I'm your financial advisor. Ask me anything about:\n\n"
                "- **Investing**: Stocks, bonds, ETFs, crypto, options\n"
                "- **Your portfolio**: Risk, correlations, hedging, P&L\n"
                "- **Finance concepts**: P/E ratio, Sharpe, inflation, interest rates\n"
                "- **Strategies**: Value investing, swing trading, DCA\n\n"
                "What would you like to know?"
            )

    # ---------------------------------------------------------------
    # 2. Thank you
    # ---------------------------------------------------------------
    if any(kw in msg for kw in ["thank", "thanks", "appreciate", "great answer"]):
        return "You're welcome! Feel free to ask anything else about finance or your portfolio."

    # ---------------------------------------------------------------
    # 3. Help
    # ---------------------------------------------------------------
    if any(kw in msg for kw in ["help", "what can you", "capabilities", "menu"]):
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
            "**Investment Advice:**\n"
            "- *What stocks should I invest in?*\n"
            "- *Where should I put my money?*\n"
            "- *Best stocks to buy right now?*\n"
            "- *Should I sell my holdings?*\n\n"
            "Ask me anything about finance!"
        )

    # ---------------------------------------------------------------
    # 4. ACTION INTENTS — buy/sell/invest advice (BEFORE education!)
    #    This is the critical fix: "what stocks to invest in" routes here,
    #    NOT to the "What is a Stock?" definition.
    # ---------------------------------------------------------------
    if _has_action_intent(msg):
        return _handle_action_intent(msg, session_state)

    # ---------------------------------------------------------------
    # 5. EDUCATIONAL INTENTS — "what is X", "explain X", "tell me about X"
    #    Only match general knowledge when user clearly wants education.
    # ---------------------------------------------------------------
    if _has_educational_intent(msg):
        general = _match_general_topic(msg)
        if general:
            return general

    # ---------------------------------------------------------------
    # 6. Portfolio-specific analysis queries (need data loaded)
    # ---------------------------------------------------------------
    if data_loaded and portfolio is not None:
        portfolio_answer = _handle_portfolio_query(msg, session_state)
        if portfolio_answer:
            return portfolio_answer

    # ---------------------------------------------------------------
    # 7. General knowledge as broad fallback (no educational prefix needed)
    #    e.g. "inflation", "crypto", "rsi" on their own
    # ---------------------------------------------------------------
    general = _match_general_topic(msg)
    if general:
        return general

    # ---------------------------------------------------------------
    # 8. No data loaded and nothing matched
    # ---------------------------------------------------------------
    if not data_loaded or portfolio is None:
        return (
            "I can answer any finance question! Try asking:\n\n"
            "- *What is a stock/bond/ETF?*\n"
            "- *Explain options / futures / crypto*\n"
            "- *How does inflation work?*\n"
            "- *What stocks should I invest in?*\n"
            "- *Tell me about value investing*\n\n"
            "For portfolio analysis, load data using the sidebar."
        )

    # ---------------------------------------------------------------
    # 9. Default catch-all with portfolio summary
    # ---------------------------------------------------------------
    summary = portfolio.summary()
    port_ret = portfolio.portfolio_returns
    import numpy as np
    ann_ret = float(port_ret.mean() * 252)
    ann_vol = float(port_ret.std() * np.sqrt(252))

    return (
        f"Great question! Here's what I can help with:\n\n"
        f"**Your Portfolio:** {', '.join(summary['tickers'][:5])} "
        f"({summary['n_assets']} instruments)\n"
        f"**Return:** {ann_ret:+.2%} | **Vol:** {ann_vol:.2%}\n\n"
        f"Try asking:\n"
        f"- *What stocks should I invest in?*\n"
        f"- *Should I sell my holdings?*\n"
        f"- *What is my VaR?* / *Market outlook*\n"
        f"- *Explain options* / *What is inflation?*\n"
        f"- *Tell me about technical analysis*"
    )


# ---------------------------------------------------------------------------
# Action intent handler — buy/sell/invest advice
# ---------------------------------------------------------------------------
def _handle_action_intent(msg: str, session_state) -> str:
    """Handle investment action queries (buy/sell/where to invest)."""
    # --- Investment / Buy advice ---
    buy_keywords = [
        "invest in", "should i buy", "what to buy", "best stocks",
        "good stocks", "recommend", "buy recommendation", "where to invest",
        "where should i", "what should i invest", "stocks to invest",
        "stocks to buy", "which stock", "worth buying", "worth investing",
        "start investing", "how to invest", "where to put money",
        "best investment", "good investment", "safe investment",
        "how much to invest", "invest my money", "grow my money",
        "time to buy",
    ]
    if any(kw in msg for kw in buy_keywords):
        return _buy_advice(msg, session_state)

    # --- Sell advice ---
    sell_keywords = [
        "should i sell", "take profit", "cut losses", "exit position",
        "sell advice", "time to sell", "what to sell",
    ]
    if any(kw in msg for kw in sell_keywords):
        return _sell_advice(msg, session_state)

    # --- Market outlook ---
    return _market_outlook(msg, session_state)


def _buy_advice(msg: str, session_state) -> str:
    """Generate buy/investment advice."""
    portfolio = getattr(session_state, "portfolio", None)
    regime_df = getattr(session_state, "regime_df", None)
    data_loaded = getattr(session_state, "data_loaded", False)

    # Generic investment advice (works without portfolio)
    generic = (
        "**Investment Suggestions:**\n\n"
        "**For Beginners:**\n"
        "- Start with broad index funds: **SPY** (S&P 500), **VTI** (Total US Market)\n"
        "- Add international exposure: **VXUS** (International stocks)\n"
        "- Bond allocation for stability: **BND** (Total Bond Market)\n\n"
        "**By Risk Tolerance:**\n"
        "- **Conservative**: 60% bonds (BND/TLT), 30% stocks (SPY), 10% gold (GLD)\n"
        "- **Moderate**: 60% stocks (SPY/QQQ), 30% bonds (BND), 10% alternatives (GLD)\n"
        "- **Aggressive**: 80% stocks (QQQ/VTI), 10% crypto (BTC-USD), 10% growth\n\n"
        "**Top Sector ETFs to Consider:**\n"
        "- Tech: **QQQ**, **XLK** | Healthcare: **XLV** | Financials: **XLF**\n"
        "- Energy: **XLE** | Consumer: **XLY** | Utilities: **XLU** (defensive)\n\n"
        "**Key Principles:**\n"
        "- Diversify across sectors and asset classes\n"
        "- Dollar-cost average rather than timing the market\n"
        "- Only invest money you won't need for 5+ years\n"
        "- Keep an emergency fund (3-6 months expenses) first"
    )

    if not data_loaded or portfolio is None:
        return generic

    # Personalized advice with portfolio context
    try:
        from core.data_fetch import get_sectors
        tickers = portfolio.tickers
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
            regime_text = f"Current regime: **{current}**. "

        all_sectors = {**sector_counts, **held_sectors}
        target_sectors = [
            "Technology", "Healthcare", "Energy", "Financials",
            "Consumer Staples", "Gold", "Long-Term Treasury",
        ]
        missing = [s for s in target_sectors if s not in all_sectors]

        response = f"**Personalized Buy Suggestions:**\n\n{regime_text}\n\n"
        response += f"Your portfolio covers: **{', '.join(sorted(sector_counts.keys()))}**.\n\n"

        if missing:
            response += "**Diversification gaps** — consider adding: "
            response += "**{}**.\n\n".format(', '.join(missing[:4]))

        # Regime-specific advice
        if regime_df is not None and len(regime_df) > 0:
            current = regime_df["regime"].iloc[-1]
            if current in ("Crisis", "High Volatility"):
                response += (
                    "**Regime advice**: In elevated volatility, favor defensive assets:\n"
                    "- **TLT** (treasuries), **GLD** (gold), **XLU** (utilities)\n"
                    "- Reduce exposure to high-beta growth stocks\n"
                    "- Consider increasing cash position\n"
                )
            else:
                response += (
                    "**Regime advice**: In low-to-normal volatility, growth assets may "
                    "offer upside:\n"
                    "- **QQQ** (tech), **XLY** (consumer), sector ETFs\n"
                    "- Good time to add equity exposure via DCA\n"
                )

        response += (
            "\n**General tips:**\n"
            "- Dollar-cost average into positions\n"
            "- Don't put more than 10-15% in any single stock\n"
            "- Review your holdings monthly"
        )
        return response
    except Exception:
        return generic


def _sell_advice(msg: str, session_state) -> str:
    """Generate sell advice based on holdings."""
    regime_df = getattr(session_state, "regime_df", None)
    held = getattr(session_state, "holdings", {})

    if not held:
        return (
            "**Sell Decision Framework:**\n\n"
            "You don't have any holdings tracked yet. Add stocks in the "
            "**My Holdings** section to get personalized sell advice.\n\n"
            "**General rules for when to sell:**\n"
            "- Take partial profit when a position is up 20%+\n"
            "- Cut losses if a stock drops 10-15% below your thesis\n"
            "- Sell if your original investment thesis has changed\n"
            "- Reduce positions when market regime turns to Crisis\n"
            "- Rebalance when any position exceeds 15% of portfolio\n"
            "- Don't sell just because of short-term volatility"
        )

    try:
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
            response += (
                f"- **{r['Ticker']}**: {r['Shares']:.1f} shares, "
                f"P&L ${r['P&L']:+,.2f} ({r['P&L %']:+.1f}%) — "
            )
            if r["P&L %"] > 20:
                response += "Consider taking partial profit.\n"
            elif r["P&L %"] < -15:
                fmt = "Significant {}, review your thesis.\n"
                response += fmt.format(pnl_label)
            else:
                response += "Hold for now.\n"

        if regime_df is not None and len(regime_df) > 0:
            current = regime_df["regime"].iloc[-1]
            if current == "Crisis":
                response += (
                    "\nIn **Crisis** regime, consider reducing high-beta positions "
                    "and increasing defensive allocations."
                )
            elif current == "High Volatility":
                response += (
                    "\nIn **High Volatility**, tighten stop-losses "
                    "and watch for breakdowns."
                )
        return response
    except Exception:
        return "Add holdings in the **My Holdings** section to get personalized sell advice."


def _market_outlook(msg: str, session_state) -> str:
    """Generate market outlook response."""
    portfolio = getattr(session_state, "portfolio", None)
    regime_df = getattr(session_state, "regime_df", None)

    if portfolio is None or portfolio.returns is None:
        return (
            "**General Market Outlook Tips:**\n\n"
            "- Check the **VIX** (fear index) — below 15 is calm, above 30 is fearful\n"
            "- Monitor the **yield curve** — inversion signals recession risk\n"
            "- Watch **Fed policy** — rate cuts boost stocks, hikes slow growth\n"
            "- Track **earnings season** — actual vs expected drives moves\n\n"
            "Load portfolio data for personalized regime-based analysis."
        )

    try:
        response = "**Market Outlook:**\n\n"
        if regime_df is not None and len(regime_df) > 0:
            current = regime_df["regime"].iloc[-1]
            from core.regime_detector import get_regime_statistics
            stats = get_regime_statistics(regime_df)
            response += f"Current regime: **{current}**\n\n"
            for name, s in stats.items():
                response += (
                    f"- {name}: {s['pct_time']:.1f}% of time "
                    f"(vol: {s['avg_vol']:.2%}, corr: {s['avg_corr']:.2f})\n"
                )
            response += "\n"

        import numpy as np
        port_ret = portfolio.portfolio_returns
        ann_ret = float(port_ret.mean() * 252)
        ann_vol = float(port_ret.std() * np.sqrt(252))
        response += (
            f"Portfolio annualized return: **{ann_ret:+.2%}**, "
            f"volatility: **{ann_vol:.2%}**.\n\n"
        )
        response += "Visit **Regime Detection** and **Risk Metrics** for deeper analysis."
        return response
    except Exception:
        return "Load portfolio data to see market outlook analysis."


# ---------------------------------------------------------------------------
# Portfolio-specific query handler
# ---------------------------------------------------------------------------
def _handle_portfolio_query(msg: str, session_state) -> str:
    """Handle portfolio-specific analysis queries. Returns None if no match."""
    portfolio = session_state.portfolio
    regime_df = getattr(session_state, "regime_df", None)
    returns = portfolio.returns
    weights = portfolio.weights
    tickers = portfolio.tickers

    # --- Correlation ---
    if any(kw in msg for kw in [
        "correlation", "corr", "diversif", "how correlated", "move together",
    ]):
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
                    f"- **{t1}-{t2} crash correlation:** {tv:.2f} "
                    f"({spike:+.2f} spike)\n"
                    f"- **Diversification ratio:** {dr:.2f}\n\n"
                    f"{'Corr spike in crashes.' if spike > 0.1 else 'Stable.'} "
                    f"Diversification ratio of {dr:.2f} means "
                    f"{'good' if dr > 1.3 else 'moderate' if dr > 1.1 else 'limited'}"
                    f" diversification.\n\n"
                    f"Visit the **Correlation Analysis** page for heatmaps."
                )
            return (
                f"Diversification ratio: {dr:.2f}. "
                f"Visit Correlation Analysis page for details."
            )
        except Exception:
            return (
                "Visit the **Correlation Analysis** page to see how "
                "your assets correlate."
            )

    # --- VaR ---
    if any(kw in msg for kw in [
        "value at risk", " var", "cvar", "expected shortfall",
        "risk metric", "how much can i lose", "worst case", "downside risk",
    ]):
        try:
            from risk.var_cvar import var_cvar_summary, regime_conditional_var
            s = var_cvar_summary(returns, weights, 0.95)
            response = (
                f"**Risk Metrics (95% confidence):**\n\n"
                f"- **Historical VaR:** {s['historical_var']:.2%} daily\n"
                f"- **CVaR (Expected Shortfall):** {s['historical_cvar']:.2%}\n"
                f"- **Parametric VaR:** {s['parametric_var']:.2%}\n\n"
                f"Worst 5% of days: lose at least **{s['historical_var']:.2%}**. "
                f"Average loss on those days: **{s['historical_cvar']:.2%}**."
            )
            if regime_df is not None:
                rv = regime_conditional_var(returns, weights, regime_df, 0.95)
                if rv:
                    lines = [
                        f"  - {k}: {v:.2%}" for k, v in rv.items()
                        if isinstance(v, float) and v == v
                    ]
                    if lines:
                        response += "\n\n**VaR by regime:**\n" + "\n".join(lines)
            response += "\n\nVisit **Risk Metrics** for full analysis."
            return response
        except Exception:
            return "Visit **Risk Metrics** for VaR and CVaR analysis."

    # --- Regime ---
    if any(kw in msg for kw in [
        "regime", "crisis", "market state", "market condition",
        "what phase", "which regime",
    ]):
        if regime_df is not None and len(regime_df) > 0:
            current = regime_df["regime"].iloc[-1]
            from core.regime_detector import get_regime_statistics
            stats = get_regime_statistics(regime_df)
            descs = {
                "Low Volatility": "Markets calm, diversification works well.",
                "Normal": "Standard conditions, typical volatility.",
                "High Volatility": "Elevated vol, watch for correlation spikes.",
                "Crisis": "Extreme vol + high correlations. Hedging critical.",
            }
            response = f"**Current Regime: {current}**\n\n"
            response += descs.get(current, "") + "\n\n"
            response += "**Historical distribution:**\n"
            for name, s in stats.items():
                response += (
                    f"- {name}: {s['pct_time']:.1f}% of time "
                    f"(vol: {s['avg_vol']:.2%}, corr: {s['avg_corr']:.2f})\n"
                )
            response += "\nVisit **Regime Detection** for timeline."
            return response
        return "Visit **Regime Detection** for regime analysis."

    # --- Hedge ---
    if any(kw in msg for kw in [
        "hedge", "protect", "insurance", "reduce risk",
        "best hedge", "hedge ratio",
    ]):
        if len(tickers) > 1:
            try:
                from risk.hedge_analysis import (
                    compare_hedges, optimal_hedge_ratio, var_impact,
                )
                port_ret = portfolio.portfolio_returns
                candidates = tickers[1:]
                hedge_df = returns[candidates]
                comparison = compare_hedges(port_ret, hedge_df)
                best = comparison.index[0]
                best_m = comparison.iloc[0]
                opt_ratio = optimal_hedge_ratio(port_ret, returns[best])
                impact = var_impact(port_ret, returns[best], opt_ratio)
                response = (
                    f"**Hedge Analysis:**\n\n"
                    f"**Best hedge: {best}**\n"
                    f"- Corr: {best_m['correlation']:.3f}, "
                    f"Tail corr: {best_m['tail_correlation']:.3f}\n"
                    f"- Variance reduction: {best_m['variance_reduction']:.1%}\n"
                    f"- Optimal ratio: {opt_ratio:.3f}\n\n"
                    f"**VaR impact:**\n"
                    f"- Before: {impact['var_before']:.2%} → "
                    f"After: {impact['var_after']:.2%}\n"
                    f"- **Reduction: {impact['reduction_pct']:.1%}**"
                )
                if len(comparison) > 1:
                    response += "\n\n**Other candidates:**\n"
                    for t in comparison.index[1:]:
                        r = comparison.loc[t]
                        response += (
                            f"- {t}: reduction {r['variance_reduction']:.1%}, "
                            f"corr {r['correlation']:.3f}\n"
                        )
                response += "\nVisit **Hedge Impact** for charts."
                return response
            except Exception:
                pass
        return "Add more assets to analyze hedging. Visit **Hedge Impact**."

    # --- Stress ---
    if any(kw in msg for kw in [
        "stress", "scenario", "black swan", "tail risk",
    ]):
        return (
            "**Stress Scenarios** test your portfolio against 4 extremes:\n\n"
            "1. **Correlation Shock** — correlations spike toward 1\n"
            "2. **Volatility Spike** — vol doubles across all assets\n"
            "3. **Liquidity Stress** — 20% return haircut\n"
            "4. **Combined Crisis** — all three simultaneously\n\n"
            "Visit **Stress Scenarios** for projected outcomes."
        )

    # --- Explain HHI / Sharpe / Monte Carlo / VaR (educational + portfolio) ---
    if any(kw in msg for kw in ["explain", "what is", "what does", "what are"]):
        if "hhi" in msg:
            hhi = portfolio.hhi_concentration()
            return (
                f"**HHI (Herfindahl-Hirschman Index)** measures concentration.\n\n"
                f"- Range: 1/n (diversified) to 1 (single asset)\n"
                f"- Your HHI: **{hhi:.4f}** "
                f"(effective {portfolio.effective_n():.1f} assets)\n"
                f"- {'Well diversified' if hhi < 0.3 else 'Moderate' if hhi < 0.5 else 'Concentrated'}"
            )
        if "sharpe" in msg:
            ann_ret = returns.mean() * 252
            port_sharpe = float(
                (ann_ret * weights).sum()
                / (portfolio.portfolio_returns.std() * 252**0.5)
            )
            return (
                f"**Sharpe Ratio** = (Return - Risk-Free) / Volatility\n\n"
                f"- Your portfolio Sharpe: **{port_sharpe:.2f}**\n"
                f"- Above 1.0 = good, above 2.0 = excellent"
            )
        if "monte carlo" in msg or "simulation" in msg:
            return (
                "**Monte Carlo Simulation** generates thousands of possible "
                "future return paths using historical stats.\n\n"
                "- **Standard MC**: Cholesky decomposition for correlated returns\n"
                "- **Regime-Aware MC**: Per-regime parameters + transitions\n\n"
                "Visit **Risk Metrics** to run simulations."
            )

    return None
