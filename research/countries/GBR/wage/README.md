# United Kingdom: average gross annual wage, 2000–2025 (GBP)

Wage side only. Rebuild: `~/miniconda3/bin/python -I build_gbr_wage.py` (needs pandas, xlrd, openpyxl).
The script reads only `raw/` and the shared OECD files in `../../wages/raw/`, and writes:
- `gbr_avg_annual_wage_2000-2025.csv`: the main series.
- `gbr_wage_comparison_2000-2025.csv`: the main series next to ASHE (UK, GB, England and Wales) and the OECD national-accounts figure, with ratios.
- `gbr_wage_checks.csv`: every check, with the published value, our value and a verdict.

**CERTAINTY: medium-high.** The series is official, has no method breaks, and reproduces ONS's own printed figures exactly (28 of 28 checks pass). It is not "high" for three reasons. It covers Great Britain, not England and Wales. Its level is 3–18% below the other ONS earnings survey (ASHE). And the two ONS surveys disagree on growth since 2000 (+133% vs +113%) (see limits 2 and 3).

## Result

| Year | **Main: AWE × 52, GB (£)** | ASHE mean annual, UK (£) | ASHE mean annual, E&W (£) | OECD D11 ÷ employees (£) | Main ÷ OECD | ASHE UK ÷ OECD |
|---|---|---|---|---|---|---|
| 2000 | **16,263** | 18,939 | 19,211 | 18,951 | 0.858 | 0.999 |
| 2007 | **21,827** | 24,972 | 25,354 | 25,700 | 0.849 | 0.972 |
| 2016 | **25,662** | 28,306 | 28,572 | 29,782 | 0.862 | 0.950 |
| 2022 | **32,023** | 33,449 | 33,835 | 35,761 | 0.896 | 0.935 |
| 2025 | **37,834** | 40,269 | 40,715 | 41,583 | 0.910 | 0.968 |

All 26 years from 2000 to 2025 are filled in every column. None were interpolated.

## Concept

**The benchmark we match.** Israel CBS "average monthly gross wage per employee post": every employee job, part-time included, no full-time-equivalent conversion, gross, whole economy, an arithmetic mean, taken from employers' payroll reports.

**Main series: ONS Average Weekly Earnings (AWE), series KAB9.** "AWE: Whole Economy Level (£): Seasonally Adjusted Total Pay Excluding Arrears", Great Britain.
- ONS describes it as "the ratio of estimated total paid in wages and salaries" to the number of employees, from the Monthly Wages and Salaries Survey of employers (`raw/ons_ashe_vs_awe_comparison_2017.html`). That makes it a mean per employee job, part-time included, with no FTE conversion. It counts every employee on the payroll, including new starters, job changers, juniors and people whose pay was reduced by absence.
- Total pay includes bonuses. Arrears are excluded.
- The annual figure is the mean of the 12 monthly values (£ per week) multiplied by 52.
- **Why this one.** On every point of definition it is the closest UK match to the CBS measure: a payroll-based mean per job over all employees. ONS also states that "There are no discontinuities or breaks in the AWE series, due to the whole series being revised back to 2000 if any major changes to methodology occur" (same article).
- There is also an empirical pointer, which is suggestive and not proof. Divided by the same OECD national-accounts measure, the Israeli benchmark gives 0.880–0.905 (2000, 2007, 2016, 2022; computed in `gbr_wage_checks.csv`). AWE gives 0.849–0.910. ASHE gives 0.935–0.999.

**Check series: ONS Annual Survey of Hours and Earnings (ASHE), table 1.7a / 7.7a "Annual pay – Gross", sheet "All" (full-time and part-time), column "Mean".**
- This series is kept as a check. It is not the main series because:
  - Its annual-pay population is restricted. The table footnote says "Employees on adult rates who have been in the same job for more than a year". That leaves out new entrants, job changers and junior rates, and so pushes the mean up.
  - It has method breaks in 2004, 2006, 2011 and 2021.
- It is the only ONS source that gives **England and Wales** (table 7, row `K04000001`), so it is the geographic check for the price series.
- Table 7's "United Kingdom" row is asserted equal to table 1's "All employees" row in every file.
- Where ONS published two bases for one year (2006: 2005 vs 2007 methodology; 2011: SOC 2000 vs SOC 2010), and for provisional vs revised files, the newer or revised basis is used. The other value is listed in the comparison CSV.
- ONS publishes no linked back-series for ASHE annual pay. The breaks are left as they are, not spliced.

## Inputs (all downloaded 2026-10-17; exact URLs in `SOURCES.csv`)

