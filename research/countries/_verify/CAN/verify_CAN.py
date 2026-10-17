"""Blind recomputation of Canada: CREA MLS residential average sale price / (SEPH AWE x 52).

Price: CREA Forecast_data_Oct_2026.xlsx, sheet "Chart", column "Residential Average Sale Price"
       (annual, actual years 1980-2025; current CREA vintage).
Wage:  StatCan 14-10-0204-01 (2001+) and archived 14-10-0245-01 (2000): Canada, All employees,
       Including overtime, Industrial aggregate excluding unclassified businesses, current dollars,
       annual average weekly earnings, x 52.
Cross-check price vintages from CMHC publications are printed alongside (values typed from the PDFs).
"""
import csv
import io
import zipfile
from pathlib import Path

import openpyxl

RAW = Path(__file__).resolve().parent / "raw"
YEARS = [2000, 2007, 2013, 2016, 2022, 2025]


def seph(zip_name, csv_name):
    out = {}
    with zipfile.ZipFile(RAW / zip_name) as z:
        with z.open(csv_name) as fh:
            for row in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8-sig")):
                if (row["GEO"] == "Canada"
                        and row["Type of employees"] == "All employees"
                        and row["Overtime"] == "Including overtime"
                        and row["North American Industry Classification System (NAICS)"].startswith(
                            "Industrial aggregate excluding unclassified businesses")
                        and row["UOM"] == "Current dollars"):
                    out[int(row["REF_DATE"])] = float(row["VALUE"])
    return out


def crea_price():
    wb = openpyxl.load_workbook(RAW / "Forecast_data_Oct_2026.xlsx", data_only=True)
    ws = wb["Chart"]
    out = {}
    for r in ws.iter_rows(values_only=True):
        if r[0] and str(r[0]).isdigit():
            out[int(r[0])] = float(r[2])
    return out


# CMHC-published vintages of the same CREA series (for revision analysis only)
CMHC_VINTAGES = {
    2000: {"CHO2010": 163992},
    2007: {"CHO2010": 307094, "CHO2011": 307132, "CHO2014": 306743},
    2013: {"CHO2014": 382576},
    2016: {"HMO Fall2017": 490032},
    2022: {"HMO Spring2024": 703959, "HMO Feb2025": 704543},
    2025: {"HMO 2026 (rounded)": 680000},
}

if __name__ == "__main__":
    awe = seph("14100245-eng.zip", "14100245.csv")
    awe_new = seph("14100204-eng.zip", "14100204.csv")
    awe.update(awe_new)
    price = crea_price()
    print("year,price,awe_weekly,wage_annual,ratio,cmhc_vintages")
    for y in YEARS:
        w = awe[y] * 52
        print(f"{y},{price[y]:.2f},{awe[y]:.2f},{w:.2f},{price[y]/w:.4f},{CMHC_VINTAGES.get(y)}")
    # splice check around 2000/2001
    print("AWE 1999,2000 (old table):", awe[1999] if 1999 in awe else None, awe[2000])
    print("AWE 2001,2002 (current table):", awe_new[2001], awe_new[2002])
