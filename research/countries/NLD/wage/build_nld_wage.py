"""Netherlands average gross annual wage per employee job, 2000-2025.

Main series: CBS StatLine 85919NED (national accounts, total economy A-U)
    Lonen (mln euro) / Banen van werknemers, voltijd en deeltijd, totaal (x 1 000).
Checks:
    - 85919NED published "Lonen per arbeidsjaar" vs Lonen / Arbeidsjaren recomputed here.
    - 81431ned (Polis-based employment & wages statistics) "Jaarloon inclusief bijzondere
      beloning" per job, total, A-U, 2009-2025.
    - Superseded NA vintages 84165NED (to 2022) and 82578NED (to 2016): per-job wage, same formula.
    - OECD NAMAIN10: D11 (S1, _T, V, XDC) / employees (SAL, S1, _T, PS), domestic concept.
All inputs are read from raw/ exactly as downloaded.
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OECD_RAW = HERE.parents[1] / "wages" / "raw"
YEARS = range(2000, 2026)
CONCEPT = ("Gross wages and salaries (national accounts 'lonen', D11, incl. employee social "
           "contributions, holiday pay, bonuses, in-kind) per average employee job (full- and "
           "part-time, no FTE conversion), total economy A-U, domestic concept; CBS 85919NED")


def annual(path):
    rows = json.load(open(path))["value"]
    return {int(r["Perioden"][:4]): r for r in rows if r["Perioden"].endswith("JJ00")}


def per_job(rows, year):
    r = rows.get(year)
    if not r or r.get("Lonen_2") is None or not r.get("Totaal_27"):
        return None
    return r["Lonen_2"] * 1e6 / (r["Totaal_27"] * 1e3)


def oecd(file, transaction, unit, extra):
    out = {}
    with open(OECD_RAW / file) as fh:
        for r in csv.DictReader(fh):
            if (r["REF_AREA"] == "NLD" and r["TRANSACTION"] == transaction and r["SECTOR"] == "S1"
                    and r["ACTIVITY"] == "_T" and r["UNIT_MEASURE"] == unit
                    and all(r[k] == v for k, v in extra.items()) and r["OBS_VALUE"]):
                y = int(r["TIME_PERIOD"])
                v = float(r["OBS_VALUE"]) * 10 ** int(r["UNIT_MULT"])
                if y in out and out[y] != v:
                    raise ValueError(f"conflicting OECD rows {file} {y}")
                out[y] = v
    return out


def main():
    na = annual(RAW / "cbs_85919NED_total_economy.json")
    polis = annual(RAW / "cbs_81431ned_total.json")
    v2023 = annual(RAW / "cbs_84165NED_total_economy_archived.json")
    v2017 = annual(RAW / "cbs_82578NED_total_economy_archived.json")
    status = {p["Key"][:4]: p["Status"] for p in json.load(open(RAW / "cbs_85919NED_Perioden.json"))["value"]}
    d11 = oecd("oecd_na_table1_income.csv", "D11", "XDC", {"PRICE_BASE": "V"})
    sal = oecd("oecd_na_table3_empdc.csv", "SAL", "PS", {})

    out_rows, check_rows = [], []
    max_fte_dev = 0.0
    for y in YEARS:
        w = per_job(na, y)
        out_rows.append({"year": y, "avg_annual_gross_wage_local": "" if w is None else round(w),
                         "currency": "EUR", "concept": CONCEPT})
        r = na.get(y)
        fte_calc = r["Lonen_2"] / r["Arbeidsjaren_20"] if r else None  # thousand euro
        fte_pub = r["LonenPerArbeidsjaar_9"] if r else None
        if fte_calc is not None:
            max_fte_dev = max(max_fte_dev, abs(fte_calc - fte_pub))
        p = polis.get(y, {}).get("JaarloonInclusiefBijzondereBeloning_6")
        o = d11[y] / sal[y] if y in d11 and y in sal else None
        a = per_job(v2023, y)
        b = per_job(v2017, y)
        check_rows.append({
            "year": y,
            "status_85919NED": status.get(str(y), ""),
            "nld_per_job_85919NED": round(w) if w else "",
            "lonen_per_arbeidsjaar_published_keur": fte_pub,
            "lonen_per_arbeidsjaar_recomputed_keur": round(fte_calc, 2) if fte_calc else "",
            "polis_jaarloon_incl_bijz_81431ned": p if p else "",
            "ratio_na_to_polis": round(w / p, 4) if w and p else "",
            "vintage_84165NED_per_job": round(a) if a else "",
            "vintage_82578NED_per_job": round(b) if b else "",
            "oecd_d11_per_employee_person": round(o) if o else "",
            "ratio_national_to_oecd": round(w / o, 4) if w and o else "",
            "oecd_d11_eur": d11.get(y, ""),
            "cbs_lonen_eur": r["Lonen_2"] * 1e6 if r else "",
        })

    with open(HERE / "nld_avg_annual_wage_2000-2025.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
        wr.writeheader()
        wr.writerows(out_rows)
    with open(HERE / "nld_wage_checks.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(check_rows[0]))
        wr.writeheader()
        wr.writerows(check_rows)

    print(f"max |Lonen/Arbeidsjaren - published Lonen per arbeidsjaar| = {max_fte_dev:.3f} thousand EUR")
    for c in check_rows:
        if c["year"] in (2000, 2007, 2009, 2016, 2022, 2025):
            print(c)


if __name__ == "__main__":
    main()
