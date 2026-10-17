# Germany: average gross annual wage per employee, 2000–2025

Output: `deu_avg_annual_wage_2000-2025.csv` (year, EUR, concept). Workings and checks are in `deu_wage_workings.csv`. Rebuild with `python -I build_deu_wage.py`.

## Concept

**Gross wages and salaries per employee, domestic concept, whole economy, annual, EUR.** The source is the Destatis national accounts (VGR des Bundes), series "Bruttolöhne/-gehälter je Arbeitnehmer (im Inland)".

- **Numerator:** gross wages and salaries (ESA 2010 D.11). This is before income tax and before the employee's social contributions. It excludes employer social contributions. It includes special payments (13th salary, Christmas and holiday money, bonuses) and wages in kind.
- **Denominator:** the annual average number of employees (Arbeitnehmer) working in Germany. The count is of persons, not jobs. It covers all employees. There is no full-time-equivalent conversion.
- **Part-time and Minijobs.** The GENESIS definition of "Arbeitnehmer" in `raw/destatis_genesis_81000-0015_information.json` says so explicitly: *"Eingeschlossen sind auch geringfügig Beschäftigte und andere marginal Beschäftigte, wie z.B. Personen in Arbeitsgelegenheiten (Ein-Euro-Jobs)"*. A person whose only job is a Minijob counts as one employee and pulls the average down. A person with a main job plus a Minijob on the side counts once, under the main job. The pay from both jobs is in the numerator, so a side Minijob raises that person's average. The Destatis table page states this rule: wages paid to main and secondary job holders, divided by main job holders only.

**Why this series.** It is the closest match to the Israeli benchmark (CBS average monthly gross wage per employee post: all employees, part-time included, gross, whole economy). The alternative was rejected:

- **Verdiensterhebung / Vierteljährliche Verdiensterhebung** (average gross monthly earnings, `raw/destatis_table_page_verdienste-lange-reihe-deutschland.html`) was rejected for three reasons:
  - It covers full-time employees only.
  - It excludes special payments ("ohne Sonderzahlungen").
  - It has a series break between 2021 and 2022.

  It is kept as a context column only.

## Inputs

| Role | Series | Agency | URL | Raw file |
|---|---|---|---|---|
| **Primary** | GENESIS 81000-0017, content `VST038` "Bruttolöhne/-gehälter je Arbeitnehmer (im Inland)", EUR, `WZ08G2=%TOTAL%`, 1991–2025, table last changed 2026-09-21 | Statistisches Bundesamt (Destatis) | https://genesis.destatis.de/genesis/api/rest/tables/81000-0017/data (+ `/structure`, `/information`) | `raw/destatis_genesis_81000-0017_*.json` |
| Check A | GENESIS 81000-0015: `VST020` gross wages (EUR bn), `ERW061` employees (1000), definitions | Destatis | https://genesis.destatis.de/genesis/api/rest/tables/81000-0015/data | `raw/destatis_genesis_81000-0015_*.json` |
| Check B/B2 | GENESIS 81000-0007: national concept (Inländer), `VST036` monthly per employee, `VST006` total | Destatis | https://genesis.destatis.de/genesis/api/rest/tables/81000-0007/data | `raw/destatis_genesis_81000-0007_*.json` |
| Printed figures | Table pages "Wichtige gesamtwirtschaftliche Größen", "Personenkonzept", "Nationaleinkommen…" (as of 25 Aug 2026) | Destatis | see `SOURCES.csv` | `raw/destatis_table_page_*.html` |
| Quality flags | GENESIS quality-sign legend (`e` = final, `p` = provisional) | Destatis | https://genesis.destatis.de/genesis/api/rest/tables/81000-0017/qualitySigns | `raw/destatis_genesis_qualitySigns.json` |
| OECD comparison | OECD NA Table 1 (D11) and Table 3 (SAL, persons) | OECD | already in `../../wages/raw/` (see `../../wages/SOURCES.csv`) | `oecd_na_table1_income.csv`, `oecd_na_table3_empdc.csv` |

All raw files are the server responses, saved unmodified.

## Method

