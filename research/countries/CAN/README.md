# Canada: average price of a home sold, 2000–2025

The price side only: the average sale price of a residential property in Canada, in Canadian dollars, one figure per year.
Rebuild: `python3 build_can.py` (needs `openpyxl`). It writes `can_avg_dwelling_price_2000-2025.csv`.
The script reads only `raw/`. It fails if the downloaded file disagrees with the figure CREA prints in its own release.

**CERTAINTY: medium-high.**
- The level is CREA's own published annual figure. No arithmetic or anchoring is done here.
- It is a plain mean of actual sale prices, the same kind of figure as Israel's CBS average.
- It falls short of "high" for two reasons:
  - the publisher is the realtors' industry body, not a statistics office;
  - MLS® sales are mostly resales, so most new-build sales are missing.

## Result

| Year | Average sale price (CAD) |
|---|---|
| 2000 | 165,245 |
| 2007 | 307,924 |
| 2016 | 493,322 |
| 2021 | 695,184 |
| 2022 (peak) | 711,942 |
| 2025 | 680,368 |

All 26 years from 2000 to 2025 are filled. None is interpolated.

## Inputs

| Input | Series | Publisher | URL (downloaded 2026-10-17) | Raw file |
|---|---|---|---|---|
| Main series | "Residential Average Sale Price", annual, Canada, 1980–2025 (plus 2026F/2027F forecast rows, not used). Sheet `Chart`, the data file behind CREA's October 2026 quarterly forecast | Canadian Real Estate Association (CREA) | https://www.crea.ca/files/mls-hpi-data/Forecast_data_Oct_2026.xlsx | `raw/crea_forecast_data_Oct_2026_annual_avg_price_1980-2025.xlsx` |
| Check 1: printed release | October 2026 quarterly forecast release page | CREA | https://www.crea.ca/housing-market-stats/canadian-housing-market-stats/quarterly-forecasts/ | `raw/crea_quarterly_forecast_page_Oct_2026.html` |
| Check 1b: revisions | January 2025 and January 2026 forecast releases | CREA | https://www.crea.ca/media-hub/news/quarterly-forecasts-4/ and https://www.crea.ca/media-hub/news/crea-downgrades-resale-housing-market-forecast-amid-tariff-uncertainty-and-economic-uncertainty/ | `raw/crea_forecast_release_2025-01-15.html`, `raw/crea_forecast_release_2026-01-15.html` |
| Check 2: quality-adjusted | MLS® Home Price Index, Aggregate, `Composite_Benchmark`, annual, not seasonally adjusted, 2005 onward | CREA | https://www.crea.ca/files/mls-hpi-data/MLS_HPI_Oct_2026.zip | `raw/crea_MLS_HPI_Oct_2026.zip` (file `Not Seasonally Adjusted (A).xlsx`) |

SHA-256 of the main file: `3ac8feff8d82d0fa6037f7979fec6cc5d880455a4c20499198b1a1f64faff152`.

**Method.**
- The value is copied from CREA's annual column and rounded to the dollar. Nothing else is done to it.
- **Concept:** the mean sale price of all residential properties sold through Canada's MLS® Systems in the year, for the whole country:
  - all property types: detached, semi-detached, townhouse and condo apartment;
  - not seasonally adjusted and not quality-adjusted.
- **No anchor.** This is a published price level, not an index scaled to a base year.
- **Sub-annual rule (task rule 6) does not apply.** CREA publishes the annual figure directly. The file does not say whether it is total dollar volume ÷ units or a mean of the months. CREA's practice of quoting annual dollar volume points to volume ÷ units, but this is not verified here.

## Check against the source's own printed figures (run by the script)

1. **The file is the one behind the published text.**
   - The October 2026 release prints "forecast to edge higher by just 0.2% … to $681,681 in 2026".
   - The file's 2026F row is 681,681.196, an exact match.
   - Working back from the printed +0.2%, 2025 lies between 679,981 and 680,660. The file's 2025 is 680,368, inside that range.
2. **Revisions are small but real.**
   - The January 2025 release implies a 2024 average of 689,471–690,130. Today's file has 691,005, which is +0.17%.
   - The January 2026 release implies 2025 at 679,515–680,176. Today's file has 680,368, which is +0.08%.
   - CREA revises past years as late reports and new boards arrive.
3. **Quality-adjusted cross-check.**
   - Over 2005–2025 the average sale price and CREA's MLS® HPI composite benchmark stay within 3% of each other: ratio 1.028 in 2005, 1.023 in 2007, 1.028 in 2016, 0.994 in 2025.
   - Growth over 2005–2025: ×2.72 for the average, ×2.81 for the benchmark.
   - So shifts in the mix of homes sold do not drive the trend.

No direct printed statement of a past year's *actual* annual average was found among the releases downloaded. CREA's January releases print December's monthly average, not the year's. The checks above are therefore checks of consistency with CREA's published text, not a match against a printed annual figure.

## Known limits (stated before anyone else finds them)

1. **Industry source, not a statistics office.**
   - CREA is the realtors' association.
   - Statistics Canada publishes only indexes: the New Housing Price Index (new houses, constant quality, no level). CMHC's current data-table catalogue (checked 2026-10-17) no longer lists an MLS® price table.
   - So no government table carrying a national average price level for 2000–2025 was found.
   - CREA's average is nonetheless the series that Canadian government bodies and the press cite as "the national average price".
2. **Mostly resales.** MLS® covers homes listed by realtors. Builder-direct sales of new homes, which are large in condo-heavy Toronto and Vancouver, are largely missing. Israel's CBS figure covers new and second-hand homes together.
3. **Not a constant basket.** A plain mean moves with the mix of what sells. In Canada that mix is heavily weighted to the two most expensive markets, Toronto and Vancouver. Over 2005–2025 the HPI check above shows this does not bend the trend, but any single year can be pulled by mix.
4. **Coverage has grown, and history is revised.** The annual series is restated as boards are added or revise their data, so figures printed at the time differ from today's file.
   - Shown above for 2024 (+0.17%) and 2025 (+0.08%).
   - Older years: the federal housing agency CMHC republished this CREA series in its Housing Market Outlooks. Its February 2025 outlook prints 2022 = $704,543; this file has $711,942 (+1.05%). Across the test years the file runs 0.3–1.1% above CMHC's printed figures, so a ratio moves by about 1% at most. The CMHC PDFs are saved in `../_verify/CAN/raw/`.
   - Always cite this file's vintage: October 2026.
5. **The HPI check covers the "Aggregate" of participating markets,** not literally all of Canada, and starts only in 2005.
6. **2025 is the latest full year and the most likely to be revised again.**
