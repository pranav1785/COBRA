"""Download two public ranking collections and audit complete strict profiles.

No outcome-based filtering is done at download time. Raw data are kept locally.
"""
import itertools
import json
from pathlib import Path
import requests
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data'
OUT.mkdir(exist_ok=True)
summary = []
for collection in ['00006 - skate', '00007 - ers']:
    api = 'https://api.github.com/repos/PrefLib/PrefLib-Data/contents/datasets/' + requests.utils.quote(collection)
    response = requests.get(api, timeout=60)
    response.raise_for_status()
    files = response.json()
    for item in files:
        if not item['name'].endswith('.soc'):
            continue
        path = OUT / item['name']
        if not path.exists():
            downloaded = requests.get(item['download_url'], timeout=60)
            downloaded.raise_for_status()
            path.write_text(downloaded.text, encoding='utf-8')
        lines = path.read_text(encoding='utf-8').splitlines()
        orders = []
        for line in lines:
            if line.startswith('#') or ':' not in line:
                continue
            count, order = line.split(':', 1)
            ranking = [int(x.strip()) for x in order.split(',')]
            orders.append((int(count), ranking))
        if not orders:
            continue
        arms = sorted(orders[0][1])
        index = {a:i for i,a in enumerate(arms)}
        k = len(arms)
        wins = np.zeros((k,k))
        total = sum(c for c,_ in orders)
        for count, ranking in orders:
            assert sorted(ranking) == arms
            for a,b in itertools.combinations(ranking,2):
                wins[index[a],index[b]] += count
        p = wins/total
        np.fill_diagonal(p,.5)
        cw = [i for i in range(k) if all(p[i,j]>.5 for j in range(k) if i!=j)]
        cycles = [(i,j,l) for i,j,l in itertools.combinations(range(k),3)
                  if (p[i,j]>.5 and p[j,l]>.5 and p[l,i]>.5)
                  or (p[j,i]>.5 and p[l,j]>.5 and p[i,l]>.5)]
        scores = (p.sum(1)-.5)/(k-1)
        gaps = np.sort(scores)
        record = dict(file=item['name'],collection=collection,k=k,voters=total,
                      condorcet=cw,cycles=len(cycles),cycle_examples=cycles[:3],
                      borda=int(scores.argmax()),borda_gap=float(gaps[-1]-gaps[-2]),
                      pair_ties=int(sum(p[i,j]==.5 for i,j in itertools.combinations(range(k),2))),
                      source=item['download_url'])
        summary.append(record)
        np.save(OUT / (path.stem+'.npy'),p)
        print(record,flush=True)
(OUT/'audit.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
