# United Kingdom: average price of a dwelling, 2000–2025 (GBP)

Price side only. Wages are handled elsewhere.
Rebuild: `python3 -I build_gbr.py`. The script reads only `raw/` and writes three files:
- `gbr_avg_dwelling_price_2000-2025.csv` is the main series.
- `gbr_ukhpi_avg_price_2000-2025.csv` is the official headline alternative.
- `gbr_series_comparison.csv` puts the two side by side and includes the checks.

**CERTAINTY: high for the main series as defined (England and Wales, arithmetic mean price paid).** It is a plain average of every standard registered sale. ONS publishes it through 2022. For 2023–2025 we computed it from the Land Registry's record-level file, and our method reproduces ONS's published 2022 figure to within 0.54%. **Medium if the series is read as "the UK".** Scotland and Northern Ireland are not in it (see limit 1).

## Result

| Year | Main: E&W arithmetic mean price paid (£) | Alternative: UK HPI average price, UK (£) | Main ÷ UK HPI (E&W) |
|---|---|---|---|
| 2000 | **107,462** | 82,534 | 1.44 |
| 2007 | **219,365** | 170,598 | 1.24 |
| 2016 | **282,701** | 195,035 | 1.35 |
| 2025 | **372,590** | 267,281 | 1.31 |

All 26 years from 2000 to 2025 are filled in both series. None were interpolated.

## Concept

- **Main series.** The arithmetic mean of the price actually paid in every standard ("category A") residential sale registered with HM Land Registry in England and Wales during the calendar year.
  - Covers new and existing dwellings.
  - Covers all property types: houses and flats.
  - Covers cash and mortgage sales.
  - This is the concept closest to Israel's CBS average: a simple mean of transacted dwellings. It is not mix-adjusted.
- **Alternative series.** The UK House Price Index "average price". This is the figure UK media quote.
  - It is not a mean of sale prices. It is a hedonic, mix-adjusted index applied to the **geometric** mean modelled price of a fixed reference set of properties, anchored to **January 2023**.
  - Source wording (`raw/govuk_uk_hpi_quality_and_methodology.html`): "price levels are derived by taking the January 2023 average price of a reference set of properties and applying individual period inflation rates to produce the full time series".
  - Source wording (`raw/govuk_about_the_uk_hpi.html`): "the standard average house price is calculated by taking the average (geometric mean) price in a base period and then recalculating it in accordance with the index change back in time and forward".
  - The arithmetic mean runs 24–46% above it, and the size of that gap changes over time. We do not recommend it for a comparison with Israel's mean, but it is kept here so that nobody can say we hid it.

## Inputs (all downloaded 2026-10-17)

| Input | Series | Publisher | URL | Raw file |
|---|---|---|---|---|
| Main, 2000–2022 | HPSSA dataset 12, table 1a, row K04000001 "England and Wales", columns "Year ending Dec YYYY". Release of 20 Sep 2023; next release "to be announced" | ONS (from HM Land Registry Price Paid) | https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/meanhousepricefornationalandsubnationalgeographiesquarterlyrollingyearhpssadataset12 (file: `.../current/hpssadataset12meanpricepaidforadministrativegeographies.xls`) | `raw/ons_hpssa_dataset12_mean_price_paid_EW.xls`, `raw/ons_hpssa_dataset12_page.html` |
| Main, 2023–2025, and the 2022 check | Price Paid Data, yearly files, category A only | HM Land Registry | http://prod1.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-YYYY.csv (files last modified 28 Sep 2026) | `raw/hmlr_price_paid/pp-2022.csv` … `pp-2025.csv` |
| Price Paid field definitions | Category A/B definitions, column order | HM Land Registry | https://www.gov.uk/guidance/about-the-price-paid-data | `raw/govuk_about_the_price_paid_data.html` |
| Alternative | UK HPI `Average_Price`, regions "United Kingdom" and "England and Wales", monthly, release of July 2026 data | HM Land Registry / ONS / Registers of Scotland / LPS NI | https://publicdata.landregistry.gov.uk/market-trend-data/house-price-index-data/Average-prices-2026-07.csv | `raw/ukhpi_average_prices_2026-07.csv` (plus the full file `raw/ukhpi_full_file_2026-07.csv`, from `.../UK-HPI-full-file-2026-07.csv`) |
| UK HPI method | Geometric mean, Jan 2023 anchor, coverage dates | HM Land Registry | https://www.gov.uk/government/publications/about-the-uk-house-price-index/about-the-uk-house-price-index and `.../quality-and-methodology` | `raw/govuk_about_the_uk_hpi.html`, `raw/govuk_uk_hpi_quality_and_methodology.html` |
| Release checks | Printed UK averages for Dec 2025 and Jul 2026 | HM Land Registry | https://www.gov.uk/government/news/uk-house-price-index-for-december-2025 and `...-for-july-2026` | `raw/govuk_news_uk_hpi_for_december_2025.html`, `raw/govuk_news_uk_hpi_for_july_2026.html` |

