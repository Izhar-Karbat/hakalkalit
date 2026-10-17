# Israel (ISR) — independent verification

Verified 2026-10-17. Step 1 was done blind: the CBS API and the CBS Table 2.2 PDFs were fetched into `raw/` (URLs in `raw/SOURCES.csv`) and computed with `verify_ISR.py`. No project file was opened before that step.

## Numbers

| year | ours price | yours price | diff % | ours wage | yours wage | diff % | ours ratio | yours ratio |
|---|---|---|---|---|---|---|---|---|
| 2000 | 752,900 | 752,900 | 0.0 | 81,468 | 81,468 | 0.0 | 9.24 | 9.24 |
| 2007 | 709,900 | 709,900 | 0.0 | 91,536 | 91,536 | 0.0 | 7.76 | 7.76 |
| 2013 | 1,270,600 | 1,270,600 | 0.0 | 108,012 | 108,012 | 0.0 | 11.76 | 11.76 |
| 2016 | 1,537,200 | 1,537,200 | 0.0 | 114,708 | 114,708 | 0.0 | 13.40 | 13.40 |
| 2022 | 2,115,000 | 2,115,000 | 0.0 | 141,192 | 141,192 | 0.0 | 14.98 | 14.98 |
| 2025 | 2,343,200 | 2,343,200 | 0.0 | 163,104 | 163,104 | 0.0 | 14.37 | 14.37 |

The anchor was rebuilt independently. It uses the latest CBS Table 2.2 vintage (Price Statistics Monthly 7/2026), giving Q2:24 2,330.0, Q3:24 2,270.4, Q4:24 2,350.9 and Q1:25 2,350.9 (NIS thousand). Their mean is 2,325.55k. The mean of index 40010 over Apr 2024 to Mar 2025 is 597.425. That gives NIS 3,892.62 per point, the same as ours.

## Findings

**OK — every URL responds and serves what it claims.** The four CBS API URLs in `rebuild_from_cbs.py` were re-fetched live today. Their data payloads are identical to `raw/*.json`, ignoring the `paging` and `update` fields. Each response has one page (`last_page = 1`), so nothing is truncated. The three cited releases (257/2025, 051/2025, 151/2025) download as PDFs that are byte-identical (same md5) to the local `cbs_release_*.pdf` copies. Each prints the quoted anchor figure: 2,330.0 and 2,350.9 in 257; 2,270.4 in 051; 2,350.9 in 151. The four revised values also match CBS Table 2.2 in the 2025–2026 issues.

**OK — our arithmetic reproduces our numbers.** `python3 rebuild_from_cbs.py --offline` reports 0 mismatches against the CSV and the xlsx for every year from 1994 to 2025.

**OK — the price index is what we say it is.** Series 40010 uses one base (1993 average = 100) for 1994–2025 and has all 12 months in every year, so no chaining is needed.

**OK — the quality-adjustment issue is disclosed.** Index 40010 is quality-adjusted (hedonic), but the shekel anchor is a raw mean of 1–6-room free-market deals. Back years are therefore "the 2024/25 average dwelling at that year's prices", not the average deal actually recorded in, say, 2000. `housing_sources_he.html` (note "מדד מול ממוצע") states this. `statement_he.html` does not, so a reader who sees only the statement page will not see this caveat.

**CONCERN — 2024 is about 2% below CBS's own published annual average.** CBS Table 2.2 publishes 2024 = NIS 2,340.3k. Ours is NIS 2,292.4k (−2.0%), which makes the ratio 14.5 where CBS's figure would give 14.8. For 2025 CBS publishes 2,330.8k and ours is 2,343.2k (+0.5%). The gap comes from the method (index scaling versus a raw annual mean), and it works against our case in 2024 rather than for it. A journalist can still put "CBS says 2,340k" next to our 2,292k, and no page addresses this. We should add one sentence.

**CONCERN — the wage is per employee post, not per person.** The wage series includes part-time posts and foreign workers. This pulls the average wage down and the ratio up compared with a per-employee wage. The statement page names the series (משרת שכיר, עובדים זרים), but it does not say which way the bias goes. It is the standard "average wage" in Israeli public debate, so this is defensible.

**CONCERN — the wage series are spliced at small breaks.** The spliced series have overlap years. In 2004, the mean of 45002 is 7,000.1 and 45637 is 7,050.4 (+0.7%). In 2011, 45637 is 8,563 and 615908 is 8,588 (+0.3%). These breaks are under 1%, so the ratio barely moves (about 0.05–0.1 years). They are undisclosed.

**CONCERN — the 2025 figures are still subject to revision.** Series 615908 was last updated 2026-09-24, and CBS revises the latest annual wage. The dwelling-index months are also two-month transaction windows that CBS revises. The 2025 ratio could still move by about ±0.1.

**CONCERN (minor) — the anchor excludes subsidised deals.** Since Q4 2022 the anchor average excludes government-subsidised (מחיר למשתכן) transactions, and the index window is not perfectly matched to the calendar quarters. Neither point is material at the published precision.

No ERRORs found.

## Verdict

VERIFIED WITH CONCERNS.
