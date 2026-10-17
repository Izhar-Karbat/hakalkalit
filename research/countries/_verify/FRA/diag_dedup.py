import csv,gzip,collections,sys,statistics as st
M=collections.defaultdict(list)
with gzip.open("raw/geodvf_2024_full.csv.gz","rt",encoding="utf-8") as f:
    for r in csv.DictReader(f):
        M[r["id_mutation"]].append(r)
DW={"Maison","Appartement"}; OK=DW|{"Dépendance"}
def ours(rows):
    r0=rows[0]
    if r0["nature_mutation"] not in ("Vente","Vente en l'état futur d'achèvement") or r0["code_departement"].startswith("97"): return None
    dw={(r["id_parcelle"],r["type_local"],r["surface_reelle_bati"],r["nombre_pieces_principales"],r["lot1_numero"]) for r in rows if r["type_local"] in DW}
    types={r["type_local"] for r in rows if r["type_local"]}
    vals={r["valeur_fonciere"] for r in rows}
    if len(dw)!=1 or types-OK or len(vals)!=1: return None
    v=next(iter(vals)); 
    if not v: return None
    p=float(v); return p if 1e4<=p<=1e7 else None
kept={k:ours(v) for k,v in M.items()}; kept={k:p for k,p in kept.items() if p is not None}
ps=sorted(kept.values()); print("ours-filter repro: n",len(ps),"mean",round(sum(ps)/len(ps)),"median",ps[len(ps)//2])
# split: dwelling appears on 1 row vs several rows
one=[p for k,p in kept.items() if sum(r["type_local"] in DW for r in M[k])==1]
multi=[k for k in kept if sum(r["type_local"] in DW for r in M[k])>1]
print("single-row dwelling: n",len(one),"mean",round(st.mean(one)))
mp=[kept[k] for k in multi]; print("multi-row dwelling: n",len(mp),"mean",round(st.mean(mp)))
# do multi-row duplicates differ only by culture?
diffcult=sum(1 for k in multi if len({r["nature_culture"] for r in M[k] if r["type_local"] in DW})>1)
print("multi-row where dwelling rows differ in nature_culture:",diffcult)
ex=multi[:3]
for k in ex:
    for r in M[k]: print(k,r["type_local"],r["id_parcelle"],r["lot1_numero"],r["surface_reelle_bati"],r["nature_culture"],r["surface_terrain"],r["valeur_fonciere"])
# without lot1 in key: how many mutations with >1 dwelling become 1
def key2(rows): return {(r["id_parcelle"],r["type_local"],r["surface_reelle_bati"],r["nombre_pieces_principales"]) for r in rows if r["type_local"] in DW}
