"""France average gross annual wage per employee (persons), 2000-2025, from INSEE annual national accounts (base 2020).

wage = D11 salaires et traitements bruts, total des branches (BDM idbank 011785411, M EUR)
       / emploi interieur salarie, personnes physiques (BDM idbank 011793486, thousands)

Every number is read from the files in raw/. Outputs:
  fra_avg_annual_wage_2000-2025.csv   the series
  fra_wage_checks.csv                 publication-table check, FTE alternative, OECD comparison
"""
import csv
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import openpyxl
import pypdf

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OECD_RAW = HERE.parents[1] / "wages" / "raw"
YEARS = range(2000, 2026)
CONCEPT = ("SMPT-type: INSEE national accounts D11 gross wages and salaries (total economy, domestic) / "
           "domestic salaried employment in persons (annual average, part-time counted as one head); "
           "France entiere incl. overseas departments; current EUR")


def bdm_series(name):
    """Return ({year: value}, {year: OBS_STATUS}, series attributes) from a BDM SDMX-ML file."""
    root = ET.parse(RAW / name).getroot()
    series = [e for e in root.iter() if e.tag.endswith("Series")]
    assert len(series) == 1, f"{name}: expected one series, got {len(series)}"
    s = series[0]
    vals, status = {}, {}
    for o in s:
        if o.tag.endswith("Obs") and o.get("OBS_VALUE") not in (None, "", "NaN"):
            y = int(o.get("TIME_PERIOD"))
            vals[y] = float(o.get("OBS_VALUE")) * 10 ** int(s.get("UNIT_MULT", "0"))
            status[y] = o.get("OBS_STATUS")
    return vals, status, dict(s.attrib)


def insee_table_total(name, unit_factor):
    """Return {year: value} of the '_T Total' row of an INSEE CNA publication table (sheet 'en niveau')."""
    wb = openpyxl.load_workbook(RAW / name, read_only=True, data_only=True)
    rows = list(wb.worksheets[1].iter_rows(values_only=True))
    hdr = next(r for r in rows if r[2] is not None and str(r[2]).isdigit())
    tot = next(r for r in rows if r[0] == "_T")
    return {int(hdr[i]): tot[i] * unit_factor for i in range(2, len(hdr))
            if hdr[i] and str(hdr[i]).isdigit() and tot[i] is not None}


def ip2079_gross_fte_monthly_2024():
    """Insee Premiere 2079, table 1, row 'Ensemble': first number = mean gross monthly wage in FTE, private sector, 2024."""
    text = " ".join(p.extract_text() for p in pypdf.PdfReader(RAW / "ip2079.pdf").pages)
    text = " ".join(text.split())
    m = re.search(r"Tertiaire [\d ,]+? Ensemble (\d) ?(\d{3}) ", text)
    assert m, "row 'Ensemble' not found in ip2079.pdf"
    return float(m.group(1) + m.group(2))


def oecd(path, want):
    """Return {year: value * 10^UNIT_MULT} for REF_AREA=FRA rows matching the `want` dimension values."""
    out = {}
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            if r["REF_AREA"] != "FRA" or r["FREQ"] != "A":
                continue
            if all(r.get(k) == v for k, v in want.items()) and r["OBS_VALUE"]:
                y = int(r["TIME_PERIOD"])
                assert y not in out, f"duplicate OECD row {path.name} {y}"
                out[y] = float(r["OBS_VALUE"]) * 10 ** int(r["UNIT_MULT"])
    return out


