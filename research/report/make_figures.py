"""Build the evidence-file charts from the source files in data/.

Every number plotted is read from a file in data/; nothing is typed in by hand
except the two Bank of Israel reference points and the CBS earners table,
whose sources are named next to them.
"""
import csv
import json
import re
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).parent
DATA = HERE / "data"
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)

font_manager.fontManager.addfont("/System/Library/Fonts/Supplemental/Arial Unicode.ttf")
plt.rcParams.update({
    "font.family": "Arial Unicode MS",
    "font.size": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.dpi": 150,
})

INK = "#1f2a44"
ACCENT = "#c0392b"
MUTED = "#9aa3b5"
TERM = "#f6d365"


def he(text):
    """Hebrew label; matplotlib >= 3.10 applies the bidi algorithm itself, so text stays in logical order."""
    return text


def shade_term(ax, label=True, bars=False):
    """Shade the term years 2003–2007: from the 2003 point to the 2007 point, or around whole bars."""
    x0, x1 = (2002.6, 2007.4) if bars else (2003, 2007)
    ax.axvspan(x0, x1, color=TERM, alpha=0.35, lw=0,
               label=he("כהונת זליכה כחשכ\"ל (2003–2007)") if label else None)


# --- data -------------------------------------------------------------------

def load_ratio():
    rows = list(csv.reader(open(DATA / "israel_apartment_price_vs_wage_1994-2025_CBS.csv", encoding="utf-8-sig")))
    out = {}
    for r in rows[1:]:
        year, price, wage = int(r[0]), float(r[1]), float(r[2])
        out[year] = price / (wage * 12)
    return out


def load_starts():
    """Housing starts in thousands: BoI table B-34 to 1994, CBS series 674272 from 1995."""
    text = subprocess.run(["pdftotext", "-layout", str(DATA / "boi_table_b34_construction_1970-2014.pdf"), "-"],
                          capture_output=True, text=True).stdout
    starts = {}
    for line in text.splitlines():
        nums = re.findall(r"[\d,]+\.?\d*", line)
        if len(nums) >= 10 and re.fullmatch(r"(19|20)\d\d", nums[-1]):
            year = int(nums[-1])
            if year < 1995:
                starts[year] = float(nums[2])          # column: starts, total (thousand dwellings)
    cbs = json.load(open(DATA / "cbs_674272_housing_starts_annual.json"))
    for o in cbs["DataSet"]["Series"][0]["obs"]:
        starts[int(o["TimePeriod"][:4])] = o["Value"] / 1000
    return dict(sorted(starts.items()))


def load_population():
    rows = json.load(open(DATA / "worldbank_population_ISR.json"))[1]
    return {int(r["date"]): r["value"] for r in rows if r["value"]}


def load_oecd():
    out = {}
    for r in csv.DictReader(open(DATA / "oecd_house_prices_ISR.csv", encoding="utf-8-sig")):
        if r["MEASURE"] == "HPI_YDH" and r["FREQ"] == "A":
            out[int(r["TIME_PERIOD"])] = float(r["OBS_VALUE"])
    return dict(sorted(out.items()))


# CBS Statistical Abstract 2008, table 5.26 (Household Expenditure Survey),
# row "Average earners in household" — file data/cbs_shnaton2008_table5_26_household_expenditure.pdf
EARNERS = {1999: 1.19, 2000: 1.20, 2001: 1.18, 2002: 1.16, 2003: 1.17, 2004: 1.18, 2005: 1.20, 2006: 1.22}

# Bank of Israel, Monetary Policy Report Jul–Dec 2013, p. 24, Figure 21 (Sep 2013 = 12.0 salary years);
# "about 8 salary years in mid-2008" as reported by Globes, 2.2.2014 and 1.6.2014.
BOI_POINTS = [(2008.5, 8.0, "בנק ישראל: כ-8 (מחצית 2008)"), (2013.7, 12.0, "בנק ישראל: 12.0 (ספטמבר 2013)")]


def load_policy_rate():
    """Bank of Israel policy rate, daily → annual average (%)."""
    by = {}
    for r in csv.DictReader(open(DATA / "boi_policy_rate_daily_1996-2025.csv", encoding="utf-8")):
        if r["SERIES_CODE"] != "MNT_RIB_BOI_D" or not r["OBS_VALUE"]:   # the file also holds other rate series
            continue
        by.setdefault(int(r["TIME_PERIOD"][:4]), []).append(float(r["OBS_VALUE"]))
    return {y: sum(v) / len(v) for y, v in by.items()}


