"""United Kingdom: average gross annual wage per employee job, 2000-2025, GBP.

Reads only raw/ (plus the shared OECD files in ../../wages/raw/). Writes:
  gbr_avg_annual_wage_2000-2025.csv     main series: ONS Average Weekly Earnings (KAB9),
                                         whole economy, total pay, Great Britain,
                                         calendar-year mean of the 12 monthly values x 52
  gbr_wage_comparison_2000-2025.csv      main series next to ASHE mean annual gross pay
                                         (UK, GB, England and Wales) and the OECD
                                         national-accounts wages-and-salaries per employee
  gbr_wage_checks.csv                    every check, with expected value, our value, verdict

Run: ~/miniconda3/bin/python -I build_gbr_wage.py   (needs pandas, xlrd, openpyxl)
"""
import csv
import glob
import html
import io
import os
import re
import zipfile

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OECD_RAW = os.path.join(HERE, "..", "..", "wages", "raw")
YEARS = range(2000, 2026)
WEEKS_PER_YEAR = 52

AWE_CSV = os.path.join(RAW, "ons_awe_kab9.csv")
GEO_ROWS = {"United Kingdom": "UK", "Great Britain": "GB", "England and Wales": "EW"}


# ---------------------------------------------------------------- AWE (main)
def awe_kab9():
    """Monthly and ONS-published annual KAB9 values (GBP per week)."""
    monthly, annual = {}, {}
    with open(AWE_CSV, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) != 2:
                continue
            key, val = row
            if re.fullmatch(r"\d{4} [A-Z]{3}", key):
                monthly.setdefault(int(key[:4]), {})[key[5:]] = float(val)
            elif re.fullmatch(r"\d{4}", key):
                annual[int(key)] = float(val)
    return monthly, annual


# ---------------------------------------------------------------- ASHE (check)
def vintage_rank(vint):
    """Prefer the newest basis ONS published for a year: revised / 2007-consistent / SOC2010."""
    v = vint.lower()
    return 1 if ("revised" in v or "w_007" in v) else 0


def ashe_annual_mean():
    """ASHE table 7.7a (work geography), sheet 'All', column 'Mean', rows UK / GB / E&W.

    Table 7 rows 'United Kingdom' equal table 1.7a 'All employees' (asserted below).
    Returns {year: {'UK':..,'GB':..,'EW':.., 'vintage':.., 'footnote':..}} using the
    preferred vintage per year, and {year: [all vintages]} for the record.
    """
    out, allv = {}, {}
    for tag in ("t7", "t1"):
        for z in sorted(glob.glob(os.path.join(RAW, f"ashe_{tag}", "*.zip"))):
            vint = os.path.basename(z).split("__")[0]
            year = int(vint[:4])
            zf = zipfile.ZipFile(z)
            names = [n for n in zf.namelist() if ".7a" in n and "CV" not in n]
            assert len(names) == 1, (z, names)
            xl = pd.read_excel(io.BytesIO(zf.read(names[0])), sheet_name=None, header=None)
            d = xl["All"]
            title = str(d.iloc[0, 0])
            assert "Annual pay - Gross" in title, (z, title)
            hdr = [i for i in range(min(15, len(d))) if d.iloc[i].astype(str).str.strip().eq("Mean").any()][0]
            mcol = [j for j in range(d.shape[1]) if str(d.iloc[hdr, j]).strip() == "Mean"][0]
            vals = {}
            foot = ""
            for i in range(len(d)):
                lab = str(d.iloc[i, 0]).strip()
                if tag == "t7" and lab in GEO_ROWS:
                    vals[GEO_ROWS[lab]] = float(d.iloc[i, mcol])
                if tag == "t1" and lab.lower() == "all employees":
                    vals["UK_t1"] = float(d.iloc[i, mcol])
                if lab.startswith("a ") or lab.startswith("a  "):
                    foot = lab[1:].strip()
            rec = allv.setdefault(year, {}).setdefault(vint, {})
            rec.update(vals)
            if foot:
                rec["footnote"] = foot
    for year, vs in allv.items():
        for vint, rec in vs.items():
            if "UK" in rec and "UK_t1" in rec:
                assert rec["UK"] == rec["UK_t1"], (year, vint, rec)
        best = max(vs, key=lambda v: (vintage_rank(v), v))
        out[year] = dict(vs[best], vintage=best)
    return out, allv


# ---------------------------------------------------------------- OECD (check)
ISR_CBS = os.path.join(HERE, "..", "..", "..", "israel_apartment_price_vs_wage_1994-2025_CBS.csv")


