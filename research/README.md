# The research behind the page

This folder holds the code, the source links and the data behind the page at
https://izhar-karbat.github.io/hakalkalit/ . Every number on the page can be rebuilt from here.

## What is where

| Path | What it builds |
|---|---|
| `rebuild_from_cbs.py` | Israel: the table of apartment price in years of salary, 1994–2025, straight from the CBS API. Runs on its own (Python 3 and curl). |
| `report/make_figures.py` | The charts on the page. |
| `report/data/israel_apartment_price_vs_wage_1994-2025_CBS.csv` | The Israel table those scripts produce. |
| `countries/<ISO>/` | One country's average dwelling price, 2000–2025: `build_<iso>.py`, the result CSV, `README.md` (method and known limits), `SOURCES.csv` (every raw file and the exact link it was downloaded from), `raw/`. |
| `countries/<ISO>/wage/` | The same country's average gross wage, from its national statistics bureau, with the same files. |
| `spain/` | Spain, built the same way (price, dwelling size and wage). |
| `countries/build_ratios.py` | Joins every country's price and wage into `countries/price_to_wage_2000-2025.csv`. |
| `countries/fig_price_to_wage.py` | The chart "Israel and seven countries". |
| `countries/_verify/<ISO>/VERIFICATION.md` | An independent rebuild of each country: the sources were found and the numbers computed again without looking at ours, then compared. Every country matched; the reports list the points a critic could raise. |
| `countries/wages/` | OECD wage files that were checked and not used (see the page). |
| `yaron_2003/` | Zelekha's own documents on the March 2003 economic plan (his 1.3.2003 paper and a November 2002 lecture), with their file dates and a comparison with the government plan. |

Countries: ISR (Israel), ESP (Spain), USA, CAN (Canada), GBR (England and Wales for prices), DEU (Germany), FRA (France), NLD (Netherlands).

## Large files are not stored here

Raw files over 5 MB (the land-registry files of England and France, some statistical-office archives) are left out to keep the repository small.
`LARGE_FILES_NOT_INCLUDED.csv` lists each one with the link it came from. Download them into the same path and the scripts run unchanged.

## Rebuild

```
cd research
python3 rebuild_from_cbs.py                 # Israel, live from the CBS
python3 countries/<ISO>/build_<iso>.py       # one country's prices (needs its raw/ files)
python3 countries/<ISO>/wage/build_<iso>_wage.py
python3 spain/build_spain_ratio.py
python3 countries/build_ratios.py            # the joined table
```

Found a mistake? Report it through the button at the bottom of the page.
