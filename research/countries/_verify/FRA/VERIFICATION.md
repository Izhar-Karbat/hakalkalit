# France (FRA): independent verification

Verifier: blind rebuild on 2026-10-17 (`verify_FRA.py`, raw files in `raw/`, URLs in `raw/SOURCES.csv`), then a comparison with `countries/FRA/`.

**Verdict: VERIFIED WITH CONCERNS.** The wage matches to the euro. The price path matches exactly. The 2024 DVF level depends on how a "single-dwelling sale" is counted in geo-DVF: my first blind filter came out 2.8% lower, and the choice between the two filters is not documented in our README.

## Table

"Yours" is my blind first pass: Vente only, exactly one Maison/Appartement **row** per mutation, metropolitan France, €10k–€10M. That gives a 2024 level of €231,601 (n = 649,829).

| year | ours price | yours price | diff % | ours wage | yours wage | diff % | ours ratio | yours ratio |
|---|---|---|---|---|---|---|---|---|
| 2000 | 93,441 | 90,790 | -2.84 | 23,204 | 23,204 | +0.00 | 4.03 | 3.91 |
| 2007 | 189,664 | 184,282 | -2.84 | 28,746 | 28,746 | +0.00 | 6.60 | 6.41 |
| 2013 | 194,048 | 188,542 | -2.84 | 32,477 | 32,477 | +0.00 | 5.97 | 5.80 |
| 2016 | 190,513 | 185,107 | -2.84 | 33,527 | 33,527 | +0.00 | 5.68 | 5.52 |
| 2022 | 248,548 | 241,496 | -2.84 | 38,071 | 38,071 | +0.00 | 6.53 | 6.34 |
| 2025 | 239,968 | 233,159 | -2.84 | 41,621 | 41,621 | +0.00 | 5.77 | 5.60 |

The price difference is a constant -2.84% because it comes entirely from the 2024 anchor. The index path is identical: the 2024 annual mean of 010001868 is 126.400 in both builds, and every other year's index mean matches.

Here is how the 2024 DVF mean moves with the filter (same raw file; md5 `d8a79478…` is identical to ours):

| Filter (metro, €10k–€10M) | n | mean | median |
|---|---|---|---|
| A: Vente, 1 dwelling row | 649,829 | 231,601 | 175,200 |
| B: Vente, 1 distinct dwelling after de-duplication | 720,870 | 239,812 | 180,000 |
| C: A, and no commercial/industrial local | 637,715 | 229,005 | 175,000 |
| D: A, plus VEFA | 660,863 | 233,119 | 178,000 |
| E: A, DOM included | 657,702 | 231,451 | 175,000 |
| **Ours re-run in my script** (Vente+VEFA, 1 de-duplicated dwelling, only Dépendance allowed besides it, a single valeur_fonciere) | **717,983** | **238,365** | **181,000** |

## Findings

1. **OK: our arithmetic reproduces.** I re-implemented our filter independently (`diag_dedup.py`) on the same file and got n = 717,983, mean €238,365 and median €181,000, which match our README and CSV exactly. The level × index arithmetic also checks: 238,365 × 49.55 / 126.40 = 93,441.
2. **OK: the wage is fully verified.** I pulled BDM idbanks 011785411 (D11, total economy, current EUR, millions) and 011793486 (salaried domestic employment, persons, thousands) independently, from different URLs than ours (the SERIES_BDM endpoint instead of the CNA-2020 dataflow keys). They give identical values for every year. Our checks file also matches the published tables 6.205 and 6.210 and OECD.
3. **OK: the index is right.** The idbank 010001868 title is "Indice des prix des logements (neufs et anciens) – Brut – Base 100 en moyenne annuelle 2015", REF_AREA = FM (metropolitan France). All four 2025 quarters are definitive (A).
4. **CONCERN: the de-duplication step adds about 3% to the level, and the README does not say so.** geo-DVF writes one row per (local × land-use line), so a house on a plot with two land-use lines shows up twice. 69,250 of the 717,983 sales we keep are dwellings that appear on several rows, and their mean is €311,509, against €230,557 for single-row dwellings. Of those, 67,075 repeat because the land-use (nature_culture) differs, so the de-duplication is correct: I checked by hand and the duplicated rows have the same parcel, surface and price, with only the land-use line different. A naive "one dwelling row" filter would therefore under-count expensive houses with land, and our level is the better one. Two points are still open to attack:
   - (a) The README calls the key "my own construction" but does not give its +3% effect.
   - (b) 2,175 multi-row cases have identical rows that do *not* differ in land-use, for example mutation 2024-62, the same 30 m² apartment ×3. These could in principle be distinct identical dwellings merged into one. That is at most 0.3% of the sample, so the effect is negligible, but it is unverified.

   Suggestion: add the A-vs-ours sensitivity line (€231.6k vs €238.4k) to the README's known limits.
5. **CONCERN: no independent published national mean exists for comparison.** I searched for an official or semi-official 2024 mean price per dwelling (INSEE, SDES, Notaires). Notaires/INSEE publish indices and median €/m², not a national mean per dwelling, so the level can only be checked against DVF itself. The best cross-check available is the README's own DVF-direct table for 2021–2025, where the index path is within ±2%. A hostile reader can say "the €238k is your own computation", and that is true. It is reproducible, but no agency publishes it.
6. **CONCERN (already stated in the README): concept mismatches that move the ratio.**
   - Mean vs median: the mean is 32% above the median.
   - Before 2021 the price is a constant-quality path, not a measured mean, so the 2000 figure is the 2024 dwelling mix at 2000 prices.
   - Price scope (metro excl. Alsace-Moselle) vs wage scope (France entière incl. DOM).
   - Wage per head with part-timers counted as whole heads, about 5.4% below the FTE figure, which pushes the ratio up.
   - 2024 wage is SD and 2025 is P.

   All of these are disclosed in FRA/README.md and FRA/wage/README.md. None is an error.
7. **OK: every URL in both SOURCES.csv files responds** with HTTP 200 and the right content type, and the byte sizes equal our raw files. That covers the INSEE SDMX price series (32,127 B), the IPLA-IPLNA-2015 dataflow (1,479,318 B), the p1644 page (59,397 B), the IR224 PDF (1,433,858 B), the three CNA-2020 SDMX keys, T_6205/6210/6211 and ip2079.pdf, and geo-DVF 2021–2025 (all 200). Minor point: the price SOURCES.csv uses a brace-expansion template URL (`{2021..2025}`) rather than five literal URLs.
8. **CONCERN (minor): the README's price table lists only 2000, 2007, 2016, 2024 and 2025.** The published years 2013 and 2022 are only in the CSV. This is cosmetic.

## Process note

While checking reproducibility I ran `countries/FRA/wage/build_fra_wage.py`, which rewrote its own output CSVs in FRA/wage/. The outputs I can see are unchanged (2023–2025 are identical to ours_FRA.csv, and the script reads only raw/). This was outside the `_verify/FRA/` write scope and is disclosed here.

## Files

- `verify_FRA.py`: the blind build (filters A–E, the INSEE series, the ratio)
- `diag_dedup.py`: reproduction of our filter and the de-duplication diagnostics
- `verify_FRA_results.csv`, `raw/` (the three INSEE SDMX files and geo-DVF 2024), `raw/SOURCES.csv`
