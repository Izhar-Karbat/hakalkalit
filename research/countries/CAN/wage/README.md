# Canada: average gross annual wage, 2000–2025

The wage side only. It is the average gross earnings per employee in Canada, in Canadian dollars, one figure per year.
Rebuild: `python3 build_can_wage.py` (standard library only). It writes `can_avg_annual_wage_2000-2025.csv`.
The script reads only `raw/` and the shared OECD files in `../../wages/raw/`. It fails if the CSV disagrees with the figures StatCan prints on its own table page.

**CERTAINTY: high for 2001–2025, medium for 2000.**
- 2001–2025 come from one official StatCan series and one survey methodology, with no arithmetic beyond ×52. They match the printed table to the cent.
- The concept is the closest match to the Israeli CBS benchmark in StatCan's catalogue:
  - per employee, with part-time workers counted as whole heads (no full-time-equivalent conversion);
  - gross payroll before deductions;
  - an annual average.
- 2000 is an official StatCan figure, but it comes from the archived pre-2001 SEPH. StatCan itself warns of level shifts across 2000/2001 (see Known limits).

## Result

| Year | Avg weekly earnings (CAD) | ×52 = annual (CAD) | Source table |
|---|---|---|---|
| 2000 | 655.55 | 34,089 | 14-10-0245-01 (archived, old method) |
| 2007 | 787.37 | 40,943 | 14-10-0204-01 |
| 2016 | 956.61 | 49,744 | 14-10-0204-01 |
| 2022 | 1,165.24 | 60,592 | 14-10-0204-01 |
| 2025 | 1,302.86 | 67,749 | 14-10-0204-01 |

All 26 years are filled. None is interpolated.

## Inputs

| Input | Series | URL (downloaded 2026-10-17) | Raw file |
|---|---|---|---|
| Main, 2001–2025 | StatCan table 14-10-0204-01 (ex-CANSIM 281-0027) "Average weekly earnings by industry, annual". Survey of Employment, Payrolls and Hours (SEPH, survey 2612). Vector **v1740722**: Canada; All employees; Including overtime; Industrial aggregate excluding unclassified businesses [11-91N] | https://www150.statcan.gc.ca/n1/tbl/csv/14100204-eng.zip | `raw/statcan_14100204-eng.zip` |
| 2000 | StatCan table 14-10-0245-01 (ex-CANSIM 281-0053, ARCHIVED). SEPH average weekly earnings by type of employee, NAICS, annual, 1991–2000. Vector **v78952340**, with the same four dimension members | https://www150.statcan.gc.ca/n1/tbl/csv/14100245-eng.zip | `raw/statcan_14100245-eng.zip` |
| Context only (not used) | StatCan table 14-10-0261-01 (ex-CANSIM 281-0006, archived). SEPH, SIC-1980 basis, 1983–2000. Vector v250810 = 626.45 for 2000 | https://www150.statcan.gc.ca/n1/tbl/csv/14100261-eng.zip | `raw/statcan_14100261-eng.zip` |
| Check | StatCan's own table pages, default view | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410020401 and …?pid=1410024501 | `raw/statcan_tbl_14-10-0204-01_page.html`, `raw/statcan_tbl_14-10-0245-01_page.html` |

SHA-256 values are listed by `shasum -a 256 raw/*`. The main zip's hash is `33a092d5…b3fd`.
URLs are listed in `SOURCES.csv`. Each one returned HTTP 200 on 2026-10-17.

## Method

- Annual figure = StatCan's published annual average weekly earnings × **52**.
  - Using 365/7 = 52.14 instead would raise every year by 0.27%.
- The script asserts each dimension label on every row it uses, plus the units (current dollars).
- Definitions, from the table's own footnotes:
  - Earnings are "gross payroll before source deductions" (note 16).
  - "All employees" is hourly-paid + salaried + other employees (note 19). It is a head count of payroll jobs and is not FTE-converted.
- **Concept column:** each row in the CSV carries its source vector, and the 2000 row is flagged as using the old method.

## Check against the agency's own printed table (run by the script)

- The default view of table 14-10-0204-01 prints the "Industrial aggregate excluding unclassified businesses" row for Canada, All employees, Including overtime: 1,130.07 / 1,165.24 / 1,204.92 / 1,260.20 / 1,302.86 for 2021–2025.
  - All five equal the CSV values to the cent.
- The archived table page 14-10-0245-01 prints 655.55, equal to the 2000 value used.
- **OECD cross-check.** OECD wages and salaries (D11, S1, current prices, CAD) ÷ OECD employees (SAL, persons):

| Year | StatCan ×52 | OECD D11/SAL | Ratio |
|---|---|---|---|
| 2000 | 34,089 | 36,114 | 0.944 |
| 2007 | 40,943 | 44,454 | 0.921 |
| 2016 | 49,744 | 52,064 | 0.955 |
| 2022 | 60,592 | 64,673 | 0.937 |
| 2025 | 67,749 | 70,815 | 0.957 |

SEPH runs 4–8% below the national-accounts figure, and the gap is stable (no trend). This is the expected sign:
- D11 includes pay that SEPH misses, such as agriculture, military pay, and some in-kind and irregular pay.
- SAL is a different count of employees from SEPH payroll jobs.

## Known limits (stated before anyone else finds them)

1. **2000/2001 methodology break.**
   - StatCan note 15: "The introduction of administrative data in 2001 and the associated change in methodology resulted in level shifts for some series. This affects the comparability of pre- and post-2001 estimates."
   - The seam is visible in the numbers:
     - old-series growth 1999→2000 is +2.35%;
     - 2000 (old) → 2001 (new) is only +0.22%;
     - new-series growth 2001→2002 is +2.40%.
   - So the 2000 level is probably about 2% too high relative to the 2001+ basis.
   - StatCan publishes no overlap year, so no bridge is possible, and none is applied.
   - **A user who wants a break-free series should start at 2001.**
2. **Coverage is not the whole economy.**
   - The "industrial aggregate" excludes agriculture, fishing and trapping, private household services, religious organisations and military personnel (note 5).
   - It also excludes businesses not yet classified.
   - Israel's CBS figure covers all employee posts. This is the main reason SEPH sits below the OECD figure.
3. **Unit = payroll jobs, not persons.** SEPH counts employees on establishment payrolls, so a person with two jobs counts twice. The CBS benchmark is "per employee post", which is the same logic.
4. **Composition effects.** 2020 shows +6.6% because low-paid jobs were lost in the pandemic, not because pay rose. 2021 continues from that higher base. This is a true average, not a fixed-weight wage index.
5. **Weeks factor.** ×52 is a convention. 52.14 is equally defensible and adds 0.27%. It does not affect ratios or trends.
6. **Data quality flags.** StatCan grades 2009–2019 "A" (excellent) and 2020–2025 "B" (very good). 2001–2008 carry no flag.
7. **Revisions.** The table was last refreshed 2026-03-26 (zip file timestamps). Recent years could be revised.
