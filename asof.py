"""Lab 16 provenance gate; standard library only.

From the repository root: py python/asof.py
From this folder: python asof.py (or py asof.py on this computer).
"""

from datetime import date

# Editable inputs. Row numbers are source identifiers, not list positions.
DECISION_DATE = "2026-03-31"
ROWS = [
    {"row": 1, "ticker": "AAA", "month": "2026-01", "published": "2026-02-10", "price": 101.0},
    {"row": 2, "ticker": "AAA", "month": "2026-02", "published": "2026-03-10", "price": 104.0},
    {"row": 3, "ticker": "AAA", "month": "2026-03", "published": "2026-04-10", "price": 109.0},
    {"row": 4, "ticker": "AAA", "month": "2026-02", "published": "2026-03-25", "price": 103.0},
    {"row": 5, "ticker": "BBB", "month": "2026-01", "published": "2026-02-10", "price": 98.0},
    {"row": 6, "ticker": "BBB", "month": "2026-02", "published": "2026-03-10", "price": 97.0},
    {"row": 7, "ticker": "BBB", "month": "2026-02", "published": "2026-03-10", "price": 97.0},
    {"row": 8, "ticker": "BBB", "month": "2026-03", "published": "2026-04-10", "price": 92.0},
    {"row": 9, "ticker": "CCC", "month": "2026-01", "published": "2026-02-10", "price": 110.0},
    {"row": 10, "ticker": "CCC", "month": "2026-02", "published": "2026-04-05", "price": 112.0},
    {"row": 11, "ticker": "", "month": "2026-02", "published": "2026-03-10", "price": 99.0},
    {"row": 12, "ticker": "CCC", "month": "2026-02", "published": "2026-03-10", "price": 111.0},
]


def quarantine_missing_tickers(rows):
    """Rule 1: retain source IDs for quarantined rows."""
    accepted, quarantined = [], []
    for row in rows:
        (accepted if row["ticker"].strip() else quarantined).append(row)
    return accepted, quarantined


def remove_exact_duplicates(rows):
    """Rule 2: row ID is provenance, so exclude it from the duplicate key."""
    seen = set()
    accepted, removed = [], []
    for row in rows:
        key = (row["ticker"], row["month"], row["published"], row["price"])
        if key in seen:
            removed.append(row)
        else:
            seen.add(key)
            accepted.append(row)
    return accepted, removed


def remove_future_publications(rows, decision_date):
    """Rule 3: a publication ON the decision date is knowable too."""
    cutoff = date.fromisoformat(decision_date)
    accepted, removed = [], []
    for row in rows:
        target = accepted if date.fromisoformat(row["published"]) <= cutoff else removed
        target.append(row)
    return accepted, removed


def keep_latest_publications(rows):
    """Rule 4: use only eligible rows supplied by earlier rules.

    The naive comparison deliberately supplies rows without a publication cutoff.
    """
    latest = {}
    for row in rows:
        key = (row["ticker"], row["month"])
        previous = latest.get(key)
        if previous is None or row["published"] > previous["published"]:
            latest[key] = row
        elif row["published"] == previous["published"] and row["price"] != previous["price"]:
            raise ValueError(f"Conflicting prices for {key} on the same publication date.")
    kept_ids = {row["row"] for row in latest.values()}
    accepted = [row for row in rows if row["row"] in kept_ids]
    replaced = [row for row in rows if row["row"] not in kept_ids]
    return accepted, replaced


def asof_panel(rows, decision_date):
    """Apply all four rules in order, returning the panel and row-level audit."""
    active = list(rows)
    audit = []
    active, removed = quarantine_missing_tickers(active)
    audit.append(("Quarantined: no ticker", removed))
    active, removed = remove_exact_duplicates(active)
    audit.append(("Exact duplicate", removed))
    active, removed = remove_future_publications(active, decision_date)
    audit.append((f"Published after {decision_date}", removed))
    active, removed = keep_latest_publications(active)
    audit.append(("Older vintage replaced by a revision", removed))
    return active, audit


def naive_panel(rows):
    """Same identity/duplicate cleanup, but ignore the publication cutoff."""
    active, _ = quarantine_missing_tickers(rows)
    active, _ = remove_exact_duplicates(active)
    active, _ = keep_latest_publications(active)
    return active


def signals(panel):
    """Latest month's price change from its preceding calendar month."""
    grouped = {}
    for row in panel:
        grouped.setdefault(row["ticker"], []).append(row)
    results = {}
    for ticker, rows in sorted(grouped.items()):
        ordered = sorted(rows, key=lambda row: row["month"])
        latest = ordered[-1]
        result = {"month": latest["month"], "value": None, "rows": [latest["row"]]}
        if len(ordered) >= 2:
            previous = ordered[-2]
            current_date = date.fromisoformat(latest["month"] + "-01")
            previous_date = date.fromisoformat(previous["month"] + "-01")
            consecutive = (current_date.year * 12 + current_date.month
                           - previous_date.year * 12 - previous_date.month == 1)
            if consecutive and previous["price"] != 0:
                result["value"] = latest["price"] / previous["price"] - 1
                result["rows"] = [previous["row"], latest["row"]]
        results[ticker] = result
    return results


def format_signal(signal):
    if signal is None:
        return "unavailable: no eligible observations"
    month = date.fromisoformat(signal["month"] + "-01").strftime("%B %Y")
    if signal["value"] is None:
        return f"unavailable ({month}; consecutive previous-month price required)"
    return f"{signal['value']:+.2%} ({month}; source rows {signal['rows']})"


def zero_coupon_yield(price):
    """Separate economic sanity calculation; not one of the provenance rules."""
    return 100 / price - 1


def main():
    panel, audit = asof_panel(ROWS, DECISION_DATE)
    print(f"Decision date: {DECISION_DATE}")
    print(f"Starting rows: {len(ROWS)}")
    print("\nRow funnel (each count applies after the preceding rule)")
    for label, removed in audit:
        print(f"  {label}: {len(removed)}; source rows {[row['row'] for row in removed]}")
    print(f"  As-of panel: {len(panel)}; source rows {[row['row'] for row in panel]}")
    print("\nAs-of panel")
    print("Row  Ticker  Month measured  Published on  Price")
    for row in panel:
        print(f"{row['row']:>3}  {row['ticker']:<6}  {row['month']:<14}  "
              f"{row['published']}  {row['price']:.1f}")
    point_in_time = signals(panel)
    naive = signals(naive_panel(ROWS))
    print("\nSignals: price change from previous month to latest available month")
    for ticker in sorted(set(point_in_time) | set(naive)):
        print(f"{ticker}: as-of {format_signal(point_in_time.get(ticker))}")
        print(f"     naive {format_signal(naive.get(ticker))}")
    print("\nNaive ignores publication dates; it is not a point-in-time trading signal.")


if __name__ == "__main__":
    main()
