"""
A simple implementation of the Cox-Ross-Rubinstein binomial option pricing model.

The module exposes a single function, ``binomial_option_price``, that can price
European or American call/put options.
"""

from __future__ import annotations

import math
from typing import Literal

OptionType = Literal["call", "put"]


def binomial_option_price(
    spot: float,
    strike: float,
    maturity: float,
    risk_free_rate: float,
    volatility: float,
    steps: int,
    option_type: OptionType = "call",
    american: bool = False,
) -> float:
    """
    Price an option using the Cox-Ross-Rubinstein binomial model.

    Parameters
    ----------
    spot:
        Current underlying price ``S_0``.
    strike:
        Option strike price ``K``.
    maturity:
        Time to maturity in years ``T``.
    risk_free_rate:
        Continuously compounded annual risk-free rate ``r`` (as a decimal).
    volatility:
        Annualized volatility of the underlying ``sigma`` (as a decimal).
    steps:
        Number of time steps for the binomial tree.
    option_type:
        ``"call"`` or ``"put"``.
    american:
        When ``True``, allows early exercise and returns the American option price.

    Returns
    -------
    float
        The discounted option price at time 0.
    """

    if steps <= 0:
        raise ValueError("steps must be a positive integer")
    if maturity <= 0:
        raise ValueError("maturity must be positive")
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'")

    dt = maturity / steps
    up = math.exp(volatility * math.sqrt(dt))
    down = 1 / up

    growth = math.exp(risk_free_rate * dt)
    probability = (growth - down) / (up - down)

    if probability < 0 or probability > 1:
        raise ValueError("No-arbitrage violation: adjust inputs to satisfy 0 <= p <= 1")

    # Prices at maturity
    values = []
    for i in range(steps + 1):
        # i up moves, (steps - i) down moves
        spot_T = spot * (up ** i) * (down ** (steps - i))
        if option_type == "call":
            payoff = max(spot_T - strike, 0.0)
        else:
            payoff = max(strike - spot_T, 0.0)
        values.append(payoff)

    discount = math.exp(-risk_free_rate * dt)

    # Backward induction
    for step in range(steps - 1, -1, -1):
        next_values = []
        for i in range(step + 1):
            continuation = discount * (
                probability * values[i + 1] + (1 - probability) * values[i]
            )

            if american:
                spot_t = spot * (up ** i) * (down ** (step - i))
                intrinsic = (
                    max(spot_t - strike, 0.0)
                    if option_type == "call"
                    else max(strike - spot_t, 0.0)
                )
                next_values.append(max(continuation, intrinsic))
            else:
                next_values.append(continuation)
        values = next_values

    return values[0]


if __name__ == "__main__":
    # Example usage
    price = binomial_option_price(
        spot=100,
        strike=100,
        maturity=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        steps=200,
        option_type="call",
        american=False,
    )
    print(f"European call option price: {price:.4f}")
