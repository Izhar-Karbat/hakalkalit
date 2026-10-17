#!/usr/bin/env python3
"""France: average price of a dwelling, annual, 2000-2025, EUR.

Reads only raw/. Writes:
  fra_avg_dwelling_price_2000-2025.csv   (the series)
  fra_dvf_direct_means_2021-2025.csv     (check: actual DVF means per year)

Method
  Level  = mean sale price of single-dwelling sales in DVF (DGFiP, via Etalab geo-DVF),
           metropolitan France, ANCHOR_YEAR.
  Path   = INSEE house price index, new + second-hand dwellings, metropolitan France,
           raw (not seasonally adjusted), base 2015, idbank 010001868; annual = mean of 4 quarters.
  Value_y = Level_anchor * I_y / I_anchor.
"""
import csv
import gzip
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
ANCHOR_YEAR = 2024
INDEX_ID = "010001868"          # IPLNA, new + second-hand, France metropolitaine, raw, 2015=100
CHECK_IDS = ("010001869", "010567058")  # new-only, second-hand-only (raw)
DVF_YEARS = range(2021, 2026)
SALE_NATURES = {"Vente", "Vente en l'état futur d'achèvement"}
DWELLING_TYPES = {"Maison", "Appartement"}
ALLOWED_TYPES = DWELLING_TYPES | {"Dépendance"}
PRICE_MIN, PRICE_MAX = 10_000.0, 10_000_000.0


def read_insee_series(path):
    """Return {idbank: {'YYYY-Qn': value}} from an INSEE BDM SDMX StructureSpecific file."""
    text = open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"<Series ([^>]*)>(.*?)</Series>", text, re.S):
        idb = re.search(r'IDBANK="(\d+)"', m.group(1)).group(1)
        obs = {}
        for o in re.finditer(r"<Obs ([^>]*)/>", m.group(2)):
            a = dict(re.findall(r'(\w+)="([^"]*)"', o.group(1)))
            if a.get("OBS_VALUE") not in (None, "", "NaN"):
                obs[a["TIME_PERIOD"]] = float(a["OBS_VALUE"])
        out[idb] = obs
    return out


def annual_means(q):
    """Annual mean of quarters; a year is kept only if all four quarters exist."""
    years = {}
    for k, v in q.items():
        years.setdefault(int(k[:4]), []).append(v)
    return {y: sum(v) / 4 for y, v in years.items() if len(v) == 4}


def dvf_year(path):
    """Mean / median price of single-dwelling sales, metropolitan France, from one geo-DVF year file."""
    muts = {}
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            m = muts.get(row["id_mutation"])
            if m is None:
                m = muts[row["id_mutation"]] = {
                    "nat": row["nature_mutation"], "dep": row["code_departement"],
                    "vals": set(), "types": set(), "dw": set(), "vefa": False}
            m["vals"].add(row["valeur_fonciere"])
            t = row["type_local"]
            if t:
                m["types"].add(t)
            if t in DWELLING_TYPES:
                # one dwelling can appear on several rows (one per land-use line): dedupe
                m["dw"].add((row["id_parcelle"], t, row["surface_reelle_bati"],
                             row["nombre_pieces_principales"], row["lot1_numero"]))
    kept, raw_all = [], []
    n_new = 0
    for m in muts.values():
        if m["nat"] not in SALE_NATURES or m["dep"].startswith("97"):
            continue
        if len(m["dw"]) != 1 or (m["types"] - ALLOWED_TYPES):
            continue
        if len(m["vals"]) != 1:
            continue
        v = next(iter(m["vals"]))
        if not v:
            continue
        p = float(v)
        raw_all.append(p)
        if PRICE_MIN <= p <= PRICE_MAX:
            kept.append(p)
            n_new += m["nat"] != "Vente"
    kept.sort()
    n = len(kept)
    med = kept[n // 2] if n % 2 else (kept[n // 2 - 1] + kept[n // 2]) / 2
    return {"n": n, "mean": sum(kept) / n, "median": med,
            "n_unfiltered": len(raw_all), "mean_unfiltered": sum(raw_all) / len(raw_all),
            "n_vefa": n_new}


def main():
    s = read_insee_series(os.path.join(RAW, "insee_bdm_series_010001868_010567058_010001869.xml"))
    idx = annual_means(s[INDEX_ID])

    dvf = {}
    for y in DVF_YEARS:
        dvf[y] = dvf_year(os.path.join(RAW, "dvf", f"geo_dvf_full_{y}.csv.gz"))
        print(y, {k: round(v) for k, v in dvf[y].items()}, file=sys.stderr)

    level = dvf[ANCHOR_YEAR]["mean"]
    factor = level / idx[ANCHOR_YEAR]

    out = os.path.join(HERE, "fra_avg_dwelling_price_2000-2025.csv")
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "avg_dwelling_price_local", "currency", "note"])
        for y in range(2000, 2026):
            if y not in idx:
                w.writerow([y, "", "EUR", "no full year of INSEE index 010001868"])
                continue
            note = (f"DVF {ANCHOR_YEAR} mean single-dwelling sale price {level:.0f} EUR x "
                    f"INSEE 010001868 annual mean {idx[y]:.2f} / {idx[ANCHOR_YEAR]:.2f}; "
                    "metropolitan France, new+existing, constant-quality path")
            if y == ANCHOR_YEAR:
                note = f"ANCHOR: DVF {y} mean single-dwelling sale price, metropolitan France (excl. Alsace-Moselle), n={dvf[y]['n']}"
            w.writerow([y, round(factor * idx[y]), "EUR", note])

    chk = os.path.join(HERE, "fra_dvf_direct_means_2021-2025.csv")
    with open(chk, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "n_sales", "n_vefa", "dvf_mean_eur", "dvf_median_eur",
                    "dvf_mean_unfiltered_eur", "n_unfiltered", "index_path_eur", "dvf_vs_index_path_pct"])
        for y in DVF_YEARS:
            d = dvf[y]
            ip = factor * idx[y]
            w.writerow([y, d["n"], d["n_vefa"], round(d["mean"]), round(d["median"]),
                        round(d["mean_unfiltered"]), d["n_unfiltered"], round(ip),
                        f"{100 * (d['mean'] / ip - 1):.1f}"])

    # Check against INSEE Informations Rapides n°224 (18 Sept 2026): year-on-year change, raw data, 2026 Q2
    for idb, printed in (("010001868", -0.8), ("010001869", 0.0), ("010567058", -0.8)):
        q = s[idb]
        yoy = 100 * (q["2026-Q2"] / q["2025-Q2"] - 1)
        print(f"check {idb}: 2026-Q2 yoy raw = {yoy:.2f}% (release prints {printed:+.1f}%)", file=sys.stderr)


if __name__ == "__main__":
    main()
