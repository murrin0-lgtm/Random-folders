"""Reproduce Lab 14 checks: py python/verify_portfolio.py from repo root."""

from pathlib import Path
import subprocess
import sys
import tempfile

import mandate
import portfolio


def main():
    source = Path(portfolio.__file__).read_text(encoding="utf-8")
    covariance = portfolio.build_covariance_matrix(portfolio.SLEEVES, portfolio.CORRELATIONS)
    known = {
        "Benchmark": ("0.0 / 0.0 / 40.0 / 60.0", "6.80%", "10.46%", "0.0%", True),
        "Equal weight": ("25.0 / 25.0 / 25.0 / 25.0", "5.20%", "5.21%", "50.0%", False),
        "Inverse volatility": ("84.3 / 6.0 / 7.0 / 2.6", "3.77%", "1.05%", "90.3%", False),
    }
    for name, weights in portfolio.define_portfolios(portfolio.SLEEVES).items():
        result = portfolio.expected_return(weights, portfolio.SLEEVES)
        actual = (
            " / ".join(f"{w * 100:.1f}" for w in weights),
            f"{result:.2%}",
            f"{portfolio.portfolio_volatility(weights, covariance):.2%}",
            f"{portfolio.reserve_eligible_weight(weights, portfolio.SLEEVES):.1%}",
            portfolio.meets_objective(result, portfolio.OBJECTIVE_RETURN),
        )
        assert actual == known[name], (name, actual)
        print(f"PASS: {name} matches every known-answer value")

    # Run edited copies as actual programs; the submitted input file stays intact.
    cases = [
        ("IG-equity correlation 0.50 in both cells",
         source.replace("0.25", "0.50"), 0, "Volatility: 11.00%"),
        ("Out-of-range correlation 1.3",
         source.replace("0.25", "1.3"), 1, "must be between -1 and 1"),
        ("Asymmetric correlation table",
         source.replace("0.25", "0.50", 1), 1, "must be symmetric"),
    ]
    with tempfile.TemporaryDirectory() as directory:
        test_file = Path(directory) / "portfolio.py"
        for label, edited_source, expected_code, message in cases:
            test_file.write_text(edited_source, encoding="utf-8")
            run = subprocess.run([sys.executable, str(test_file)], capture_output=True, text=True)
            assert run.returncode == expected_code, run.stdout + run.stderr
            assert message in run.stdout + run.stderr, run.stdout + run.stderr
            print(f"PASS: {label}: {message}")

    assert Path(portfolio.__file__).read_text(encoding="utf-8") == source
    reserve_minimum = mandate.QUARTERS_TO_COVER * mandate.QUARTERLY_DISTRIBUTION / mandate.RESERVE_SIZE * 100
    checks = mandate.check_candidate(mandate.CANDIDATES["E"], reserve_minimum)
    failures = [(label, value) for label, value, passed in checks if not passed]
    assert failures == [(f"Reserve >= {reserve_minimum:.1f}%", 0)]
    print("PASS: Candidate E fails only the reserve rule, with 0.0% reserve")
    print("PASS: Original portfolio.py is unchanged; IG-equity correlation remains 0.25")


if __name__ == "__main__":
    main()