def load_gdp_growth():
    """Real GDP growth (%), World Bank NY.GDP.MKTP.KD.ZG."""
    rows = json.loads((DATA / "worldbank_gdp_growth_ISR_1996-2010.json").read_text())[1]
    return {int(r["date"]): r["value"] for r in rows if r["value"] is not None}


# --- figures ----------------------------------------------------------------

def fig_ratio(ratio):
    fig, ax = plt.subplots(figsize=(10, 5.2))
    shade_term(ax)
    pre = [y for y in ratio if y <= 2000]
    post = [y for y in ratio if y >= 2000]
    ax.plot(pre, [ratio[y] for y in pre], color=MUTED, lw=2, ls="--",
            label=he("1994–1999: הרחבה, לא בטבלה שנמסרה"))
    ax.plot(post, [ratio[y] for y in post], color=INK, lw=2.6, marker="o", ms=4,
            label=he("הטבלה שנמסרה לגלובס (2000–2025)"))
    for x, y, lab in BOI_POINTS:
        ax.plot(x, y, marker="D", ms=9, color=ACCENT, zorder=5)
        ax.annotate(he(lab), (x, y), xytext=(12, -6) if y < 10 else (14, -14), textcoords="offset points",
                    color=ACCENT, fontsize=11, ha="left", va="top")
    ax.plot([], [], marker="D", ls="", color=ACCENT, label=he("בנק ישראל (כפי שפורסם בגלובס, 2014)"))
    ax.set_ylabel(he("שנות שכר לדירה ממוצעת"))
    ax.set_title(he("מחיר דירה ממוצעת בשנות שכר ממוצע (ברוטו) למשרת שכיר"), loc="right", fontsize=14)
    ax.set_xlim(1993.5, 2025.8)
    ax.legend(loc="upper left", fontsize=10, frameon=False)
    fig.text(0.99, 0.01, he("מקור: למ\"ס, מדד 40010 ושכר למשרת שכיר (סדרות 30014, 45002, 45637, 615908); בנק ישראל"),
             ha="right", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "fig1_ratio.png")
    plt.close(fig)


def fig_yoy(ratio):
    years = [y for y in ratio if y >= 2001]
    chg = [100 * (ratio[y] / ratio[y - 1] - 1) for y in years]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    shade_term(ax, bars=True)
    colors = []
    for y, c in zip(years, chg):
        if c < 0 and 2003 <= y <= 2007:
            colors.append(ACCENT)
        elif c < 0:
            colors.append("#e8a39b")
        else:
            colors.append(MUTED)
    ax.bar(years, chg, color=colors, width=0.75)
    ax.axhline(0, color="#333", lw=0.8)
    ax.set_ylabel(he("שינוי שנתי ביחס מחיר/שכר (%)"))
    ax.set_title(he("שנות ירידה רצופות ביחס מחיר/שכר, 2001–2025"), loc="right", fontsize=14)
    ax.annotate(he("5 שנות ירידה רצופות"), (2005, min(chg[2:7]) - 1), ha="center", color=ACCENT, fontsize=11)
    ax.annotate(he("3 שנים"), (2019, -6.5), ha="center", color="#b5534a", fontsize=10)
    ax.annotate(he("3 שנים"), (2024, -6.5), ha="center", color="#b5534a", fontsize=10)
    ax.set_ylim(-9, 18)
    ax.legend(loc="upper left", fontsize=10, frameon=False)
    fig.text(0.99, 0.01, he("מקור: הטבלה שנמסרה לגלובס (נתוני למ\"ס)"), ha="right", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "fig2_yoy.png")
    plt.close(fig)


