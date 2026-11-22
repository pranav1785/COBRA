import concurrent.futures, itertools, json, re
from pathlib import Path
import requests
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'data'
base='https://raw.githubusercontent.com/PrefLib/PrefLib-Data/main/datasets/00007%20-%20ers/'
def fetch(idx):
    name=f'00007-{idx:08d}.soi'; path=D/name
    if not path.exists():
        r=requests.get(base+name,timeout=45)
        if r.status_code!=200:return None
        path.write_text(r.text,encoding='utf-8')
    text=path.read_text(encoding='utf-8'); k=int(re.search(r'# NUMBER ALTERNATIVES: (\d+)',text)[1])
    wins=np.zeros((k,k)); total=0
    for line in text.splitlines():
        if line.startswith('#') or ':' not in line:continue
        c,rank=line.split(':'); c=int(c); rank=[int(x.strip())-1 for x in rank.split(',') if x.strip()]
        pos={a:i for i,a in enumerate(rank)}; total+=c
        for i,j in itertools.combinations(range(k),2):
            a,b=pos.get(i,k),pos.get(j,k)
            w=1 if a<b else 0 if a>b else .5
            wins[i,j]+=c*w; wins[j,i]+=c*(1-w)
    p=wins/total;np.fill_diagonal(p,.5);np.save(D/(path.stem+'.npy'),p)
    b=(p.sum(1)-.5)/(k-1)
    cw=[i for i in range(k) if all(p[i,j]>.5 for j in range(k) if i!=j)]
    cyc=[t for t in itertools.combinations(range(k),3) if (p[t[0],t[1]]>.5 and p[t[1],t[2]]>.5 and p[t[2],t[0]]>.5) or (p[t[1],t[0]]>.5 and p[t[2],t[1]]>.5 and p[t[0],t[2]]>.5)]
    return dict(file=name,k=k,voters=total,cw=cw,cycles=len(cyc),examples=cyc[:5],gap=float(np.sort(b)[-1]-np.sort(b)[-2]),h=float(np.min(np.abs(p[np.triu_indices(k,1)]-.5))),source=base+name)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    results=[r for r in pool.map(fetch,range(1,88)) if r]
(D/'ers_audit.json').write_text(json.dumps(results,indent=2))
print('ERS full-profile no-CW:',[r for r in results if not r['cw']])
