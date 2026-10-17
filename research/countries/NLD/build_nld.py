"""Netherlands: average sale price of an existing owner-occupied dwelling, 2000-2025, EUR.

Reads only raw/. Main value = CBS's own annual figure in table 85773NED
(GemiddeldeVerkoopprijs_7, period 'YYYYJJ00'). The script checks it three ways:
  1. equals total value / number of sales in the same table (transaction-weighted mean);
  2. equals the Netherlands row of the separate annual table 83625NED;
  3. 2025 rounds to the 480 thousand euro printed in the CBS news release.
It also reports the plain mean of the 12 monthly averages, for comparison only.
"""
import csv, json, re, html
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE / "nld_avg_dwelling_price_2000-2025.csv"

monthly_tbl = json.load(open(RAW / "cbs_85773NED_existing_dwellings_price_index_avg_price_monthly_annual_typeddataset.json"))["value"]
regional = json.load(open(RAW / "cbs_83625NED_avg_sale_price_existing_dwellings_netherlands_annual.json"))["value"]

annual, months, count, total = {}, {}, {}, {}
for r in monthly_tbl:
    p = r["Perioden"]
    y = int(p[:4])
    if p.endswith("JJ00"):
        annual[y] = r["GemiddeldeVerkoopprijs_7"]
        count[y] = r["VerkochteWoningen_4"]
        total[y] = r["TotaleWaardeVerkoopprijzen_8"]
    elif re.fullmatch(r"\d{4}MM\d{2}", p) and r["GemiddeldeVerkoopprijs_7"] is not None:
        months.setdefault(y, []).append(r["GemiddeldeVerkoopprijs_7"])

reg = {int(r["Perioden"][:4]): r["GemiddeldeVerkoopprijs_1"] for r in regional
       if r["RegioS"].strip() == "NL01" and r["Perioden"].endswith("JJ00")}

rows = []
for y in range(2000, 2026):
    v = annual.get(y)
    if v is None:
        rows.append((y, "", "EUR", "not published")); continue
    implied = total[y] * 1e6 / count[y]          # total value is in mln euro, rounded
    assert abs(implied / v - 1) < 0.001, (y, v, implied)
    assert reg[y] == v, (y, v, reg[y])
    m = months.get(y, [])
    mm = sum(m) / len(m) if len(m) == 12 else None
    note = ("CBS annual mean sale price, existing dwellings bought by private persons; "
            f"= total value/sales ({implied:,.0f}); "
            f"plain mean of 12 monthly averages = {mm:,.0f}" if mm else "monthly incomplete")
    rows.append((y, v, "EUR", note))

# Check 3: CBS news release 2026/08 prints Nederland 480 (x 1 000 euro) for 2025
t = open(RAW / "cbs_news_2026-08_koopwoning_kostte_gemiddeld_480_duizend_euro_in_2025.html", encoding="utf-8").read()
t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
m = re.search(r"Nederland (\d{3}) Den Helder", t)
assert m and int(m.group(1)) == round(annual[2025] / 1000), m and m.group(1)
print(f"Release check: release prints Nederland {m.group(1)}k for 2025; table gives {annual[2025]:,}")

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["year", "avg_dwelling_price_local", "currency", "note"])
    w.writerows(rows)
for y, v, _, n in rows:
    print(y, v, "|", n[-45:])
print("wrote", OUT)
