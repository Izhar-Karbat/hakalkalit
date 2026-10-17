"""Germany: average gross annual wage per employee, 2000-2025, from Destatis national accounts.

Primary series: GENESIS 81000-0017, content VST038 "Bruttolöhne/-gehälter je Arbeitnehmer
(im Inland)", EUR per year, WZ08G2=%TOTAL% (all industries).

Checks (all computed from files in raw/):
  A. Recompute VST038 from 81000-0015: VST020 (gross wages, EUR bn) / ERW061 (employees, 1000).
  B. 81000-0007 VST036 (gross wages per employee per month, national concept) x 12 vs. the
     Destatis "Wichtige gesamtwirtschaftliche Größen" table page (monthly 2023-2025).
  C. Year-on-year % change of VST038 vs. the Destatis "Personenkonzept" table page.
  D. OECD D11 / SAL ratio (domestic concept, S1, _T, persons).
  E. Verdiensterhebung full-time monthly earnings (rejected concept) printed for context.

Run:  python -I build_deu_wage.py   (from any directory)
"""
import csv
import html
import json
import re
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OECD = HERE.parents[1] / "wages" / "raw"
YEARS = range(2000, 2026)


def jsonstat(table):
    """Return {(content, other dims..., year): (value, status)} for a saved GENESIS table."""
    d = json.loads((RAW / f"destatis_genesis_{table}_data.json").read_text())["data"][0]
    ids, sizes = d["id"], d["size"]
    cats = []
    for dim in ids:
        idx = d["dimension"][dim]["category"]["index"]
        cats.append(sorted(idx, key=idx.get))
    out = {}
    for n, combo in enumerate(product(*cats)):
        key = dict(zip(ids, combo))
        out[tuple(key[k] for k in ids if k not in ("statistic", "DINSG"))] = (
            d["value"][n], d["status"][n])
    assert len(out) == len(d["value"]) == eval("*".join(map(str, sizes)))
    return out


def page_text(name):
    t = (RAW / name).read_text(encoding="utf-8")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


def de_num(s):
    return float(s.replace(" ", "").replace(" ", "").replace(".", "").replace(",", "."))


