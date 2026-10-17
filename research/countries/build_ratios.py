"""Average dwelling price in years of average gross wage, 2000–2025, for eight countries.

Price: each country's own series (countries/<ISO>/, Spain in ../spain/, Israel in ../report/data/).
Wage, two denominators:
  - OECD average annual wage, national currency, current prices (AV_AN_WAGE, PRICE_BASE=V): one definition
    for every country; full-time-equivalent employees.
  - each country's national statistics bureau: Israel (CBS wage per employee post × 12), Spain (INE ETCL × 12),
    and <ISO>/wage/<iso>_avg_annual_wage_2000-2025.csv for the other six (concept and limits in each README).
Writes price_to_wage_2000-2025.csv (long form) and prints the wide table.
"""
import csv
from pathlib import Path

HERE = Path(__file__).parent
YEARS = range(2000, 2026)
COUNTRIES = ["ISR", "ESP", "USA", "CAN", "GBR", "DEU", "FRA", "NLD"]


def prices():
    out = {}
    for iso in COUNTRIES[2:]:
        f = HERE / iso / f"{iso.lower()}_avg_dwelling_price_2000-2025.csv"
        out[iso] = {int(r["year"]): float(r["avg_dwelling_price_local"])
                    for r in csv.DictReader(open(f, encoding="utf-8")) if r["avg_dwelling_price_local"]}
    rows = list(csv.reader(open(HERE.parent / "report/data/israel_apartment_price_vs_wage_1994-2025_CBS.csv", encoding="utf-8-sig")))[1:]
    out["ISR"] = {int(r[0]): float(r[1]) for r in rows}
    national = {"ISR": {int(r[0]): 12 * float(r[2]) for r in rows}}
    esp = list(csv.DictReader(open(HERE.parent / "spain/spain_price_vs_wage_2004-2025.csv", encoding="utf-8")))
    out["ESP"] = {int(r["year"]): float(r["avg_dwelling_price_EUR"]) for r in esp}
    national["ESP"] = {int(r["year"]): 12 * float(r["gross_monthly_wage_EUR"]) for r in esp}
    for iso in COUNTRIES[2:]:
        f = HERE / iso / "wage" / f"{iso.lower()}_avg_annual_wage_2000-2025.csv"
        national[iso] = {int(r["year"]): float(r["avg_annual_gross_wage_local"])
                         for r in csv.DictReader(open(f, encoding="utf-8")) if r["avg_annual_gross_wage_local"]}
    return out, national


def oecd_wages():
    out = {}
    for r in csv.DictReader(open(HERE / "wages/raw/oecd_av_an_wage_all.csv", encoding="utf-8-sig")):
        if r["REF_AREA"] in COUNTRIES and r["PRICE_BASE"] == "V" and r["UNIT_MEASURE"] != "USD_PPP" and r["OBS_VALUE"]:
            out.setdefault(r["REF_AREA"], {})[int(r["TIME_PERIOD"])] = float(r["OBS_VALUE"])
    return out


def main():
    price, national = prices()
    wage = oecd_wages()
    long = []
    for iso in COUNTRIES:
        for y in YEARS:
            p = price[iso].get(y)
            a = p / wage[iso][y] if p and y in wage[iso] else None
            b = p / national[iso][y] if p and iso in national and y in national[iso] else None
            long.append([iso, y, p, wage[iso].get(y), a, national.get(iso, {}).get(y), b])
    with open(HERE / "price_to_wage_2000-2025.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["country", "year", "avg_dwelling_price_local", "oecd_avg_annual_wage_local",
                     "years_of_oecd_wage", "national_annual_wage_local", "years_of_national_wage"])
        for r in long:
            w.writerow([r[0], r[1]] + ["" if v is None else (f"{v:.2f}" if isinstance(v, float) and v < 100 else f"{v:.0f}") for v in r[2:]])
    show = [2000, 2003, 2007, 2010, 2013, 2016, 2019, 2022, 2025]
    print("years of OECD average wage")
    print("     " + " ".join(f"{y:>6}" for y in show))
    for iso in COUNTRIES:
        cells = [next((f"{r[4]:6.1f}" for r in long if r[0] == iso and r[1] == y and r[4]), "     -") for y in show]
        print(f"{iso:4s} " + " ".join(cells))
    print("years of national wage")
    print("     " + " ".join(f"{y:>6}" for y in show))
    for iso in COUNTRIES:
        cells = [next((f"{r[6]:6.1f}" for r in long if r[0] == iso and r[1] == y and r[6]), "     -") for y in show]
        print(f"{iso:4s} " + " ".join(cells))


if __name__ == "__main__":
    main()
