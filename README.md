# 20251121

This repository provides a simple Python implementation of the Cox-Ross-Rubinstein
binomial option pricing model. The `binomial_option_pricing.py` module exposes a
`binomial_option_price` function that can price European or American call/put options.

The repository also includes `monte_carlo_option_pricing.py`, which performs Monte
Carlo pricing under geometric Brownian motion. You can provide any payoff as a Python
expression in terms of the terminal price `s` (e.g., `max(s - 100, 0)` for a European
call).

## Quick start

```bash
python binomial_option_pricing.py
```

To try the Monte Carlo pricer interactively and enter your own payoff expression:

```bash
python monte_carlo_option_pricing.py
```

The example in the `__main__` block prices a one-year at-the-money European call
with a 5% risk-free rate, 20% volatility, and 200 time steps.
