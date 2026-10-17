"""Blind verification: Germany price / wage / ratio.
Price 2024 = AK OGA IMB 2025 (Abb. 4-20/4-21): (Eigenheime + Eigentumswohnungen) Geldumsatz / Transaktionen.
Other years = 2024 level x HPI(y)/HPI(2024), Destatis 61262-0001 (PRE026, 2025=100).
Wage = Destatis 81000-0017 VST038 (gross wages & salaries per employee, domestic concept), total economy.
Cross-check: AK OGA IMB 2015 means per sale for 2012/2013 (Abb. 3-49/3-50/3-68/3-71)."""
import json, os
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")

def cube(fn):
    d = json.load(open(os.path.join(RAW, fn)))["data"][0]
    return d

def get(d, coords):
    idx = 0
    for dim, size in zip(d["id"], d["size"]):
        idx = idx * size + (d["dimension"][dim]["category"]["index"][coords[dim]] if dim in coords else 0)
    return d["value"][idx], d["status"][idx]

hpi = cube("genesis_61262-0001_data.json")
wag = cube("genesis_81000-0017_data.json")
H = lambda y: get(hpi, {"content": "PRE026$QMU", "JAHR": str(y)})
W = lambda y: get(wag, {"content": "VST038$QMU", "WZ08G2": "%TOTAL%", "JAHR": str(y)})

# AK OGA IMB 2025, p.37 Abb. 4-20 / 4-21 (2024)
EH_n, ETW_n = 252_900, 255_600
EH_eur, ETW_eur = 84.3e9, 62.9e9
anchor = (EH_eur + ETW_eur) / (EH_n + ETW_n)
print(f"anchor 2024 = {anchor:,.0f} EUR  (EH {EH_eur/EH_n:,.0f}, ETW {ETW_eur/ETW_n:,.0f})")

rows = []
for y in [2000, 2007, 2013, 2016, 2022, 2024, 2025]:
    h, hs = H(y); w, ws = W(y)
    p = anchor * h / H(2024)[0]
    rows.append((y, p, w, p / w))
    print(f"{y}  HPI {h:6.1f}{hs}  price {p:>10,.0f}  wage {w:>8,.0f}{ws}  ratio {p/w:5.2f}")

# independent AK OGA mean-per-sale levels (IMB 2015) vs index-chained
for y, eh_e, eh_n, etw_e, etw_n in [(2012, 43.7e9, 233e3, 41.5e9, 283.8e3), (2013, 44.5e9, 236e3, 45.8e9, 287.9e3)]:
    direct = (eh_e + etw_e) / (eh_n + etw_n)
    chained = anchor * H(y)[0] / H(2024)[0]
    print(f"check {y}: AK OGA direct {direct:,.0f} vs chained {chained:,.0f}  ({chained/direct-1:+.1%})")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_DEU.csv"), "w") as f:
    f.write("year,price_eur,wage_eur,ratio\n")
    for y, p, w, r in rows:
        f.write(f"{y},{p:.0f},{w:.0f},{r:.3f}\n")

# Eigenheime-only, 2007 (IMB 2015 Abb. 3-49/3-50; 2007 coverage flagged limited by AK OGA)
eh07 = 31.5e9 / 179e3
eh_ch = (EH_eur / EH_n) * H(2007)[0] / H(2024)[0]
print(f"check 2007 Eigenheime only: direct {eh07:,.0f} vs chained {eh_ch:,.0f} ({eh_ch/eh07-1:+.1%})")