def main():
    d11, d11_st, d11_attr = bdm_series("insee_cna2020_cpeb_D11_total.xml")
    pp, pp_st, pp_attr = bdm_series("insee_cna2020_emploi_salarie_pp.xml")
    etp, _, etp_attr = bdm_series("insee_cna2020_emploi_salarie_etp.xml")
    # Units: D11 in millions of euros (UNIT_MULT=6), employment in thousands of persons.
    assert d11_attr["IDBANK"] == "011785411" and d11_attr["UNIT_MEASURE"] == "EUROS_COURANTS"
    assert pp_attr["IDBANK"] == "011793486" and pp_attr["UNIT_MEASURE"] == "MILLIERS_ACTIFS_OCCUPES_PP"
    assert etp_attr["IDBANK"] == "011793487"
    pp = {y: v * 1000 for y, v in pp.items()}
    etp = {y: v * 1000 for y, v in etp.items()}

    wage = {y: d11[y] / pp[y] for y in YEARS if y in d11 and y in pp}

    with open(HERE / "fra_avg_annual_wage_2000-2025.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "avg_annual_gross_wage_local", "currency", "concept"])
        for y in YEARS:
            w.writerow([y, f"{wage[y]:.0f}" if y in wage else "", "EUR", CONCEPT])

    # Check 1: published INSEE tables 6.205 (D11, bn EUR) and 6.210 (salaried persons, thousands)
    t6205 = insee_table_total("T_6205_fr.xlsx", 1e9)
    t6210 = insee_table_total("T_6210_fr.xlsx", 1e3)
    t6211 = insee_table_total("T_6211_fr.xlsx", 1e3)
    # Check 2: Insee Premiere 2079 private-sector gross FTE wage 2024 (monthly)
    ip_month = ip2079_gross_fte_monthly_2024()
    # Check 3: OECD D11 / SAL persons
    o_d11 = oecd(OECD_RAW / "oecd_na_table1_income.csv",
                 {"TRANSACTION": "D11", "SECTOR": "S1", "ACTIVITY": "_T", "PRICE_BASE": "V", "UNIT_MEASURE": "XDC"})
    o_sal = oecd(OECD_RAW / "oecd_na_table3_empdc.csv",
                 {"TRANSACTION": "SAL", "SECTOR": "S1", "ACTIVITY": "_T", "UNIT_MEASURE": "PS"})

    with open(HERE / "fra_wage_checks.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "wage_per_head", "d11_bdm", "d11_table6205", "employees_pp_bdm", "employees_pp_table6210",
                    "obs_status_d11", "obs_status_emp", "wage_per_fte_bdm", "employees_fte_table6211",
                    "oecd_d11", "oecd_sal_persons", "oecd_wage_per_head", "ratio_insee_over_oecd"])
        for y in YEARS:
            ow = o_d11[y] / o_sal[y] if y in o_d11 and y in o_sal else None
            w.writerow([y, f"{wage[y]:.2f}", f"{d11[y]:.0f}", f"{t6205[y]:.0f}" if y in t6205 else "",
                        f"{pp[y]:.0f}", f"{t6210[y]:.0f}" if y in t6210 else "",
                        d11_st[y], pp_st[y], f"{d11[y] / etp[y]:.2f}", f"{t6211[y]:.0f}" if y in t6211 else "",
                        f"{o_d11[y]:.0f}" if y in o_d11 else "", f"{o_sal[y]:.0f}" if y in o_sal else "",
                        f"{ow:.2f}" if ow else "", f"{wage[y] / ow:.4f}" if ow else ""])

    print("year  wage/head   wage/FTE   D11 vs T6205   emp vs T6210   OECD/head   ratio")
    for y in YEARS:
        ow = o_d11[y] / o_sal[y] if y in o_d11 and y in o_sal else None
        print(f"{y}  {wage[y]:9.0f}  {d11[y] / etp[y]:9.0f}  {d11[y] - t6205.get(y, float('nan')):+12.0f}"
              f"  {pp[y] - t6210.get(y, float('nan')):+12.0f}  {ow or float('nan'):10.0f}"
              f"  {(wage[y] / ow) if ow else float('nan'):.4f}")
    print(f"\nIP2079 private-sector gross FTE 2024: {ip_month:.0f} EUR/month = {12 * ip_month:.0f} EUR/yr; "
          f"national-accounts per head 2024 = {wage[2024]:.0f}; per FTE 2024 = {d11[2024] / etp[2024]:.0f}")


if __name__ == "__main__":
    main()
