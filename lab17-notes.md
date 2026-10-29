# Lab 17 - Point-in-Time Audit

## Decision question

Was each number in my series knowable on the day I would have traded on it, and may Project 2 use it?

Selected series: DGS10, confirmed for this lab. Built with AI help; a learning demonstration, not investment advice. Source downloads and checks below were performed October 29, 2026. The practice exchanges and proposed decision are drafts for review, not a record of partner participation or the student's own source checks.

## Run the app

From the repository root:

```powershell
py -m pip install -r python/requirements-lab17.txt
py -m streamlit run python/asof_app.py --server.port 8502
```

Open `http://localhost:8502`. The different port allows the Lab 15 app to remain on 8501. No API key, account or ALFRED login is needed.

```powershell
py python/verify_lab17.py
py python/verify_lab17_ui.py
```

The first command verifies live downloads and saves raw evidence; the second replays those real responses to check the app controls without making additional requests.

## What the app does

- Begins with BAA, FEDFUNDS, DGS10 and MORTGAGE30US selected; accepts an additional typed series ID such as PAYEMS.
- Starts the charts on January 1, 2020, with the vintage date set to the current local date.
- Uses one cached download function for today's FRED CSV and a separate cached function for the ALFRED vintage CSV. Successful responses are reused for one hour; a new date is a different cache key.
- Draws a chart of today's history for each selected series and displays its last numeric date known in the requested vintage.
- Shows the latest vintage and current dates/values, later-observation counts and matching-date revision counts. Each series links to its FRED page.
- Treats a dot or empty source cell as missing, not zero. Missing observations do not count as later numeric values or numeric revisions.
- Catches an unknown series or download error for that series, leaving the other series usable. Errors are not replaced with made-up values.

The table's counts begin on the selected start date. Latest known dates use each full source snapshot. A later count measures observations after the vintage's last numeric date; it is not a count of every potential missing value inside the earlier window. Revisions compare dates with numeric values in both snapshots. The CSV response for a vintage gives the archived information set; it does not identify every row's first publication timestamp.

## Verified known answer: As known on October 5, 2026

All four live ALFRED observations matched the handout. Monthly dates appear as the first day of the measured month in the raw CSV.

| Series | Last date known then | Value known then | Last date in today's download | Value today | Later numeric values | Revised matching dates |
|---|---|---:|---|---:|---:|---:|
| BAA | September 2026 | 6.47 | September 2026 | 6.47 | 0 | 0 |
| FEDFUNDS | September 2026 | 3.75 | September 2026 | 3.75 | 0 | 0 |
| DGS10 | October 2, 2026 | 5.28 | October 27, 2026 | 4.99 | 16 | 0 |
| MORTGAGE30US | October 1, 2026 | 7.28 | October 29, 2026 | 7.24 | 4 | 0 |

Values are annualized percentage rates in their source conventions. These are measured-date labels, not publication dates. The current column is the response downloaded on October 29 and may change when the app is refreshed after a new release.

## PAYEMS probe: Does the app actually use an older vintage?

For an as-known date of **January 15, 2025**, PAYEMS's latest available month was December 2024, with **159,536 thousand persons**. Today's value for that SAME December 2024 observation is **158,316 thousand persons**, a downward revision of 1,220 thousand persons. Today's latest month is September 2026, at 159,044 thousand persons; that is a different observation and is not the December revision comparison.

With the count window starting January 2020, the audit finds **59 revised matching dates** and **21 later monthly observations**. The nonzero same-date revision count and changed December observation demonstrate that the app is not downloading today's history twice. PAYEMS units and seasonal adjustment are documented on its [FRED page](https://fred.stlouisfed.org/series/PAYEMS).

## DGS10 data card