## Method

- **Main series, 2000–2022.** These are ONS's published values. Each covers the four quarters ending in December, so it is the mean over every sale in the calendar year, weighted by transactions. It is not a mean of monthly means.
- **Main series, 2023–2025.** The script takes the mean of column 2 (price) over all rows of `pp-YYYY.csv` where column 15 (PPD category) is "A".
  - It asserts that every row's transfer date falls in that year.
  - It asserts that every row has record status "A".
  - Sales counted: 708,315 (2023), 763,905 (2024), 809,461 (2025).
- **Alternative series.** The mean of the 12 monthly UK HPI average prices in each year.
- **Anchor.** The main series has none, because it is a direct mean of prices. The alternative is anchored to January 2023 (see Concept).

## Checks against the sources' own printed numbers

1. **Our method against ONS for 2022.** ONS publishes £367,163. Our computation from `pp-2022.csv` gives £369,156, which is +0.54%. The small gap is expected: the Land Registry file is a 2026 vintage, so it contains sales registered late, after ONS cut its 2023 release. This shows that "category A, E&W, mean" is ONS's definition.
2. **UK HPI, July 2026.** The release says "the average property in the UK valued at £273,000". The file has £272,611 (rounds to £273,000). Match.
3. **UK HPI, December 2025.** The release of 18 Feb 2026 printed £270,000. The current file has £268,493 (rounds to £268,000). The first estimate has since been revised down by about 0.6%. UK HPI levels are revised after first publication.

## Known limits (stated before anyone else finds them)

1. **The main series is England and Wales, not the UK.** Scotland and Northern Ireland are missing.
   - Both have lower prices. UK HPI 2025 averages are £189,196 for Scotland and £189,530 for NI, against £283,688 for E&W. `build_gbr.py` prints these.
   - So a true UK arithmetic mean would be somewhat lower than our main figure.
   - We have not computed how much lower, because Scotland and NI have no matching category-A mean price paid series in the files we downloaded.
2. **It splices two vintages at 2022/2023.** ONS stopped updating HPSSA after Sep 2023. 2023–2025 are our own computation from Land Registry records, using the same definition. The overlap year differs by 0.54% (check 1), so the splice may overstate 2022→2023 growth by up to about half a percent.
3. **2025 may be incomplete, and it is distorted.**
   - Registration lags, so December 2025 holds 57k category-A sales against 69k in December 2024 (69k against 84k counting both categories). Late registrations will move the 2025 mean slightly.
   - March 2025 has 145k sales, twice a normal month. This is the rush before the 1 April 2025 stamp duty change, and it changes the mix of buyers within the year.
4. **A plain mean is driven by the mix of sales.**
   - The mean tracks what was sold, not only price change. 2009–2013 is the clearest case: cheaper sales collapsed after the crash, and the mean rose while the mix-adjusted index fell.
   - London and high-value sales pull the mean up. The median would be much lower.
   - Israel's CBS mean has the same property, so the concepts match. But anyone comparing UK *trends* through the mix-adjusted UK HPI will see a different shape: the ratio between the two series moves between 1.24 and 1.46.
5. **The UK's headline "average house price" is the lower figure.** A hostile reader will quote "£267k in 2025", not £373k. The two differ in concept (geometric, hedonic, Jan 2023 anchor) and in coverage (UK vs E&W). Both are in the folder, and the comparison file shows the ratio for every year.
6. **What category A leaves out.** It excludes repossessions, buy-to-let purchases identified by mortgage, sales to companies or other non-private buyers, and "other" property types (category B, identified only from Oct 2013). It also excludes right-to-buy discounts and non-market transfers. Category A has existed since Jan 1995, so the definition is stable across 2000–2025. Including category B would raise 2025 to £390,815 (column `ppd_mean_cat_A_plus_B` in `gbr_series_comparison.csv`).
7. **The UK HPI before 2004/2005 is not a true UK series.** Its own documents say Scotland is covered from Jan 2004 and NI from Jan 2005. Earlier UK values rely on E&W data and a back series from the discontinued ONS HPI. This affects only the alternative series.
