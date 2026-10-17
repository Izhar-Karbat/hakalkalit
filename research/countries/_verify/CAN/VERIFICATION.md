# Canada (CAN): independent verification

Verifier's blind build: `verify_CAN.py` (reads only `raw/` here; sources in `raw/SOURCES.csv`).
Our values: `../ours_CAN.csv`. Our build: `countries/CAN/` (price) and `countries/CAN/wage/` (wage).

## Comparison

| year | ours price | yours price | diff % | ours wage | yours wage | diff % | ours ratio | yours ratio |
|---|---|---|---|---|---|---|---|---|
| 2000 | 165,245 | 165,245.05 | 0.00 | 34,089 | 34,088.60 | 0.00 | 4.85 | 4.848 |
| 2007 | 307,924 | 307,923.89 | 0.00 | 40,943 | 40,943.24 | 0.00 | 7.52 | 7.521 |
| 2013 | 385,336 | 385,336.27 | 0.00 | 47,387 | 47,386.56 | 0.00 | 8.13 | 8.132 |
| 2016 | 493,322 | 493,322.03 | 0.00 | 49,744 | 49,743.72 | 0.00 | 9.92 | 9.917 |
| 2022 | 711,942 | 711,942.13 | 0.00 | 60,592 | 60,592.48 | 0.00 | 11.75 | 11.750 |
| 2025 | 680,368 | 680,368.45 | 0.00 | 67,749 | 67,748.72 | 0.00 | 10.04 | 10.043 |

The blind search arrived at the same three files independently: CREA `Forecast_data_Oct_2026.xlsx`, StatCan
`14100204-eng.zip`, StatCan `14100245-eng.zip`. Their SHA-256 hashes match ours byte for byte
(3ac8feff…, 33a092d5…, 350e2fb1…). All differences are rounding to the dollar.

### Price cross-check against government-published vintages of the same CREA series (CMHC)

| year | CREA file Oct 2026 (used) | CMHC-published figure (vintage) | today vs CMHC |
|---|---|---|---|
| 2000 | 165,245 | 163,992 (Canadian Housing Observer 2010, Table 1) | +0.76% |
| 2007 | 307,924 | 307,094 (CHO 2010) / 307,132 (CHO 2011) / 306,743 (CHO 2014, Table 6) | +0.27% to +0.39% |
| 2013 | 385,336 | 382,576 (CHO 2014, Table 6) | +0.72% |
| 2016 | 493,322 | 490,032 (Housing Market Outlook, Fall 2017) | +0.67% |
| 2022 | 711,942 | 703,959 (HMO Spring 2024) / 704,543 (HMO Feb 2025) | +1.05% to +1.13% |
| 2025 | 680,368 | 680,000, rounded (HMO 2026 web page) | +0.05% |

## Findings

1. **OK: arithmetic.** Price = CREA annual column, rounded. Wage = AWE × 52. Ratio = price ÷ wage. Re-derived
   from identical raw files, so every number in `ours_CAN.csv` is reproduced. Vector v1740722 (2001+) and
   v78952340 (2000) are the right series for the stated concept: Canada, All employees, Including overtime,
   Industrial aggregate excluding unclassified, current dollars.
2. **OK: URLs.** All 10 URLs in both SOURCES.csv files returned HTTP 200 on 2026-10-17, with the claimed
   content type and the same byte size as our raw files. The two "January" CREA release files are dated
   January 15, 2025 and January 15, 2026 in their text, and they print the forecast sentences the README
   quotes ($722,221 at +4.7%; $698,881 at +2.8%).
3. **OK: concept.** The CREA "Residential Average Sale Price" is the mean MLS® residential sale price. StatCan
   14-10-0204-01 is the annual SEPH average weekly earnings, gross payroll, head count of payroll jobs.
   Both match the claimed CONCEPT.
4. **CONCERN: the README understates historical revisions and how far back a government source goes.** The
   price README says older-year revisions are "not quantified" and that "no government table carrying a
   national average price level for 2000–2025 was found". CMHC, a federal Crown corporation, did publish
   this CREA series every year: Canadian Housing Observer appendix tables 2003–2014, then Housing Market
   Outlook. Those contemporaneous figures sit 0.3–1.1% *below* today's file in every test year (table above).
   - A hostile reader can quote "CMHC: $704,543 for 2022" against our $711,942.
   - The effect on the ratio is at most about 1% (2022: 11.63 against 11.75). The direction is the same in
     every year, so trends barely move.
   - Fix: cite the CMHC vintages in the README as a quantified revision band. The data needs no change.
5. **CONCERN: the 2000/2001 wage seam inflates the starting-point ratio gap.** This is already disclosed in
   the wage README: StatCan note 15, +0.22% growth across the seam against about 2.4% on either side. It
   matters for the headline because the 2000 wage is probably about 2% too high, so the 2000 ratio (4.85) is
   about 2% too low and the 2000→2025 rise looks slightly bigger.
   - Hypothesis, not tested: bridging the seam with neighbouring-year growth gives a 2000 wage of about
     33,400 and a ratio of about 4.95.
   - The archived SIC-basis table (14-10-0261-01, 626.45/week) would give 32,575 and a ratio of 5.07.
   - The wage README shows that series as context only. It belongs in any public footnote for 2000, because
     a hostile reader could pick it.
6. **CONCERN: the two series cover different populations.** Already disclosed. MLS® is mostly resale and
   excludes builder-direct new sales. SEPH excludes agriculture, the military and similar groups and runs
   4–8% below OECD D11/SAL. Both are stated in the READMEs; nothing to add.
7. **CONCERN (minor): the 2025 price is the least settled year.** Today's file is +0.08% above what the
   January 2026 release implied. The README already says this.
8. **OK: the `ours_CAN.csv` ratio column** is rounded to 2 decimals and matches to ±0.005.

No ERROR found.
