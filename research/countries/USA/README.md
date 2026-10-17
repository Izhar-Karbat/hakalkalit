# United States: average price of a dwelling, 2000–2025 (USD)

Price side only; wages are handled elsewhere.
Rebuild: `python3 build_usa.py` → `usa_avg_dwelling_price_2000-2025.csv`.
The script reads only `raw/`, and checks the 2023–2025 figures against the table the Census Bureau prints in its own release.

**Concept, plainly:** the **mean** sales price of **new** single-family houses sold, whole country, land included, as published annually by the Census Bureau and HUD.
It is **not** a price of all dwellings transacted. Existing homes are most sales and are not in it. Condominium flats are not in it either.

**CERTAINTY: medium.**
- The numbers themselves are high-certainty: an official federal survey, published annually, and matched to the printed release.
- The concept is the weak point. The United States has no official mean price of all dwellings transacted, existing and new. "New houses only" is the closest official *level*, and it is a different market from Israel's all-transactions figure.

## Result

| Year | Average price of a new house sold (USD) |
|---|---|
| 2000 | 207,000 |
| 2007 | 313,600 |
| 2016 | 360,900 |
| 2025 | **523,800** |

All 26 years from 2000 to 2025 are filled. None are blank and none are interpolated.

## Inputs

| Input | Series | Publisher | URL | Raw file | Downloaded |
|---|---|---|---|---|---|
| Main series | Sales price of new privately-owned houses sold, United States, **Average sales price**, sheet "Annual" (monthly sheet also present). Same concept as FRED `ASPUS`, which is a republication. | U.S. Census Bureau and HUD, Survey of Construction (New Residential Sales) | https://www.census.gov/construction/nrs/xls/price_cust.xlsx | `raw/census_nrs_price_cust_new_houses_sold_median_avg_price.xlsx` | 2026-10-17 |
| Check: printed release | Quarterly Sales by Price and Financing, Table Q6 "Median and Average Sales Price of New Houses Sold by Region", release of July 24, 2026 | Census / HUD | https://www.census.gov/construction/nrs/pdf/quarterly_sales.pdf | `raw/census_nrs_quarterly_sales_release.pdf` | 2026-10-17 |
| Definitions | Survey of Construction methodology page | Census | https://www.census.gov/construction/soc/methodology.html | `raw/census_soc_methodology.html` | 2026-10-17 |
| Check: market-wide trend | FHFA House Price Index, traditional, **purchase-only**, quarterly, `USA`, not seasonally adjusted | Federal Housing Finance Agency | https://www.fhfa.gov/hpi/download/monthly/hpi_master.csv | `raw/fhfa_hpi_master_all_indexes.csv` | 2026-10-17 |

FRED's own copy of `ASPUS` could not be downloaded (the connection stalled), so it is not used. Census is the primary publisher anyway.
NAR (an industry body) is not used, not even as a check.

**Method.**
- The CSV uses the **annual average as Census publishes it**. No months or quarters are averaged.
- Census computes that figure from all houses sold in the year. It is not a mean of monthly averages.
- The script prints the mean of the 12 published monthly averages for comparison. It runs **0.5–2.4% below** the published annual figure in every year. Census footnotes that the annual figures "may reflect revisions not distributed to months". The published annual figure is the one used.
- No anchoring and no index arithmetic. Every value is a published level.

**Source check (recorded).** The script parses Table Q6 of the release PDF and compares it with the xlsx:

| Year | xlsx | Printed in release (Q6) | |
|---|---|---|---|
| 2023 | 514,000 | 514,000 | match |
| 2024 | 514,500 | 514,500 | match |
| 2025 | 523,800 | 523,800 | match |

## Known limits (stated before anyone else finds them)

1. **New homes only.**
   - Existing homes are not included. They are most US sales: the release counts about 0.68 million new houses sold in 2025.
   - New homes are bigger and built further out, so their price level and trend differ from the market as a whole.
2. **Understates price growth since 2016, against the whole market.** The FHFA purchase-only index covers existing and new homes bought with conforming mortgages. Both series below are indexed to 2000 = 100:

   | Year | Census average, new | FHFA purchase-only |
   |---|---|---|
   | 2007 | 151.5 | 157.3 |
   | 2011 | 129.4 | 126.0 |
   | 2016 | 174.3 | 160.9 |
   | 2025 | **253.0** | **306.5** |

   - Between 2022 and 2025 the new-home average was flat while the whole-market index kept rising. Why is not tested here. One hypothesis is a shift in the mix of new homes sold toward smaller or cheaper ones.
   - A critic can therefore say this series makes 2025 US housing look **cheaper** than the market really is.
   - The reverse holds in some earlier years (2016).
3. **Houses, not flats.**
   - The series covers single-family houses only. Condominium apartments are excluded.
   - Israel's figure is mostly apartments.
4. **Not quality-adjusted.**
   - A plain mean, so mix effects pass straight through: house size, lot, region.
   - The mean is pulled up by expensive homes. In 2025 the median was 417,400, about 20% below the mean.
5. **Sample and imputation.**
   - It is a survey estimate, not a registry. The relative standard error of the national annual average is about 3% (Table Q6).
   - The methodology page states that the weighted item response rate for sales price was 65% in 2025. The rest is imputed.
   - In January 2005 the survey changed its sample of permit offices, which shifted toward outlying areas. Census notes this could lower measured prices.
6. **Revisions.**
   - Census revises published figures, including annual ones.
   - Numbers here are as downloaded on 2026-10-17.
   - An older, pre-revision Census workbook is still online (`usprice_cust.xls`, last modified Feb 2024). It shows 2022 at $540,000 against $521,500 here (+3.5%; ratio 7.72 instead of 7.45). It is superseded, not an error, but it can be quoted against us. A copy is in `../_verify/USA/raw/`.
7. **Contract price vs. sales price.** The figure is the sales price including the improved lot. It reflects the time of sale, not the time of completion.
