# France — average gross annual wage per employee, 2000–2025

Output: `fra_avg_annual_wage_2000-2025.csv` (year, avg_annual_gross_wage_local, currency, concept).
Checks: `fra_wage_checks.csv`. Built by `build_fra_wage.py` from the files in `raw/`. URLs are in `SOURCES.csv`.

## Concept
This is the national-accounts **salaire moyen par tête (SMPT)**: gross wages and salaries (D11) divided by the number of
salaried persons, for the whole economy, as an annual average, in current euros.

- **Gross.** D11 "salaires et traitements bruts" includes the employee's own social contributions and CSG/CRDS. It
  excludes employer contributions (D12).
- **Per head, part-time included.** The denominator is *emploi intérieur salarié en nombre de personnes physiques*. A
  part-time employee counts as one person, not as a fraction of a full-time equivalent.
- **Whole economy, domestic concept.** All branches (market, public and household employers). The wages are those paid
  by resident producers, and the employees are the people working in them.

This is the closest INSEE concept to the Israeli CBS benchmark (average monthly gross wage per employee post, part-time
included, whole economy). The one difference is that CBS counts **posts**, while INSEE counts **persons**: a French
person holding two jobs is one head. INSEE's figures are annual, so the Israeli comparator is the CBS monthly figure × 12.

**Geography: France entière (metropolitan France plus the overseas departments, REF_AREA="FE").** The annual national
accounts do not publish this aggregate for metropolitan France alone. Our price series (DVF) covers metropolitan
France only. See Known limits.

## Inputs
| What | Agency / series | Raw file |
|---|---|---|
| D11 salaires et traitements bruts, total des branches, prix courants (M EUR) | INSEE BDM idbank **011785411**, dataflow CNA-2020-CPEB | `raw/insee_cna2020_cpeb_D11_total.xml` |
| Emploi intérieur salarié, total des branches, personnes physiques (thousands) | INSEE BDM idbank **011793486**, dataflow CNA-2020-EMPLOI | `raw/insee_cna2020_emploi_salarie_pp.xml` |
| Same, in full-time equivalents (thousands). Used only for the check | INSEE BDM idbank **011793487** | `raw/insee_cna2020_emploi_salarie_etp.xml` |
| Published table 6.205 (D11 by branch, bn EUR) | INSEE, Comptes nationaux annuels 2025 (base 2020) | `raw/T_6205_fr.xlsx` |
| Published table 6.210 (salaried employment, persons) | same | `raw/T_6210_fr.xlsx` |
| Published table 6.211 (salaried employment, FTE) | same | `raw/T_6211_fr.xlsx` |
| Insee Première n° 2079, "Les salaires dans le secteur privé en 2024" | INSEE (Oct 2025) | `raw/ip2079.pdf` |
| OECD D11 and SAL (persons), FRA | OECD, shared files | `../../wages/raw/oecd_na_table1_income.csv`, `oecd_na_table3_empdc.csv` |

All of these are INSEE annual national accounts, base 2020, in the vintage of the May 2026 release. The BDM
series were last updated on 2026-05-29.

## Method
wage[y] = D11[y] (EUR) / salaried persons[y]. There is no interpolation, smoothing or FTE conversion. All 26 years are
present. Status flags from BDM: 2000–2023 are definitive (A), **2024 is semi-definitive (SD)** and **2025 is provisional (P)**,
so both will be revised.

Selected values (EUR/year): 2000 **23,204** · 2007 **28,746** · 2016 **33,527** · 2022 **38,071** · 2025 **41,621**.

## Checks
1. **Against INSEE's own published tables.** For every year 2000–2025, the D11 total in table 6.205 (row `_T`) equals
   the BDM series exactly. For example, 2025 = 1 129,309 bn EUR and 2000 = 542,929 bn EUR. The persons total in table 6.210
   matches the BDM to within 0.2 thousand, because the table rounds older years to whole thousands. For example, 2025 =
   27 133,2 thousand in both, and 2016 is 24 920 in the table against 24 920,2 in the BDM.
2. **Against a printed salary figure, a different concept and labelled as such.** Insee Première 2079 (table 1, "Ensemble") prints a
   private-sector mean **gross wage in FTE** of 3 602 EUR/month for 2024, which is 43,224 EUR/year. The national-accounts
   whole-economy wage **per FTE** for 2024 is 43,689 EUR/year (+1.1%). The headline **per-head** figure is 40,897 EUR, 5.4% below
   the FTE figure. The gap is what we expect from counting part-timers as whole heads. The two figures differ in field (private sector
   vs whole economy) and source (DSN vs national accounts), so this is an order-of-magnitude check, not an identity.
3. **Against OECD** (D11, S1, _T, XDC, V ÷ SAL, PS). The ratio INSEE/OECD is **1.0000** for 2000, 2007, 2016 and 2022, and
   for every other year. This only confirms that the arithmetic and units are right. **It is not an independent check**:
   OECD's French national accounts are INSEE's own transmission, and the two differ only by OECD's rounding of employment to
   whole thousands.

FTE alternative, a check only: `wage_per_fte_bdm` in `fra_wage_checks.csv`. That column is **full-time equivalent** and must not be
used as the benchmark match.

## Known limits (stated before anyone else finds them)
- **Geography mismatch.** The wage covers France entière including the DOM (Guadeloupe, Martinique, Guyane, La Réunion,
  Mayotte). Our price series is metropolitan only. The DOM are a few percent of employees, and their mean wage differs
  from the metropolitan mean. INSEE national accounts do not publish a metropolitan-only aggregate, so the size
  of this bias is **not measured here**.
- **Persons, not posts.** CBS divides by employee posts. INSEE divides by persons, so a multiple job-holder's wages are
  summed into one head. This makes the French figure somewhat higher than a per-post figure would be. The size of the
  difference is not measured.
- **National-accounts wages are not payroll records.** D11 includes imputed and estimated items, such as wages in kind and
  INSEE's adjustments for undeclared work. The CBS figure comes from employer reports to the tax and social-security authorities. Both are gross.
- **Gross includes CSG/CRDS.** French gross pay carries much heavier employee deductions than Israeli gross pay. A
  gross-to-gross comparison is the right like-for-like, but it overstates French take-home pay relative to Israel.
- **Revisions.** 2024 (semi-definitive) and 2025 (provisional) will be revised. All years are revised at each base change. This is
  base 2020, and earlier publications in base 2014 give different levels.
- **2020 dip** (34,258, down from 35,562). This is the COVID year: short-time work allowances (activité partielle) are not D11
  wages, while the furloughed staff stay in the headcount. It is real in the accounts, but it is not a fall in pay rates.
- The persons series in published table 6.210 is rounded to whole thousands for older years. We use the unrounded BDM
  series, and the difference is at most 0.2 thousand persons, or under 0.001%.

## CERTAINTY: high
The series is INSEE's own published aggregates, one division with no adjustments. The inputs reproduce the
agency's printed tables exactly, and the concept (gross, per head, part-time included, whole economy) matches the CBS
benchmark on every axis except posts vs persons and the DOM inclusion. Those two known biases are small, but they are not
quantified, and they are the reason this is not "very high". The 2024 and 2025 values are less certain than the rest because
they are not final.
