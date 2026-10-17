"""Independent rebuild of Spain price/wage ratio from raw/ (BdE si_1_5, INE ETCL 11221, Registradores ERI yearbooks)."""
import csv, json, os, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw')
YEARS = [2000, 2007, 2013, 2016, 2022, 2025]
# National average constructed m2 of dwellings in registered sales, "General", quoted from each ERI Anuario's own text
SURF = {2007: 100.36,   # ERI_Anuario_2007.pdf, sec. superficie media: "se ha situado en los 100,36 m²"
        2013: 97.97,    # ERI_Anuario_2013.pdf: "durante el año 2013 ha sido de 97,97 m²"
        2016: 97.73,    # ERI_Anuario_2016.pdf: "situándose en los 97,73 m²"
        2022: 100.5,    # ERI_Anuario_2022.pdf, sec. 8 headline "General 100,5"
        2025: 100.6}    # ERI_Anuario_2025.pdf, sec. 8 headline "General 100,6"
rows = list(csv.reader(open(os.path.join(R, 'bde_si_1_5.csv'), encoding='latin-1')))
i = rows[0].index('DHIVTNOAPLPMMUVT_RLI.T')
pm2 = {}
for r in rows:
    p = r[0].split()
    if len(p) == 2 and p[1].isdigit() and r[i].strip() not in ('', '_'):
        pm2.setdefault(int(p[1]), []).append(float(r[i]))
d = json.load(open(os.path.join(R, 'ine_11221.json')))
s = [x for x in d if x['COD'] == 'ETCL13724'][0]
assert 'no ajustados' in s['Nombre'] and 'Coste salarial total' in s['Nombre']
wq = {}
for o in s['Data']:
    wq.setdefault(o['Anyo'], []).append(o['Valor'])
print('year,pm2_mean,n_q,surface_m2,price,wage_month_mean,n_q,wage_annual,ratio')
for y in YEARS:
    pq, w = pm2.get(y, []), wq.get(y, [])
    pmean = sum(pq)/len(pq) if len(pq) == 4 else None
    wa = sum(w)/len(w)*12 if len(w) == 4 else None
    price = pmean*SURF[y] if (pmean and y in SURF) else None
    ratio = price/wa if (price and wa) else None
    f = lambda v, n=1: '' if v is None else f'{v:.{n}f}'
    print(f'{y},{f(pmean,2)},{len(pq)},{SURF.get(y,"")},{f(price,0)},{f(sum(w)/len(w) if w else None,2)},{len(w)},{f(wa,0)},{f(ratio,2)}')
