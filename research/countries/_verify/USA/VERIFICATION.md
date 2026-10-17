# Verification: United States (USA)

Independent rebuild, 2026-10-17. Step 1 was done blind (no project files opened); raw files in `raw/`, URLs in `raw/SOURCES.csv`, computation in `verify_USA.py` (output `verify_USA_out.csv`).

Sources found blind:
- Price: Census/HUD Survey of Construction, `price_cust.xlsx`, sheet "Annual", United States, Average sales price (new privately-owned houses sold, land included).
- Wage: BLS QCEW annual averages, row area_fips=US000, own_code=0, industry_code=10, size_code=0: `avg_annual_pay` (also recomputed as total_annual_wages / annual_avg_emplvl; agrees within $0.4). 2016/2022/2025 from the QCEW open-data API slices; 2000/2007/2013 from the `<year>_annual_singlefile.zip` files (the API slices return 404 before 2014).

| year | ours price | yours price | diff % | ours wage | yours wage | diff % | ours ratio | yours ratio |
|---|---|---|---|---|---|---|---|---|
| 2000 | 207,000 | 207,000 | 0.0 | 35,331 | 35,331 | 0.0 | 5.86 | 5.859 |
| 2007 | 313,600 | 313,600 | 0.0 | 44,458 | 44,458 | 0.0 | 7.05 | 7.054 |
| 2013 | 324,500 | 324,500 | 0.0 | 49,808 | 49,808 | 0.0 | 6.52 | 6.515 |
| 2016 | 360,900 | 360,900 | 0.0 | 53,621 | 53,621 | 0.0 | 6.73 | 6.731 |
| 2022 | 521,500 | 521,500 | 0.0 | 69,986 | 69,986 | 0.0 | 7.45 | 7.451 |
| 2025 | 523,800 | 523,800 | 0.0 | 78,720 | 78,720 | 0.0 | 6.65 | 6.654 |

Largest difference: none (0.0% on every cell). The blind price workbook is byte-identical to ours (SHA-1 b627147e...), as are the 2025 QCEW slice and the 2000 singlefile zip.

## Findings

**OK: (a) URLs.** All 4 price URLs and 15 of 16 wage URLs respond 200/206 with the stated content type. The BLS API JSON files are QCEW series ENUUS000{1,3,5}0010, as claimed.

**CONCERN (minor): (a) one URL is not reproducible by script.** `https://www.bls.gov/cew/publications/employment-and-wages-annual-averages/2007/tables/total-coverage-by-ownership.pdf` returns 403 to curl (bls.gov bot blocking, both a browser UA and a generic one). The saved file is a genuine 1-page PDF containing "Annual wages per employee ... $35,323 ... $44,458" as the README says. It is a check only, not an input. A reader using a browser should get it; a reader using curl will not.

**OK: (b) arithmetic.** Both build scripts, run on a copy outside the project tree, reproduce `usa_avg_dwelling_price_2000-2025.csv` and `usa_avg_annual_wage_2000-2025.csv` byte-for-byte. The price Q6 check against the release PDF matches for 2023-2025. Ratios = price / wage, rounded to 2 dp, are correct.

**OK: (c) concept.** The price is what the source says: the mean sales price of new single-family houses sold, land included ("Sales Price of New Privately-Owned Houses Sold"; NRS "houses" = single-family). The wage is QCEW total-covered, all ownerships, all industries, average annual pay = total annual wages / annual average employment, confirmed from the raw row.

**CONCERN: (d) a stale Census file shows a different 2022 price.** Census still serves the older workbook `https://www.census.gov/construction/nrs/xls/usprice_cust.xls` (Last-Modified 2024-02-26, saved in `raw/usprice_cust.xls`). It gives 2022 = **540,000** against the current 521,500 (+3.5%), 2021 = 464,200 against 458,300 (+1.3%), and 2023 = 511,100 against 514,000. 2000-2016 are identical. This is a pre-revision vintage, not an error in our numbers, but a hostile reader who finds that file (or quotes a 2023-era news story) will claim our 2022 is wrong by 18,500 USD. With 540,000 the 2022 ratio would be 7.72, not 7.45. The README mentions revisions only generically ("Census revises published figures"). Suggest naming the 2022 revision explicitly.

**CONCERN (already stated in README, restated for completeness): (d) new-only, houses-only.** The price excludes existing homes (most transactions) and condominiums, and its 2022-2025 trend diverges from FHFA purchase-only (flat vs rising). The README states all of this, including the direction of the bias for 2025. Nothing further to add, except that this is the largest attack surface: the 2022-to-2025 drop in the ratio (7.45 to 6.65) is driven by a flat new-home average, which the README itself shows is not what the wider market did.

**CONCERN (minor): (d) README result table omits 2013 and 2022.** The price README's table lists 2000, 2007, 2016, 2025 only; the comparison uses 2013 and 2022 too. The CSV has them; the README does not show them.

**OK: (d) wage limits.** README covers coverage (~95%), jobs-not-people, bonus/stock-option inclusion, the 2020 composition jump, the $8 revision for 2000, and the ~5% gap to OECD D11/SAL. I found nothing additional.

## Verdict
VERIFIED WITH CONCERNS. No ERROR: every number reproduces exactly from independently downloaded official files.
