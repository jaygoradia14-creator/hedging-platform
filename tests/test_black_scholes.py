"""Tests for risk/black_scholes.py - Black-Scholes option pricing."""

import numpy as np

from risk.black_scholes import (
    black_scholes_put,
    black_scholes_call,
    protective_put_cost,
    put_greeks,
)


# Common test parameters
S = 100.0   # spot
K = 100.0   # ATM strike
T = 0.25    # 3 months
r = 0.05    # 5% risk-free
sigma = 0.20  # 20% vol


class TestPutCallParity:
    """Put-call parity: C - P = S - K * e^(-rT)."""

    def test_atm(self):
        call = black_scholes_call(S, K, T, r, sigma)
        put = black_scholes_put(S, K, T, r, sigma)
        parity = S - K * np.exp(-r * T)
        assert abs((call - put) - parity) < 1e-10

    def test_itm_put(self):
        K_itm = 110.0
        call = black_scholes_call(S, K_itm, T, r, sigma)
        put = black_scholes_put(S, K_itm, T, r, sigma)
        parity = S - K_itm * np.exp(-r * T)
        assert abs((call - put) - parity) < 1e-10

    def test_otm_put(self):
        K_otm = 90.0
        call = black_scholes_call(S, K_otm, T, r, sigma)
        put = black_scholes_put(S, K_otm, T, r, sigma)
        parity = S - K_otm * np.exp(-r * T)
        assert abs((call - put) - parity) < 1e-10

    def test_long_expiry(self):
        T_long = 2.0
        call = black_scholes_call(S, K, T_long, r, sigma)
        put = black_scholes_put(S, K, T_long, r, sigma)
        parity = S - K * np.exp(-r * T_long)
        assert abs((call - put) - parity) < 1e-10


class TestPutMonotonicity:
    """Put price should increase with volatility, time, and strike."""

    def test_put_increases_with_volatility(self):
        p_low = black_scholes_put(S, K, T, r, 0.15)
        p_high = black_scholes_put(S, K, T, r, 0.30)
        assert p_high > p_low

    def test_put_increases_with_time(self):
        p_short = black_scholes_put(S, K, 1 / 12, r, sigma)
        p_long = black_scholes_put(S, K, 6 / 12, r, sigma)
        assert p_long > p_short

    def test_put_increases_with_strike(self):
        p_low_k = black_scholes_put(S, 90.0, T, r, sigma)
        p_high_k = black_scholes_put(S, 110.0, T, r, sigma)
        assert p_high_k > p_low_k

    def test_put_positive(self):
        p = black_scholes_put(S, K, T, r, sigma)
        assert p > 0


class TestPutGreeks:
    """Greeks sanity checks."""

    def test_atm_delta_approx_minus_half(self):
        greeks = put_greeks(S, K, T, r, sigma)
        assert -0.6 < greeks["delta"] < -0.4

    def test_delta_negative(self):
        greeks = put_greeks(S, K, T, r, sigma)
        assert greeks["delta"] < 0

    def test_gamma_positive(self):
        greeks = put_greeks(S, K, T, r, sigma)
        assert greeks["gamma"] > 0

    def test_vega_positive(self):
        greeks = put_greeks(S, K, T, r, sigma)
        assert greeks["vega"] > 0

    def test_deep_itm_delta_near_minus_one(self):
        greeks = put_greeks(50.0, 100.0, T, r, sigma)
        assert greeks["delta"] < -0.9

    def test_deep_otm_delta_near_zero(self):
        greeks = put_greeks(200.0, 100.0, T, r, sigma)
        assert greeks["delta"] > -0.1


class TestProtectivePutCost:
    """Protective put total cost calculation."""

    def test_exact_100_shares(self):
        put_price = black_scholes_put(S, K, T, r, sigma)
        cost = protective_put_cost(S, K, T, r, sigma, 100)
        # 1 contract * 100 shares * put_price
        assert abs(cost - put_price * 100) < 1e-10

    def test_150_shares_needs_2_contracts(self):
        put_price = black_scholes_put(S, K, T, r, sigma)
        cost = protective_put_cost(S, K, T, r, sigma, 150)
        assert abs(cost - put_price * 200) < 1e-10

    def test_50_shares_needs_1_contract(self):
        put_price = black_scholes_put(S, K, T, r, sigma)
        cost = protective_put_cost(S, K, T, r, sigma, 50)
        assert abs(cost - put_price * 100) < 1e-10

    def test_cost_positive(self):
        cost = protective_put_cost(S, K, T, r, sigma, 100)
        assert cost > 0

    def test_cost_scales_with_contracts(self):
        cost_100 = protective_put_cost(S, K, T, r, sigma, 100)
        cost_500 = protective_put_cost(S, K, T, r, sigma, 500)
        assert abs(cost_500 - 5 * cost_100) < 1e-10


class TestEdgeCases:
    """Boundary and edge-case behavior."""

    def test_very_short_expiry(self):
        # ATM put with very short expiry should be near zero but positive
        p = black_scholes_put(S, K, 1 / 252, r, sigma)
        assert 0 < p < 5

    def test_high_volatility(self):
        p = black_scholes_put(S, K, T, r, 1.0)  # 100% vol
        assert p > black_scholes_put(S, K, T, r, 0.20)

    def test_zero_rate(self):
        call = black_scholes_call(S, K, T, 0.0, sigma)
        put = black_scholes_put(S, K, T, 0.0, sigma)
        # Put-call parity with r=0: C - P = S - K
        assert abs((call - put) - (S - K)) < 1e-10
