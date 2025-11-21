# 20251121

This repository provides a simple Python implementation of the Cox-Ross-Rubinstein
binomial option pricing model. The `binomial_option_pricing.py` module exposes a
`binomial_option_price` function that can price European or American call/put options.

The repository also includes `monte_carlo_option_pricing.py`, which performs Monte
Carlo pricing under geometric Brownian motion. You can provide any payoff as a Python
expression in terms of the terminal price `s` (e.g., `max(s - 100, 0)` for a European
call).

Finally, `web_option_app.py` starts a small Flask server that exposes a web form for
Monte Carlo pricing with custom payoffs.

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

To launch the web interface (requires `flask`):

```bash
pip install flask
python web_option_app.py
```

Then visit `http://localhost:8000` in your browser, fill in the model parameters, and
provide a payoff expression in terms of `s` (for example, `max(s - 100, 0)` for a call
or `max(120 - s, 0)` for a put). The page will display the discounted Monte Carlo
estimate.
