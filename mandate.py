"""Meridian Foundation mandate checker. Run: python python/mandate.py"""

# Editable inputs: weights are percentages; monetary amounts are USD millions.
HOLDINGS = {
    "Cash": {"issuer": "none", "days": 0, "reserve_eligible": True},
    "Treasury bills": {"issuer": "U.S. Treasury", "days": 1, "reserve_eligible": True},
    "Treasury 10-year note": {"issuer": "U.S. Treasury", "days": 1, "reserve_eligible": True},
    "Global equity index fund": {"issuer": "diversified fund", "days": 2, "reserve_eligible": False},
    "Investment-grade bond fund": {"issuer": "diversified fund", "days": 3, "reserve_eligible": False},
    "Private real estate fund": {"issuer": "diversified fund", "days": 90, "reserve_eligible": False},
    "Acme Corp bonds": {"issuer": "Acme Corp", "days": 4, "reserve_eligible": False},
    "Acme Corp stock": {"issuer": "Acme Corp", "days": 1, "reserve_eligible": False},
}
# Each row follows the holding order above, including zero-weight positions.
CANDIDATES = {
    "A": dict(zip(HOLDINGS, [2, 2, 10, 60, 26, 0, 0, 0])),
    "B": dict(zip(HOLDINGS, [1, 0, 0, 55, 20, 15, 5, 4])),
    "C": dict(zip(HOLDINGS, [1, 1, 0, 70, 20, 0, 0, 8])),
    "D": dict(zip(HOLDINGS, [100, 0, 0, 0, 0, 0, 0, 0])),
}
RESERVE_SIZE = 100
QUARTERLY_DISTRIBUTION = 0.75
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW = 5
MINIMUM_LIQUID_SHARE = 90
ISSUER_LIMIT = 8
EXEMPT_ISSUERS = {"none", "U.S. Treasury", "diversified fund"}
TOLERANCE = 1e-9


def check_candidate(weights, reserve_minimum):
    """Return measured values and pass flags, computed only from inputs."""
    if set(weights) != set(HOLDINGS):
        raise ValueError("Each candidate must specify every holding exactly once.")
    company_weights = {}
    for holding, weight in weights.items():
        issuer = HOLDINGS[holding]["issuer"]
        if issuer not in EXEMPT_ISSUERS:
            company_weights[issuer] = company_weights.get(issuer, 0) + weight
    total = sum(weights.values())
    lowest = min(weights.values())
    reserve = sum(w for h, w in weights.items() if HOLDINGS[h]["reserve_eligible"])
    liquid = sum(w for h, w in weights.items() if HOLDINGS[h]["days"] <= LIQUIDITY_WINDOW)
    largest_company = max(company_weights.values(), default=0)
    return [
        ("Weights sum to 100", total, abs(total - 100) <= TOLERANCE),
        ("Long-only (lowest weight)", lowest, lowest >= -TOLERANCE),
        (f"Reserve >= {reserve_minimum:.1f}%", reserve, reserve >= reserve_minimum - TOLERANCE),
        (f"Redeemable in {LIQUIDITY_WINDOW} days >= {MINIMUM_LIQUID_SHARE:.1f}%", liquid, liquid >= MINIMUM_LIQUID_SHARE - TOLERANCE),
        (f"Largest single company <= {ISSUER_LIMIT:.1f}%", largest_company, largest_company <= ISSUER_LIMIT + TOLERANCE),
    ]


def main():
    reserve_minimum = QUARTERS_TO_COVER * QUARTERLY_DISTRIBUTION / RESERVE_SIZE * 100
    print(f"Reserve minimum: {reserve_minimum:.1f}%")
    for name, weights in CANDIDATES.items():
        print(f"\nCandidate {name}")
        checks = check_candidate(weights, reserve_minimum)
        for label, value, passed in checks:
            print(f"  {label}: {value:.1f} {'pass' if passed else 'FAIL'}")
        print("  Calendar-year loss: requires CIO clarification")
        failures = sum(not passed for _, _, passed in checks)
        print("  " + (f"fails {failures} rule(s)" if failures else "passes every checkable rule"))


if __name__ == "__main__":
    main()