def fig_earners():
    years = list(EARNERS)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    shade_term(ax)
    ax.plot(years, [EARNERS[y] for y in years], color=INK, lw=2.6, marker="o")
    for y in years:
        ax.annotate(f"{EARNERS[y]:.2f}", (y, EARNERS[y]), xytext=(0, 8), textcoords="offset points",
                    ha="center", fontsize=10)
    ax.set_ylim(1.12, 1.26)
    ax.set_ylabel(he("מפרנסים למשק בית (ממוצע)"))
    ax.set_title(he("מספר המפרנסים הממוצע במשק בית, 1999–2006"), loc="right", fontsize=14)
    ax.legend(loc="upper left", fontsize=10, frameon=False)
    fig.text(0.99, 0.01, he("מקור: למ\"ס, שנתון סטטיסטי 2008, לוח 5.26 (סקר הוצאות משק הבית)"),
             ha="right", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "fig3_earners.png")
    plt.close(fig)


def fig_starts(starts, pop):
    years = [y for y in starts if y in pop]
    per_k = {y: starts[y] * 1000 / pop[y] * 1000 for y in years}
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 7.5), sharex=True)
    for ax in (a1, a2):
        shade_term(ax, label=(ax is a1))
    a1.plot(years, [starts[y] for y in years], color=INK, lw=2.2)
    a1.set_ylabel(he("אלפי דירות"))
    a1.set_ylim(12, None)
    a1.set_title(he("התחלות בניית דירות, 1970–2025"), loc="right", fontsize=14)
    lo = min((y for y in years if y < 1995), key=lambda y: starts[y])
    a1.annotate(he(f"{lo}: {starts[lo]:.1f} אלף"), (lo, starts[lo]), xytext=(0, -16),
                textcoords="offset points", ha="center", fontsize=10, color=ACCENT)
    a1.annotate(he(f"2004: {starts[2004]:.1f} אלף"), (2004, starts[2004]), xytext=(0, -18),
                textcoords="offset points", ha="center", fontsize=10, color=ACCENT)
    a1.legend(loc="upper left", fontsize=10, frameon=False)
    a2.plot(years, [per_k[y] for y in years], color=INK, lw=2.2)
    a2.set_ylabel(he("לכל 1,000 תושבים"))
    a2.set_title(he("התחלות בנייה לנפש"), loc="right", fontsize=13)
    lo2 = min(years, key=lambda y: per_k[y])
    a2.annotate(he(f"שפל: {lo2} ({per_k[lo2]:.2f})"), (lo2, per_k[lo2]), xytext=(30, 30),
                textcoords="offset points", ha="left", fontsize=10, color=ACCENT,
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=0.8))
    a2.annotate(he(f"1986: {per_k[1986]:.2f}"), (1986, per_k[1986]), xytext=(0, -16),
                textcoords="offset points", ha="center", fontsize=10, color=ACCENT)
    a2.set_ylim(2.5, None)
    fig.text(0.99, 0.005, he("מקור: בנק ישראל, לוח ב'-נ'-34 (1970–1994); למ\"ס סדרה 674272 (1995–2025); אוכלוסייה: הבנק העולמי"),
             ha="right", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    fig.savefig(FIG / "fig4_starts.png")
    plt.close(fig)
    return per_k


def fig_oecd(oecd):
    years = list(oecd)
    fig, ax = plt.subplots(figsize=(9, 4.4))
    shade_term(ax)
    ax.plot(years, [oecd[y] for y in years], color=INK, lw=2.6, marker="o", ms=4)
    ax.set_ylabel(he("מדד (2015 = 100)"))
    ax.set_title(he("OECD: יחס מחיר דירה להכנסה פנויה לנפש, ישראל"), loc="right", fontsize=14)
    ax.legend(loc="upper right", fontsize=10, frameon=False)
    fig.text(0.99, 0.01, he("מקור: OECD, Analytical house price indicators (HPI_YDH)"), ha="right", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "fig5_oecd.png")
    plt.close(fig)


def fig_demand(ratio, starts, pop, rate, gdp):
    """2000–2010: the ratio against the drivers the 'business cycle' story names."""
    years = list(range(2000, 2011))
    fig, axes = plt.subplots(4, 1, figsize=(9, 10), sharex=True)
    panels = [
        (ratio, "שנות שכר לדירה", "מחיר דירה בשנות שכר", ACCENT),
        ({y: starts[y] * 1e6 / pop[y] for y in years}, "לכל 1,000 תושבים", "התחלות בנייה לנפש (ההיצע)", INK),
        (rate, "%", "ריבית בנק ישראל, ממוצע שנתי", INK),
        (gdp, "%", "צמיחת התמ\"ג", INK),
    ]
    for ax, (series, ylab, title, color) in zip(axes, panels):
        shade_term(ax, label=False)
        ax.plot(years, [series[y] for y in years], color=color, lw=2.4, marker="o", ms=4)
        ax.set_ylabel(he(ylab), fontsize=10)
        ax.set_title(he(title), loc="right", fontsize=12)
    axes[-1].axhline(0, color="#555", lw=0.8)
    axes[-1].set_xticks(years)
    fig.suptitle(he("2003–2007: ריבית יורדת, צמיחה חזקה, מעט בנייה — והמחיר בשנות שכר יורד"), x=0.99, ha="right", fontsize=14)
    fig.text(0.99, 0.005, he("מקור: למ\"ס (40010, שכר למשרת שכיר, 674272); בנק ישראל (ריבית); הבנק העולמי (צמיחה, אוכלוסייה)"),
             ha="right", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    fig.savefig(FIG / "fig6_demand.png")
    plt.close(fig)


# Investor purchase tax on a second home: 8% from the first shekel (24.6.2015),
# cut to 5% (Calcalist 12.7.2020), back to 8% (Calcalist 1.11.2021).
TAX_EVENTS = [(2015.48, "6.2015: מס רכישה 8% למשקיעים"), (2020.53, "7.2020: הורדה ל-5%"), (2021.83, "11.2021: חזרה ל-8%")]


def fig_supply_vs_price(ratio, starts):
    years = [y for y in range(1990, 2026) if y in starts]
    pre = [y for y in years if y in ratio and y <= 2000]
    post = [y for y in years if y in ratio and y >= 2000]
    fig, ax = plt.subplots(figsize=(11, 5.4))
    shade_term(ax, bars=True)
    ax.bar(years, [starts[y] for y in years], color=MUTED, width=0.75, label=he("התחלות בנייה (אלפי דירות)"))
    ax.set_ylabel(he("התחלות בנייה, אלפי דירות"))
    ax2 = ax.twinx()
    ax2.plot(pre, [ratio[y] for y in pre], color=ACCENT, lw=2.2, ls="--", marker="o", ms=3,
             label=he("1994–1999: הרחבה, לא בטבלה שנמסרה"))
    ax2.plot(post, [ratio[y] for y in post], color=ACCENT, lw=2.6, marker="o", ms=4, label=he("מחיר דירה בשנות שכר"))
    ax2.set_ylabel(he("שנות שכר לדירה"), color=ACCENT)
    ax2.set_ylim(0, 16.5)
    ax2.spines["right"].set_visible(True)
    ax2.grid(False)
    for k, (x, lab) in enumerate(TAX_EVENTS, 1):
        ax.axvline(x, color=INK, lw=0.9, ls=":")
        ax2.annotate(str(k), (x, 16.1), ha="center", va="center", fontsize=9, color="white",
                     bbox=dict(boxstyle="circle,pad=0.25", fc=INK, ec="none"))
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(0.28, 1.0), fontsize=10, frameon=False)
    ax2.set_ylim(0, 16.8)
    ax.set_title(he("בונים יותר — והדירה לא נעשית זולה יותר, 1990–2025"), loc="right", fontsize=14)
    fig.text(0.99, 0.01, he("מקור: למ\"ס 674272, 40010, שכר למשרת שכיר; מס הרכישה: כלכליסט"),
             ha="right", fontsize=8, color="#555")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "fig7_supply_vs_price.png")
    plt.close(fig)


if __name__ == "__main__":
    ratio = load_ratio()
    starts = load_starts()
    pop = load_population()
    oecd = load_oecd()
    fig_ratio(ratio)
    fig_yoy(ratio)
    fig_earners()
    per_k = fig_starts(starts, pop)
    fig_oecd(oecd)
    fig_demand(ratio, starts, pop, load_policy_rate(), load_gdp_growth())
    fig_supply_vs_price(ratio, starts)

    print("ratio (salary years):", {y: round(v, 2) for y, v in ratio.items()})
    print("declining years:", [y for y in ratio if y - 1 in ratio and ratio[y] < ratio[y - 1]])
    print("lowest starts per 1,000:", sorted(per_k.items(), key=lambda kv: kv[1])[:6])
    print("lowest absolute starts:", sorted(starts.items(), key=lambda kv: kv[1])[:6])
