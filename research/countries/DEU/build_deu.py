#!/usr/bin/env python3
"""Germany: average price of a dwelling, annual, 2000-2025, EUR.

Reads only raw/. Writes:
  deu_avg_dwelling_price_2000-2025.csv   (year, avg_dwelling_price_local, currency, note)
  deu_workings.csv                       (every intermediate number, per year)

Method
  Level  : AK OGA Immobilienmarktbericht Deutschland 2025, reference year 2024.
           Mean price per transacted dwelling =
             (money turnover Eigenheime + money turnover Eigentumswohnungen)
           / (transactions Eigenheime + transactions Eigentumswohnungen)
           taken from Abb. 4-20 (counts) and Abb. 4-21 (turnover).
  Motion : Destatis Haeuserpreisindex (HPI), GENESIS table 61262-0001, annual average,
           all residential property (new + existing; houses + flats).
  Series : price(y) = level_2024 * HPI(y) / HPI(2024)

Check columns (workings only, not in the main CSV):
  - Destatis annual index vs the mean of the four quarters of table 61262-0002.
  - AK OGA direct mean (turnover / count) 2009-2024, read from the report's time-series
    charts Abb. 4-37, 4-38, 4-68, 4-69 (counts in thousands, turnover in EUR bn, both rounded).
  - AK OGA's own printed national mean for condominiums 2024 (Abb. 4-76, 246.000 EUR)
    against turnover/count for condominiums.

Requires: pdftotext (poppler) on PATH.
"""
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
ANCHOR_YEAR = 2024
YEARS = range(2000, 2026)


# ---------- Destatis GENESIS JSON-stat ----------

