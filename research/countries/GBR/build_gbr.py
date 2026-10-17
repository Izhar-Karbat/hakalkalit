"""United Kingdom: average price of a dwelling, annual, 2000-2025, GBP.

Reads only raw/. Writes:
  gbr_avg_dwelling_price_2000-2025.csv   main series: arithmetic mean price paid,
                                          England and Wales, all dwellings (new + existing)
  gbr_ukhpi_avg_price_2000-2025.csv      alternative: UK HPI average price, whole UK
                                          (hedonic, geometric mean, Jan 2023 anchor)
  gbr_series_comparison.csv               both series side by side, and the checks

Run: python3 -I build_gbr.py
"""
import csv
import os
from collections import defaultdict

import xlrd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
YEARS = range(2000, 2026)

HPSSA = os.path.join(RAW, "ons_hpssa_dataset12_mean_price_paid_EW.xls")
UKHPI = os.path.join(RAW, "ukhpi_average_prices_2026-07.csv")
PPD_DIR = os.path.join(RAW, "hmlr_price_paid")
PPD_YEARS = (2022, 2023, 2024, 2025)


def hpssa_ew_mean():
    """ONS HPSSA dataset 12, table 1a, row 'England and Wales', columns 'Year ending Dec YYYY'."""
    sh = xlrd.open_workbook(HPSSA).sheet_by_name("1a")
    header = sh.row_values(6)
    row = next(sh.row_values(i) for i in range(sh.nrows) if sh.row_values(i)[1] == "England and Wales")
    assert row[0] == "K04000001", row[:2]
    out = {}
    for col, label in enumerate(header):
        if isinstance(label, str) and label.startswith("Year ending Dec "):
            out[int(label[-4:])] = float(row[col])
    return out


def ppd_mean(year):
    """Arithmetic mean of HMLR Price Paid, PPD category A, for transactions dated in `year`.

    Columns (HMLR Price Paid guidance): 1 price, 2 date of transfer, 4 property type,
    5 new build Y/N, 14 PPD category type (A standard / B additional), 15 record status.
    """
    total, n_a, n_all, total_all = 0, 0, 0, 0
    with open(os.path.join(PPD_DIR, f"pp-{year}.csv"), newline="") as fh:
        for r in csv.reader(fh):
            assert r[2][:4] == str(year), r[2]
            assert r[15] == "A", r[15]
            n_all += 1
            total_all += int(r[1])
            if r[14] == "A":
                total += int(r[1])
                n_a += 1
    return total / n_a, n_a, n_all, total_all / n_all


def ukhpi_annual(region):
    """Mean of the 12 monthly Average_Price values for `region` in each year."""
    months = defaultdict(list)
    with open(UKHPI, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["Region_Name"] == region:
                months[int(r["Date"][:4])].append(float(r["Average_Price"]))
    return {y: sum(v) / len(v) for y, v in months.items() if len(v) == 12}


def main():
    hpssa = hpssa_ew_mean()
    ppd = {y: ppd_mean(y) for y in PPD_YEARS}
    uk = ukhpi_annual("United Kingdom")
    ew_hpi = ukhpi_annual("England and Wales")

    # Main series: HPSSA as published through 2022; 2023-2025 computed from Price Paid
    # with the same definition (category A, E&W, calendar year of transaction).
    main_rows = []
    for y in YEARS:
        if y in hpssa:
            v, note = hpssa[y], ("ONS HPSSA dataset 12 table 1a, England and Wales, year ending Dec; "
                                 "arithmetic mean of all category-A sales registered with HM Land Registry")
        elif y in ppd:
            m, n_a = ppd[y][0], ppd[y][1]
            v, note = m, (f"computed from HM Land Registry Price Paid pp-{y}.csv, category A, "
                          f"England and Wales, n={n_a}; same definition as HPSSA")
        else:
            v, note = None, "not sourced"
        main_rows.append((y, None if v is None else round(v), "GBP", note))

    with open(os.path.join(HERE, "gbr_avg_dwelling_price_2000-2025.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "avg_dwelling_price_local", "currency", "note"])
        for row in main_rows:
            w.writerow(["" if x is None else x for x in row])

    with open(os.path.join(HERE, "gbr_ukhpi_avg_price_2000-2025.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "avg_dwelling_price_local", "currency", "note"])
        for y in YEARS:
            w.writerow([y, round(uk[y]) if y in uk else "", "GBP",
                        "UK HPI, United Kingdom, all property types, mean of 12 monthly average prices "
                        "(hedonic, geometric mean, anchored to Jan 2023)"])

    with open(os.path.join(HERE, "gbr_series_comparison.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "ew_mean_price_paid", "ukhpi_ew_avg_price", "ukhpi_uk_avg_price",
                    "ratio_mean_paid_to_ukhpi_ew", "ppd_own_computation_cat_A", "ppd_n_cat_A", "ppd_n_all", "ppd_mean_cat_A_plus_B"])
        for (y, v, _, _) in main_rows:
            own = ppd.get(y)
            w.writerow([y, v, round(ew_hpi[y]), round(uk[y]),
                        f"{v / ew_hpi[y]:.3f}" if v else "",
                        round(own[0]) if own else "", own[1] if own else "", own[2] if own else "",
                        round(own[3]) if own else ""])

    # Checks printed for the README.
    print("main series (E&W arithmetic mean price paid):")
    for y, v, _, _ in main_rows:
        print(f"  {y} {v}  UK HPI UK {round(uk[y])}  ratio vs UK HPI E&W {v / ew_hpi[y]:.3f}")
    m22 = ppd[2022][0]
    print(f"check 2022: HPSSA published {hpssa[2022]:.0f}; own Price Paid computation {m22:.0f}; "
          f"diff {100 * (m22 / hpssa[2022] - 1):+.2f}%")
    for region in ("England and Wales", "Scotland", "Northern Ireland"):
        print(f"UK HPI 2025 annual mean, {region}: {ukhpi_annual(region)[2025]:.0f}")
    with open(UKHPI, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["Region_Name"] == "United Kingdom" and r["Date"] in ("2025-12-01", "2026-07-01"):
                print(f"check UK HPI {r['Date']}: {r['Average_Price']}")


if __name__ == "__main__":
    main()
