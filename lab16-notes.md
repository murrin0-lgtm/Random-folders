# Lab 16 - Provenance Gate

## Decision question

On the day you would have traded, what did this data actually say, and how much of what you see now came later?

Decision date: **March 31, 2026**. Source: the fictional AAA, BBB and CCC one-year zero-coupon bond-fund table supplied in the Lab 16 handout. These are course training values, not market observations or an actual ALFRED download. Code and these notes were prepared with AI help.

## Run commands

From the repository root:

```powershell
py python/asof.py
py python/verify_asof.py
```

From inside the `python` folder, use `py asof.py`. On a computer with the `python` command configured, `python asof.py` also works. Both scripts use only Python's standard library; no API key or package installation is required.

Opener question: What is the difference between month measured and publication date?

The month measured tells us which period the observation describes. The publication date tells us when that particular version became available. AAA's March observation measures March 2026, but row 3 was not published until April 10, so it cannot be used for a March 31 decision. A period ending does not show its data has already been published.

## Inputs and the four ordered rules

The 12 source records are editable in `python/asof.py`; their original row numbers remain attached throughout processing. `DECISION_DATE` is an editable ISO date at the top of the file.

1. Quarantine a record without a ticker: its identity cannot be established.
2. Remove exact duplicates, comparing ticker, month, publication date and price. The source row number is excluded from this comparison, because duplicate records have different row numbers.
3. Remove records published after the decision date. A publication on the decision date is included under the handout's date-only convention.
4. For each ticker and month, keep the latest publication remaining after rule 3. Earlier vintages are removed from the active panel but their row numbers remain in the audit.

The comparison still quarantines missing identities and removes exact duplicates, but skips the publication cutoff before choosing the latest publication for each ticker/month.

## Verified row funnel

| Step | Count removed from active rows | Source rows |
|---|---:|---|
| Quarantined: no ticker | 1 | 11 |
| Exact duplicate | 1 | 7 |
| Published after March 31 | 3 | 3, 8, 10 |
| Older vintage replaced by a revision | 1 | 2 |
| As-of panel remaining | 6 | 1, 4, 5, 6, 9, 12 |

Reconciliation: 12 starting rows minus 1 minus 1 minus 3 minus 1 equals 6 surviving rows. These counts are sequential, so each excluded row is attributed to its first applicable rule.

## Verified as-of panel

| Row | Ticker | Month measured | Published on | Price |
|---|---|---|---|---:|
| 1 | AAA | 2026-01 | 2026-02-10 | 101.0 |
| 4 | AAA | 2026-02 | 2026-03-25 | 103.0 |
| 5 | BBB | 2026-01 | 2026-02-10 | 98.0 |
| 6 | BBB | 2026-02 | 2026-03-10 | 97.0 |
| 9 | CCC | 2026-01 | 2026-02-10 | 110.0 |
| 12 | CCC | 2026-02 | 2026-03-10 | 111.0 |

## Verified signals: What could have been known on March 31?

Signal = latest monthly price / previous calendar month's price minus 1. The code requires consecutive months; it does not silently label a multi-month change as a monthly return.

| Ticker | As-of signal | Source rows | Naive signal | Source rows |
|---|---|---|---|---|
| AAA | +1.98% (February) | 1, 4 | +5.83% (March) | 4, 3 |
| BBB | -1.02% (February) | 5, 6 | -5.15% (March) | 6, 8 |
| CCC | +0.91% (February) | 9, 12 | +1.82% (February, revised) | 9, 10 |

Calculation checks:

```text
AAA as-of: (103 / 101 - 1) × 100 = +1.98%
AAA naive: (109 / 103 - 1) × 100 = +5.83%
BBB as-of: ( 97 /  98 - 1) × 100 = -1.02%
BBB naive: ( 92 /  97 - 1) × 100 = -5.15%
CCC as-of: (111 / 110 - 1) × 100 = +0.91%
CCC naive: (112 / 110 - 1) × 100 = +1.82%
```

Keeping row 2 instead of row 4 would give AAA `(104 / 101 - 1) × 100 = +2.97%`. Row 4 is the later February publication and was available by March 31, so +1.98% is correct.

## Yield sanity check: Which admitted prices violate the training assumptions?

A one-year zero-coupon bond pays 100 at maturity and no interim coupon. Yield = `100 / price - 1`.

| Row | Fund | Month | Price | Yield calculation | Yield | Breaks |
|---|---|---|---:|---|---:|---|
| 1 | AAA | January | 101.0 | 100 / 101 - 1 | -0.99% | Negative yield |
| 4 | AAA | February | 103.0 | 100 / 103 - 1 | -2.91% | Negative yield |
| 5 | BBB | January | 98.0 | 100 / 98 - 1 | +2.04% | Nothing under the stated checks |
| 6 | BBB | February | 97.0 | 100 / 97 - 1 | +3.09% | Nothing under the stated checks |
| 9 | CCC | January | 110.0 | 100 / 110 - 1 | -9.09% | Negative yield; priced above BBB and AAA |
| 12 | CCC | February | 111.0 | 100 / 111 - 1 | -9.91% | Negative yield; priced above BBB and AAA |

These calculations match the handout and were checked by the verification script.

