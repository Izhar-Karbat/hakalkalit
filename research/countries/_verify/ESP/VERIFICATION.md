# Spain (ESP) — independent verification

Blind rebuild: `verify_ESP.py` over `raw/` (sources and URLs in `raw/SOURCES.csv`, fetched 2026-10-17).
Price = annual mean of 4 quarters of BdE si_1_5 `DHIVTNOAPLPMMUVT_RLI.T` (MIVAU appraised €/m², free-market dwellings) × Registradores ERI "General" average m² stated in each yearbook.
Wage = annual mean of 4 quarters of INE 11221 `ETCL13724` × 12.

| year | ours price | yours price | diff % | ours wage | yours wage | diff % | ours ratio | yours ratio |
|---|---|---|---|---|---|---|---|---|
| 2000 | — | — (no ERI m²; see C2) | — | — | 16,022 | — | — | — |
| 2007 | 206,375 | 206,375 | 0.00 | 20,558 | 20,558 | 0.00 | 10.04 | 10.04 |
| 2013 | 146,499 | 146,499 | 0.00 | 22,605 | 22,605 | 0.00 | 6.48 | 6.48 |
| 2016 | 146,852 | 146,852 | 0.00 | 22,770 | 22,770 | 0.00 | 6.45 | 6.45 |
| 2022 | 174,968 | 174,968 | 0.00 | 25,382 | 25,382 | 0.00 | 6.89 | 6.89 |
| 2025 | 214,034 | 214,034 | 0.00 | 28,519 | 28,519 | 0.00 | 7.51 | 7.51 |

Inputs found blind: €/m² means 2007 2056.35, 2013 1495.35, 2016 1502.62, 2022 1740.97, 2025 2127.57; m² 100.36 (ERI 2007), 97.97 (ERI 2013), 97.73 (ERI 2016), 100.5 (ERI 2022), 100.6 (ERI 2025); monthly wage means 1713.16, 1883.76, 1897.50, 2115.14, 2376.55.

## Findings

**No ERROR found.** Every checked number is reproduced exactly.

- **OK — sources respond and match.** Every non-MISSING URL in our SOURCES.csv returns HTTP 200 with the right content type and the same byte size as our raw file. Our BdE CSV is byte-identical to a fresh download. The ERI 2007/2013/2016/2022/2025 PDFs are byte-identical to fresh downloads. The ETCL13724 quarterly values are identical, 2000Q1–2026Q2.
- **OK — arithmetic.** I ran `build_spain_ratio.py` on a scratch copy of our raw/. It reproduces `spain_price_vs_wage_2004-2025.csv` byte for byte, and its asserts (each m² string present in the yearbook text) pass.
- **OK — concept.** BdE labels the series "Precio medio m2 de viviendas libres tasadas. Total nacional", €/m², source Ministerio de Vivienda y Agenda Urbana. INE labels ETCL13724 "Datos no ajustados… Coste salarial total por trabajador. Euros". The ERI methodology uses constructed m², converting useful area to constructed when only that is given, so it is on the same m² basis as the BdE "m2 construido" price. The BdE methodology note confirms that the BdE's own price-to-income ratio uses the Registradores size, so the README's claim holds.
- **CONCERN C1 — README limit 3 is factually false.** The README says "2005 is missing. No yearbook found states the 2005 dwelling size." But our own `raw/registradores_anuarios/ERI_Anuario_2005.pdf` says: "La superficie media de las transacciones de vivienda se ha situado en 2005 en los 97,36 m²". `ERI_Anuario_2006.pdf` repeats the 97,36 figure. 2005 can be computed, and a hostile reader who opens our own raw file will catch this.
- **CONCERN C2 — 2000 (and 2001–2003) are omitted without saying why.** Both the €/m² price and the ETCL wage cover 2000. Only the ERI size starts in 2004. For 2000 the price per m² is 880.23 and the annual wage is 16,022. With the 2004 ERI size (97.30 m²) the 2000 ratio is about **5.35**. With the BdE's pre-2004 anchor (93.75 m², the old Ministerio de Fomento figure cited in the BdE note) it is about **5.15**. The README should either state this method or explain the exclusion.
- **CONCERN C3 — SOURCES.csv hygiene.** Two raw files have URL `MISSING`: `bde_si_1_5_methodology_note.pdf` (which the README cites as evidence) and `oecd_house_prices_ESP.csv`. The `downloaded` column says "see README", but the README holds no dates. The INE URLs have no `tip`/`nult` parameters. They do serve the same data, so this is a reproducibility nit only.
- **CONCERN C4 — size population mismatch.** The price is free-market (libre) dwellings only. The m² is ERI "General", which includes new protected (VPO) dwellings averaging about 85 m². The effect is small, because VPO is a small share and the General and Usada sizes differ by about 1 m², but it is not stated.
- **CONCERN C5 — wage scope (hypothesis, not checked against INE methodology in this run).** As far as I know, the ETCL does not cover agriculture or household employers. The README states the part-time inclusion but not the sector scope.
- **OK — appraisal lag is disclosed.** README limit 1 covers it. As a check, the registered €/m² of 2,284 for 2025 does appear in ERI 2025, and the ERI average price per dwelling for 2025 is 214,581 €, within 0.3% of our 214,034. This supports the 2025 level.
