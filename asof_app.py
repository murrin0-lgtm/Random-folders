"""Lab 17: py -m streamlit run python/asof_app.py"""
from datetime import date, datetime, timezone
from urllib.parse import urlencode

import pandas as pd
import streamlit as st

from rates_audit import SERIES, compare_snapshots, download_csv, parse_csv, validate_id


@st.cache_data(ttl=3600, show_spinner=False)
def download_today(series_id, download_day):
    """One FRED request per series/cache period; retain response and timestamp."""
    series_id = validate_id(series_id)
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?" + urlencode({"id": series_id})
    text = download_csv(url)
    return {"values": parse_csv(text), "raw": text, "url": url,
            "downloaded_at": datetime.now(timezone.utc).isoformat()}


@st.cache_data(ttl=3600, show_spinner=False)
def download_as_known(series_id, as_known_on, download_day):
    """A genuine ALFRED vintage snapshot, not today's data with a fixed lag."""
    series_id = validate_id(series_id)
    vintage_date = date.fromisoformat(str(as_known_on)).isoformat()
    url = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?" + urlencode(
        {"id": series_id, "vintage_date": vintage_date})
    text = download_csv(url)
    return {"values": parse_csv(text), "raw": text, "url": url,
            "downloaded_at": datetime.now(timezone.utc).isoformat()}


def main():
    today = date.today()
    st.set_page_config(page_title="Point-in-Time Rates Audit", layout="wide")
    st.title("Point-in-Time Rates Audit")
    st.caption(f"Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, downloaded {today:%Y-%m-%d}; "
               "built with AI help, a learning demonstration, not investment advice.")
    chosen = st.sidebar.multiselect("Series", list(SERIES), default=list(SERIES), key="chosen",
                                    format_func=lambda key: f"{key} — {SERIES[key]}")
    extra = st.sidebar.text_input("Add another FRED series ID", placeholder="e.g. PAYEMS", key="extra")
    start = st.sidebar.date_input("Start date", value=date(2020, 1, 1), max_value=today)
    known_on = st.sidebar.date_input("As known on", value=today, max_value=today, key="known-on")
    if extra.strip():
        try:
            extra_id = validate_id(extra)
            if extra_id not in chosen:
                chosen.append(extra_id)
        except ValueError as error:
            st.error(f"Additional series: {error}")
    st.caption("Counts begin at the selected start date. ‘Later’ counts numeric observations after the last "
               "date known then; ‘revised’ compares numeric values on matching observation dates. "
               "Missing days are gaps, never zero. Latest observation dates use the complete downloads.")
    if start > known_on:
        st.info("The chart starts after the vintage date. Latest known dates still use full history; "
                "revision counts in this selected window may be zero.")
    summaries = []
    for series_id in chosen:
        st.subheader(f"{series_id} — {SERIES.get(series_id, 'Additional FRED series')}")
        try:
            with st.spinner(f"Loading {series_id} from FRED and ALFRED…"):
                current = download_today(series_id, today.isoformat())
                vintage = download_as_known(series_id, known_on.isoformat(), today.isoformat())
            summary = compare_snapshots(current["values"], vintage["values"], start)
            chart_rows = [{"Date": day, "Today's value": value}
                          for day, value in sorted(current["values"].items()) if day >= start]
            if chart_rows:
                frame = pd.DataFrame(chart_rows).set_index("Date")
                st.line_chart(frame, x_label="Date measured",
                              y_label="Percent" if series_id in SERIES else "Source units (see FRED)")
            else:
                st.info("No observations in the selected chart window.")
            st.write(f"Last numeric observation known on {known_on}: "
                     f"**{summary['known_date']}**, value **{summary['known_value']:,.4g}**.")
            st.caption(f"[FRED series page](https://fred.stlouisfed.org/series/{series_id}) · "
                       f"[Today's CSV]({current['url']}) · [Vintage CSV]({vintage['url']}) · "
                       f"Fetched UTC: {current['downloaded_at']} / {vintage['downloaded_at']}")
            summaries.append({"Series": f"https://fred.stlouisfed.org/series/{series_id}",
                              "Last measured date known then": summary["known_date"],
                              "Value known then": summary["known_value"],
                              "Last measured date today": summary["today_date"],
                              "Value today": summary["today_value"],
                              "Later numeric values": summary["later_count"],
                              "Revised matching dates": summary["revised_count"]})
        except Exception as error:
            st.error(f"{series_id}: could not load or compare this series: {error}")
            st.caption("Other selected series continue independently. Try another ID or vintage date.")
    st.subheader("As-known comparison")
    if summaries:
        st.dataframe(pd.DataFrame(summaries), hide_index=True, width="stretch",
                     column_config={"Series": st.column_config.LinkColumn("Series", display_text=r"series/(.*)"),
                                    "Value known then": st.column_config.NumberColumn(format="%.4f"),
                                    "Value today": st.column_config.NumberColumn(format="%.4f")})
    else:
        st.info("Select a valid series with data available for the chosen vintage.")
    st.caption("An ALFRED snapshot identifies what the archive exposed on that date; it does not provide "
               "each row's exact intraday publication time. Zero revisions in this comparison does not "
               "prove a series can never be corrected.")


if __name__ == "__main__":
    main()
