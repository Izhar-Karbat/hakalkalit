# Germany: average price of a dwelling, 2000–2025 (EUR)

Price side only. Rebuild with `python3 build_deu.py` (needs `pdftotext`). It writes `deu_avg_dwelling_price_2000-2025.csv` and `deu_workings.csv`.
The script reads only `raw/`. All files were downloaded on 2026-10-17.

**CERTAINTY: medium.**
- 2014–2025 is close to high. The level is a true mean of every recorded sale of a house or flat in 2024, and Destatis guarantees that its index is comparable over time from 2014.
- 2000–2013 is low to medium. Destatis says in writing that the index was "still in its build-up phase" before 2014. Where a direct mean exists (2009–2013), it sits 5–9% below the index-chained value.

## Result

| Year | Average dwelling price (EUR) | Direct AK OGA mean, check (EUR) |
|---|---|---|
| 2000 | **165,203** | n/a |
| 2007 | **158,930** | n/a |
| 2016 | **210,313** | 201,576 |
| 2022 (peak) | **321,145** | 312,869 |
| 2024 (anchor) | **289,479** | 289,422 |
| 2025 | **298,740** | not yet published |

**Concept:** the mean price per transacted dwelling, whole country. A dwelling here means a single- or two-family house, a terraced or semi-detached house, or a condominium flat. New and existing sales are both included, and the price includes the land. These are actual notarised transaction prices, not asking prices or appraisals. Transfer tax and other fees are excluded.

## Inputs

| Input | Series | Publisher | URL | Raw file |
|---|---|---|---|---|
| Level (2024) | Money turnover and number of transactions by category, residential property, 2024: Abb. 4-20 (counts) and Abb. 4-21 (EUR bn). Uses Eigenheime and Eigentumswohnungen. | Arbeitskreis der Oberen Gutachterausschüsse (AK OGA) with BBSR, *Immobilienmarktbericht Deutschland 2025* (published 2025-12-15) | https://redaktion-akoga.niedersachsen.de/download/224020 | `raw/akoga_Immobilienmarktbericht_Deutschland_2025.pdf` |
| Movement | GENESIS 61262-0001, Häuserpreisindex (`PRE026`), annual average, 2025=100 | Statistisches Bundesamt (Destatis) | https://genesis.destatis.de/genesis/api/rest/tables/61262-0001/data (plus `/structure` and `/information`) | `raw/destatis_genesis_61262-0001_HPI_annual_*.json` |
| Check: quarters | GENESIS 61262-0002, Häuserpreisindex, quarterly | Destatis | https://genesis.destatis.de/genesis/api/rest/tables/61262-0002/data | `raw/destatis_genesis_61262-0002_HPI_quarterly_*.json` |
| Check: printed values | Destatis table page "Preisindizes für Wohnimmobilien" (status 24 Sept 2026) | Destatis | https://www.destatis.de/DE/Themen/Wirtschaft/Preise/Baupreise-Immobilienpreisindex/Tabellen/Haeuserpreise-Bauland.html | `raw/destatis_table_page_Haeuserpreise-Bauland.html` |
| Method / caveats | Qualitätsbericht Häuserpreisindex (2018) | Destatis | https://www.destatis.de/DE/Methoden/Qualitaet/Qualitaetsberichte/Preise/haeuserpreisindex.pdf?__blob=publicationFile | `raw/destatis_Qualitaetsbericht_Haeuserpreisindex.pdf` |
| Quality flags | GENESIS quality-sign legend ("e" = final) | Destatis | https://genesis.destatis.de/genesis/api/rest/tables/61262-0002/qualitySigns | `raw/destatis_genesis_qualitySigns.json` |

The GENESIS JSON files are the server's responses saved unmodified. The classic `genesisWS` API rejected guest access, so the files came from the public REST API behind genesis.destatis.de/datenbank/online.

## Method

1. **Anchor level, 2024.** From AK OGA Abb. 4-20 and 4-21:
   - Eigenheime: 252,900 sales for EUR 84.3 bn.
   - Eigentumswohnungen: 255,600 sales for EUR 62.9 bn.
   - Level = (84.3 + 62.9) bn ÷ (252,900 + 255,600) = **EUR 289,479**.

   Building plots and multi-family houses are excluded, because they are not single dwellings.
