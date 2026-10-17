# Spain: price of an average dwelling in monthly gross wages

The same measure as the Israel table: average dwelling price ÷ average gross monthly wage.
Rebuild: `python3 build_spain_ratio.py` → `spain_price_vs_wage_2004-2025.csv`.
The script reads only `raw/` and checks every dwelling size and every registered sale price against the sentence in the yearbook that prints it.

## Result

| Year | Monthly wages per dwelling | Salary years |
|---|---|---|
| 2007 (peak) | **120.5** | 10.0 |
| 2015 | **76.4** | 6.4 |
| 2025 | **90.1** | 7.5 |

Cross-checks for 2025:
- Actual registered sale prices (Registradores): 96.7.
- INE transaction index: 112.3.

Every measure shows the same three things: 2025 is above 2015, 2025 is below 2007, and the ratio rose sharply in 2025.

## Inputs

| Input | Series | Source | File |
|---|---|---|---|
| Price per m² | `DHIVTNOAPLPMMUVT_RLI.T`, average appraised price of free-market dwellings, national, quarterly | Ministerio de Vivienda y Agenda Urbana, as republished by Banco de España, Síntesis de indicadores, table si_1_5: https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/si_1_5.csv | `raw/bde_si_1_5_housing_indicators.csv` |
| Dwelling size | National average m² of dwellings in registered sales, one figure per year | Colegio de Registradores, Estadística Registral Inmobiliaria, yearbooks 2004–2025: https://www.registradores.org/actualidad/portal-estadistico-registral/estadisticas-de-propiedad | `raw/registradores_anuarios/` |
| Wage | `ETCL13724`, total gross wage per worker per month, national, not seasonally adjusted, base 2012, quarterly | INE, Encuesta Trimestral de Coste Laboral, table 11221: https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/11221 | `raw/ine_etcl_table11221_wages.json` |
| Check: registered sale prices | €/m² of actual sales, 2021–2025 | Registradores yearbooks, same as above | same |
| Check: transaction index | `IPV1276`, annual average, national, general | INE Índice de Precios de Vivienda, table 80271: https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/80271 | `raw/ine_ipv_table80271_price_index.json` |

**Method.**
- Annual figures are the mean of four quarters.
- Size uses the same source as the Bank of Spain's own price-to-income ratio. See `raw/bde_si_1_5_methodology_note.pdf`, section "Precio de la vivienda/Renta Bruta por hogar".
- The ETCL wage includes part-time workers and extra payments ("pagas extra"). This matches Israel's CBS wage per employee post.

## Known limits (stated before anyone else finds them)

1. **Appraisals lag the market.**
   - Since 2016 the appraisal series has run below the INE transaction index, by up to 20% in 2025.
   - Because of this the main figure is the conservative one.
   - Actual registered sale prices for 2021–2025 sit between the two series: 7–10% above appraisals.
2. **The INE check column is a construction.** It takes the 2015 appraisal level and moves it by the INE index. The INE index is quality-adjusted, while the main figure is a plain average.
3. **The series starts in 2004.** Price and wage go back to 2000, but the Registradores yearbooks, the only source of the national dwelling size, start with 2004. 2000–2003 would need a size from another source, so they are left out.
4. **Not the Bank of Spain's ratio.** The Bank publishes 7.98 years (Q4 2025) against median household gross income. That uses a different denominator, so it is not comparable to the salary-years figure here.
5. **Price and size cover slightly different dwellings.** The appraisal price is for free-market dwellings only; the yearbook size is the average of all registered sales, subsidised (VPO) dwellings included. The effect is small.
