# 20251121

This repository provides a simple Python implementation of the Cox-Ross-Rubinstein
binomial option pricing model. The `binomial_option_pricing.py` module exposes a
`binomial_option_price` function that can price European or American call/put options.

## Quick start

```bash
python binomial_option_pricing.py
```

The example in the `__main__` block prices a one-year at-the-money European call
with a 5% risk-free rate, 20% volatility, and 200 time steps.
