"""Independent rebuild of Israel price/wage ratio from CBS raw files in raw/."""
import json, statistics as st, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
YEARS = [2000, 2007, 2013, 2016, 2022, 2025]

# price index 40010, monthly, base 1993=100
d = json.load(open(f"{R}/price_40010.json"))
idx = {(x["year"], x["month"]): x["currBase"]["value"] for x in d["month"][0]["date"]}
assert all(len([k for k in idx if k[0] == y]) == 12 for y in range(1999, 2026))
ann_idx = {y: st.mean(idx[(y, m)] for m in range(1, 13)) for y in range(1999, 2026)}

# CBS Table 2.2 average dwelling prices (NIS thousand), latest vintage = Price Statistics Monthly 7/2026
AVG = {"2024Q2": 2330.0, "2024Q3": 2270.4, "2024Q4": 2350.9, "2025Q1": 2350.9}
AVG_ANNUAL_PUBLISHED = {2024: 2340.3, 2025: 2330.8}
idx_window = st.mean([idx[(2024, m)] for m in range(4, 13)] + [idx[(2025, m)] for m in range(1, 4)])
nis_per_point = st.mean(AVG.values()) * 1000 / idx_window

def obs(i):
    s = json.load(open(f"{R}/wage_{i}.json"))["DataSet"]["Series"][0]
    return {o["TimePeriod"]: o["Value"] for o in s["obs"]}
w30014, w45002, w45637, w615908 = (obs(i) for i in (30014, 45002, 45637, 615908))
def monthly_mean(o, y): 
    v = [o[f"{y}-{m:02d}"] for m in range(1, 13)]; return st.mean(v)
def wage_m(y):
    if y <= 2001: return monthly_mean(w30014, y)
    if y <= 2003: return monthly_mean(w45002, y)
    if y <= 2010: return w45637[f"{y}-01"]
    return w615908[f"{y}-01"]

print(f"index window mean Apr24-Mar25 = {idx_window:.4f}; avg price mean = {st.mean(AVG.values()):.2f}k; NIS/point = {nis_per_point:.1f}")
print("splice checks: 2004 45002 mean", round(monthly_mean(w45002, 2004), 1), "vs 45637", w45637["2004-01"],
      "| 2011 45637", w45637["2011-01"], "vs 615908", w615908["2011-01"])
print("year,index_mean,price_nis,wage_month,wage_year,ratio")
for y in YEARS:
    p = round(ann_idx[y] * nis_per_point, -2)
    wm = wage_m(y); wy = wm * 12
    print(f"{y},{ann_idx[y]:.3f},{p:.0f},{wm:.1f},{wy:.0f},{p/wy:.2f}")
for y, a in AVG_ANNUAL_PUBLISHED.items():
    print(f"cross-check {y}: CBS published annual avg {a*1000:.0f} vs index-scaled {ann_idx[y]*nis_per_point:.0f} ({(ann_idx[y]*nis_per_point/(a*1000)-1)*100:+.1f}%)")