def jsonstat_values(path, content_code):
    """Return {(year, quarter-or-None): (value, status)} for one content variable."""
    ds = json.loads(path.read_text())["data"][0]
    ids, sizes, dims = ds["id"], ds["size"], ds["dimension"]
    inv = {}
    for d in ids:
        inv[d] = {v: k for k, v in dims[d]["category"]["index"].items()}
    out = {}
    strides = []
    s = 1
    for n in reversed(sizes):
        strides.insert(0, s)
        s *= n
    for flat, val in enumerate(ds["value"]):
        coord = {}
        rem = flat
        for d, st in zip(ids, strides):
            coord[d] = inv[d][rem // st]
            rem %= st
        if coord["content"] != content_code:
            continue
        status = ds["status"][flat] if "status" in ds else ""
        out[(int(coord["JAHR"]), coord.get("QUARTG"))] = (val, status)
    return out


def base_label(structure_path, var):
    st = json.loads(structure_path.read_text())
    s = json.dumps(st, ensure_ascii=False)
    i = s.find(f'"{var}": {{"label"')
    m = re.search(r'"QMU": \{"label": \{"de": "([^"]+)"', s[i:])
    return m.group(1)


# ---------- AK OGA report text ----------

def pdf_text(path):
    return subprocess.run(["pdftotext", "-layout", str(path), "-"],
                          capture_output=True, text=True, check=True).stdout


def de_num(s):
    return float(s.replace(".", "").replace(",", "."))


def caption_index(lines, caption_prefix):
    hits = [i for i, l in enumerate(lines) if l.strip().startswith(caption_prefix)]
    if not hits:
        sys.exit(f"caption not found: {caption_prefix}")
    return hits[0]


def bar_block(lines, caption_prefix, labels):
    """Read 'label   number (share%)' rows printed just above a bar-chart caption."""
    ci = caption_index(lines, caption_prefix)
    found = {}
    for l in lines[max(0, ci - 12):ci]:
        for lab in labels:
            m = re.match(r"\s*" + re.escape(lab) + r"\s+([\d.,]+)\s+\(", l)
            if m:
                found[lab] = de_num(m.group(1))
    missing = [x for x in labels if x not in found]
    if missing:
        sys.exit(f"{caption_prefix}: missing rows {missing}")
    return found


def germany_row(lines, caption_prefix):
    ci = caption_index(lines, caption_prefix)
    for l in lines[max(0, ci - 25):ci]:
        m = re.match(r"\s*Deutschland\s+([\d.]+)\s*$", l)
        if m:
            return de_num(m.group(1))
    sys.exit(f"{caption_prefix}: no 'Deutschland' row")


def time_series_chart(lines, caption_prefix, first=2009, last=2024):
    """Bar labels of a 2009-2024 chart, ordered left to right by text column.

    Percent labels (year-on-year changes) and the year axis are skipped. The block runs from
    the caption up to the chart title line that ends in 'Vorjahr)'.
    """
    ci = caption_index(lines, caption_prefix)
    j = ci - 1
    while j > 0 and "Vorjahr)" not in lines[j]:
        j -= 1
    vals = []
    for l in lines[j + 1:ci]:
        if re.search(r"\b2009\b", l):
            continue  # x axis
        for m in re.finditer(r"-?\d[\d.,]*%?", l):
            tok = m.group(0)
            if tok.endswith("%"):
                continue
            vals.append((m.start(), de_num(tok)))
    vals.sort()
    n = last - first + 1
    if len(vals) != n:
        sys.exit(f"{caption_prefix}: expected {n} bar labels, read {len(vals)}: {vals}")
    return {first + k: v for k, (_, v) in enumerate(vals)}


def main():
    # Destatis HPI
    ann_path = RAW / "destatis_genesis_61262-0001_HPI_annual_data.json"
    q_path = RAW / "destatis_genesis_61262-0002_HPI_quarterly_data.json"
    base = base_label(RAW / "destatis_genesis_61262-0001_HPI_annual_structure.json", "PRE026")
    hpi_raw = jsonstat_values(ann_path, "PRE026$QMU")
    hpi = {y: v for (y, _), (v, st) in hpi_raw.items()}
    hpi_status = {y: st for (y, _), (v, st) in hpi_raw.items()}
    hpi_q = jsonstat_values(q_path, "PRE026$QMU")
    q_mean = {}
    for y in YEARS:
        qs = [hpi_q.get((y, f"QUART{k}")) for k in range(1, 5)]
        if all(q is not None for q in qs):
            q_mean[y] = sum(q[0] for q in qs) / 4

    # AK OGA 2025 report
    lines = pdf_text(RAW / "akoga_Immobilienmarktbericht_Deutschland_2025.pdf").splitlines()
    cats = ["Eigentumswohnungen", "Eigenheime"]
    n24 = bar_block(lines, "Abb. 4-20:", cats)          # transactions
    eur24 = bar_block(lines, "Abb. 4-21:", cats)        # EUR bn
    etw_printed_mean = germany_row(lines, "Abb. 4-76:")
    eh_n = time_series_chart(lines, "Abb. 4-37:")        # thousand
    eh_eur = time_series_chart(lines, "Abb. 4-38:")      # EUR bn
    etw_n = time_series_chart(lines, "Abb. 4-68:")       # thousand
    etw_eur = time_series_chart(lines, "Abb. 4-69:")     # EUR bn

    # internal consistency: chart 2024 bars == exact 2024 category figures
    assert abs(eh_eur[2024] - eur24["Eigenheime"]) < 1e-9, (eh_eur[2024], eur24)
    assert abs(etw_eur[2024] - eur24["Eigentumswohnungen"]) < 1e-9
    assert abs(etw_n[2024] * 1000 - n24["Eigentumswohnungen"]) < 1e-6
    assert abs(eh_n[2024] * 1000 - n24["Eigenheime"]) <= 500

    level = ((eur24["Eigenheime"] + eur24["Eigentumswohnungen"]) * 1e9
             / (n24["Eigenheime"] + n24["Eigentumswohnungen"]))
    etw_mean_computed = eur24["Eigentumswohnungen"] * 1e9 / n24["Eigentumswohnungen"]

    akoga_direct = {y: (eh_eur[y] + etw_eur[y]) * 1e9 / ((eh_n[y] + etw_n[y]) * 1000)
                    for y in eh_n}

    rows, work = [], []
    for y in YEARS:
        if y not in hpi:
            rows.append([y, "", "EUR", "no Destatis HPI value"])
            continue
        price = level * hpi[y] / hpi[ANCHOR_YEAR]
        note = (f"AK OGA {ANCHOR_YEAR} mean per transacted dwelling ({level:,.0f} EUR) "
                f"x Destatis HPI 61262-0001 ({base}) {hpi[y]}"
                f"/{hpi[ANCHOR_YEAR]}")
        if y < 2014:
            note += "; Destatis: HPI comparable over time only since 2014 (build-up phase before)"
        rows.append([y, round(price), "EUR", note])
        d = akoga_direct.get(y)
        work.append({
            "year": y,
            "hpi_annual": hpi[y],
            "hpi_status": hpi_status[y],
            "hpi_mean_of_quarters": round(q_mean[y], 3) if y in q_mean else "",
            "price_hpi_chained": round(price),
            "akoga_eigenheime_n_thousand": eh_n.get(y, ""),
            "akoga_eigenheime_eur_bn": eh_eur.get(y, ""),
            "akoga_etw_n_thousand": etw_n.get(y, ""),
            "akoga_etw_eur_bn": etw_eur.get(y, ""),
            "akoga_direct_mean_eur": round(d) if d else "",
            "chained_minus_direct_pct": round(100 * (price / d - 1), 1) if d else "",
        })

    out = HERE / "deu_avg_dwelling_price_2000-2025.csv"
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "avg_dwelling_price_local", "currency", "note"])
        w.writerows(rows)
    with (HERE / "deu_workings.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(work[0]))
        w.writeheader()
        w.writerows(work)

    print(f"HPI base: {base}")
    print(f"AK OGA 2024: Eigenheime {n24['Eigenheime']:,.0f} sales / EUR {eur24['Eigenheime']} bn; "
          f"Eigentumswohnungen {n24['Eigentumswohnungen']:,.0f} / EUR {eur24['Eigentumswohnungen']} bn")
    print(f"Anchor level 2024 = {level:,.1f} EUR per dwelling")
    print(f"Check: condo mean computed {etw_mean_computed:,.0f} vs printed (Abb. 4-76) {etw_printed_mean:,.0f}")
    worst = max(abs(hpi[y] - q_mean[y]) for y in q_mean)
    print(f"Check: max |annual HPI - mean of 4 quarters| over {min(q_mean)}-{max(q_mean)} = {worst:.3f} index points")
    if ANCHOR_YEAR + 1 in hpi:
        print(f"Check: HPI {ANCHOR_YEAR + 1} vs {ANCHOR_YEAR}: {100 * (hpi[ANCHOR_YEAR + 1] / hpi[ANCHOR_YEAR] - 1):+.1f}% "
              "(Destatis table page prints +3,2)")
    for r in work:
        print(r["year"], r["hpi_annual"], r["hpi_status"], r["price_hpi_chained"],
              r["akoga_direct_mean_eur"], r["chained_minus_direct_pct"])


if __name__ == "__main__":
    main()
