"""Streamlit tests replay actual saved source responses, without more requests."""
from datetime import date
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent


def saved_response(url):
    query = parse_qs(urlparse(url).query)
    series = query["id"][0]
    if series == "NOT_A_REAL_LAB17_SERIES":
        raise ValueError("Unknown series ID (test of independent error handling)")
    vintage = query.get("vintage_date")
    suffix = f"asof_{vintage[0]}" if vintage else f"today_{date.today()}"
    return (ROOT / "data/lab17" / f"{series}_{suffix}.csv").read_text(encoding="utf-8")


def main():
    with patch("rates_audit.download_csv", side_effect=saved_response):
        app = AppTest.from_file(str(ROOT / "python/asof_app.py"))
        app.session_state["known-on"] = date(2026, 10, 5)
        app.run(timeout=45)
        assert not app.exception, app.exception
        assert not app.error, app.error
        assert len(app.get("arrow_vega_lite_chart")) + len(app.get("vega_lite_chart")) == 4, str(app)
        frame = app.dataframe[0].value
        assert list(frame["Value known then"]) == [6.47, 3.75, 5.28, 7.28], frame
        print("PASS: app renders four live-source replay charts and all known-answer table values")
        app.sidebar.text_input[0].set_value("NOT_A_REAL_LAB17_SERIES").run(timeout=45)
        assert not app.exception and len(app.error) == 1
        assert len(app.dataframe[0].value) == 4
        print("PASS: invalid ID produces a per-series error without breaking other results")
        app.sidebar.multiselect[0].set_value([])
        app.sidebar.text_input[0].set_value("PAYEMS")
        app.sidebar.date_input[1].set_value(date(2025, 1, 15))
        app.run(timeout=45)
        assert not app.exception and not app.error
        frame = app.dataframe[0].value
        assert frame.iloc[0]["Value known then"] == 159536
        assert frame.iloc[0]["Revised matching dates"] > 0
        print("PASS: typed PAYEMS and changed vintage show 159536 and nonzero revisions")


if __name__ == "__main__":
    main()
