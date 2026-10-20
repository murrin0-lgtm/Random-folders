# Lab 14 - Portfolio Baselines

## Question and inputs

What does each simple portfolio earn and risk, and does any meet the Meridian mandate?

The engine uses the course-authored training returns, volatilities and correlations, not market estimates. The return objective is 6.5%: an explicitly estimated 2.5% CPI plus 4%.

## Run commands

From the repository root on this computer:

```powershell
py python/portfolio.py
py python/mandate.py
py python/verify_portfolio.py
```

The `python` Windows alias was inaccessible in this session; the installed interpreter works through `py`. From inside the `python` folder, use `py portfolio.py`. Where the `python` command is configured, `python portfolio.py` also works.

## Verified results

Weights are bills / 10-year note / IG bonds / equity. All outputs below were computed by the engine and checked against the handout.

| Portfolio | Weights (%) | Return | Volatility | Reserve eligible | Meets 6.5%? |
|---|---|---|---|---|---|
| Benchmark | 0.0 / 0.0 / 40.0 / 60.0 | 6.80% | 10.46% | 0.0% | Yes |
| Equal weight | 25.0 / 25.0 / 25.0 / 25.0 | 5.20% | 5.21% | 50.0% | No |
| Inverse volatility | 84.3 / 6.0 / 7.0 / 2.6 | 3.77% | 1.05% | 90.3% | No |

The displayed inverse-volatility weights total 99.9% because each is rounded to one decimal. Calculations use unrounded weights normalized to 100%.

## Tests performed

- All five output fields for each portfolio match the known answer.
- Changing both IG-equity correlation cells to 0.50 produces benchmark volatility of 11.00%.
- Setting both cells to 1.3 makes the program exit with status 1 and a message that correlations must be between -1 and 1.
- Changing just one cell makes the program exit with status 1 and a message that the table must be symmetric.
- These changes were executed in temporary copies of the program. The submitted file retains the original 0.25 correlation.
- Candidate E was added to the Lab 13 checker: 40% IG bonds and 60% equity. It fails the 3.0% reserve requirement with 0.0% reserve; every other implemented check passes. A-D retain their prior results.

The reproducible tests are in `python/verify_portfolio.py`. All passed on October 20, 2026.

## Diversification and the hand calculation

Diversification combines assets whose returns do not move perfectly together. Correlation below +1 lowers the covariance contribution compared with an otherwise identical perfectly correlated mix. It does not guarantee lower risk than either individual asset.

For the benchmark:

```text
variance = (0.40^2 * 0.06^2) + (0.60^2 * 0.16^2)
           + 2 * 0.40 * 0.60 * 0.25 * 0.06 * 0.16
         = 0.000576 + 0.009216 + 0.001152
         = 0.010944
volatility = sqrt(0.010944) = 0.1046136 = 10.46%
```

The code builds each covariance as correlation times the two volatilities. Its double sum includes every asset pair, so the two off-diagonal terms supply the factor of two in the hand calculation. It takes the square root only after summing the variance terms.

## Interpretation

Inverse volatility piles into bills because their 0.5% volatility is much smaller than the other sleeves' volatilities. The reciprocal is therefore much larger. Normalizing those reciprocals assigns about 84.3% to bills. This procedure does not enforce a return objective.

The benchmark is a useful first comparison for the CIO because it is Meridian's stated reference portfolio and exposes the conflict between the return target and reserve requirement. It exceeds the expected return objective but fails the reserve rule. The other two baselines miss the return objective. None of the three demonstrates full mandate compliance, and the Lab 13 calendar-year loss requirement still needs clarification.

### AI quiz

Line chosen: OBJECTIVE_RETURN = 0.065  # CPI estimate of 2.5% plus 4%.

AI's question: If the CPI estimate rises from 2.5% to 3.0%, what should OBJECTIVE_RETURN become, and would the benchmark’s 6.80% expected return still meet that objective?

Objective return should become 0.07 because 3.0% CPI + 4% = 7%
The benchmark's 6.8% expected return wouldn't meet that objective.

### Partner activities

Why can diversification lower risk? 
Because assets don't always rise and fall together. When their correlation is below +1, their movements partially offset, which reduces the portfolio's volatility compared with a partially correlated mix.
Since the benchmark holds 40% IG bonds and 60% equity the volatility is: 10.46%, which is below equity's 16% volatility, even though it's above bonds' 6%. Diversification doesn't always make a portfolio safer than either asset alone.

### Explain portfolio-volatility code

1. def portfolio_volatility(weights, covariance):
This defines a function that receives portfolio weights and the covariance matrix

2. variance = sum(
This adds the contributions from every asset pair to calculate portfolio variances.

weights[i] * weights[j] * covariance[i][j]
Multiplies the two assets' weights by their covariance. Covariance was calculated earlier as their correlation times both volatilities.

My partner's question: Why doesn't the code multiply the covariance term by two?

Answer: The loops include both the bond-equity pair and the equity-bond pair. Those equal contributions provide the factor of two used in the hand calculation.

We then ran each others files and compared three portfolios with the known answers. We changed the IG-equity correlation to 1.3. The program refused to run because correlations must be between -1 and +1. We then restored both correlation cells to 0.25 and confirmed the original results came back.

### Reflection

Why does inverse volatility pile into bills?
Inverse volatility assigns weights proportional to one divided by volatility. Bills only have 0.5% volatility, so their reciprocal is larger than the ones of the other assets. 

Which baseline would you show the CIO first, why?
I'd show the benchmark first because it's Meridian's stated comparison portfolio. Its 6.8% expected return exceeds the objective, but its 0% reserve allocation fails the 3% reserve requirement.