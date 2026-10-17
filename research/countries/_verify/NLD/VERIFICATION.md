# Netherlands (NLD) — independent verification

Verifier blind step: downloaded CBS StatLine OData v3 tables 85773NED and 85919NED (full TypedDataSet, unfiltered) into `raw/`, computed with `verify_NLD.py`. Then compared with `../ours_NLD.csv` and `countries/NLD/`.

| year | ours price | yours price | diff % | ours wage | yours wage | diff % | ours ratio | yours ratio |
|---|---|---|---|---|---|---|---|---|
| 2000 | 172,050 | 172,050 | 0.00 | 24,229 | 24,229 | 0.00 | 7.10 | 7.10 |
| 2007 | 248,325 | 248,325 | 0.00 | 29,472 | 29,472 | 0.00 | 8.43 | 8.43 |
| 2013 | 213,353 | 213,353 | 0.00 | 32,885 | 32,885 | 0.00 | 6.49 | 6.49 |
| 2016 | 243,837 | 243,837 | 0.00 | 34,050 | 34,050 | 0.00 | 7.16 | 7.16 |
| 2022 | 428,591 | 428,591 | 0.00 | 39,323 | 39,323 | 0.00 | 10.90 | 10.90 |
| 2025 | 479,527 | 479,527 | 0.00 | 46,744 | 46,744 | 0.00 | 10.26 | 10.26 |

Wage = `Lonen_2` (mln EUR) × 10^6 / (`Totaal_27` banen, ×1 000 × 10^3), sector `T001081` (A-U). Price = `GemiddeldeVerkoopprijs_7`, period `YYYYJJ00`.

## Findings

- **OK — numbers.** All 18 values match exactly. Our raw 85773NED file is row-for-row identical to a fresh download today; our 85919NED raw file is identical to the T001081 subset of a fresh full download.
- **OK — arithmetic reproduces.** `build_nld.py` and `wage/build_nld_wage.py`, run on a scratch copy, regenerate `nld_avg_dwelling_price_2000-2025.csv`, `nld_avg_annual_wage_2000-2025.csv` and `nld_wage_checks.csv` byte-identically. (The wage script needs `countries/wages/raw/` for the OECD check; it fails if `NLD/` is copied alone. That's cosmetic.)
- **OK — URLs.** Every URL in both SOURCES.csv files returns HTTP 200 and serves the claimed table, including the CBS news release.
- **OK — concept.** The 85773NED metadata confirms the scope: existing dwellings on Dutch territory "verkocht aan een particulier", Kadaster-based. The 85919NED metadata confirms Lonen and banen (full- plus part-time) for whole-economy employees. 2025 is "Voorlopig" in 85919NED, and the README says so.
- **CONCERN — price SOURCES.csv provenance.** The rows for `raw/cbs_83625NED_regions_dimension.json` and `raw/cbs_83625NED_tableinfos.json` give the 83625NED *TypedDataSet* URL. The files actually hold the RegioS dimension and the TableInfos. The correct URLs are `https://opendata.cbs.nl/ODataApi/odata/83625NED/RegioS` and `.../83625NED/TableInfos` (both 200). These are only cross-check files, so no number is affected, but a hostile reader who follows the links will see the wrong content.
- **CONCERN — README price limit 7 is inaccurate.** The README says 85773NED's recent months are provisional and 2025 "may still be revised". The table's own TableInfos says "De cijfers in deze tabel zijn direct definitief", with revision only in exceptional cases. The statement is harmless but wrong. Replace it with CBS's wording.
- **CONCERN — per-job vs per-FTE wage, which is especially sensitive for NL.** The Netherlands has an unusually high part-time share. Per FTE (`LonenPerArbeidsjaar_9`), the ratio would be 5.55 (2000), 6.40 (2007), 4.85 (2013), 5.37 (2016), 8.29 (2022) and 7.81 (2025), about 24% lower than ours. The README states the 28-34% per-job/per-FTE gap in general terms but does not flag that NL is an outlier here. A hostile reader can say the per-job denominator flatters NL's "unaffordability" relative to countries with fewer part-timers. It is defensible because it matches Israel's per-post concept, but the reason should be stated explicitly.
- **CONCERN (already stated in README) — price scope.** The price covers existing homes only, bought by private persons, and is an unadjusted mean (CBS warns it is not a price-change indicator). The README discloses all of this; it is listed here only for completeness.
- **OK — 2025 cross-check.** 479,527 rounds to the "480 duizend" in the CBS 2026/08 news release.