def main():
    t17 = jsonstat("81000-0017")
    t15 = jsonstat("81000-0015")
    t07 = jsonstat("81000-0007")

    rows, work = [], []
    for y in YEARS:
        ys = str(y)
        k = ("VST038$QMU", "%TOTAL%", ys)
        if k not in t17 or t17[k][0] is None:
            rows.append([y, "", "EUR", ""])
            continue
        v, st = t17[k]
        wages_bn = t15[("VST020$QMU", "%TOTAL%", ys)][0]
        emp_k = t15[("ERW061$QMU", "%TOTAL%", ys)][0]
        recomputed = wages_bn * 1e9 / (emp_k * 1e3)
        monthly_nat = t07[("VST036$QMU", ys)][0]
        # A: published per-employee figure equals totals / employees within rounding
        assert abs(recomputed - v) / v < 0.002, (y, v, recomputed)
        rows.append([y, round(v), "EUR",
                     "Destatis VGR 81000-0017 VST038 gross wages and salaries per employee, "
                     "domestic concept, all employees incl. part-time and marginal (persons), "
                     f"annual; status {st}"])
        work.append(dict(year=y, vst038_eur=v, status=st, vst020_bn=wages_bn,
                         erw061_thousand=emp_k, recomputed_eur=round(recomputed, 1),
                         vst036_monthly_national_concept=monthly_nat,
                         vst036_x12=monthly_nat * 12 if monthly_nat else None))

    with open(HERE / "deu_avg_annual_wage_2000-2025.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "avg_annual_gross_wage_local", "currency", "concept"])
        w.writerows(rows)

    # B: printed monthly figures (domestic concept) on the Destatis key-aggregates page
    x = page_text("destatis_table_page_inlandsprodukt-gesamtwirtschaft.html")
    m = re.search(r"Bruttolöhne und -gehälter je Arbeitnehmer je Monat Euro "
                  r"(\d \d{3}) (\d \d{3}) (\d \d{3}) je geleisteter", x)
    printed_monthly = dict(zip((2023, 2024, 2025), (de_num(g) for g in m.groups())))
    print("Check B: printed monthly (page) vs VST038/12 (domestic) and VST036 (national)")
    for y, p in printed_monthly.items():
        g = t17[("VST038$QMU", "%TOTAL%", str(y))][0] / 12
        n = t07[("VST036$QMU", str(y))][0]
        print(f"  {y}: page {p:.0f}  VST038/12 {g:.1f}  VST036 {n:.0f}  "
              f"{'MATCH' if round(g) == p else 'DIFF'}")
        assert round(g) == p  # page is the domestic concept: VST038 / 12

    # C: printed yoy % change of gross wages per employee, all industries (Personenkonzept page)
    x = page_text("destatis_table_page_inlandsprodukt-personenkonzept.html")
    m = re.search(r"Bruttolöhne und -gehälter je Arbeitnehmer 3 .*?Alle Wirtschaftsbereiche "
                  r"(-?[\d,]+) (-?[\d,]+) (-?[\d,]+)", x)
    printed_yoy = dict(zip((2023, 2024, 2025), (de_num(g) for g in m.groups())))
    print("Check C: printed yoy % (page) vs VST038 yoy")
    for y, p in printed_yoy.items():
        a = t17[("VST038$QMU", "%TOTAL%", str(y))][0]
        b = t17[("VST038$QMU", "%TOTAL%", str(y - 1))][0]
        g = round((a / b - 1) * 100, 1)
        print(f"  {y}: page {p}  computed {g}  {'MATCH' if abs(g - p) <= 0.1 else 'DIFF'}")
        assert abs(g - p) <= 0.1

    # B2: printed wage totals (EUR bn, national concept) on the income-distribution page
    x = page_text("destatis_table_page_bip-einkommensverteilung.html")
    m = re.search(r"Bruttolöhne und -gehälter (\d \d{3},\d{3}) (\d \d{3},\d{3}) (\d \d{3},\d{3})", x)
    print("Check B2: printed wage total, EUR bn (page) vs 81000-0007 VST006 / 81000-0015 VST020")
    for y, p in zip((2023, 2024, 2025), (de_num(g) for g in m.groups())):
        n = t07[("VST006$QMU", str(y))][0]
        d = t15[("VST020$QMU", "%TOTAL%", str(y))][0]
        print(f"  {y}: page {p}  VST006 national {n}  VST020 domestic {d}")
        assert abs(n - p) < 0.001

    # D: OECD D11 / SAL
    def oecd(fname, flt):
        out = {}
        with open(OECD / fname, newline="") as f:
            for r in csv.DictReader(f):
                if r["REF_AREA"] == "DEU" and all(r[k] == v for k, v in flt.items()):
                    if r["OBS_VALUE"]:
                        out[int(r["TIME_PERIOD"])] = float(r["OBS_VALUE"]) * 10 ** int(r["UNIT_MULT"])
        return out
    d11 = oecd("oecd_na_table1_income.csv", dict(TRANSACTION="D11", SECTOR="S1", ACTIVITY="_T",
                                                  PRICE_BASE="V", UNIT_MEASURE="XDC"))
    sal = oecd("oecd_na_table3_empdc.csv", dict(TRANSACTION="SAL", SECTOR="S1", ACTIVITY="_T",
                                                 UNIT_MEASURE="PS"))
    natl = {r[0]: r[1] for r in rows if r[1] != ""}
    print("Check D: national / OECD (D11/SAL)")
    for wrow in work:
        y = wrow["year"]
        o = d11[y] / sal[y] if y in d11 and y in sal else None
        wrow["oecd_d11_per_sal_eur"] = round(o, 1) if o else None
        wrow["ratio_national_to_oecd"] = round(wrow["vst038_eur"] / o, 4) if o else None
    for y in (2000, 2007, 2016, 2022):
        r = next(w for w in work if w["year"] == y)
        print(f"  {y}: national {natl[y]}  OECD {r['oecd_d11_per_sal_eur']}  "
              f"ratio {r['ratio_national_to_oecd']}")

    # E: Verdiensterhebung (full-time only, excl. special payments) - context only
    x = page_text("destatis_table_page_verdienste-lange-reihe-deutschland.html")
    ver = {}
    for m in re.finditer(r"\b(19\d\d|20\d\d) (?:2 )?(\d \d{3}) (\d \d{3}) (\d \d{3})", x):
        ver[int(m.group(1))] = de_num(m.group(2))
    for wrow in work:
        v = ver.get(wrow["year"])
        wrow["verdienst_fulltime_monthly_excl_special"] = v
        wrow["verdienst_x12"] = v * 12 if v else None
    print("Check E: Verdiensterhebung full-time monthly x12 vs VST038")
    for y in (2000, 2007, 2016, 2022, 2025):
        r = next(w for w in work if w["year"] == y)
        print(f"  {y}: VE x12 {r['verdienst_x12']:.0f}  VGR {r['vst038_eur']:.0f}  "
              f"VGR/VE {r['vst038_eur'] / r['verdienst_x12']:.3f}")

    with open(HERE / "deu_wage_workings.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(work[0].keys()))
        w.writeheader()
        w.writerows(work)

    print("\nOutput:")
    for y in (2000, 2007, 2016, 2022, 2025):
        print(f"  {y}: {natl[y]} EUR")
    print("  years with values:", min(natl), "-", max(natl), f"({len(natl)})")


if __name__ == "__main__":
    main()