2. **Movement.** Price(y) = 289,479 × HPI(y) ÷ HPI(2024), with HPI(2024) = 96.9 (2025=100). Every value is flagged "e" (final).
3. **Annual values.** These are Destatis's own annual averages of table 61262-0001. The script checks them against the mean of the four quarters in 61262-0002. The largest gap over 2000–2025 is 0.05 index points.

**Checks against the sources' own printed numbers.** The script runs each one and prints the result.
- **Condominium mean.** Turnover ÷ count for condominiums gives EUR 246,088. AK OGA prints EUR 246,000 for Germany (Abb. 4-76).
- **2025 vs 2024.** The HPI moves +3.2%. The Destatis table page prints +3,2 (2025 vs 2024).
- **Annual index values.** The annual values 2020–2025 in GENESIS (90.8, 101.4, 107.5, 98.4, 96.9, 100.0) match the Destatis table page exactly.
- **Charts against category tables.** The AK OGA time-series charts (Abb. 4-37/38/68/69) agree with the exact 2024 category figures (Abb. 4-20/21). The script asserts this.

**Second check: direct mean 2009–2024.** AK OGA prints transaction counts and turnover for both categories every year from 2009 (Abb. 4-37, 4-38, 4-68, 4-69). Turnover ÷ count gives a plain mean with no index involved. It is in `deu_workings.csv`, column `akoga_direct_mean_eur`. The chained series minus the direct mean:

| 2009 | 2012 | 2015 | 2018 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|
| +9.2% | +7.4% | +3.4% | +5.7% | +0.4% | −1.6% | +2.6% | +4.0% | 0.0% |

## Known limits (stated before anyone else finds them)

1. **2000–2013 rest on an index Destatis itself qualifies.** Qualitätsbericht §6.2: comparability over time is "seit dem Jahr 2014 gewährleistet. Zuvor befand sich der Häuserpreisindex noch in der Aufbauphase". Before 2014 far fewer valuation committees reported (§1.8). Every pre-2014 row in the CSV carries this note.
2. **No official level exists before 2009.** For 2000–2008 the price is the 2024 level moved back by the index. No German source publishes a national mean dwelling price for those years. The direct check covers only 2009–2024.
3. **The index is quality-adjusted; the anchor is not.**
   - The HPI is hedonic: it holds quality constant, per Qualitätsbericht §3.3.
   - The AK OGA mean is a plain average of what sold, like Israel's CBS average.
   - Hypothesis, not tested: the 5–9% gap in 2009–2013 comes from the mix of dwellings sold getting larger or better over time, which the index removes and a plain mean keeps. Whatever the cause, the early years in the main series are probably **too high** relative to a plain mean. That flatters Germany's price level in 2000–2013.
4. **The AK OGA totals are partly estimated.** Valuation committees covering about 88% of the area supplied data for 2024. AK OGA estimates the rest statistically (report §2 and the text above Abb. 4-16).
5. **Rounding.** AK OGA prints counts to the nearest 100 and turnover to EUR 0.1 bn, so the anchor is good to about ±0.1%. The 2009–2023 chart values (counts in thousands) are less precise, about ±0.3%.
6. **Category edges.** "Eigenheime" includes about 4.7% "übrige Eigenheime" (other owner-occupied homes). "Eigentumswohnungen" includes 8.5% not assignable to new or existing. All of these are dwellings, so they are kept.
7. **Different coverage in the two sources.** The HPI covers only turnkey new builds and existing homes at least 3 years old (Qualitätsbericht §1.2). Self-build on a bought plot is excluded from both sources.
8. **One anchor year.** If 2022 were used as the anchor, all years would be about 2.6% lower. That is the size of the anchor-year sensitivity.
9. **2025 depends on the index alone.** AK OGA has not yet published 2025 transaction totals.
10. **About 21,800 condominium sales the report cannot classify are included in the anchor.** The report says they may include non-residential units; they average only about €105k. Dropping them raises every year's price by about 2.8%. Keeping them is the conservative choice (it lowers Germany's ratio).
11. **Two states delivered only part of their data for 2024:** Baden-Württemberg about 22% and Saxony about 48%. AK OGA estimates the rest (see limit 4).
12. **Pre-2014 levels are probably too high.** Plain mean prices in the older official market reports (2013 and 2015 editions) put the index-based values 4–7% too high for 2007–2013, so the German ratio for those years is probably somewhat overstated.
