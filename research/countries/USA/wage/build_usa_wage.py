"""United States average gross annual wage per job, 2000-2025, from BLS QCEW.

Concept: QCEW U.S. total, total covered (UI + UCFE), all ownerships, all industries:
    total annual wages / annual average employment
Part-time jobs are included; a person holding two covered jobs counts twice (jobs basis).

Inputs (all in raw/, unmodified as downloaded; see SOURCES.csv):
  2001-2025  BLS Public Data API v2, QCEW series
               ENUUS00010010  employment, monthly (persons/jobs)
               ENUUS00030010  total wages, quarterly (thousands of USD)
               ENUUS00050010  average annual pay, annual (USD) -- BLS's own published value
  2000       2000_annual_singlefile.zip (QCEW annual averages, all areas), row
               area_fips=US000, own_code=0, industry_code=10
  check      qcew_open_{2014,2025}_a_area_US000.csv (QCEW open-data slices)
             bls_ew_annual_2007_total_coverage_by_ownership.pdf (printed Table 1,
               "Employment and Wages, Annual Averages 2007"; values transcribed in
               PRINTED_2007_TABLE below and compared, not used as inputs)
  OECD       ../../wages/raw/oecd_na_table1_income.csv, oecd_na_table3_empdc.csv
"""
import csv
import io
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OECD_RAW = HERE.parent.parent / "wages" / "raw"
YEARS = range(2000, 2026)
WINDOWS = ["2001-2010", "2011-2020", "2021-2025"]
CONCEPT = ("BLS QCEW, U.S. total covered (UI+UCFE), all ownerships, all industries: "
           "total annual wages / annual average employment; jobs basis, part-time included, gross")

# Printed in BLS "Employment and Wages, Annual Averages 2007", Table 1, Total covered
# (UI and UCFE), row "Annual wages per employee" (raw/bls_ew_annual_2007_total_coverage_by_ownership.pdf).
PRINTED_2007_TABLE = {2000: 35323, 2001: 36219, 2002: 36764, 2003: 37765, 2004: 39354,
                      2005: 40677, 2006: 42535, 2007: 44458}


def api_series(series_id):
    rows = []
    for w in WINDOWS:
        d = json.loads((RAW / f"bls_api_{series_id}_{w}.json").read_text())
        assert d["status"] == "REQUEST_SUCCEEDED", (series_id, w, d["message"])
        (s,) = d["Results"]["series"]
        assert s["seriesID"] == series_id
        rows += s["data"]
    return rows


def by_year(rows, n_periods):
    out = {}
    for r in rows:
        out.setdefault(int(r["year"]), {})[r["period"]] = float(r["value"])
    complete = {y: v for y, v in out.items() if len(v) == n_periods}
    return complete


def qcew_us_total_row(fh):
    for r in csv.DictReader(fh):
        if (r["area_fips"], r["own_code"], r["industry_code"], r["size_code"], r["qtr"]) == \
                ("US000", "0", "10", "0", "A"):
            return r
    raise LookupError("US000 own 0 industry 10 row not found")


def oecd_value(path, filt):
    vals = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            if all(r[k] == v for k, v in filt.items()) and r["OBS_VALUE"] != "":
                y = int(r["TIME_PERIOD"])
                assert y not in vals, (path, y)
                vals[y] = float(r["OBS_VALUE"]) * 10 ** int(r["UNIT_MULT"])
    return vals


def main():
    emp = by_year(api_series("ENUUS00010010"), 12)          # monthly employment
    wages = by_year(api_series("ENUUS00030010"), 4)         # quarterly wages, $ thousands
    pub = {int(r["year"]): int(r["value"]) for r in api_series("ENUUS00050010")
           if r["period"] == "A01"}

    series, notes = {}, []
    for y in YEARS:
        if y in emp and y in wages:
            avg_emp = sum(emp[y].values()) / 12
            tot = sum(wages[y].values()) * 1000
            series[y] = tot / avg_emp
            # BLS truncates/rounds its own published value; it must agree within $1
            assert abs(round(series[y]) - pub[y]) <= 1, (y, series[y], pub[y])

    with zipfile.ZipFile(RAW / "2000_annual_singlefile.zip") as z:
        (name,) = z.namelist()
        with z.open(name) as fh:
            r2000 = qcew_us_total_row(io.TextIOWrapper(fh, encoding="utf-8"))
    series[2000] = float(r2000["total_annual_wages"]) / float(r2000["annual_avg_emplvl"])
    assert abs(round(series[2000]) - int(r2000["avg_annual_pay"])) <= 1

    # Cross-check: open-data annual slices vs the API-derived values
    for y in (2014, 2025):
        with open(RAW / f"qcew_open_{y}_a_area_US000.csv", newline="") as fh:
            r = qcew_us_total_row(fh)
        od = float(r["total_annual_wages"]) / float(r["annual_avg_emplvl"])
        notes.append(f"open-data {y}: {od:,.0f} vs API-derived {series[y]:,.0f} "
                     f"(published avg_annual_pay {r['avg_annual_pay']})")

    for y, printed in PRINTED_2007_TABLE.items():
        notes.append(f"printed 2007 Table 1, {y}: ${printed:,} vs this series "
                     f"{series[y]:,.0f} (diff {series[y] - printed:+,.0f})")

    out = HERE / "usa_avg_annual_wage_2000-2025.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "avg_annual_gross_wage_local", "currency", "concept"])
        for y in YEARS:
            w.writerow([y, f"{series[y]:.0f}" if y in series else "", "USD", CONCEPT])

    # OECD national-accounts wages and salaries per employee, USA
    d11 = oecd_value(OECD_RAW / "oecd_na_table1_income.csv",
                     dict(REF_AREA="USA", TRANSACTION="D11", SECTOR="S1", ACTIVITY="_T",
                          PRICE_BASE="V", UNIT_MEASURE="XDC"))
    sal = oecd_value(OECD_RAW / "oecd_na_table3_empdc.csv",
                     dict(REF_AREA="USA", TRANSACTION="SAL", SECTOR="S1", ACTIVITY="_T",
                          UNIT_MEASURE="PS"))
    cmp_rows = []
    for y in YEARS:
        o = d11[y] / sal[y] if (y in d11 and y in sal) else None
        cmp_rows.append([y, f"{series[y]:.0f}" if y in series else "",
                         f"{o:.0f}" if o else "",
                         f"{series[y] / o:.4f}" if (o and y in series) else ""])
    with open(HERE / "usa_vs_oecd_d11_per_employee.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "bls_qcew_avg_annual_wage", "oecd_d11_per_employee", "ratio_bls_over_oecd"])
        w.writerows(cmp_rows)

    print("year  QCEW  OECD-D11/SAL  ratio")
    for y, a, b, c in cmp_rows:
        print(y, a, b, c)
    print()
    for n in notes:
        print(n)


if __name__ == "__main__":
    main()