| Field | Evidence and rule |
|---|---|
| Series ID | DGS10 |
| Source and link | Board of Governors of the Federal Reserve System, H.15, distributed by the Federal Reserve Bank of St. Louis: [FRED DGS10](https://fred.stlouisfed.org/series/DGS10); historical snapshots: [ALFRED DGS10](https://alfred.stlouisfed.org/series?seid=DGS10). |
| Measure | Market yield on U.S. Treasury securities at 10-year constant maturity, quoted on an investment basis. It is a yield, not a fund price or realized total return. |
| Units and frequency | Percent per annum; daily; not seasonally adjusted. For calculations needing a decimal rate, 5.26% becomes 0.0526. A change from 5.26% to 4.99% is -0.27 percentage points. |
| Publication lag | A short business-day lag is observed: the September 30 vintage ends at September 29. The FRED page labels October 27's observation as updated October 28. H.15 posts at 4:15 p.m. on weekdays, excluding holidays/closures; the exact usable information depends on trade time. Never assume observation date equals publication time. |
| Revisions | No changed matching values in the comparisons below, starting January 2020. This is evidence for these snapshots, not proof that corrections are impossible. |
| Missing values | Dots/blank cells remain missing. No zero substitution or invented observation for holidays. |
| Download date | October 29, 2026; exact UTC retrieval times, URLs and SHA-256 hashes are preserved in `data/lab17/audit_results.json`. |
| As-of usage rule | Select the ALFRED snapshot appropriate to each historical decision. For an intraday trade, use a prior completed vintage unless the release timestamp can be proved to precede the trade. Do not substitute today's values using an assumed fixed lag. |

Measure, units, frequency and update labels: [FRED DGS10](https://fred.stlouisfed.org/series/DGS10). Release schedule and constant-maturity description: [Federal Reserve H.15](https://www.federalreserve.gov/releases/h15/).

## DGS10 experiment: Last day of last month versus today

| As known on | Last measured date available | Yield | Later values now present | Revised matching dates |
|---|---|---:|---:|---:|
| September 30, 2026 | September 29, 2026 | 5.26% | 19 | 0 |
| October 29, 2026 | October 27, 2026 | 4.99% | 0 | 0 |

Nineteen numeric observations in today's history come after the September 29 endpoint and vanish when that earlier archived information set is used. The lag is short relative to a monthly macro series, but it is not zero. Matching historical values in this selected period were unchanged; their omission from the earlier vintage was a timing issue, not a revision.

## Three source-value checks:

The downloaded current DGS10 CSV was compared by AI with the visible observations on the [FRED DGS10 page](https://fred.stlouisfed.org/series/DGS10), October 29, 2026:

| Measured date | Downloaded CSV | FRED page | AI check |
|---|---:|---:|---|
| October 27, 2026 | 4.99 | 4.99 | Match |
| October 26, 2026 | 5.00 | 5.00 | Match |
| October 23, 2026 | 5.00 | 5.00 | Match |

### Self-check

I checked DGS10 for October 27, 26, and 23, 2026 against the FRED page. The app and FRED showed 4.99%, 5.00%, and 5.00% respectively. I checked this on 10/29/26

### Practice opener question: Why might this rate move my fund universe?

Treasury yields affect the pricing environment for my government and investment-grade bond funds, including IEF and LQD. Higher yields generally lower the prices of existing fixed-rate bonds, while lower yields generally raise them, although duration and credit spreads also matter. DGS10 is context for my universe, not a substitute for the funds' adjusted-price returns.


### Explain the vintage-download function line by line

The function is download_as_known in python/asof_app.py:

```python
@st.cache_data(ttl=3600, show_spinner=False)
def download_as_known(series_id, as_known_on, download_day):
    series_id = validate_id(series_id)
    vintage_date = date.fromisoformat(str(as_known_on)).isoformat()
    url = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?" + urlencode(
        {"id": series_id, "vintage_date": vintage_date})
    text = download_csv(url)
    return {"values": parse_csv(text), "raw": text, "url": url,
            "downloaded_at": datetime.now(timezone.utc).isoformat()}
```

| Line | Explanation |
|---|---|
| `@st.cache_data(...)` | Reuses a successful result for matching arguments for up to 3,600 seconds. The series, vintage and download-day arguments all affect the cache key. |
| `def download_as_known(...)` | Defines the function called by the app for the historical information set. `download_day` separates today's cache from a previous day's cache. |
| `validate_id(...)` | Normalizes the series ID and rejects invalid characters. |
| `date.fromisoformat(...).isoformat()` | Validates and formats the vintage date as YYYY-MM-DD. |
| `url = ...` and `urlencode(...)` | Builds the ALFRED URL with both the series ID and the requested vintage date. This is the crucial difference from the current FRED request. |
| `text = download_csv(url)` | Makes the public request and reads the original response. |
| `parse_csv(text)` | Parses dates and numbers, preserving missing observations as `None`. |
| Remaining returned fields | Retain the raw response, requested URL and actual UTC download timestamp for audit evidence. |

### Practice partner question: Does a zero revision count mean I can use today's data for past trades?

No. The count only compares dates present in both snapshots. later observations were not available at the earlier decision. DGS10 has zero matching-date revisions here but 19 later observations after the September-end snapshot, so availability still matters.

### Practice quiz question: What happens when I change only the as-known date?

The ALFRED request gets a different vintage_date and therefore a different cache key. Today's FRED history can stay cached, while the app recomputes the comparison using the newly selected historical snapshot. This is practice material, not an actual answer-before-explanation quiz record.


#### Partner attack: He asked: How do you know this rate was published before your trade?

I checked the ALFRED snapshot for the decision date to see whether that observation was available then. Because the snapshot doesn't prove the exact publication time, I would use a prior completed vintage for an intraday trade unless I could verify the release happened before the trade.

Evidence: The September 30 ALFRED snapshot ends at Sept. 29, showing that an observation's measured date doesn't guarantee availability that day. H.15's 4:15 p.m. release schedule also means a date only snapshot can't prove the rate was available before an earlier intraday trade.


#### Proposed call: Admit

I would allow DGS10 as a contextual interest-rate input only using the ALFRED vintage available at each decision date. My comparison found 19 later observations and no revisions on matching dates, showing that publication timing still matters. For intraday trades, I'd use a prior completed vintage unless I could verify publication before the trade. I would quarantine the series if the appropriate vintage or timing evidence were unavailable.

##### Learn: What is a data card, and which fields prevent a leak?

A data card records a series' identity, source, meaning, units, frequency, publication timing, revision behavior, download date and permitted use. The source/ID prevents using the wrong series; units prevent treating a percent rate as a decimal or price; publication timing and archived vintages prevent importing future information; revision evidence warns against using a revised history as if it were available originally. Retrieval timestamps and saved snapshots make the claim reproducible.

“Cleaned the data” does not name the source, explain the units, establish availability or identify a vintage. A cleaned current series can still leak future publications or revisions into a backtest.

##### Practice reflection question: How late is DGS10 published, and what does the as-known control show?

It has a short observed business-day lag, not immediate availability at the measured date. September 30's archived snapshot stops at September 29, while today's data reaches October 27; moving the control backward removes observations that had not entered the earlier archive.

##### Practice reflection question: What would a backtest on today's values overstate?

It could overstate how current the strategy's information was and how quickly it could react to rate changes. This DGS10 comparison found no numeric revisions on matching dates, so I cannot claim measured revision-driven performance inflation here; the demonstrated issue is access to later observations. A performance effect requires an actual trading rule and cannot be inferred from the count alone.

Submit these main GitHub links:

- `python/asof_app.py` - the app and two cached download functions.
- `python/rates_audit.py` - imported parsing and comparison functions; required to run the app.
- `notes/lab17-notes.md` - the data card, results, explanations and proposed call.

Include supporting files in the repository: `python/requirements-lab17.txt`, `python/verify_lab17.py`, `python/verify_lab17_ui.py`, and `data/lab17/` with the raw source CSVs and audit manifest. The app reads live sources, not hard-coded test values or the saved test snapshots.