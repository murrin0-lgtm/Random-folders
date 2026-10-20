"""Lab 14 portfolio baselines. Run from this folder: py portfolio.py.

Course-authored training inputs, not market estimates. All rates are decimals.
"""

import math
import sys

# Editable inputs; matrix rows and columns follow this sleeve order.
SLEEVES = [
    {"name": "Treasury bills", "return": 0.035, "volatility": 0.005, "reserve_eligible": True},
    {"name": "Treasury 10-year note", "return": 0.043, "volatility": 0.070, "reserve_eligible": True},
    {"name": "Investment-grade bond fund", "return": 0.050, "volatility": 0.060, "reserve_eligible": False},
    {"name": "Global equity index fund", "return": 0.080, "volatility": 0.160, "reserve_eligible": False},
]
CORRELATIONS = [
    [1.00, 0.10, 0.05, 0.00],
    [0.10, 1.00, 0.80, -0.10],
    [0.05, 0.80, 1.00, 0.25],
    [0.00, -0.10, 0.25, 1.00],
]
OBJECTIVE_RETURN = 0.065  # CPI estimate of 2.5% plus 4%.


def validate_inputs(sleeves, correlations):
    """Reject malformed, out-of-range or asymmetric correlation inputs."""
    n = len(sleeves)
    if not n or len(correlations) != n or any(len(row) != n for row in correlations):
        raise ValueError("Correlation table must have one row and column per sleeve.")
    for sleeve in sleeves:
        if not math.isfinite(sleeve["volatility"]) or sleeve["volatility"] <= 0:
            raise ValueError("Every volatility must be finite and positive.")
        if not math.isfinite(sleeve["return"]):
            raise ValueError("Every expected return must be finite.")
    for i in range(n):
        for j in range(n):
            value = correlations[i][j]
            if not math.isfinite(value) or not -1 <= value <= 1:
                raise ValueError(f"Correlation [{i}][{j}] must be between -1 and 1; got {value}.")
            if not math.isclose(value, correlations[j][i], rel_tol=0, abs_tol=1e-12):
                raise ValueError(f"Correlation table must be symmetric: [{i}][{j}] differs from [{j}][{i}].")
        if not math.isclose(correlations[i][i], 1, rel_tol=0, abs_tol=1e-12):
            raise ValueError("Each diagonal correlation must equal 1.")


def build_covariance_matrix(sleeves, correlations):
    validate_inputs(sleeves, correlations)
    return [
        [correlations[i][j] * a["volatility"] * b["volatility"]
         for j, b in enumerate(sleeves)]
        for i, a in enumerate(sleeves)
    ]


def equal_weights(sleeves):
    return [1 / len(sleeves)] * len(sleeves)


def inverse_volatility_weights(sleeves):
    inverse = [1 / sleeve["volatility"] for sleeve in sleeves]
    return [value / sum(inverse) for value in inverse]


def define_portfolios(sleeves):
    benchmark = {"Investment-grade bond fund": 0.40, "Global equity index fund": 0.60}
    return {
        "Benchmark": [benchmark.get(s["name"], 0) for s in sleeves],
        "Equal weight": equal_weights(sleeves),
        "Inverse volatility": inverse_volatility_weights(sleeves),
    }


def expected_return(weights, sleeves):
    return sum(weight * sleeve["return"] for weight, sleeve in zip(weights, sleeves))


def portfolio_volatility(weights, covariance):
    # Include every pair, including both off-diagonal covariance terms.
    variance = sum(
        weights[i] * weights[j] * covariance[i][j]
        for i in range(len(weights))
        for j in range(len(weights))
    )
    if variance < -1e-12:
        raise ValueError("Inputs produce a negative portfolio variance.")
    return math.sqrt(max(0, variance))


def reserve_eligible_weight(weights, sleeves):
    return sum(w for w, s in zip(weights, sleeves) if s["reserve_eligible"])


def meets_objective(portfolio_return, objective):
    return portfolio_return >= objective


def main():
    try:
        covariance = build_covariance_matrix(SLEEVES, CORRELATIONS)
        print("Course training values; CPI estimate: 2.5%; objective: "
              f"{OBJECTIVE_RETURN:.2%}")
        print("Weight order: " + " / ".join(s["name"] for s in SLEEVES))
        for name, weights in define_portfolios(SLEEVES).items():
            result = expected_return(weights, SLEEVES)
            print(f"\n{name}")
            print("  Weights (%): " + " / ".join(f"{w * 100:.1f}" for w in weights))
            print(f"  Expected return: {result:.2%}")
            print(f"  Volatility: {portfolio_volatility(weights, covariance):.2%}")
            print(f"  Reserve-eligible: {reserve_eligible_weight(weights, SLEEVES):.1%}")
            print(f"  Meets objective: {'yes' if meets_objective(result, OBJECTIVE_RETURN) else 'no'}")
    except ValueError as error:
        print(f"Cannot run: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
