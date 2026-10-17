# Germany (DEU): independent verification

Verifier run 2026-10-17. Step 1 was done blind. Sources were found and downloaded independently into `raw/` (see `raw/SOURCES.csv`) and computed with `verify_DEU.py`. Our files were opened only afterwards.

**Verdict: VERIFIED WITH CONCERNS.** Every number reproduces exactly. The concerns are about how far the pre-2014 years and the anchor's category edges can be trusted. None of them is an arithmetic error.

## Numbers

| year | ours price | yours price | diff % | ours wage | yours wage | diff % | ours ratio | yours ratio |
|---|---|---|---|---|---|---|---|---|
| 2000 | 165,203 | 165,203 | 0.00 | 25,497 | 25,497 | 0.00 | 6.48 | 6.48 |
| 2007 | 158,930 | 158,930 | 0.00 | 27,876 | 27,876 | 0.00 | 5.70 | 5.70 |
| 2013 | 181,036 | 181,036 | 0.00 | 31,976 | 31,976 | 0.00 | 5.66 | 5.66 |
| 2016 | 210,313 | 210,313 | 0.00 | 34,828 | 34,828 | 0.00 | 6.04 | 6.04 |
| 2022 | 321,145 | 321,145 | 0.00 | 41,043 | 41,043 | 0.00 | 7.82 | 7.82 |
| 2025 | 298,740 | 298,740 | 0.00 | 48,005 | 48,005 | 0.00 | 6.22 | 6.22 |

**Blind inputs**
- **Anchor.** AK OGA *Immobilienmarktbericht Deutschland 2025*, Abb. 4-20 and 4-21: (84.3 + 62.9) bn EUR ÷ (252,900 + 255,600) = 289,479 EUR (2024).
- **Price index.** GENESIS 61262-0001, `PRE026`, base 2025=100, all values flagged `e`.
- **Wage.** GENESIS 81000-0017, `VST038`, `%TOTAL%`. Values for 2023–2025 are flagged `p`.

The raw files downloaded independently are byte-identical (md5) to ours for the AK OGA PDF, both GENESIS data cubes and the Qualitätsbericht.

## Independent check of the index-chained early years

Older AK OGA reports were downloaded independently: IMB 2015 (`raw/AKOGA_imd2015.pdf`, Abb. 3-49, 3-50, 3-68, 3-71) and IMB 2013. They print turnover and counts for the vintage of that time. A plain mean, with no index involved, compares with the chained value as follows:

| year | AK OGA direct mean (old vintage) | chained (ours) | chained vs direct |
|---|---|---|---|
| 2012 | 164,861 | 175,659 | +6.5% |
| 2013 | 172,361 | 181,036 | +5.0% |
| 2007, houses only (2007 data flagged "eingeschränkte Genauigkeit" by AK OGA) | 175,978 | 183,007 | +4.0% |

These results agree with our own README, which uses the 2025-vintage charts: +7.4% in 2012 and +4.6% in 2013.

## Findings

1. **OK: Arithmetic.** Running `build_deu.py` and `wage/build_deu_wage.py` on a copy of our `raw/` reproduces `deu_avg_dwelling_price_2000-2025.csv`, `deu_workings.csv` and both wage CSVs byte-for-byte. Note that the wage script needs `countries/wages/raw/` (OECD) present.

2. **OK: URLs.** All 23 URLs in the two SOURCES.csv files respond with HTTP 200 and serve the claimed type. The GENESIS URLs and the AK OGA PDF (46.68 MB) are identical to the files saved.

3. **CONCERN: Wrong URLs in SOURCES.csv.** In `DEU/SOURCES.csv`, the rows for `..._61262-0001_HPI_annual_information.json`, `..._61262-0001_HPI_annual_structure.json` and `..._61262-0002_HPI_quarterly_structure.json` all give the `/data` URL. The correct URLs are `/information` and `/structure`. A reader who fetches the listed URL gets a different file. This is a provenance slip and changes no number.

4. **OK: The anchor is right, with one edge.** Abb. 4-20 and 4-21 give exactly the figures used. AK OGA's own printed condominium mean (Abb. 4-76, 246,000) confirms the division. The concept "one/two-family houses + condominium flats" is slightly loose: AK OGA's "Eigenheime" also includes terraced and semi-detached houses and "übrige Eigenheime" such as Resthöfe and Wochenendhäuser. The README states this.

5. **CONCERN: The "not assignable" condominium sales may not all be dwellings.** README limit 6 says these sales are kept because "all of these are dwellings". AK OGA's own text (§4.2.3, at the category definitions) does not say that. It says that the unassignable category can include *Teileigentum*, units it says "eigentlich den Wirtschaftsimmobilien zuzuordnen" (that properly belong to commercial property), and that they are kept because they are "vermutlich in erster Linie" (presumably mainly) housing. These 21,800 sales average about EUR 105,500 (2.3 bn ÷ 21,800), against EUR 259,000 for identified flats.
   - Hypothesis, not tested: some of these are garages, parking spaces or commercial units.
   - If the category is dropped, the anchor rises to EUR 297,719 (+2.8%).
   - If "übrige Eigenheime" (11,900 sales, EUR 3.7 bn) are also dropped, the anchor is EUR 297,388 (+2.7%).
   - Every year moves by the same factor. The README sentence should be corrected to quote AK OGA's own caveat, and this sensitivity should be stated.

6. **CONCERN: The pre-2014 index is a weak support, and the README already says so.**
   - Destatis Qualitätsbericht §4.1 and §6.2: comparability over time is "seit dem Jahr 2014 gewährleistet. Zuvor … Aufbauphase". Before 2014 far fewer valuation committees reported (§1).
   - Independent checks against AK OGA plain means show that the chained series runs 4–7% above the direct mean in 2007–2013, in both the 2015 and 2025 report vintages. The direction is consistent, so 2000–2013 German prices, and therefore the ratios, are probably overstated by about that much relative to a plain mean.
   - The README discloses all of this (limits 1–3) and labels the cause as a hypothesis, which is correct. Not one German source gives a national mean for 2000–2008, so 2000 (6.48) and 2007 (5.70) rest on the index alone.
   - **Recommendation:** in public use, footnote 2000, 2007 and 2013 as "index-extrapolated; Destatis does not guarantee comparability before 2014".

7. **CONCERN: Coverage of the anchor is uneven.** The README states the 88% national data-provision rate. It does not state that Baden-Württemberg, an expensive Land, supplied only 22% and Sachsen 48% (IMB 2025 text at Abb. 4-33/4-34). Those gaps are filled by AK OGA statistical estimates. A short note would pre-empt this attack.

8. **OK: The wage concept matches the claim.** `VST038` is gross wages and salaries per employee, domestic concept, EUR per year. It counts persons and includes marginal and part-time workers, as the README documents. Dividing by 12 reproduces the monthly figures Destatis prints. 2023–2025 are provisional (`p`), which the README states.

9. **CONCERN (minor): 2025 mixes sources of different finality.** The 2025 price depends on the index alone, because AK OGA has no 2025 totals yet. The 2025 wage is provisional. Both are disclosed (README price limit 9, wage limit 5).

10. **OK: Annual vs quarterly index.** Our check that the annual HPI equals the mean of the four quarters (max gap 0.05) runs as stated.
