"""Blind recomputation: NLD dwelling price / gross wage per employee job, CBS StatLine."""
import json, sys
from pathlib import Path
R = Path(__file__).resolve().parent / "raw"
YEARS = [2000, 2007, 2013, 2016, 2022, 2025]
p = {r["Perioden"]: r for r in json.load(open(R / "85773NED_TypedDataSet.json"))["value"]}
w = {r["Perioden"]: r for r in json.load(open(R / "85919NED_TypedDataSet.json"))["value"]
     if r["BedrijfstakkenBranchesSBI2008"].strip() == "T001081"}
print("year,price_eur,lonen_mln,jobs_k,wage_per_job_eur,ratio,lonen_per_arbeidsjaar_k,arbeidsjaren_k,ratio_fte")
for y in YEARS:
    k = f"{y}JJ00"
    price = p[k]["GemiddeldeVerkoopprijs_7"]
    L = w[k]["Lonen_2"]; jobs = w[k]["Totaal_27"]
    wage = L * 1e6 / (jobs * 1e3)
    fte = w[k]["LonenPerArbeidsjaar_9"]
    print(f"{y},{price},{L},{jobs},{wage:.0f},{price/wage:.3f},{fte},{w[k]['Arbeidsjaren_20']},{price/(fte*1000):.3f}")
