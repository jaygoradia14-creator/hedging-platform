"""
Black-Scholes option pricing for protective put hedging.
"""

import numpy as np
from scipy.stats import norm


def black_scholes_put(S, K, T, r, sigma):
    """Black-Scholes European put option price.

    Args:
        S: Current underlying price.
        K: Strike price.
        T: Time to expiry in years.
        r: Risk-free interest rate (annualized).
        sigma: Annualized volatility of the underlying.

    Returns:
        Put option price.
    """
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def black_scholes_call(S, K, T, r, sigma):
    """Black-Scholes European call option price.

    Args:
        S: Current underlying price.
        K: Strike price.
        T: Time to expiry in years.
        r: Risk-free interest rate (annualized).
        sigma: Annualized volatility of the underlying.

    Returns:
        Call option price.
    """
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def protective_put_cost(S, K, T, r, sigma, shares):
    """Total cost to hedge a position with protective puts.

    Args:
        S: Current underlying price.
        K: Strike price.
        T: Time to expiry in years.
        r: Risk-free interest rate.
        sigma: Annualized volatility.
        shares: Number of shares held.

    Returns:
        Total hedge cost (put_price * contracts * 100).
    """
    put_price = black_scholes_put(S, K, T, r, sigma)
    contracts = int(np.ceil(shares / 100))
    return put_price * contracts * 100


def put_greeks(S, K, T, r, sigma):
    """Compute Greeks for a European put option.

    Args:
        S: Current underlying price.
        K: Strike price.
        T: Time to expiry in years.
        r: Risk-free interest rate.
        sigma: Annualized volatility.

    Returns:
        Dict with delta, gamma, theta (per day), and vega (per 1% vol move).
    """
    sqrt_T = np.sqrt(T)
    d1 = (np.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    delta = norm.cdf(d1) - 1  # put delta is negative
    gamma = norm.pdf(d1) / (S * sigma * sqrt_T)

    # Theta: per-day decay
    theta_term1 = -(S * norm.pdf(d1) * sigma) / (2 * sqrt_T)
    theta_term2 = r * K * np.exp(-r * T) * norm.cdf(-d2)
    theta = (theta_term1 + theta_term2) / 252  # daily

    # Vega: price change per 1% increase in volatility
    vega = S * norm.pdf(d1) * sqrt_T * 0.01

    return {
        "delta": delta,
        "gamma": gamma,
        "theta": theta,
        "vega": vega,
    }
