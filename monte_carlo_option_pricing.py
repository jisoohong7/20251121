"""
A Monte Carlo option pricer that allows custom payoff definitions.

The module exposes two primary helpers:
- ``monte_carlo_option_price``: Simulate geometric Brownian motion paths and
  discount the average payoff.
- ``parse_payoff_expression``: Convert a user-provided expression into a
  callable payoff function accepting the terminal price ``s``.

Example
-------
```
from monte_carlo_option_pricing import monte_carlo_option_price, parse_payoff_expression

payoff = parse_payoff_expression("max(s - 100, 0)")
price = monte_carlo_option_price(
    spot=100,
    maturity=1.0,
    risk_free_rate=0.05,
    volatility=0.2,
    num_paths=100_000,
    payoff=payoff,
)
print(f"Price: {price:.4f}")
```
"""

from __future__ import annotations

import ast
import math
import random
from typing import Callable


def parse_payoff_expression(expression: str) -> Callable[[float], float]:
    """
    Convert a string expression into a payoff function ``f(s)``.

    Parameters
    ----------
    expression:
        A Python expression using ``s`` for the terminal underlying price. The
        names ``max``, ``min``, and the ``math`` module are available, while
        builtins are otherwise disabled for safety.

    Returns
    -------
    Callable[[float], float]
        A function that evaluates the payoff for a given terminal price.

    Raises
    ------
    ValueError
        If the expression is empty or contains disallowed syntax.
    """

    if not expression.strip():
        raise ValueError("Payoff expression cannot be empty")

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid expression: {exc}") from exc

    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Num,
        ast.Constant,
        ast.Name,
        ast.Call,
        ast.Attribute,
        ast.keyword,
        ast.Load,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.USub,
        ast.UAdd,
        ast.Compare,
        ast.Gt,
        ast.Lt,
        ast.GtE,
        ast.LtE,
        ast.Eq,
        ast.NotEq,
        ast.BoolOp,
        ast.And,
        ast.Or,
        ast.IfExp,
    )

    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError("Unsupported syntax in payoff expression")

    allowed_globals = {"max": max, "min": min, "math": math}

    def payoff(s: float) -> float:
        return float(eval(compile(tree, "<payoff>", "eval"), {"__builtins__": {}}, {"s": s, **allowed_globals}))

    return payoff


def monte_carlo_option_price(
    spot: float,
    maturity: float,
    risk_free_rate: float,
    volatility: float,
    num_paths: int,
    payoff: Callable[[float], float],
) -> float:
    """
    Price an option via Monte Carlo simulation under geometric Brownian motion.

    Parameters
    ----------
    spot:
        Current underlying price ``S_0``.
    maturity:
        Time to maturity in years ``T``.
    risk_free_rate:
        Continuously compounded annual risk-free rate ``r``.
    volatility:
        Annualized volatility ``sigma``.
    num_paths:
        Number of simulated paths for the terminal price.
    payoff:
        Callable receiving the terminal price ``s`` and returning the payoff.

    Returns
    -------
    float
        The discounted expected payoff estimate.
    """

    if maturity <= 0:
        raise ValueError("maturity must be positive")
    if volatility < 0:
        raise ValueError("volatility cannot be negative")
    if num_paths <= 0:
        raise ValueError("num_paths must be positive")

    drift = (risk_free_rate - 0.5 * volatility**2) * maturity
    diffusion = volatility * math.sqrt(maturity)
    discount = math.exp(-risk_free_rate * maturity)

    total = 0.0
    for _ in range(num_paths):
        z = random.gauss(0.0, 1.0)
        terminal_price = spot * math.exp(drift + diffusion * z)
        total += payoff(terminal_price)

    average_payoff = total / num_paths
    return discount * average_payoff


def _interactive_cli() -> None:
    print("Monte Carlo option pricer with custom payoff")
    spot = float(input("Spot price S0: "))
    maturity = float(input("Maturity in years T: "))
    risk_free_rate = float(input("Risk-free rate r: "))
    volatility = float(input("Volatility sigma: "))
    num_paths = int(input("Number of simulated paths: "))
    expression = input("Payoff expression using s (e.g., max(s - 100, 0)): ")

    payoff = parse_payoff_expression(expression)
    price = monte_carlo_option_price(
        spot=spot,
        maturity=maturity,
        risk_free_rate=risk_free_rate,
        volatility=volatility,
        num_paths=num_paths,
        payoff=payoff,
    )
    print(f"Estimated option price: {price:.6f}")


if __name__ == "__main__":
    _interactive_cli()
