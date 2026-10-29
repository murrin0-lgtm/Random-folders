"""Live Lab 17 checks; preserve raw sources, hashes and computed evidence."""
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path

from asof_app import download_today, download_as_known
from rates_audit import SERIES, compare_snapshots, parse_csv

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "lab17"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    today = date.today()
    start = date(2020, 1, 1)
    evidence = {"download_date": today.isoformat(), "count_start": start.isoformat(),
                "training": {}, "sources": [], "failures": []}

    def save(series_id, kind, response):
        path = OUT / f"{series_id}_{kind}.csv"
        path.write_text(response["raw"], encoding="utf-8")
        evidence["sources"].append({"file": str(path.relative_to(ROOT)), "url": response["url"],
                                   "downloaded_at": response["downloaded_at"],
                                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

    def pair(series_id, known_on):
        now = download_today(series_id, today.isoformat())
        then = download_as_known(series_id, known_on, today.isoformat())
        save(series_id, f"today_{today}", now)
        save(series_id, f"asof_{known_on}", then)
        return now, then, compare_snapshots(now["values"], then["values"], start)

    # Expected values appear only in tests, never in the app or download logic.
    expected = {"BAA": ("2026-09-01", 6.47), "FEDFUNDS": ("2026-09-01", 3.75),
                "DGS10": ("2026-10-02", 5.28), "MORTGAGE30US": ("2026-10-01", 7.28)}
    for series_id, (day, value) in expected.items():
        _, _, result = pair(series_id, "2026-10-05")
        evidence["training"][series_id] = result
        passed = result["known_date"].isoformat() == day and abs(result["known_value"] - value) < 1e-9
        if not passed:
            evidence["failures"].append(f"{series_id} differs from handout")
        print(f"{'PASS' if passed else 'FAIL'}: {series_id}: {result}")

    now, then, result = pair("PAYEMS", "2025-01-15")
    december = date(2024, 12, 1)
    result["december_2024_then"] = then["values"].get(december)
    result["december_2024_today"] = now["values"].get(december)
    evidence["payems"] = result
    passed = (result["known_date"] == december and result["known_value"] == 159536
              and now["values"][december] < 159536 and result["revised_count"] > 0)
    if not passed:
        evidence["failures"].append("PAYEMS differs from handout")
    print(f"{'PASS' if passed else 'FAIL'}: PAYEMS probe: {result}")

    last_month = today.replace(day=1) - timedelta(days=1)
    evidence["dgs10"] = {}
    for label, day in [("last_month_end", last_month), ("today", today)]:
        now, then, result = pair("DGS10", day.isoformat())
        evidence["dgs10"][label] = result
        print(f"DGS10 {label}: {result}")
    evidence["dgs10"]["three_source_checks"] = [
        {"date": day.isoformat(), "value": value} for day, value in
        sorted(((d, v) for d, v in now["values"].items() if v is not None), reverse=True)[:3]]

    # Independent tiny CSV check: missing days do not count as new data or revisions.
    current = parse_csv("observation_date,X\n2020-01-01,1\n2020-01-02,.\n2020-01-03,3\n2020-01-06,4\n")
    vintage = parse_csv("observation_date,X_20200103\n2020-01-01,2\n2020-01-02,.\n2020-01-03,3\n")
    counts = compare_snapshots(current, vintage, start)
    assert counts["later_count"] == 1 and counts["revised_count"] == 1
    assert compare_snapshots(current, vintage, date(2020, 1, 3))["revised_count"] == 0
    print("PASS: missing-day parsing, same-date revision comparison and start-date scope")
    (OUT / "audit_results.json").write_text(json.dumps(evidence, indent=2, default=str), encoding="utf-8")
    if evidence["failures"]:
        raise AssertionError(evidence["failures"])


if __name__ == "__main__":
    main()
