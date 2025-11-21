"""Web interface for Monte Carlo option pricing.

The application exposes a single-page form that lets users provide
model inputs (spot, maturity, risk-free rate, volatility, number of
paths) and a custom payoff expression. Results are computed using the
``monte_carlo_option_pricing`` helpers.
"""

from __future__ import annotations

from typing import Any, Dict

from flask import Flask, Response, flash, render_template_string, request, url_for

from monte_carlo_option_pricing import monte_carlo_option_price, parse_payoff_expression

app = Flask(__name__)
app.secret_key = "mc-option-demo"


PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Monte Carlo Option Pricer</title>
    <style>
      body { font-family: system-ui, -apple-system, sans-serif; max-width: 960px; margin: 0 auto; padding: 2rem; background: #f8f9fa; }
      h1 { margin-bottom: 0.5rem; }
      form { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
      label { display: block; font-weight: 600; margin-bottom: 0.4rem; }
      input, textarea { width: 100%; padding: 0.55rem 0.7rem; border: 1px solid #ced4da; border-radius: 8px; font-size: 1rem; }
      .actions { grid-column: 1 / -1; display: flex; gap: 0.75rem; align-items: center; }
      button { background: #0d6efd; color: white; border: none; padding: 0.7rem 1.2rem; border-radius: 8px; font-size: 1rem; cursor: pointer; }
      button:hover { background: #0b5ed7; }
      .result, .error { margin-top: 1.5rem; padding: 1rem 1.25rem; border-radius: 10px; background: white; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }
      .result strong { font-size: 1.25rem; }
      .error { border-left: 4px solid #dc3545; }
      .muted { color: #6c757d; font-size: 0.95rem; }
    </style>
  </head>
  <body>
    <h1>Monte Carlo Option Pricer</h1>
    <p class="muted">Simulate terminal prices under geometric Brownian motion and estimate discounted payoffs.</p>
    <form method="post" action="{{ url_for('price') }}">
      <div>
        <label for="spot">Spot price S<sub>0</sub></label>
        <input id="spot" name="spot" type="number" step="any" min="0" value="{{ form_values.spot }}" required>
      </div>
      <div>
        <label for="maturity">Maturity (years)</label>
        <input id="maturity" name="maturity" type="number" step="any" min="0" value="{{ form_values.maturity }}" required>
      </div>
      <div>
        <label for="risk_free_rate">Risk-free rate r</label>
        <input id="risk_free_rate" name="risk_free_rate" type="number" step="any" value="{{ form_values.risk_free_rate }}" required>
      </div>
      <div>
        <label for="volatility">Volatility σ</label>
        <input id="volatility" name="volatility" type="number" step="any" min="0" value="{{ form_values.volatility }}" required>
      </div>
      <div>
        <label for="num_paths">Number of paths</label>
        <input id="num_paths" name="num_paths" type="number" step="1" min="1" value="{{ form_values.num_paths }}" required>
      </div>
      <div>
        <label for="payoff">Payoff expression (use <code>s</code>)</label>
        <textarea id="payoff" name="payoff" rows="3" required>{{ form_values.payoff }}</textarea>
      </div>
      <div class="actions">
        <button type="submit">Estimate price</button>
        <span class="muted">Examples: <code>max(s - 100, 0)</code>, <code>max(120 - s, 0)</code></span>
      </div>
    </form>

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, msg in messages %}
          <div class="error">{{ msg }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {% if result is not none %}
    <div class="result">
      <strong>Estimated price:</strong> {{ "{:.6f}".format(result) }}<br>
      <span class="muted">Discounted expected payoff over {{ form_values.num_paths }} paths.</span>
    </div>
    {% endif %}
  </body>
</html>
"""


def _float_from_form(data: Dict[str, str], key: str, positive: bool = False) -> float:
    value = float(data.get(key, "0"))
    if positive and value <= 0:
        raise ValueError(f"{key.replace('_', ' ')} must be positive")
    return value


def _int_from_form(data: Dict[str, str], key: str, positive: bool = False) -> int:
    value = int(data.get(key, "0"))
    if positive and value <= 0:
        raise ValueError(f"{key.replace('_', ' ')} must be positive")
    return value


def _validate_inputs(form: Dict[str, str]) -> Dict[str, Any]:
    values: Dict[str, Any] = {
        "spot": _float_from_form(form, "spot", positive=True),
        "maturity": _float_from_form(form, "maturity", positive=True),
        "risk_free_rate": _float_from_form(form, "risk_free_rate"),
        "volatility": _float_from_form(form, "volatility"),
        "num_paths": _int_from_form(form, "num_paths", positive=True),
        "payoff": form.get("payoff", "").strip(),
    }
    if not values["payoff"]:
        raise ValueError("Payoff expression cannot be empty")
    if values["volatility"] < 0:
        raise ValueError("volatility cannot be negative")
    return values


@app.route("/", methods=["GET"])
def home() -> Response:
    defaults = {
        "spot": 100,
        "maturity": 1.0,
        "risk_free_rate": 0.05,
        "volatility": 0.2,
        "num_paths": 50000,
        "payoff": "max(s - 100, 0)",
    }
    return render_template_string(PAGE_TEMPLATE, form_values=defaults, result=None)


@app.route("/price", methods=["POST"])
def price() -> Response:
    try:
        inputs = _validate_inputs(request.form)  # type: ignore[arg-type]
        payoff_fn = parse_payoff_expression(inputs["payoff"])
        estimate = monte_carlo_option_price(
            spot=inputs["spot"],
            maturity=inputs["maturity"],
            risk_free_rate=inputs["risk_free_rate"],
            volatility=inputs["volatility"],
            num_paths=inputs["num_paths"],
            payoff=payoff_fn,
        )
    except Exception as exc:  # noqa: BLE001
        flash(str(exc))
        # Fall back to submitted values when displaying the form again.
        return render_template_string(PAGE_TEMPLATE, form_values=request.form, result=None)

    form_values: Dict[str, Any] = dict(inputs)
    form_values["payoff"] = inputs["payoff"]
    return render_template_string(PAGE_TEMPLATE, form_values=form_values, result=estimate)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
