"""Canada average gross annual wage, 2000-2025, from Statistics Canada SEPH.

Reads only wage/raw/. Writes wage/can_avg_annual_wage_2000-2025.csv and prints
the checks (printed-table match, OECD ratio). Fails loudly if a check fails.

Series:
  2001-2025  table 14-10-0204-01, vector v1740722
             Canada / All employees / Including overtime /
             Industrial aggregate excluding unclassified businesses [11-91N]
  2000       archived table 14-10-0245-01, vector v78952340, same four
             dimensions, pre-2001 SEPH methodology (no bridge, no splice)
Annual = average weekly earnings x WEEKS.
"""
import csv
import io
import re
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OECD_RAW = HERE.parents[1] / "wages" / "raw"
OUT = HERE / "can_avg_annual_wage_2000-2025.csv"

WEEKS = 52  # annualisation factor; 365/7 = 52.14 would add 0.27 %

CUR_ZIP, CUR_CSV, CUR_VEC = "statcan_14100204-eng.zip", "14100204.csv", "v1740722"
OLD_ZIP, OLD_CSV, OLD_VEC = "statcan_14100245-eng.zip", "14100245.csv", "v78952340"
DIMS = {
    "GEO": "Canada",
    "Overtime": "Including overtime",
}

CONCEPT_CUR = ("SEPH avg weekly earnings incl. overtime x52; all employees (part-time incl., "
               "no FTE); gross payroll; industrial aggregate excl. unclassified; StatCan 14-10-0204-01 v1740722")
CONCEPT_OLD = ("SEPH avg weekly earnings incl. overtime x52; all employees; gross payroll; "
               "industrial aggregate excl. unclassified; ARCHIVED StatCan 14-10-0245-01 v78952340, "
               "pre-2001 methodology (StatCan: level shift vs 2001+, not comparable)")


def read_vector(zip_name, csv_name, vector):
    with zipfile.ZipFile(RAW / zip_name) as z:
        text = z.read(csv_name).decode("utf-8-sig")
    out = {}
    for r in csv.DictReader(io.StringIO(text)):
        if r["VECTOR"] != vector:
            continue
        for k, v in DIMS.items():
            assert r[k] == v, (vector, k, r[k])
        assert r["Type of employees"] == "All employees", r["Type of employees"]
        naics = r["North American Industry Classification System (NAICS)"]
        assert naics.startswith("Industrial aggregate excluding unclassified businesses"), naics
        assert r["UOM"] == "Current dollars" and r["SCALAR_FACTOR"].strip() == "units"
        if r["VALUE"]:
            out[int(r["REF_DATE"])] = (float(r["VALUE"]), r["STATUS"])
    return out


def check_printed_table(cur):
    """The default view of StatCan's own table page prints the aggregate row."""
    page = (RAW / "statcan_tbl_14-10-0204-01_page.html").read_text(encoding="utf-8")
    m = re.search(r'"rows":\[\{"values":\[\{"value":"Industrial aggregate excluding '
                  r'unclassified businesses".*?\]\}', page, flags=re.S)
    assert m, "aggregate row not found on table page"
    printed = [float(x.replace(",", "")) for x in re.findall(r'"formattedValue":"([0-9,.]+)"', m.group(0))]
    years = list(range(2021, 2026))
    assert len(printed) == len(years), printed
    for y, p in zip(years, printed):
        assert abs(cur[y][0] - p) < 0.005, (y, cur[y][0], p)
    print("CHECK printed table 14-10-0204-01 (Canada, all employees, incl. OT), 2021-2025:",
          dict(zip(years, printed)), "== CSV: OK")

    page2 = (RAW / "statcan_tbl_14-10-0245-01_page.html").read_text(encoding="utf-8")
    assert '"formattedValue":"655.55"' in page2
    print("CHECK printed table 14-10-0245-01 shows 655.55 (2000): OK")


def read_oecd(fname, filt):
    out = {}
    with open(OECD_RAW / fname, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["REF_AREA"] != "CAN" or r["FREQ"] != "A":
                continue
            if all(r[k] == v for k, v in filt.items()) and r["OBS_VALUE"]:
                y = int(r["TIME_PERIOD"])
                val = float(r["OBS_VALUE"]) * 10 ** int(r["UNIT_MULT"])
                assert y not in out, (fname, y, "duplicate row for filter")
                out[y] = val
    return out


def main():
    cur = read_vector(CUR_ZIP, CUR_CSV, CUR_VEC)
    old = read_vector(OLD_ZIP, OLD_CSV, OLD_VEC)
    check_printed_table(cur)

    rows = []
    weekly = {}
    for y in range(2000, 2026):
        if y in cur:
            w, concept = cur[y][0], CONCEPT_CUR
        elif y in old:
            w, concept = old[y][0], CONCEPT_OLD
        else:
            rows.append([y, "", "CAD", ""])
            continue
        weekly[y] = w
        rows.append([y, f"{w * WEEKS:.0f}", "CAD", concept])
    with open(OUT, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["year", "avg_annual_gross_wage_local", "currency", "concept"])
        wr.writerows(rows)
    print(f"wrote {OUT.name}")

    # Break diagnostics: growth across the 2000/2001 seam vs neighbours.
    print("old 1999->2000 growth %.2f%%; seam 2000(old)->2001(new) %.2f%%; new 2001->2002 %.2f%%" % (
        100 * (old[2000][0] / old[1999][0] - 1), 100 * (cur[2001][0] / old[2000][0] - 1),
        100 * (cur[2002][0] / cur[2001][0] - 1)))

    d11 = read_oecd("oecd_na_table1_income.csv", {"TRANSACTION": "D11", "SECTOR": "S1", "ACTIVITY": "_T",
                                                  "PRICE_BASE": "V", "UNIT_MEASURE": "XDC"})
    sal = read_oecd("oecd_na_table3_empdc.csv", {"TRANSACTION": "SAL", "SECTOR": "S1", "ACTIVITY": "_T",
                                                 "UNIT_MEASURE": "PS"})
    print("year  weekly  annual(x%d)  OECD D11/SAL  ratio" % WEEKS)
    for y in (2000, 2007, 2016, 2022, 2025):
        a = weekly[y] * WEEKS
        o = d11[y] / sal[y] if (y in d11 and y in sal) else None
        print(f"{y}  {weekly[y]:8.2f}  {a:10.0f}  " + (f"{o:12.0f}  {a / o:.3f}" if o else "     n/a"))


if __name__ == "__main__":
    main()
