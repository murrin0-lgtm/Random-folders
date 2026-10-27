"""Lab 16 known answers, actual later-date run, and rule boundary checks."""
from pathlib import Path
import subprocess
import sys
import tempfile

import asof


def main():
    panel, audit = asof.asof_panel(asof.ROWS, "2026-03-31")
    assert [[r["row"] for r in removed] for _, removed in audit] == [[11], [7], [3, 8, 10], [2]]
    assert [r["row"] for r in panel] == [1, 4, 5, 6, 9, 12]
    point_in_time = asof.signals(panel)
    naive = asof.signals(asof.naive_panel(asof.ROWS))
    expected = {"AAA": ("+1.98%", "2026-02", "+5.83%", "2026-03"),
                "BBB": ("-1.02%", "2026-02", "-5.15%", "2026-03"),
                "CCC": ("+0.91%", "2026-02", "+1.82%", "2026-02")}
    for ticker, (pit_value, pit_month, naive_value, naive_month) in expected.items():
        assert f"{point_in_time[ticker]['value']:+.2%}" == pit_value
        assert point_in_time[ticker]["month"] == pit_month
        assert f"{naive[ticker]['value']:+.2%}" == naive_value
        assert naive[ticker]["month"] == naive_month
    print("PASS: complete row funnel, panel, all six signals and their months")

    later, later_audit = asof.asof_panel(asof.ROWS, "2026-04-15")
    assert asof.signals(later) == naive
    assert [r["row"] for r in later] == [1, 3, 4, 5, 6, 8, 9, 10]
    assert later_audit[2][1] == []
    print("PASS: April 15 as-of signals equal naive signals, ticker for ticker")

    source = Path(asof.__file__).read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as directory:
        changed = Path(directory) / "asof.py"
        changed.write_text(source.replace('DECISION_DATE = "2026-03-31"',
                                         'DECISION_DATE = "2026-04-15"'), encoding="utf-8")
        result = subprocess.run([sys.executable, str(changed)], capture_output=True, text=True, check=True)
        assert "Decision date: 2026-04-15" in result.stdout
        for ticker in naive:
            assert f"{ticker}: as-of {asof.format_signal(naive[ticker])}" in result.stdout
    assert Path(asof.__file__).read_text(encoding="utf-8") == source
    print("PASS: edited-copy command-line run; original decision date remains March 31")

    # A publication on the decision date must pass; April 5 admits CCC's revision.
    boundary, _ = asof.asof_panel(asof.ROWS, "2026-03-25")
    assert 4 in [r["row"] for r in boundary]
    april5, _ = asof.asof_panel(asof.ROWS, "2026-04-05")
    assert asof.signals(april5)["CCC"]["rows"] == [9, 10]
    assert 3 not in [r["row"] for r in april5]
    reversed_panel, _ = asof.asof_panel(list(reversed(asof.ROWS)), "2026-03-31")
    assert asof.signals(reversed_panel)["AAA"]["value"] == point_in_time["AAA"]["value"]
    missing_month = [r for r in asof.ROWS if r["row"] in (1, 3)]
    assert asof.signals(missing_month)["AAA"]["value"] is None
    print("PASS: inclusive date boundary, intermediate revision, unsorted input and missing month")

    expected_yields = {1: "-0.99%", 4: "-2.91%", 5: "+2.04%", 6: "+3.09%", 9: "-9.09%", 12: "-9.91%"}
    for row in panel:
        result = f"{asof.zero_coupon_yield(row['price']):+.2%}"
        assert result == expected_yields[row["row"]]
        print(f"PASS: sanity calculation row {row['row']}: yield {result}")


if __name__ == "__main__":
    main()