Under this exercise's equal-maturity assumptions, prices should satisfy AAA > BBB > CCC. In January, CCC is 110 versus AAA 101 and BBB 98; in February, CCC is 111 versus AAA 103 and BBB 97. CCC has the highest price and lowest yield despite being the riskiest rating.

The provenance gate admits all six observations because they are identifiable, distinct, on time and the latest eligible vintages. It does not test economic plausibility. The negative-yield flag is a stated training sanity rule, not a claim that negative yields are impossible in all real markets.

## Rule 4 explanation: How does the code choose the latest eligible revision?

This block is inside `keep_latest_publications` in `python/asof.py`:

```python
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
```

| Line or expression | Explanation |
|---|---|
| `latest = {}` | Start a dictionary that stores one selected record per ticker/month. |
| `for row in rows:` | Examine each eligible record. The as-of caller has already removed future publications. |
| `key = (row["ticker"], row["month"])` | Group versions of the same observation without merging different months or funds. |
| `previous = latest.get(key)` | Retrieve the version selected so far, or `None` if none has been seen. |
| `previous is None or ...` | Select the first version, or replace it if this version was published later. |
| `latest[key] = row` | Store the complete selected record, including its original source row number. |
| `elif ...` and `raise ValueError(...)` | Refuse an ambiguous same-day pair with conflicting prices; exact duplicates were already handled by rule 2. |
| `kept_ids = ...` | Collect the source row numbers of the winning records. |
| `accepted = ...` | Keep the winning rows, preserving their input order. |
| `replaced = ...` | Collect superseded rows for the audit. |
| `return accepted, replaced` | Return both the active observations and the removed vintages. |

ISO dates use `YYYY-MM-DD`, so their string order matches calendar order. The cutoff comparison in rule 3 explicitly parses dates. Rule 4 relies on the correctly formatted input dates.

AI quiz question: Why use both ticker and month in the dictionary key?

A ticker alone would combine January and February into one entry and erase the history needed to calculate a return. The `(ticker, month)` pair makes publications compete only with other versions of the same observation.

AI feedback: Correct. AAA January and AAA February need separate keys; rows 2 and 4 share the February key, so row 4 replaces row 2. This is a worked practice answer, not a recorded answer-before-explanation quiz attempt.

## Partner questions

partner question: Why does CCC row 10 not replace row 12 on March 31?

Row 10 was published on April 5, after the decision date. Rule 3 removes it before rule 4 runs. Row 12 is therefore the latest eligible February record, even though a newer revision exists in the full source table.

## Later-date experiment: What changes on April 15?

The verification script ran an edited temporary copy of `asof.py` with `DECISION_DATE = "2026-04-15"`. It checked the program's actual printed results and confirmed that the original file still uses March 31. This was an automated experiment, not a partner file swap.

| Step on April 15 | Source rows removed |
|---|---|
| Missing ticker | 11 |
| Exact duplicate | 7 |
| Published after decision date | None |
| Superseded vintage | 2, 12 |
| Panel remaining | 1, 3, 4, 5, 6, 8, 9, 10 |

| Ticker | April 15 as-of | Naive |
|---|---|---|
| AAA | +5.83% (March) | +5.83% (March) |
| BBB | -5.15% (March) | -5.15% (March) |
| CCC | +1.82% (February, revised) | +1.82% (February, revised) |

By April 15 every publication in this training table has arrived, so the two columns match. This does not establish that there could never be another future revision outside the supplied table.

Why did the signals change if the prices were not edited?

Changing the decision date changes which publications the gate admits. On April 15, the March AAA and BBB records and the revised February CCC record are available, so their signals match the naive calculation. Restoring March 31 excludes those later publications again.

## Learn: What is look-ahead bias, and how do event time, publication time and revision differ?

Look-ahead bias occurs when an analysis of a past decision uses information that was not available at that time. Here, event time is the month measured; publication time is when a particular price record became available; a revision is a later publication changing the same ticker's value for the same month.

AAA February first appeared as 104 on March 10 and was revised to 103 on March 25. Both publications were knowable on March 31, so the revised 103 is appropriate. AAA March's price of 109 was published on April 10, so the naive +5.83% March return was unavailable on March 31. The knowable latest signal was only +1.98% for February. These refer to different return periods, which must remain labelled.

### Reflection questions

Which rule removed the row that mattered most?

For the look-ahead-bias lesson, rule 3 matters most: it removes AAA row 3 and prevents the unavailable March price from driving a March 31 decision. Rule 4 is also essential because it replaces AAA row 2 with row 4, correcting February's signal from +2.97% to +1.98%.

What would a backtest using the naive column claim?

It would act as though March 31 already revealed AAA's +5.83% March rise, BBB's -5.15% March fall and CCC's revised +1.82% February rise. A strategy could appear to select winners or avoid losses using future publications. Its actual investment performance cannot be calculated without a trading rule, but its information set would be invalid.

What fifth rule would quarantine rows 1, 4, 9 and 12?

Add a separate sanity gate that quarantines any positive one-year zero-coupon price above face value 100, equivalently any yield `100 / price - 1 < 0`, under the exercise's stated assumptions. That flags rows 1, 4, 9 and 12. Also flag within-month violations of the expected AAA > BBB > CCC ordering for review, which identifies the CCC inconsistencies.

This proposed fifth rule is documented separately; it is not silently inserted into the four-rule provenance funnel. If applied, returns requiring quarantined observations would become unavailable until the data were resolved. On time is not the same as true.