def oecd_per_employee(area="GBR"):
    d11, sal = {}, {}
    with open(os.path.join(OECD_RAW, "oecd_na_table1_income.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r["REF_AREA"], r["TRANSACTION"], r["SECTOR"], r["ACTIVITY"], r["PRICE_BASE"], r["UNIT_MEASURE"]) == (
                area, "D11", "S1", "_T", "V", "XDC") and r["OBS_VALUE"]:
                d11[int(r["TIME_PERIOD"])] = float(r["OBS_VALUE"]) * 10 ** int(r["UNIT_MULT"])
    with open(os.path.join(OECD_RAW, "oecd_na_table3_empdc.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r["REF_AREA"], r["TRANSACTION"], r["SECTOR"], r["ACTIVITY"], r["UNIT_MEASURE"]) == (
                area, "SAL", "S1", "_T", "PS") and r["OBS_VALUE"]:
                sal[int(r["TIME_PERIOD"])] = float(r["OBS_VALUE"]) * 10 ** int(r["UNIT_MULT"])
    return {y: (d11[y], sal[y], d11[y] / sal[y]) for y in d11 if y in sal}


# ---------------------------------------------------------------- bulletin text
def page_text(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    t = re.sub(r"<script.*?</script>", " ", t, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t)


def bulletin_awe_level(path):
    """'Average weekly earnings (AWE) were estimated at £733 for total earnings ... in August 2025'"""
    m = re.search(r"were estimated at £([\d,]+) for total earnings and £[\d,]+ for regular earnings in (\w+) (\d{4})",
                  page_text(path))
    mon = {"january": "JAN", "february": "FEB", "march": "MAR", "april": "APR", "may": "MAY", "june": "JUN",
           "july": "JUL", "august": "AUG", "september": "SEP", "october": "OCT", "november": "NOV",
           "december": "DEC"}[m.group(2).lower()]
    return int(m.group(3)), mon, float(m.group(1).replace(",", "")), m.group(0)


def main():
    monthly, annual_pub = awe_kab9()
    ashe, ashe_all = ashe_annual_mean()
    oecd = oecd_per_employee()
    checks = []

    # ---- main series
    main_rows, awe_annual = [], {}
    for y in YEARS:
        months = monthly.get(y, {})
        if len(months) == 12:
            wk = sum(months.values()) / 12
            awe_annual[y] = (wk, wk * WEEKS_PER_YEAR)
            main_rows.append([y, round(wk * WEEKS_PER_YEAR), "GBP", "Great Britain",
                              "AWE KAB9 whole economy total pay (incl. bonuses, excl. arrears), SA, "
                              "mean per employee job incl. part-time; calendar-year mean of monthly GBP/week x 52"])
        else:
            main_rows.append([y, "", "GBP", "Great Britain", "not available (fewer than 12 months published)"])
    with open(os.path.join(HERE, "gbr_avg_annual_wage_2000-2025.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "avg_annual_gross_wage_local", "currency", "geography", "concept"])
        w.writerows(main_rows)

    # ---- check 1: our 12-month mean vs ONS's own published annual KAB9 value (rounded to £1/week)
    for y in YEARS:
        if y in awe_annual and y in annual_pub:
            ok = abs(awe_annual[y][0] - annual_pub[y]) <= 0.5 + 1e-9
            checks.append(["awe_annual_vs_ons_published_annual", y, annual_pub[y], round(awe_annual[y][0], 2),
                           "PASS" if ok else "FAIL", "raw/ons_awe_kab9.csv annual row (GBP/week, rounded)"])
    # ---- check 2: monthly level printed in ONS AWE bulletins
    for b in ("ons_awe_bulletin_2025-10.html", "ons_awe_bulletin_2026-09.html"):
        y, mon, printed, quote = bulletin_awe_level(os.path.join(RAW, b))
        ours = monthly[y][mon]
        checks.append([f"awe_{y}_{mon}_vs_bulletin_print", y, printed, ours,
                       "PASS" if ours == printed else f"DIFF {ours - printed:+.0f} (later revision?)",
                       f"raw/{b}: \"{quote}\""])
    # ---- check 3: ASHE 2016 bulletin states its own like-for-like ASHE vs AWE gap (GB, April 2016)
    t = page_text(os.path.join(RAW, "ons_ashe_bulletin_2016.html"))
    m = re.search(r"ASHE estimate of mean gross weekly pay \(excluding bonuses\).*?was £(\d+).*?"
                  r"comparable estimate from the AWE \(regular pay\) was £(\d+)", t)
    a, b_ = float(m.group(1)), float(m.group(2))
    checks.append(["ons_stated_ashe_over_awe_gap_apr2016", 2016, round(a / b_, 4), "",
                   "INFO", f"raw/ons_ashe_bulletin_2016.html: ASHE £{a:.0f} vs AWE regular £{b_:.0f}, GB, April 2016"])

    # ---- comparison table
    comp = []
    for y in YEARS:
        r = {"year": y}
        if y in awe_annual:
            r["awe_kab9_weekly_mean"] = round(awe_annual[y][0], 2)
            r["awe_annual_x52_GB"] = round(awe_annual[y][1])
        if y in ashe:
            a = ashe[y]
            r["ashe_mean_annual_UK"] = a.get("UK", "")
            r["ashe_mean_annual_GB"] = a.get("GB", "")
            r["ashe_mean_annual_EW"] = a.get("EW", "")
            r["ashe_vintage_used"] = a["vintage"]
            r["ashe_other_vintages_UK"] = "; ".join(
                f"{v}={rec.get('UK', rec.get('UK_t1'))}" for v, rec in sorted(ashe_all[y].items()) if v != a["vintage"])
            if a.get("GB") and a.get("EW"):
                r["ashe_EW_over_GB"] = round(a["EW"] / a["GB"], 4)
            if a.get("UK") and y in awe_annual:
                r["ashe_UK_over_awe"] = round(a["UK"] / awe_annual[y][1], 4)
        if y in oecd:
            d11, sal, pe = oecd[y]
            r["oecd_D11_GBP"] = round(d11)
            r["oecd_SAL_persons"] = round(sal)
            r["oecd_D11_per_employee"] = round(pe)
            if y in awe_annual:
                r["ratio_awe_over_oecd"] = round(awe_annual[y][1] / pe, 4)
            if y in ashe and ashe[y].get("UK"):
                r["ratio_ashe_UK_over_oecd"] = round(ashe[y]["UK"] / pe, 4)
            if y in ashe and ashe[y].get("EW"):
                r["ratio_ashe_EW_over_oecd"] = round(ashe[y]["EW"] / pe, 4)
        comp.append(r)
    cols = ["year", "awe_kab9_weekly_mean", "awe_annual_x52_GB", "ashe_mean_annual_UK", "ashe_mean_annual_GB",
            "ashe_mean_annual_EW", "ashe_vintage_used", "ashe_other_vintages_UK", "ashe_EW_over_GB",
            "ashe_UK_over_awe", "oecd_D11_GBP", "oecd_SAL_persons", "oecd_D11_per_employee",
            "ratio_awe_over_oecd", "ratio_ashe_UK_over_oecd", "ratio_ashe_EW_over_oecd"]
    with open(os.path.join(HERE, "gbr_wage_comparison_2000-2025.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(comp)

    # ---- context: the Israeli benchmark's own ratio to the same OECD measure (CBS monthly wage x 12)
    isr = oecd_per_employee("ISR")
    with open(ISR_CBS, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    for row in rows[1:]:
        y = int(row[0])
        if y in (2000, 2007, 2016, 2022) and y in isr:
            checks.append(["context_israel_cbs_wage_x12_over_oecd_isr", y, "", round(float(row[2]) * 12 / isr[y][2], 4),
                           "INFO", "../../../israel_apartment_price_vs_wage_1994-2025_CBS.csv col 3 x12 / OECD ISR D11/SAL"])

    with open(os.path.join(HERE, "gbr_wage_checks.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["check", "year", "expected_published", "ours", "verdict", "source"])
        w.writerows(checks)

    # ---- console summary
    feet = sorted({rec.get("footnote", "") for vs in ashe_all.values() for rec in vs.values()})
    print("ASHE 'All' sheet footnotes seen:", *feet, sep="\n  ")
    print("\nyear  AWE_x52_GB  ASHE_UK  ASHE_EW  OECD/emp  AWE/OECD  ASHE_UK/OECD")
    for r in comp:
        print(r["year"], r.get("awe_annual_x52_GB"), r.get("ashe_mean_annual_UK"), r.get("ashe_mean_annual_EW"),
              r.get("oecd_D11_per_employee"), r.get("ratio_awe_over_oecd"), r.get("ratio_ashe_UK_over_oecd"))
    print("\nchecks:")
    for c in checks:
        if c[4] != "PASS":
            print(" ", c)
    print("  PASS count:", sum(c[4] == "PASS" for c in checks), "of", len(checks))


if __name__ == "__main__":
    main()