`build_deu_wage.py` decodes the JSON-stat cube and takes `VST038` for all industries, 2000–2025. Values are rounded to whole euros. No conversion is needed, because the series is already annual EUR per employee. No year is missing, so nothing is interpolated.

## Checks (all asserted or printed by the script)

- **A. Recomputation.** `VST020 × 10⁹ / (ERW061 × 10³)` reproduces `VST038` within 0.2% in every year. In practice the difference is ≤ 0.2 EUR. Example: 2000 gives 916.951 bn / 35,963k = 25,497.1.
- **B. Printed agency figure.** The Destatis page "Wichtige gesamtwirtschaftliche Größen" prints gross wages per employee per month as **3,643 / 3,832 / 4,000 EUR** for 2023/2024/2025. `VST038 / 12` gives 3,643.3 / 3,832.2 / 4,000.4, an exact match. This also shows that the printed headline is the domestic concept. The national-concept series `VST036` would give 3,667 / 3,857 / 4,026.
- **B2.** The printed wage totals (1,845.625 / 1,946.775 / 2,032.072 bn) equal GENESIS 81000-0007 `VST006` exactly.
- **C.** The printed year-on-year change in gross wages per employee (Personenkonzept page) is +6.5 / +5.2 / +4.4%. The values computed from `VST038` match all three.
- **D. OECD.** D11 / SAL (DEU, S1, _T, XDC, persons) gives the following:

| Year | Destatis (EUR) | OECD D11/SAL (EUR) | Ratio national/OECD |
|---|---|---|---|
| 2000 | 25,497 | 25,497.1 | 1.0000 |
| 2007 | 27,876 | 27,875.8 | 1.0000 |
| 2016 | 34,828 | 34,827.7 | 1.0000 |
| 2022 | 41,043 | 41,043.4 | 1.0000 |

  The agreement is within ±0.001%. The OECD figure is Destatis's own transmission, so this confirms the decoding and the concept. **It is not an independent source.**
- **E. Context.** The Verdiensterhebung full-time figure × 12 is 1.2–1.3× higher, with VGR/VE = 0.77–0.83. That gap is expected: VE excludes part-time and Minijob workers but also excludes special payments.

## Known limits (stated before anyone else finds them)

1. **Persons, not posts.** Israel CBS divides by employee *posts* (jobs), so a worker with two jobs counts twice. Destatis divides by *persons* (main job only) while paying in all jobs' wages. For the same economy, the German construction gives a higher average than a per-post one. The size of this effect is not quantified here.
2. **Minijobs are in, which lowers the level.** Every person whose only job is a Minijob counts as a full employee. Their number is not in these raw files and is not quantified here. This matches the "part-time included" benchmark, but it makes Germany's average lower than a full-time-only figure. Anyone quoting a "German average salary" of about €58k is quoting the full-time Verdiensterhebung (Check E), not this series.
3. **Special payments and wages in kind are included.** This should be checked against what the CBS monthly wage × 12 contains. If CBS excludes some bonuses or in-kind benefits, the German figure is slightly high relative to the benchmark.
4. **Domestic concept.** The series covers jobs located in Germany, including cross-border in-commuters. The national concept runs about 0.6% higher (Check B). Use the domestic concept consistently.
5. **2023–2025 are provisional** (GENESIS flag `p`) and will be revised. All years are subject to VGR benchmark revisions. These values are the vintage of 2026-09-21.
6. **2020.** Short-time work (Kurzarbeit) kept headcount up while wages fell. The Kurzarbeitergeld benefit is not a wage. The result is a slight dip (38,136 → 38,054). This is a real feature of the concept, not an error.
7. **The OECD comparison is not independent.** The OECD republishes Destatis, so a ratio of 1.0000 proves correct handling of the data, not correctness of the data.

## CERTAINTY: high

The source is the official Destatis series, downloaded directly. Its definitions, published in GENESIS, explicitly cover all employees including marginal ones. The series reconciles with its own components, with three printed Destatis figures, and with the OECD relay. The residual uncertainty concerns comparability with Israel, not the German numbers: persons vs. posts (limit 1) and bonus coverage (limit 3).
