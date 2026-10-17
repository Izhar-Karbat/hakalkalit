# France: average price of a dwelling, 2000–2025 (EUR)

The price side only. Wages are handled elsewhere.
Rebuild: `python3 -I build_fra.py` (about 2 minutes). It writes `fra_avg_dwelling_price_2000-2025.csv`, and also `fra_dvf_direct_means_2021-2025.csv`, which holds the check column. The script reads only `raw/`.

**CERTAINTY: medium-high.**
- High for the path from year to year. The index is INSEE's official transaction index, and our download reproduces the year-on-year changes printed in INSEE's own release (see Check below).
- High for the 2021–2025 level. It is computed from every recorded sale in the DGFiP register.
- Medium for 2000–2020. Those years are the 2024 level moved back in time by a constant-quality index, not a measured average for each year. No official open source gives a national average dwelling price for France before 2014. For the 2021–2025 window the method lands within 2% of the measured averages.

## Result

| Year | Average dwelling price (EUR) | How it was obtained |
|---|---|---|
| 2000 | 93,441 | index path |
| 2007 | 189,664 | index path |
| 2016 | 190,513 | index path |
| 2024 | **238,365** | anchor: mean of 717,983 actual sales (DVF) |
| 2025 | 239,968 | index path (the direct DVF mean is 244,506) |

Every year from 2000 to 2025 is filled. No year is blank and none is interpolated.

## Inputs

| Input | Series | Publisher | URL | Raw file |
|---|---|---|---|---|
| Path (main) | idbank `010001868`: Indice des prix des logements (neufs et anciens), raw series, base 2015 = 100, quarterly, 2000-Q1 to 2026-Q2, France métropolitaine | INSEE, with SDES and Notaires de France | https://www.bdm.insee.fr/series/sdmx/data/SERIES_BDM/010001868+010567058+010001869 | `raw/insee_bdm_series_010001868_010567058_010001869.xml` |
| Check only | `010001869` (new dwellings only), `010567058` (existing dwellings only, Notaires-Insee), both raw | INSEE | same request | same file |
| Full dataflow (provenance) | Dataflow `IPLA-IPLNA-2015`, all series | INSEE | https://www.bdm.insee.fr/series/sdmx/data/IPLA-IPLNA-2015 | `raw/insee_bdm_IPLA-IPLNA-2015_dataflow.xml` |
| Level (anchor) | Demandes de valeurs foncières (DVF): every registered sale, 2021–2025, as geocoded by Etalab | DGFiP, republished by Etalab on data.gouv.fr | https://files.data.gouv.fr/geo-dvf/latest/csv/{2021..2025}/full.csv.gz (server timestamp 2026-05-18) | `raw/dvf/geo_dvf_full_{year}.csv.gz` (565 MB in total) |
| Check (published) | Informations Rapides n° 224, 18 Sept 2026 | INSEE | https://www.insee.fr/fr/statistiques/fichier/version-html/9050027/IR224_IPLNA-2T26.pdf | `raw/insee_IR224_IPLNA_2T2026_release.pdf` |
| Definition of the index | Indicator page p1644 | INSEE | https://www.insee.fr/fr/metadonnees/source/indicateur/p1644/presentation | `raw/insee_IPL_methodology_p1644.html` |

All files were downloaded on 2026-10-17 and saved unmodified.

## Method

1. **Index, annual.** The index value for each year is the mean of its four quarters of the raw (not seasonally adjusted) series. A year is used only if all four quarters exist.
2. **Level in the anchor year (2024).** Mean sale price of single-dwelling sales in DVF. A sale counts when all of these hold:
   - Its type is a sale (`Vente`) or an off-plan sale of new-build (`Vente en l'état futur d'achèvement`, VEFA). Exchanges, auctions, expropriations and building-land sales are excluded.
   - It is in metropolitan France. Departments 97x are dropped to match the index, which also excludes the overseas departments.
   - It contains exactly one dwelling (Maison or Appartement), plus any number of outbuildings (`Dépendance`). Sales that include a commercial or industrial unit are dropped, and so are bundles of several dwellings.
     - DVF writes one row per land-use line, so the same dwelling can appear on several rows. Dwellings are therefore counted after de-duplicating on (parcel, type, built surface, rooms, first lot number). This step matters: counting rows instead drops houses that appear on several rows (they average about €311k) and gives a 2024 mean of €231,601, 2.8% lower. In 2,175 cases the repeated rows are fully identical and could be separate identical dwellings; that is at most 0.3% of the sample.
   - It has a single price (`valeur_fonciere`) between €10,000 and €10,000,000. This filter removes symbolic €0.15 transfers and a €58M outlier. Without it the 2024 mean is €238,440 rather than €238,365 (+0.03%).
