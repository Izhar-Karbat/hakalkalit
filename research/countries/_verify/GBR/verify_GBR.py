"""Independent verification: England & Wales mean price paid / (KAB9 annual mean x 52)."""
import csv, sys, os
from collections import defaultdict
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
YEARS = [2000, 2007, 2013, 2016, 2022, 2025]

# Wage: KAB9 monthly values (£/week), calendar-year mean x 52
kab9 = {}
with open(os.path.join(RAW, "kab9_lms.csv")) as f:
    for row in csv.reader(f):
        if len(row) == 2 and len(row[0]) == 8 and row[0][4] == " ":
            kab9[row[0]] = float(row[1])
annual_wk = {}
for y in YEARS:
    vals = [v for k, v in kab9.items() if k.startswith(str(y))]
    assert len(vals) == 12, (y, len(vals))
    annual_wk[y] = sum(vals) / 12
kab9_annual_published = {}
with open(os.path.join(RAW, "kab9_lms.csv")) as f:
    for row in csv.reader(f):
        if len(row) == 2 and len(row[0]) == 4 and row[0].isdigit():
            kab9_annual_published[int(row[0])] = float(row[1])

# Price from PPD yearly files
def ppd_stats(y):
    s = defaultdict(lambda: [0, 0.0])
    with open(os.path.join(RAW, f"pp-{y}.csv")) as f:
        for r in csv.reader(f):
            p = float(r[1]); cat = r[14]; typ = r[4]; status = r[15]
            if status == "D":
                continue
            s[("all",)][0] += 1; s[("all",)][1] += p
            s[("cat", cat)][0] += 1; s[("cat", cat)][1] += p
            if cat == "A" and typ != "O":
                s[("A_noO",)][0] += 1; s[("A_noO",)][1] += p
            if typ != "O":
                s[("noO",)][0] += 1; s[("noO",)][1] += p
    return {k: (n, t / n) for k, (n, t) in s.items()}

# HPSSA dataset 12, table 1a, England and Wales, year ending Dec
x = pd.read_excel(os.path.join(RAW, "hpssadataset12meanpricepaidforadministrativegeographies.xls"), "1a", header=None)
hdr = x.iloc[6].tolist()
ew = x[x[0] == "K04000001"].iloc[0]
hpssa = {}
for i, h in enumerate(hdr):
    if isinstance(h, str) and h.startswith("Year ending Dec"):
        hpssa[int(h[-4:])] = float(ew[i])

out = []
for y in YEARS:
    st = ppd_stats(y)
    wage = annual_wk[y] * 52
    price_ppdA = st[("cat", "A")][1]
    price = hpssa.get(y, price_ppdA)
    src = "HPSSA12" if y in hpssa else "PPD cat A"
    print(f"{y}: HPSSA={hpssa.get(y)}  PPD: " + "  ".join(f"{k}=n{n}/{m:,.0f}" for k, (n, m) in sorted(st.items())))
    print(f"   KAB9 mean/wk={annual_wk[y]:.3f} (published annual {kab9_annual_published.get(y)}), wage={wage:,.0f}")
    out.append((y, round(price), src, round(price_ppdA), round(wage), round(price / wage, 3), round(price_ppdA / wage, 3)))
with open(os.path.join(HERE, "verify_GBR_out.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["year", "price", "price_src", "price_ppd_catA", "wage", "ratio", "ratio_ppd_catA"]); w.writerows(out)
for r in out: print(r)
