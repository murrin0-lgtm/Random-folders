Purpose: Determine which candidate portfolios pass the rules implemented in the checker and identify what remains unresolved before portfolio optimization
S1	Horizon seven years; annual rebalancing.
Hard constraint: It sets the investment time frame and rebalancing schedule.
S2	Objective: CPI + 4% a year, net of costs, over rolling five-year periods.
Objective: This defines the return the client would like to achieve. It's a target not a result.
S3	Pays out $0.75 million every quarter; twelve months of payouts held in cash or daily-liquid government securities.
Hard constraint: This requires $3 million, or 3% of the $100 million portfolio in reserve eligible holdings
S4	Benchmark: 60% global equities, 40% U.S. investment-grade bonds.
Preference: This shows a comparison standard, but doesn't necessarily require matching the weights or have a tracking error limit.
S5	Long-only: no borrowing, short sales or derivatives.
Hard constraint: Prohibits particular positions and investment methods
S6	No single issuer above 8%.
Hard constraint: Puts a cap on combined exposure to any non-exempt issuer. which includes the company's stocks and bonds.
S7	Annual turnover at most 25% without committee approval.
Hard constraint: Limits trading unless the committee approves an exception.
S8	At least 90% redeemable within five business days.
Hard constraint: Sets a measurable minimum for portfolio liquidity.
S9	"The reserve cannot have a calendar-year loss greater than 10%." No measure, no breach rule.
Unverifiable promise: The checker can't guarantee future losses stay below 10%. The CIO needs to clarify the risk measure.
S10	No sector, ESG, tax or home-bias preference; nobody has said what the pilot should optimize.
Missing: The CIO hasn't specified what the optimizer should maximize or minimize.

## Checker results:

The required reserve is:

4 quarters × $0.75 million = $3 million, or **3.0%** of the $100 million portfolio.

| Check | Candidate A | Candidate B | Candidate C |
|---|---|---|---|
| Weights total 100% | 100.0% — pass | 100.0% — pass | 100.0% — pass |
| Lowest weight is nonnegative | 0.0% — pass | 0.0% — pass | 0.0% — pass |
| Reserve-eligible holdings ≥ 3% | 14.0% — pass | 1.0% — FAIL | 2.0% — FAIL |
| Redeemable within five business days ≥ 90% | 100.0% — pass | 85.0% — FAIL | 100.0% — pass |
| Largest non-exempt issuer ≤ 8% | 0.0% — pass | 9.0% — FAIL | 8.0% — pass |
| Calendar-year loss limit | Requires CIO clarification | Requires CIO clarification | Requires CIO clarification |
| **Verdict** | **Passes every checkable rule** | **Fails 3 rules** | **Fails 1 rule** |

Candidate B fails the reserve, liquidity and issuer checks. Its 5% in Acme bonds and 4% in Acme stock combine into a 9% exposure to the same issuer.

Candidate C fails only the reserve requirement. Its 8% Acme exposure is permitted because the issuer limit allows exactly 8%.

Candidate A passes all five implemented checks. This does not establish that it meets the return objective or every part of the client’s mandate.

## Negative-cash test

I temporarily changed candidate A’s cash weight to −2% and its global equity fund weight to 64%. Total weights remained 100%.

The lowest weight was −2.0%, so the long-only check failed. Reserve-eligible holdings remained 10.0%, liquidity remained 100.0%, and non-exempt issuer exposure remained 0.0%. All other implemented checks passed.

This confirms that weights adding to 100% do not necessarily make a portfolio long-only. I restored candidate A’s original weights and reran the checker to confirm it passed again.

## code understanding quiz

Line to be checked: company_weights[issuer] = company_weights.get(issuer, 0) + weight

Question: If the script encounters 5% in Acme bonds and then 4% in Acme stock, what value will it store for Acme—and why does the checker combine them?

Answer: It will store 9% for Acme because the 5% and 4% are from the same issuer.

