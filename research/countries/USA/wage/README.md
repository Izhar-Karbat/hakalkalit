# United States: average gross annual wage, 2000-2025 (BLS QCEW)

Output: `usa_avg_annual_wage_2000-2025.csv` (year, avg_annual_gross_wage_local, currency, concept)
Built by: `python3 -I build_usa_wage.py`. It reads only `raw/` and `../../wages/raw/`.

## Concept
**BLS Quarterly Census of Employment and Wages (QCEW), U.S. total, total covered (UI + UCFE),
all ownerships (private + federal + state + local government), all industries:**
total annual wages / annual average employment. BLS publishes this as "average annual pay"
(it was printed as "annual wages per employee" in older tables).

How it matches the Israeli benchmark (CBS average monthly gross wage per employee post, all employees,
part-time included, whole economy, annual average):

| Benchmark property | QCEW |
|---|---|
| Whole economy, all employees | Yes: private and all levels of government, about 95% of U.S. jobs |
| Part-time included, no FTE conversion | Yes: every covered job counts as one, whatever its hours |
| Per post (job), not per person | Yes: employment is a count of jobs on payrolls in the pay period including the 12th, so a person with two jobs counts twice |
| Gross | Yes: wages before taxes and employee deductions |
| Annual average | Yes: employment is the mean of the 12 monthly counts and wages are the sum over the 4 quarters |

**Why not the CES alternative:** CES average weekly earnings of all employees cover only the private
sector and start in 2006. That would leave out all government jobs and the years
2000-2005. QCEW is a census of UI tax records rather than a sample, and it covers the full period.

## Inputs
Agency: U.S. Bureau of Labor Statistics. Exact URLs and timestamps are in `SOURCES.csv`; all files are
unmodified in `raw/`.

| Use | Series / file | Unit |
|---|---|---|
| 2001-2025 employment | `ENUUS00010010` (QCEW, U.S. total, size 0, ownership 0 = total covered, industry 10 = total all industries), BLS Public Data API v2 | jobs, monthly |
| 2001-2025 wages | `ENUUS00030010` (same, total wages), API v2 | USD thousands, quarterly |
| 2001-2025 cross-check | `ENUUS00050010` (same, average annual pay as published by BLS), API v2 | USD, annual |
| 2000 | `2000_annual_singlefile.zip`, the row area_fips=US000, own_code=0, industry_code=10, size 0, qtr A. The API series begin in 2001. | USD, jobs |
| Cross-check | `qcew_open_2014_a_area_US000.csv`, `qcew_open_2025_a_area_US000.csv` (QCEW open-data slices) | |
| Printed check | `bls_ew_annual_2007_total_coverage_by_ownership.pdf`: BLS *Employment and Wages, Annual Averages 2007*, Table 1 | |

API URL pattern: `https://api.bls.gov/publicAPI/v2/timeseries/data/<series>?startyear=<a>&endyear=<b>`.
Unregistered access is limited to 10 years per request, so there are three windows per series.

## Method
For each year from 2001 to 2025: (sum of the 4 quarterly total-wage values × 1000) / (mean of the 12
monthly employment values). For 2000: total_annual_wages / annual_avg_emplvl from the 2000 annual file.
The script asserts that every computed year agrees within $1 with BLS's own published average annual pay
(`ENUUS00050010`, or the `avg_annual_pay` field for 2000), and every year does. No interpolation.
Every year from 2000 to 2025 is filled.

## Check against the agency's printed table
BLS *Employment and Wages, Annual Averages 2007*, Table 1, "Total covered (UI and UCFE)", row
"Annual wages per employee" (`raw/bls_ew_annual_2007_total_coverage_by_ownership.pdf`):

| Year | Printed | This series |
|---|---|---|
| 2000 | $35,323 | 35,331 (+8, see limits) |
| 2001-2007 | 36,219 / 36,764 / 37,765 / 39,354 / 40,677 / 42,535 / 44,458 | identical |

The open-data slices for 2014 and 2025 reproduce the API-derived values exactly (51,364 and 78,720).

## Comparison with the OECD national-accounts figure
OECD D11 wages and salaries (S1, _T, current prices, national currency) divided by SAL employees
(persons), REF_AREA=USA. Full table: `usa_vs_oecd_d11_per_employee.csv`.

| Year | QCEW | OECD D11/SAL | QCEW / OECD |
|---|---|---|---|
| 2000 | 35,331 | 37,478 | 0.943 |
| 2007 | 44,458 | 46,471 | 0.957 |
| 2016 | 53,621 | 56,272 | 0.953 |
| 2022 | 69,986 | 74,010 | 0.946 |

Across 2000-2023 the ratio stays between 0.942 and 0.965. The OECD file has no USA value for 2024-2025.
*Hypothesis, not tested here:* the roughly 5% gap comes from the national-accounts scope. NIPA wages
include pay that QCEW does not cover (military, some non-covered sectors, imputations), and the
national-accounts employee count is defined differently. Because the gap is stable, the choice between
the two sources barely changes the trend. It does change the level by about 5%.

## Known limits (stated before anyone else finds them)
1. **Coverage is about 95%, not 100%.** QCEW excludes the self-employed, members of the armed forces,
   most railroad workers, some agricultural and domestic workers, small nonprofits and religious
   organisations, and others not covered by unemployment insurance. The excluded wage earners are not
   a random sample.
2. **Wage definition is broader than base salary.** QCEW wages include bonuses, tips, severance, the
   value of exercised stock options and, in most states, employee contributions to deferred
   compensation plans (401(k)). The definition varies slightly by state. Stock-option income at the top
   inflates the mean, and in the U.S. the mean sits well above the median. This series is a **mean**,
   as the CBS benchmark is.
3. **Jobs, not people.** A worker with two part-time jobs counts as two low-paid posts, which lowers
   the average. This matches CBS's "per employee post" concept, but it is not a "typical worker's
   income".
4. **2020 composition jump.** The +8.1% in 2020 (59,209 to 64,021) is mostly a mix effect. Low-wage jobs
   disappeared in the COVID shock, which pushed the average up. It is not a pay rise for anyone in
   particular. 2021 and later are partly affected by the same effect.
5. **Revisions.** The 2000 value in the current file (35,331) differs by $8 (0.02%) from the 2007
   printed table (35,323). BLS revised the data afterwards, and the file is dated 2015. The 2025 value
   is the first annual release (2026) and may be revised slightly.
6. **Seam at 2000/2001.** 2000 comes from the annual data file and 2001-2025 from the time-series API.
   Both are the same QCEW concept, and the printed 2007 table shows the two joining without a break.
7. **Level vs national accounts.** The value is about 5% below the OECD D11/SAL figure (see above). If
   another country in the comparison uses national-accounts wages, the U.S. level here is not on
   exactly the same footing.

## CERTAINTY: high
The figure comes from a census-based official series, is computed from saved raw files, and matches
BLS's own published average annual pay to the dollar for every year. It matches the printed 2007 table
exactly for 2001-2007, with an explained $8 revision for 2000. The concept lines up with the CBS
benchmark on every axis that matters: whole economy, part-time included, per post, gross, annual
average. The remaining risks are about definitions (limits 1, 2 and 7), not about the data.
