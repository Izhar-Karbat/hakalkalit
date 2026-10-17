"""United States: average price of a dwelling, annual, 2000-2025, USD.

Reads only raw/. Writes usa_avg_dwelling_price_2000-2025.csv.

Main series: Census Bureau / HUD, Survey of Construction, AVERAGE sales price of
new privately-owned single-family houses sold, United States, annual (sheet
"Annual" of price_cust.xlsx). Census publishes the annual average directly
(computed from all houses sold in the year), so no averaging of months is done
for the CSV.

Printed to stdout only (not in the CSV), as cross-checks:
  * the published annual figures vs Table Q6 of the Census quarterly release PDF;
  * the published annual figure vs the mean of the 12 published monthly averages;
  * cumulative growth vs the FHFA purchase-only house price index (NSA, USA),
    which covers existing + new homes with conforming mortgages.
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
XLSX = RAW / "census_nrs_price_cust_new_houses_sold_median_avg_price.xlsx"
PDF = RAW / "census_nrs_quarterly_sales_release.pdf"
FHFA = RAW / "fhfa_hpi_master_all_indexes.csv"
OUT = HERE / "usa_avg_dwelling_price_2000-2025.csv"
YEARS = range(2000, 2026)
NOTE = ("Census/HUD SOC average sales price of NEW single-family houses sold "
        "(incl. land), annual as published; new homes only, excludes existing homes")


def load_annual():
    a = pd.read_excel(XLSX, sheet_name="Annual", header=None)
    assert "Average sales price" in str(a.iloc[5, 2]), a.iloc[5].tolist()
    out = {}
    for _, r in a.iloc[6:].iterrows():
        y = r[0]
        if isinstance(y, (int, float)) and not pd.isna(y) and 1900 < y < 2100:
            out[int(y)] = float(r[2])
    return out


def load_monthly():
    m = pd.read_excel(XLSX, sheet_name="Monthly", header=None)
    assert "Average sales price" in str(m.iloc[5, 2])
    m = m.iloc[6:]
    m = m[pd.to_datetime(m[0], errors="coerce").notna()].copy()
    m["date"] = pd.to_datetime(m[0])
    m["avg"] = pd.to_numeric(m[2], errors="coerce")
    return m


def pdf_annual_avg():
    txt = subprocess.run(["pdftotext", "-layout", str(PDF), "-"],
                         capture_output=True, text=True, check=True).stdout
    sec = txt.split("Table Q6.")[1].split("\nAverage Sales Price")[1].split("QUARTERLY DATA")[0]
    got = {}
    for line in sec.splitlines():
        mm = re.match(r"\s+(\d{4})\s+([\d,]+)\s", line)
        if mm:
            got[int(mm.group(1))] = float(mm.group(2).replace(",", ""))
    return got


def fhfa_po_annual():
    d = pd.read_csv(FHFA, low_memory=False)
    d = d[(d.hpi_type == "traditional") & (d.hpi_flavor == "purchase-only")
          & (d.frequency == "quarterly") & (d.place_id == "USA")]
    d = d[d.yr.between(2000, 2025)]
    g = d.groupby("yr")
    assert (g.size() == 4).all(), g.size()
    return g.index_nsa.mean().to_dict()


def main():
    annual = load_annual()
    rows = []
    for y in YEARS:
        v = annual.get(y)
        rows.append({"year": y,
                     "avg_dwelling_price_local": "" if v is None else f"{v:.0f}",
                     "currency": "USD", "note": NOTE})
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["year", "avg_dwelling_price_local", "currency", "note"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT.name}: {sum(1 for r in rows if r['avg_dwelling_price_local'])} years")

    # Check 1: CSV vs the release PDF's printed annual averages (Table Q6).
    printed = pdf_annual_avg()
    for y, v in sorted(printed.items()):
        ok = annual[y] == v
        print(f"check Q6 {y}: xlsx {annual[y]:,.0f} vs release PDF {v:,.0f} -> {'MATCH' if ok else 'MISMATCH'}")
        if not ok:
            sys.exit(1)

    # Check 2: published annual vs mean of published monthly averages.
    m = load_monthly()
    print("\nyear  published_annual  mean_of_12_months  diff%")
    for y in YEARS:
        mv = m[m.date.dt.year == y]["avg"]
        if len(mv) == 12:
            print(f"{y}  {annual[y]:>10,.0f}  {mv.mean():>12,.0f}  {100*(annual[y]/mv.mean()-1):+5.1f}")

    # Check 3: growth vs FHFA purchase-only index (existing + new).
    po = fhfa_po_annual()
    print("\nyear  Census_avg_new  idx(2000=100)  FHFA_PO_NSA idx(2000=100)")
    for y in (2000, 2006, 2007, 2011, 2016, 2020, 2022, 2025):
        print(f"{y}  {annual[y]:>10,.0f}  {100*annual[y]/annual[2000]:6.1f}  {100*po[y]/po[2000]:6.1f}")


if __name__ == "__main__":
    main()
