# Netherlands: average price of a dwelling, 2000–2025

Average sale price of an **existing** owner-occupied dwelling, whole country, euro, annual.
Rebuild: `python3 -I build_nld.py` → `nld_avg_dwelling_price_2000-2025.csv`.
The script reads only `raw/`. It checks every year against a second CBS table and against total value ÷ number of sales, and checks 2025 against the CBS news release.

**CERTAINTY: high** for "mean transaction price of existing dwellings". This is CBS's own published annual number, built from the complete Kadaster land register (every registered sale, not a sample or appraisal). No index, anchor or interpolation is involved. It is **medium** as a match to Israel's concept, because new-build sales are excluded (see limits).

## Result

| Year | Average sale price (EUR) |
|---|---|
| 2000 | **172,050** |
| 2007 | **248,325** |
| 2008 (pre-2013 peak) | 254,918 |
| 2013 (trough) | 213,353 |
| 2016 | **243,837** |
| 2025 | **479,527** |

All 26 years from 2000 to 2025 are filled. No year is blank.

## Inputs

| Input | Series | Publisher | URL | Raw file |
|---|---|---|---|---|
| Main series | 85773NED, `GemiddeldeVerkoopprijs_7`, period `YYYYJJ00` (annual); also monthly values, number of sales, total value | CBS (Statistics Netherlands) with Kadaster | https://opendata.cbs.nl/ODataApi/odata/85773NED/TypedDataSet?$format=json | `raw/cbs_85773NED_existing_dwellings_price_index_avg_price_monthly_annual_typeddataset.json` |
| Table metadata / definition | 85773NED TableInfos | CBS | https://opendata.cbs.nl/ODataApi/odata/85773NED/TableInfos | `raw/cbs_85773NED_tableinfos.json` |
| Cross-check table | 83625NED, `GemiddeldeVerkoopprijs_1`, region NL01 (Nederland) | CBS | https://opendata.cbs.nl/ODataApi/odata/83625NED/TypedDataSet?$filter=RegioS eq 'NL01  '&$format=json | `raw/cbs_83625NED_avg_sale_price_existing_dwellings_netherlands_annual.json` (+ `_regions_dimension.json`, `_tableinfos.json`) |
| Publication check | News release "Koopwoning kostte gemiddeld 480 duizend euro in 2025" (2026, week 08) | CBS | https://www.cbs.nl/nl-nl/nieuws/2026/08/koopwoning-kostte-gemiddeld-480-duizend-euro-in-2025 | `raw/cbs_news_2026-08_koopwoning_kostte_gemiddeld_480_duizend_euro_in_2025.html` |

All files were downloaded on 2026-10-17 and are stored unmodified. 85773NED was last modified by CBS on 2026-09-22, and 83625NED on 2026-02-17.

## Method

- The annual value is **CBS's own annual figure** (`JJ00` period), not computed by us from months. The script confirms that it equals total value of sales ÷ number of sales to within 0.1%. The total is published rounded to €1 million. So it is a **transaction-weighted mean** over all registered sales in the year.
- Rule 6 (mean of months) is not used for the main value, because CBS publishes the annual directly. For comparison, the plain mean of the 12 monthly averages is written in the `note` column. It differs by at most 0.5% in every year (e.g. 2000: 171,046 vs 172,050; 2025: 478,818 vs 479,527).
- Two independent CBS tables (85773NED and 83625NED) give identical values for every year from 2000 to 2025. The script asserts this.
- **Publication check:** the CBS news release table "Gemiddelde transactieprijs bestaande koopwoningen, 2025" prints *Nederland 480* (×1,000 euro). Our 479,527 rounds to 480. The release text says the 2025 average was "bijna 29 duizend euro hoger" than in 2024. Our figures give 479,527 − 450,985 = 28,542. Both checks pass, and the script asserts the first.
- No anchor year and no index arithmetic: these are levels as published.

## Known limits (stated before anyone else finds them)

1. **Existing dwellings only; new builds excluded.** CBS publishes no national average *transaction price* for new-build homes over 2000–2025. Its new-build tables are cost and price *indices* only (85772NED, 80334ned, 85728NED). Israel's figure covers all transactions. New builds are a minority of Dutch sales, but they are typically priced above the existing-stock average. So the Dutch level is, if anything, slightly understated.
2. **Buyer restriction:** CBS counts only dwellings bought **by a private person** (`verkocht aan een particulier`). Purchases by investors, companies and housing associations are excluded.
3. **Unadjusted mean, not a price index.** CBS itself warns that the average sale price "is geen indicator voor de prijsontwikkeling": the mix of homes sold changes from year to year. 2009–2013 are an example: sales fell ~40%, and the mix shifted. For *price change* CBS points to its index (PBK, `PrijsindexVerkoopprijzen_1`, in the same raw file). We use the mean because the comparison is about *levels* (what an average dwelling costs), which is what Israel's figure is.
4. **Date = registration at the Kadaster,** not contract signing. Registration typically lags the deal by a few months, so a calendar year partly reflects prices agreed in the previous autumn.
5. **Pre-2002 euros are converted guilders.** The 2000–2001 values are in euro, presumably converted by CBS at the fixed rate (2.20371 NLG/EUR). We did not see this stated in the downloaded metadata.
6. **Mean, not median.** A few very expensive sales (e.g. Blaricum at €1.1m) pull the mean above the typical sale. The median is not published in these tables.
7. **Revisions:** CBS publishes 85773NED as final on release ("direct definitief"), so the 2025 price is not expected to change. The 2025 wage (85919NED) is provisional. The tables were downloaded 2026-10-17.
8. **Per job, not per full-time equivalent.** The Netherlands has an unusually high share of part-time jobs. Dividing wages by full-time equivalents instead of jobs would lower its ratio by about 24% (2025: 7.8 instead of 10.3). We divide by jobs because that is Israel's CBS concept (wage per employee post); a per-FTE comparison would have to convert Israel too.