3. **Arithmetic.**
   - The 2024 index mean is 126.40 (quarters 126.0, 125.7, 127.6, 126.3).
   - Factor = 238,365 / 126.40 = 1,885.8 EUR per index point.
   - Value for year y = 1,885.8 × index_y. For example, 2000 = 1,885.8 × 49.55 = 93,441.
4. **Why 2024.** 2025 is DVF's first full-year release (May 2026), so it may still be revised. 2024 has been through more releases. Anchoring on 2025 instead would raise every year by 1.9%.

## Check

**Index against INSEE's printed release.** Informations Rapides n° 224 prints these year-on-year changes for 2026-Q2 on raw data. The script recomputes them from the downloaded series.

| Series | Printed | From our file |
|---|---|---|
| New + existing (`010001868`) | −0.8% | −0.79% |
| New (`010001869`) | 0.0% | 0.00% |
| Existing (`010567058`) | −0.8% | −0.79% |

**Index path against actual DVF means** (`fra_dvf_direct_means_2021-2025.csv`):

| Year | Sales counted | DVF mean | DVF median | Index path | DVF vs path |
|---|---|---|---|---|---|
| 2021 | 1,061,491 | 238,412 | 180,150 | 234,027 | +1.9% |
| 2022 | 1,015,918 | 252,824 | 191,950 | 248,548 | +1.7% |
| 2023 | 795,745 | 246,582 | 187,000 | 247,464 | −0.4% |
| 2024 | 717,983 | 238,365 | 181,000 | 238,365 | anchor |
| 2025 | 805,119 | 244,506 | 187,625 | 239,968 | +1.9% |

## Known limits (stated before anyone else finds them)

1. **2000–2020 are not measured averages.** They are the 2024 average moved back by a constant-quality (hedonic) index.
   - The figure for 2000 means: the 2024 mix of dwellings, priced at 2000 prices. It is not the mean of the dwellings actually sold in 2000.
   - If dwellings sold today are larger or better than those sold in 2000, the true mean in 2000 was lower than shown. In that case the 2000→2025 rise is understated, which is the conservative direction for a "prices rose" claim.
2. **Mean, not median.** The mean is about 32% above the median (2024: €238k against €181k). This choice matches the Israeli definition (average).
3. **Alsace-Moselle is missing from the level.** Departments 57, 67 and 68 keep their own land register and are not in DVF, which leaves out about 4% of the population. The index does cover them. Mayotte is excluded from both.
4. **New-build is under-weighted in the anchor.**
   - VEFA single-dwelling sales are only 1.5% of the 2024 sales counted, against an 8.1% weight for new dwellings in the 2026 index.
   - Off-plan sales are often recorded as multi-lot or delayed mutations, and VEFA counts fall from 32,945 (2021) to 5,291 (2025), which looks like registration lag.
   - New dwellings cost more per unit, so the level is probably a little low.
5. **Price concepts differ slightly between the two sources.**
   - The index uses the seller's net price, excluding transfer taxes, notary fees and agency commission. For new-build it uses the reservation price including VAT.
   - DVF `valeur_fonciere` is the price declared in the deed. It includes land and outbuildings and excludes notary fees. **I have not verified from a DGFiP document** whether it includes an agency fee paid by the buyer.
6. **Index scope.**
   - The new-dwelling index covers only ECLN-surveyed developments: permits for 5 or more dwellings sold to private buyers. Individually built houses are not covered.
   - The existing-dwelling index comes from notarial databases.
7. **Single-dwelling filter.** Mutations bundling 2+ dwellings, or a dwelling together with a shop, are dropped (about 57,000 in 2024). These are mostly investor or block sales. The de-duplication key is my own construction. Etalab's geo-DVF has no dwelling identifier.
8. **DVF is republished by Etalab.** The geocoded version is Etalab's reformatting of the DGFiP file, not DGFiP's own raw text file. It is official open data, but one step removed from the source.
9. **2025 DVF is a first release**, and the 2026 index quarters are provisional (2026 is not used in the series).
