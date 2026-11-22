"""Ranking -> empirical pair matrix; unranked alternatives jointly last.

No smoothing. Tied voter preferences contribute 1/2. Bernoulli simulation
therefore randomizes those ties. Candidate IDs are preserved in metadata.
"""
from pathlib import Path
import re,itertools,json
import numpy as np

def load_rankings(path):
    text=Path(path).read_text(encoding='utf-8-sig');k=int(re.search(r'# NUMBER ALTERNATIVES: (\d+)',text)[1])
    wins=np.zeros((k,k));total=0;profiles=0
    for line in text.splitlines():
        if line.startswith('#') or ':' not in line:continue
        count,ranking=line.split(':',1);count=int(count);ranking=ranking.strip()
        if '{' in ranking:raise ValueError('This loader supports strict SOC/SOI rankings only')
        rank=[int(x.strip())-1 for x in ranking.split(',') if x.strip()]
        if len(set(rank))!=len(rank) or any(x<0 or x>=k for x in rank):raise ValueError('Invalid ranking')
        pos={a:i for i,a in enumerate(rank)};total+=count;profiles+=1
        for i,j in itertools.combinations(range(k),2):
            x,y=pos.get(i,k),pos.get(j,k);v=1 if x<y else 0 if x>y else .5
            wins[i,j]+=count*v;wins[j,i]+=count*(1-v)
    p=wins/total;np.fill_diagonal(p,.5);b=(p.sum(1)-.5)/(k-1)
    cycles=sum((p[i,j]>.5 and p[j,l]>.5 and p[l,i]>.5) or (p[j,i]>.5 and p[l,j]>.5 and p[i,l]>.5) for i,j,l in itertools.combinations(range(k),3))
    cw=[i+1 for i in range(k) if all(p[i,j]>.5 for j in range(k) if i!=j)]
    collection='00006%20-%20skate' if str(path).endswith('.soc') else '00007%20-%20ers'
    meta=dict(k=k,voters=total,distinct_rankings=profiles,cycles=int(cycles),condorcet=cw,
              borda_winner=int(b.argmax())+1,gap=float(np.sort(b)[-1]-np.sort(b)[-2]),scores=b.tolist(),
              tied_pairs=int(np.sum(p[np.triu_indices(k,1)]==.5)),missing_rule='unranked jointly last',
              source=f'https://raw.githubusercontent.com/PrefLib/PrefLib-Data/main/datasets/{collection}/{Path(path).name}')
    return p,meta

if __name__=='__main__':
    import requests
    root=Path(__file__).resolve().parents[1]/'data';root.mkdir(exist_ok=True)
    for collection,file in [('00006%20-%20skate','00006-00000028.soc'),('00007%20-%20ers','00007-00000005.soi')]:
        dest=root/file
        if not dest.exists():
            r=requests.get(f'https://raw.githubusercontent.com/PrefLib/PrefLib-Data/main/datasets/{collection}/{file}',timeout=60);r.raise_for_status();dest.write_text(r.text,encoding='utf-8')
    from borda_study import prepare_real
    print(json.dumps(prepare_real(),indent=2))
