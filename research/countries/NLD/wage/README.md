# Netherlands: average gross annual wage per employee job, 2000-2025

## Concept
Gross wages and salaries per average employee job, whole economy, EUR per year. Every job counts
as one (full-time and part-time, no FTE conversion), so this matches the Israeli benchmark
(CBS Israel, average monthly gross wage per employee post, × 12).

Formula: `Lonen (mln EUR) × 10^6 / (Banen van werknemers, voltijd en deeltijd, totaal (×1 000) × 10^3)`,
sector A-U "Alle economische activiteiten".

"Lonen" is the national-accounts D11 item. CBS defines it as wages paid by the employer, including
income tax withheld and the employee's own social contributions, bonuses, overtime, tips, holiday
pay (vakantiegeld), wages in kind (company car, free housing and so on) and commuting allowances.
Sick pay is moved out to employer social contributions. "Banen" is the annual-average number of
employee jobs. A person with two jobs counts twice, and two consecutive six-month jobs count as one.

## Inputs (all CBS Statistics Netherlands, StatLine OData v3; exact URLs in `SOURCES.csv`)
| Role | Table | Raw file |
|---|---|---|
| **Main** | 85919NED "Beloning en arbeidsvolume van werknemers; bedrijfstak, nationale rekeningen" (1995-2025, updated 2026-07-02) | `raw/cbs_85919NED_total_economy.json` (+ TableInfos, DataProperties, Perioden) |
| Check (Polis micro-data, per job) | 81431ned "Werkgelegenheid; banen, lonen, arbeidsduur, SBI2008; kerncijfers" (2009-2025) | `raw/cbs_81431ned_total.json` (+ TableInfos, DataProperties) |
| Revision check | 84165NED (vintage to 2022, discontinued 2024) | `raw/cbs_84165NED_total_economy_archived.json` |
| Revision check | 82578NED (vintage 1969-2016, discontinued 2018) | `raw/cbs_82578NED_total_economy_archived.json` |
| OECD comparison | NAMAIN10 T0103 D11 / T0111 SAL, read from `../../wages/raw/` | not copied |

## Method
`build_nld_wage.py` reads only the raw files and writes `nld_avg_annual_wage_2000-2025.csv` and
`nld_wage_checks.csv`. Annual periods (`JJ00`) only. Nothing is interpolated, and all 26 years are
populated.

## Why this table and not the others
- **85919NED (chosen):** this is the only CBS series that covers all of 2000-2025 in one consistent
  vintage. CBS recalculated it back to 1995 after each national-accounts revision. Both the numerator
  (gross wages including special payments) and the denominator (jobs, part-time included) fit the benchmark.
- **81431ned "Jaarloon inclusief bijzondere beloning"** is also gross pay per job including special
  payments, but it starts in 2009 and has a method break in 2010 (`2010X000` vs `2010JJ00`). We
  kept it as a check.
- **"Lonen per arbeidsjaar"** is per FTE, so it does not match the benchmark. It is about 28-34% higher
  than the per-job figure (for example 51.7k vs 39.3k EUR in 2022). We used it only to verify the arithmetic.

## Checks (all in `nld_wage_checks.csv`)
1. **Against the agency's printed figure.** We recomputed Lonen / Arbeidsjaren and compared it with
   the "Lonen per arbeidsjaar" that CBS publishes in the same table. Over 2000-2025 the largest gap is
   0.047k EUR, which is rounding (CBS prints one decimal). For 2022 we get 51.74 against the printed 51.7.
   This confirms that the fields and units are read correctly.
2. **Against an independent CBS source (Polis per-job annual wage).** The NA per-job figure divided by
   the Polis figure is 1.012 in 2009, 1.010 in 2016, 0.985 in 2022 and 0.985 in 2025. Two
   different CBS sources agree within about 1.5%.
3. **Against revisions.** The 2000 figure is 24,229 in the current vintage, 24,295 in 84165NED and 24,160 in 82578NED.
   The 2016 figure is 34,050, 33,979 and 33,803. The 2022 figure is 39,323 against 39,507. So the
   2017-2024 revisions moved the level by less than 1%.
4. **OECD.** OECD D11 for NLD equals CBS Lonen exactly, to the million, in every year from 2000 to 2024; in 2025
   the two differ by 2 mln. Dividing our national figure by OECD D11 per employee *person* gives 0.942 (2000), 0.939 (2007),
   0.938 (2016) and 0.940 (2022), and stays within 0.935-0.946 across 2000-2025. The gap is entirely in the denominator: there are about 6% more jobs than
   employed persons, because of second jobs. This is the expected direction for a per-job concept.

## Values (EUR)
2000: 24,229 · 2007: 29,472 · 2016: 34,050 · 2022: 39,323 · 2025: 46,744 (provisional)

## Known limits (stated before anyone else finds them)
- **2025 is provisional** ("voorlopig") in 85919NED. The final figure is due around January 2027.
  2024 became final on 2026-07-02.
- **The Dutch numerator is broader than a payroll wage.** National-accounts lonen include wages in
  kind and commuting allowances. Whether the Israeli "average wage per employee post" includes
  these depends on Israel's payroll (form 102) definition. If it does not, NLD is slightly
  inflated relative to ISR. The Polis per-job wage, which is closer to payroll, is about 1-1.5% lower
  in 2022-2025 and about 1% higher in 2009-2016, so the difference is small either way.
- **What counts as a job.** CBS's annual-average job count weights each job by how long it lasted,
  not by its hours. Israel counts posts per month and averages them. Small part-time jobs
  pull the per-job average down. That is
  correct for this concept but makes NL look lower than a per-FTE comparison would. In this table
  per-job and per-FTE differ by 28-34%.
- **Domestic concept.** The figure covers jobs at employers resident in NL, including cross-border
  commuters, and excludes Dutch residents working abroad.
- **Rounding.** The inputs are rounded to 1 mln EUR and 1,000 jobs, so the per-job figure carries
  about ±10 EUR of rounding error. The values in the CSV are rounded to whole euros.
- **Revisions.** Future NA revisions will restate the whole series. The past three vintages moved levels by less than 1%.

## CERTAINTY: high
The data comes from one official table and one consistent vintage, with no gaps or splicing for 2000-2025.
The arithmetic reproduces CBS's own printed per-FTE figure. An independent CBS micro-data source
agrees within 1.5%, revisions moved the level by less than 1%, and OECD D11 matches CBS exactly. The
remaining uncertainty is conceptual (in-kind wages and allowances, how jobs are counted against
Israel's definition), not about the data. It is worth about ±1.5%.
