"""Spain: average dwelling price in monthly gross wages, 2004-2025, built the way the Israel table is built.

    price of an average dwelling = average appraised price per m² (Ministry of Housing, via Bank of Spain)
                                   × average size of a registered dwelling sale (Colegio de Registradores)
    monthly wage                 = average gross wage per worker per month (INE, labour cost survey ETCL)

Every input is read from the files in raw/. Each dwelling size is checked against the sentence in the
yearbook that states it. Run with: python3 build_spain_ratio.py
"""
import csv
import json
import re
import statistics
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw"

BDE_PRICE_SERIES = "DHIVTNOAPLPMMUVT_RLI.T"   # Precio medio m2 de viviendas libres tasadas. Total nacional
INE_WAGE_SERIES = "ETCL13724"                 # Total Nacional. No ajustados. Coste salarial total por trabajador. Euros
INE_IPV_SERIES = "IPV1276"                    # Nacional. Media anual. General (transaction index, 2025 = 100)
REGISTRADORES_PRICE_M2 = {2021: 1823, 2022: 1944, 2023: 1963, 2024: 2086, 2025: 2284}  # actual registered sales

# year -> (m², yearbook that states it, text as printed there)
DWELLING_M2 = {
    2004: (97.30, 2004, "97,30"), 2005: (97.36, 2005, "superficie media fue de 97,36"), 2006: (97.46, 2007, "97,46"), 2007: (100.36, 2007, "100,36"),
    2008: (100.05, 2008, "100,05"), 2009: (98.78, 2009, "98,78"), 2010: (98.93, 2010, "98,93"),
    2011: (98.61, 2011, "98,61"), 2012: (98.31, 2012, "98,31"), 2013: (97.97, 2013, "97,97"),
    2014: (98.34, 2014, "98,34"), 2015: (98.49, 2015, "98,49"), 2016: (97.73, 2017, "97,73"),
    2017: (97.75, 2017, "97,75"), 2018: (98.01, 2018, "98,01"), 2019: (98.69, 2019, "98,69"),
    2020: (100.85, 2020, "100,85"), 2021: (102.0, 2021, "102 m"), 2022: (100.5, 2022, "100,5"),
    2023: (99.1, 2023, "99,1"), 2024: (99.9, 2024, "99,9"), 2025: (100.6, 2025, "100,6"),
}


def yearbook_text(year):
    pdf = RAW / "registradores_anuarios" / f"ERI_Anuario_{year}.pdf"
    out = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    return re.sub(r"\s+", " ", out)


def check_sources():
    for year, (_, book, printed) in DWELLING_M2.items():
        assert printed in yearbook_text(book), f"{year}: '{printed}' not found in yearbook {book}"
    for year, value in REGISTRADORES_PRICE_M2.items():
        printed = f"{value // 1000}.{value % 1000:03d} €/m²"
        assert printed in yearbook_text(year), f"{year}: '{printed}' not found in yearbook {year}"


def annual_means(pairs):
    by_year = {}
    for year, value in pairs:
        by_year.setdefault(year, []).append(value)
    return {y: (statistics.mean(v), len(v)) for y, v in by_year.items()}


def load_wage():
    series = next(s for s in json.load(open(RAW / "ine_etcl_table11221_wages.json")) if s["COD"] == INE_WAGE_SERIES)
    return annual_means((d["Anyo"], d["Valor"]) for d in series["Data"])


def load_price_m2():
    rows = list(csv.reader(open(RAW / "bde_si_1_5_housing_indicators.csv", encoding="latin-1")))
    col = rows[0].index(BDE_PRICE_SERIES)
    pairs = [(int(r[0][-4:]), float(r[col])) for r in rows[6:]
             if r[0][-4:].isdigit() and r[col] not in ("_", "")]
    return annual_means(pairs)


def load_ipv():
    series = next(s for s in json.load(open(RAW / "ine_ipv_table80271_price_index.json")) if s["COD"] == INE_IPV_SERIES)
    return {d["Anyo"]: d["Valor"] for d in series["Data"]}


def main():
    check_sources()
    wage, price_m2, ipv = load_wage(), load_price_m2(), load_ipv()
    header = ["year", "gross_monthly_wage_EUR", "appraised_price_EUR_per_m2", "dwelling_m2",
              "avg_dwelling_price_EUR", "monthly_wages_per_dwelling", "salary_years",
              "check_registered_sales_monthly_wages", "check_INE_index_monthly_wages"]
    out = [header]
    for year in sorted(DWELLING_M2):
        (w, nw), (p, np_) = wage[year], price_m2[year]
        assert nw == 4 and np_ == 4, f"{year}: incomplete year"
        m2 = DWELLING_M2[year][0]
        months = p * m2 / w
        reg = REGISTRADORES_PRICE_M2.get(year)
        idx = price_m2[2015][0] * ipv[year] / ipv[2015] * m2 / w if year in ipv else None
        out.append([year, f"{w:.2f}", f"{p:.1f}", m2, f"{p * m2:.0f}", f"{months:.1f}", f"{months / 12:.2f}",
                    f"{reg * m2 / w:.1f}" if reg else "", f"{idx:.1f}" if idx else ""])
    with open(HERE / "spain_price_vs_wage_2004-2025.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(out)
    for row in out:
        print("\t".join(str(c) for c in row))


if __name__ == "__main__":
    main()
