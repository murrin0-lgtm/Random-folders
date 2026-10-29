"""Pure CSV parsing and point-in-time comparison for the Lab 17 app."""
import csv
from datetime import date
import io
import math
import re
from urllib.request import Request, urlopen

SERIES = {
    "BAA": "Moody's Baa corporate bond yield",
    "FEDFUNDS": "Effective federal funds rate",
    "DGS10": "10-year Treasury yield",
    "MORTGAGE30US": "30-year fixed mortgage rate",
}


def validate_id(series_id):
    series_id = series_id.strip().upper()
    if not re.fullmatch(r"[A-Z0-9_]{1,80}", series_id):
        raise ValueError("Use a FRED series ID containing letters, numbers or underscores.")
    return series_id


def download_csv(url):
    request = Request(url)
    with urlopen(request, timeout=45) as response:
        return response.read().decode("utf-8-sig")


def parse_csv(text):
    rows = list(csv.reader(io.StringIO(text)))
    if not rows or len(rows[0]) != 2 or rows[0][0].lower() not in {"observation_date", "date"}:
        raise ValueError("The source did not return a two-column observation CSV. Check the series ID.")
    values = {}
    for row in rows[1:]:
        if not row:
            continue
        if len(row) != 2:
            raise ValueError("Unexpected CSV row; no data were silently discarded.")
        measured = date.fromisoformat(row[0])
        raw = row[1].strip()
        value = None if raw in {".", ""} else float(raw)
        if value is not None and not math.isfinite(value):
            raise ValueError("Nonfinite source value.")
        if measured in values:
            raise ValueError("Duplicate observation date in source snapshot.")
        values[measured] = value
    if not any(value is not None for value in values.values()):
        raise ValueError("No numeric observations available for this series and vintage.")
    return values


def compare_snapshots(current, vintage, start):
    """Counts use the selected start date; latest dates use full source history.

    A missing observation (including a holiday '.') is never a zero or revision.
    """
    now_valid = {day: value for day, value in current.items() if value is not None}
    then_valid = {day: value for day, value in vintage.items() if value is not None}
    now_date, then_date = max(now_valid), max(then_valid)
    common = sorted(day for day in now_valid.keys() & then_valid.keys() if day >= start)
    revisions = [day for day in common
                 if not math.isclose(now_valid[day], then_valid[day], rel_tol=0, abs_tol=1e-9)]
    later = [day for day in now_valid if day >= start and day > then_date]
    return {"known_date": then_date, "known_value": then_valid[then_date],
            "today_date": now_date, "today_value": now_valid[now_date],
            "later_count": len(later), "revised_count": len(revisions),
            "revised_dates": revisions}
