"""Short-horizon real-subset comparison; no claim of hybrid superiority."""
import sys,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'experiments'))
from run_study import paired,rucb
meta=json.loads((R/'results/real_metadata.json').read_text());res=[]
for m in meta:
    p=np.array(m['matrix']);T=300000
    for s in range(20):
        for r in paired(p,5000+s,delta=T**-2,horizon=T,batch=256):r.update(case=m['name']);res.append(r)
    for s in range(8):res.append(dict(case=m['name'],method='RUCB',regret=rucb(p,6000+s,T,[T])[T],complete=False))
(R/'results/real_regret.json').write_text(json.dumps(res,indent=2))
print([(m['name'],method,float(np.mean([x['regret'] for x in res if x['case']==m['name'] and x['method']==method]))) for m in meta for method in ['Restart','Reuse','RUCB']])
