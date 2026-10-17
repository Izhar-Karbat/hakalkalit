"""Blind verification of France price/wage ratio (DVF 2024 level x INSEE HPI; INSEE NA wage)."""
import csv, gzip, re, sys, os, collections, json
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, "raw")

def insee(idb):
    t = open(os.path.join(RAW, f"insee_{idb}.xml")).read()
    return {m.group(1): float(m.group(2)) for m in re.finditer(r'TIME_PERIOD="([^"]+)" OBS_VALUE="([^"]+)"', t)}

def dvf_variants():
    muts = collections.defaultdict(lambda: {"val": None, "nature": None, "dep": None, "dw_rows": 0, "dw_keys": set(), "other_local": 0})
    with gzip.open(os.path.join(RAW, "geodvf_2024_full.csv.gz"), "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            m = muts[r["id_mutation"]]
            m["nature"] = r["nature_mutation"]; m["dep"] = r["code_departement"]
            if r["valeur_fonciere"]: m["val"] = float(r["valeur_fonciere"])
            if r["code_type_local"] in ("1", "2"):
                m["dw_rows"] += 1
                m["dw_keys"].add((r["id_parcelle"], r["lot1_numero"], r["code_type_local"], r["surface_reelle_bati"], r["nombre_pieces_principales"]))
            elif r["code_type_local"] == "4":
                m["other_local"] += 1
    out = {}
    def agg(name, pred):
        v = [m["val"] for m in muts.values() if pred(m)]
        v.sort(); n = len(v)
        out[name] = {"n": n, "mean": sum(v) / n, "median": v[n // 2]}
    metro = lambda m: not m["dep"].startswith("97")
    band = lambda m: m["val"] is not None and 10_000 <= m["val"] <= 10_000_000
    agg("A Vente, 1 dwelling row, metro, 10k-10M", lambda m: m["nature"] == "Vente" and m["dw_rows"] == 1 and metro(m) and band(m))
    agg("B Vente, 1 distinct dwelling (dedup), metro, band", lambda m: m["nature"] == "Vente" and len(m["dw_keys"]) == 1 and metro(m) and band(m))
    agg("C as A + no commercial local", lambda m: m["nature"] == "Vente" and m["dw_rows"] == 1 and m["other_local"] == 0 and metro(m) and band(m))
    agg("D Vente+VEFA, 1 dwelling row, metro, band", lambda m: m["nature"] in ("Vente", "Vente en l'état futur d'achèvement") and m["dw_rows"] == 1 and metro(m) and band(m))
    agg("E as A incl. DOM", lambda m: m["nature"] == "Vente" and m["dw_rows"] == 1 and band(m))
    return out

if __name__ == "__main__":
    hpi = insee("010001868"); d11 = insee("011785411"); emp = insee("011793486")
    ann = {y: sum(hpi[f"{y}-Q{q}"] for q in range(1, 5)) / 4 for y in range(2000, 2026)}
    v = dvf_variants()
    for k, s in v.items(): print(f"{k}: n={s['n']} mean={s['mean']:.0f} median={s['median']:.0f}")
    lvl = v["A Vente, 1 dwelling row, metro, 10k-10M"]["mean"]
    print(f"HPI 2024 annual mean (unrounded) = {ann[2024]:.3f}")
    rows = []
    for y in (2000, 2007, 2013, 2016, 2022, 2025):
        p = lvl * ann[y] / ann[2024]
        w = d11[str(y)] * 1e6 / (emp[str(y)] * 1e3)
        rows.append((y, p, w, p / w)); print(f"{y}  HPI={ann[y]:.2f}  price={p:,.0f}  wage={w:,.0f}  ratio={p/w:.2f}")
    with open(os.path.join(HERE, "verify_FRA_results.csv"), "w") as f:
        f.write("year,price,wage,ratio\n"); [f.write(f"{y},{p:.0f},{w:.0f},{r:.3f}\n") for y, p, w, r in rows]
