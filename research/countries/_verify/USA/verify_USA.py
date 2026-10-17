"""Independent verification: USA new single-family house average price / QCEW avg annual pay."""
import csv, io, os, zipfile, sys
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, "raw")
YEARS = [2000, 2007, 2013, 2016, 2022, 2025]

# Price: Census/HUD SOC, Annual sheet, United States average sales price (col 2)
a = pd.read_excel(os.path.join(RAW, "price_cust.xlsx"), sheet_name="Annual", header=None)
price = {}
for _, r in a.iterrows():
    try: y = int(r[0])
    except (ValueError, TypeError): continue
    price[y] = float(r[2])

# Wage: QCEW US000, own 0, industry 10 (total all industries), annual avg
def us_row(rows):
    for r in rows:
        if r["area_fips"] == "US000" and r["own_code"] == "0" and r["industry_code"] == "10" and r["size_code"] == "0":
            return r
wage = {}
for y in YEARS:
    p = os.path.join(RAW, f"qcew_{y}_a_US000.csv")
    if os.path.exists(p):
        r = us_row(csv.DictReader(open(p)))
    else:
        z = zipfile.ZipFile(os.path.join(RAW, f"{y}_annual_singlefile.zip"))
        r = us_row(csv.DictReader(io.TextIOWrapper(z.open(z.namelist()[0]))))
    tw, emp = float(r["total_annual_wages"]), float(r["annual_avg_emplvl"])
    wage[y] = dict(pub=float(r["avg_annual_pay"]), calc=tw / emp)

w = csv.writer(sys.stdout)
w.writerow(["year", "price", "wage_published", "wage_tw_over_emp", "ratio"])
for y in YEARS:
    w.writerow([y, int(price[y]), int(wage[y]["pub"]), round(wage[y]["calc"], 1), round(price[y] / wage[y]["pub"], 3)])