AI said: It stores 9% for Acme because the 5% bond position and 4% stock position belong to the same issuer. The 8% limit applies to the company’s combined exposure, so this fails the issuer check.

## Candidate D: testing the checker’s limits

Candidate D allocates 100% to cash and 0% to every other holding.

| Check | Result |
|---|---|
| Weights total 100% | 100.0% — pass |
| Lowest weight is nonnegative | 0.0% — pass |
| Reserve-eligible holdings ≥ 3% | 100.0% — pass |
| Redeemable within five business days ≥ 90% | 100.0% — pass |
| Largest non-exempt issuer ≤ 8% | 0.0% — pass |

The objection is that passing these checks does not demonstrate that an all-cash portfolio can meet **S2’s CPI + 4% return objective, net of costs**.

I agree that the CIO could reject candidate D because passing the checker doesn't necessarily mean that holding 100% cash will meet the return objective. S2 supports the objection because it targets CPI 4% annually. The checker does not evaluate this.

## question for the CIO

Should the pilot minimize risk when they are targeting CPI + 4%, or should they maximize expected return?

If the CIO were to choose minimize risk, I would probably find the lowest risk mix expected to meet the target, which may favor more bonds. If they choose to maximize, I could assocate more to equities. 

## Investment Policy Statement

An Investment Policy Statement (IPS) records the client’s investment objectives, constraints and rules for managing and reviewing the portfolio. It guides portfolio decisions and provides a standard for evaluating whether the investments remain suitable.

Objectives describe what the portfolio aims to achieve. Constraints limit the choices available when pursuing those objectives. Passing the constraints does not guarantee that the objective will be achieved.

For Meridian, the statements map to the IPS as follows:

- S1: Investment horizon and rebalancing schedule.
- S2: Return objective.
- S3: Distribution needs and minimum reserve requirement.
- S4: Benchmark for evaluating performance.
- S5: Restrictions on investment methods.
- S6: Issuer concentration limit.
- S7: Turnover limit and approval process.
- S8: Liquidity requirement.
- S9: Risk requirement needing clarification before it can be implemented.
- S10: Unspecified optimization objective and no stated additional investment preferences.

The IPS needs clarification on S9 and S10 before it can fully guide portfolio optimization.

## reflections

Why passing the checker doesn't guarantee stability:
A portfolio can pass every check and still not meet the client's needs because the checker only covers part of the mandate. Candidate D's 100% cash allocation passes the weight, reserve, liquidity, and issuer checks, but those results don't demonstrate that it can achieve S2's CPI + 4% return objective after costs.

The classification I wasn't sure about:
I was least sure about S4 because the 60% equity and 40% bond benchmark could be mistaken for a required allocation. I showed it as a preference or reference benchmark because the statement doesn't require the portfolio to match those weights.

## Project 2: My Client’s Mandate

Client: A hypothetical individual investing $100,000 for retirement in 20 years. The client holds a separate emergency fund and expects no withdrawals from this portfolio during that period.

Objective

The portfolio aims to grow purchasing power by earning CPI plus 3% annually, net of investment costs, over rolling five-year periods. This is a target, not a guaranteed return.

Hard constraints

- Use a 20-year investment horizon and rebalance annually.
- Maintain fully invested portfolio weights totaling 100%, including cash.
- Use long-only investments with no borrowing, short sales or derivatives.
- Invest only in cash, government securities and diversified stock or investment-grade bond funds.
- Keep at least 95% of the portfolio redeemable within five business days.
- Limit any single fund to 40% of the portfolio.

One question for the client

Should the portfolio seek the lowest risk consistent with the return target, or pursue higher expected returns while accepting larger temporary losses?

How the answer changes the design

If the client prioritizes lower risk, I would seek the lowest-risk allocation expected to meet the target, potentially holding more bonds. If the client prioritizes higher expected returns, I would consider more equities after agreeing on a measurable risk limit. If the target cannot reasonably be achieved within the client’s risk tolerance, we would revisit the target before choosing portfolio weights.