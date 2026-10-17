# GBR verification (England & Wales price, GB wage) — 2026-10-17

**Verdict: VERIFIED WITH CONCERNS.** All six years reproduce exactly from independently downloaded official files. No number in `ours_GBR.csv` is wrong. The concerns are about provenance records and README wording.

Independent inputs (`raw/`, URLs in `raw/SOURCES.csv`): ONS KAB9 csv (LMS dataset, release 15-09-2026), ONS HPSSA dataset 12 xls, HM Land Registry `pp-2000/2007/2013/2016/2022/2025.csv` (last-modified 28 Sep 2026). Script: `verify_GBR.py`, output `verify_GBR_out.csv`.

Method used blind: price = HPSSA 12 table 1a, row K04000001, "Year ending Dec YYYY" for 2000–2022; 2025 = mean of PPD category A rows in `pp-2025.csv`. Wage = mean of 12 monthly KAB9 values × 52.

| year | ours price | yours price | diff % | ours wage | yours wage | diff % | ours ratio | yours ratio |
|---|---|---|---|---|---|---|---|---|
| 2000 | 107,462 | 107,462 | 0.00 | 16,263 | 16,263 | 0.00 | 6.61 | 6.61 |
| 2007 | 219,365 | 219,365 | 0.00 | 21,827 | 21,827 | 0.00 | 10.05 | 10.05 |
| 2013 | 247,196 | 247,196 | 0.00 | 24,215 | 24,215 | 0.00 | 10.21 | 10.21 |
| 2016 | 282,701 | 282,701 | 0.00 | 25,662 | 25,662 | 0.00 | 11.02 | 11.02 |
| 2022 | 367,163 | 367,163 | 0.00 | 32,023 | 32,023 | 0.00 | 11.47 | 11.47 |
| 2025 | 372,590 | 372,590 | 0.00 | 37,834 | 37,834 | 0.00 | 9.85 | 9.85 |

Cross-check: the same category-A mean computed from the current (2026-vintage) PPD files for each HPSSA year gives 2000 107,511 (+0.05%), 2007 219,397 (+0.01%), 2013 247,221 (+0.01%), 2016 282,737 (+0.01%), 2022 369,156 (+0.54%). So HPSSA = PPD category A, E&W, by date of transfer. The 2022 gap is the only one above 0.05%, which fits late registrations after ONS's Sep 2023 cut. Including category B would make the price 3–17% higher in the post-2013 years (2016 313,751; 2022 414,657; 2025 390,815).

## Findings

1. **OK — numbers.** Price, wage and ratio match to the pound for all six years. The raw files are byte-identical to ours (md5 match for `pp-2022.csv`, `pp-2025.csv` and the HPSSA xls). KAB9 data rows are identical; only the header differs, because ours came from the `/lms` dataset URI and theirs from `/emp`. Re-running `build_gbr.py` on our raw files regenerates `gbr_avg_dwelling_price_2000-2025.csv` byte-identically.
2. **OK — URLs.** Every URL in both SOURCES.csv files returned HTTP 200 on 2026-10-17. The UK HPI csvs re-download with identical md5.
3. **CONCERN — SOURCES.csv provenance, price side.**
   - (a) The row for `raw/ukhpi_full_file_2026-07.csv` gives the URL `.../Average-prices-2026-07.csv`. The file actually comes from `.../UK-HPI-full-file-2026-07.csv`: md5 07692c80… matches that URL, not the Average-prices one. The README has it right; SOURCES.csv is wrong.
   - (b) The HPSSA xls row gives the landing-page URL, not the file URL (`https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/housing/datasets/meanhousepricefornationalandsubnationalgeographiesquarterlyrollingyearhpssadataset12/current/hpssadataset12meanpricepaidforadministrativegeographies.xls`).
   - (c) `raw/hmlr_price_paid` is listed as one row with a `pp-YYYY.csv` placeholder. There is no per-file row for 2022–2025.
4. **CONCERN — the 2022/2023 splice changes the direction of the 2022→2023 move.** Not one of the six headline years, but visible in the full series. Published HPSSA 2022 is 367,163 and our 2023 is 368,021, which reads as +0.2%. Like-for-like from the same PPD vintage, 2022 is 369,156 and 2023 is 368,021, which is −0.3%. The README says the splice "may overstate 2022→2023 growth by up to about half a percent". It does not say the sign flips. Option: use the PPD own-computation for 2022 as well, or state the like-for-like change.
5. **CONCERN — README wording errors, no number affected.**
   - (a) Price README says the UK HPI "runs 24–46% below the arithmetic mean". The data say the mean is 24–46% *above* the HPI (ratio 1.243–1.464), which means the HPI is about 20–32% *below* the mean.
   - (b) Price README limit 3: "December 2025 holds 69k sales against 84k in Dec 2024" are all-category (A+B) counts. For the category A rows actually used, it is 57,425 vs 68,923 (−17%).
   - (c) The wage README header says ASHE is "3–15% above" AWE. Limit 2 and the comparison CSV say 3–18%, and the actual range is 3.3–17.6%. The header is wrong.
6. **CONCERN — 2025 completeness, magnitude bounded.** Category A counts by month in `pp-2025.csv`: Dec 57,425 against 68,923 for Dec 2024, so roughly 10–15k late registrations are still to come. Rough arithmetic bound: if 15k more sales arrive at December's mean (£356k), the 2025 mean falls about 0.3% (372.6k → ~372.3k). The ratio moves by about 0.03. Small, but the README does not quantify it.
7. **CONCERN (stated in README, but it is the main attack surface) — the wage level depends on the survey.** AWE×52 is 4–18% below ASHE mean annual pay. On ASHE, 2000's ratio would be ~5.7, not 6.6, and 2025's ~9.3, not 9.85. AWE growth 2000–2025 is +133% against ASHE +113%. So the claimed 2000→2025 rise in UK unaffordability (6.6 → 9.85) is about 8 percentage points larger on AWE than it would be on ASHE. The README discloses this (limits 2–3). Any trend claim should be shown on both series.
8. **CONCERN (stated) — geography mismatch.** Price is E&W, wage is GB. The README quantifies it at about 1%. OK as disclosed.
9. **OK — concept.** HPSSA metadata: "count, median price, mean price … of all dwellings sold and registered in a given period of four consecutive quarters … calculated using open data from the HM Land Registry". The PPD reproduction (finding above the table) confirms this means category A only, by transfer date. KAB9's title is "AWE: Whole Economy Level (£): Seasonally Adjusted Total Pay Excluding Arrears", matching the claimed concept. The ONS annual KAB9 values equal our 12-month means rounded, for all six years.
10. **OK — stamp-duty distortion.** March 2025 category A = 123,605 sales at a mean of £387k, against April at 33,952 and £338k. The mix shift is real and the README states it.
