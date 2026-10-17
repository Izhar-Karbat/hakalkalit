"""Chart: average dwelling price in years of each country's national average wage, 2000–2025, eight countries, Israel thick.
Reads price_to_wage_2000-2025.csv (run build_ratios.py first). Writes fig_price_to_wage_2000-2025.png."""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "report"))
import make_figures as mf  # noqa: E402  shared fonts and colours
import matplotlib.pyplot as plt  # noqa: E402

NAMES = {"ISR": "ישראל", "ESP": "ספרד", "USA": "ארה\"ב", "CAN": "קנדה", "GBR": "אנגליה ווילס",
         "DEU": "גרמניה", "FRA": "צרפת", "NLD": "הולנד"}
COLORS = {"ESP": "#e69f00", "USA": "#0072b2", "CAN": "#009e73", "GBR": "#cc79a7", "DEU": "#56b4e9",
          "FRA": "#7f7f7f", "NLD": "#d55e00"}

series = {}
for r in csv.DictReader(open(HERE / "price_to_wage_2000-2025.csv", encoding="utf-8")):
    if r["years_of_national_wage"]:
        series.setdefault(r["country"], {})[int(r["year"])] = float(r["years_of_national_wage"])

fig, ax = plt.subplots(figsize=(11, 7))
labels = []
for iso, s in series.items():
    ys = sorted(s)
    if iso == "ISR":
        ax.plot(ys, [s[y] for y in ys], color=mf.ACCENT, lw=5, zorder=5, solid_capstyle="round")
        labels.append((NAMES[iso], s[ys[-1]], dict(color=mf.ACCENT, fontsize=13)))
    else:
        full = range(ys[0], ys[-1] + 1)  # a missing year breaks the line instead of being bridged
        ax.plot(list(full), [s.get(y, float("nan")) for y in full], color=COLORS[iso], lw=1.8, marker="o", ms=2.5)
        labels.append((NAMES[iso], s[ys[-1]], dict(color=COLORS[iso], fontsize=10)))
labels.sort(key=lambda t: t[1])
last = None
for name, y, style in labels:
    y = max(y, last + 0.28) if last is not None else y
    ax.text(2025.3, y, mf.he(name), va="center", ha="left", **style)
    last = y
ax.set_xlim(2000, 2029.5)
ax.set_xticks(range(2000, 2026))
ax.tick_params(axis="x", labelrotation=45)
ax.set_ylim(0, None)
ax.grid(axis="y", color="#e3e6ec", lw=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylabel(mf.he("שנות שכר ממוצע לדירה ממוצעת"))
ax.set_title(mf.he("כמה שנות שכר עולה דירה ממוצעת, 2000–2025: ישראל ושבע מדינות"), loc="right", fontsize=15)
fig.text(0.99, 0.012, mf.he(
    "שכר: הלשכה הלאומית לסטטיסטיקה של כל מדינה, שכר ברוטו ממוצע לשכיר כולל משרות חלקיות. מחיר: מקור רשמי לכל מדינה. הפירוט והמגבלות בקובצי README.\n"
    "ארה\"ב: דירות חדשות בלבד; הולנד: יד שנייה בלבד; קנדה: איגוד המתווכים; ספרד: אין נתון ל-2005."), ha="right", fontsize=7.5, color="#555")
fig.tight_layout(rect=(0, 0.05, 1, 1))
out = HERE / "fig_price_to_wage_2000-2025.png"
fig.savefig(out, dpi=200)
fig.savefig(mf.FIG / "fig9_countries.png", dpi=200)  # the copy the statement page inlines
print("wrote", out, "and", mf.FIG / "fig9_countries.png")