| Input | Series | Agency | URL | Raw file |
|---|---|---|---|---|
| Main | AWE KAB9, dataset EMP, release 15-09-2026 | ONS | https://www.ons.gov.uk/generator?format=csv&uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/timeseries/kab9/emp | `raw/ons_awe_kab9.csv`, `raw/ons_awe_kab9_page.html` |
| Check | ASHE table 1 (UK), all vintages 2000–2025 | ONS | https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/allemployeesashetable1 | `raw/ashe_t1/*.zip`, `raw/ons_ashe_t1_page.html` |
| Check / E&W | ASHE table 7 (work geography: UK, GB, E&W), 2000–2025 | ONS | https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/placeofworkbylocalauthorityashetable7 | `raw/ashe_t7/*.zip`, `raw/ons_ashe_t7_page.html` |
| Printed figures | AWE bulletins Oct 2025 and Sep 2026; ASHE bulletins 2016 and 2025; ONS ASHE vs AWE comparison article (2017) | ONS | see `SOURCES.csv` | `raw/ons_awe_bulletin_*.html`, `raw/ons_ashe_bulletin_*.html`, `raw/ons_ashe_vs_awe_comparison_2017.html` |
| OECD comparison | D11 wages and salaries (S1, _T, V, XDC) ÷ SAL employees (S1, _T, PS), GBR | OECD | `../../wages/SOURCES.csv` | `../../wages/raw/oecd_na_table1_income.csv`, `oecd_na_table3_empdc.csv` |

Every URL responded with the saved content on 2026-10-17. Each file was also checked to make sure it was not a Cloudflare rate-limit page: ONS returned "Error code: 1015" on the first attempt, and those files were deleted and fetched again with throttling. One requested page, the 2007 ASHE bulletin, returned "Page not found". It was discarded and is not listed.

## Method

1. AWE: for each year 2000–2025, take the 12 monthly KAB9 values, average them, and multiply by 52. The script leaves a year blank if fewer than 12 months are published; none are blank.
2. ASHE: open the `.7a` workbook in each zip, use sheet "All", find the "Mean" column from the header, and read the rows "United Kingdom", "Great Britain" and "England and Wales" (table 7) and "All Employees" (table 1).
3. OECD: D11 × 10^UNIT_MULT ÷ SAL × 10^UNIT_MULT, REF_AREA = GBR.

## Checks (`gbr_wage_checks.csv`)

- **Printed AWE bulletin levels, exact match.**
  - The October 2025 bulletin prints "Average weekly earnings (AWE) were estimated at £733 for total earnings … in August 2025". Our raw KAB9 value for 2025 AUG is 733. PASS.
  - The September 2026 bulletin prints "£756 … in July 2026". Ours is 756. PASS.
- **ONS's own annual KAB9 figure.** For all 26 years, our 12-month mean agrees with ONS's published annual value in the same file (rounded to £1/week). 26/26 PASS. For example, 2025: ONS 728, ours 727.58.
- **The level gap is ONS's own, not ours.** The 2016 ASHE bulletin prints, for Great Britain in April 2016, an ASHE like-for-like mean weekly pay of £525 against an AWE regular pay of £472, a ratio of 1.11. ONS itself states that the two surveys differ in level.

## Known limits (stated before anyone else finds them)

1. **The main series is Great Britain, not England and Wales.** AWE is only published for GB. Our price series is E&W. In ASHE, the E&W mean is 0.5–1.2% above the GB mean in every year (`ashe_EW_over_GB`), so the E&W wage is probably about 1% above the main series. It has not been adjusted.
2. **The level depends on the survey.** ASHE mean annual pay is 3–18% above AWE × 52 (16% in 2000, 6% in 2025). Using ASHE would lower UK price-to-wage ratios by that much. We chose AWE on definition. A reader who prefers ASHE has a defensible alternative, and the numbers are in the comparison CSV.
3. **The two ONS surveys disagree on growth.**
   - From 2000 to 2025, AWE × 52 rises 133% (16,263 → 37,834). ASHE UK rises 113% (18,939 → 40,269).
   - Most of the convergence happens after 2019. AWE's ratio to OECD climbs from about 0.86 to 0.91 over the same period.
   - We do not know which survey is right about the trend. Any claim about the *change* in UK affordability should be shown on both series.
4. **× 52 understates a calendar year by about 0.3%.** A year has 365/7 ≈ 52.18 weeks. We used 52 as specified.
5. **The AWE series is seasonally adjusted.** The annual mean of seasonally adjusted months should be close to the unadjusted mean, but the two are not identical. We did not download the non-adjusted series.
6. **Small firms are estimated, not surveyed.** The AWE survey covers businesses with 20 or more employees. ONS adjusts for smaller firms using ASHE relationships. Before July 2010 the series was re-estimated backwards rather than collected on the current method.
7. **Arrears are excluded from AWE.** CBS pay may include back-pay in the month it is paid. The size of this difference is unknown.
8. **Jobs vs persons.** AWE is per job, like CBS's "per employee post". OECD SAL counts persons, so OECD per employee is higher for anyone holding two jobs. The ratio to OECD is a sanity bound, not a match.
9. **ASHE breaks (2004, 2006, 2011, 2021) are not spliced.** One more caveat: the "All" sheet footnote in two ASHE files (2022 revised, 2023 provisional) reads "whose pay … was not affected by absence" instead of "same job for more than a year". We take this to be a template slip, because the values continue smoothly, but we have not verified it.
10. **2020–2021 are pandemic years.** AWE includes furlough pay as paid by employers. ASHE 2020–2021 annual figures include furloughed employees (table footnote). Composition effects make both noisy in these years.
11. **The 2025 ASHE figures are provisional.** AWE 2025 may also be revised in later releases (this file is the 15-09-2026 release).
