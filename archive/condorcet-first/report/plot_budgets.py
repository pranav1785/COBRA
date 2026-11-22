from pathlib import Path
import json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'experiments'))
from run_study import cap_count,matrix,scores
S=json.loads((R/'results/summary.json').read_text());meta=json.loads((R/'results/real_metadata.json').read_text())
cases=[('Cycle',matrix()),('Near boundary',matrix(.55,.75,.51))]+[(x['name'],np.array(x['matrix'])) for x in meta]
caps=[];observed=[];diagnosis=[]
for name,p in cases:
    k=len(p);d=.05/3;h=.8*np.min(np.abs(p[np.triu_indices(k,1)]-.5));gap=np.sort(scores(p))[-1]-np.sort(scores(p))[-2]
    nd=int(np.ceil(np.log(4*k/d)/(2*h*h)));cap=2*(k-1)*nd+k*cap_count(k,gap,d)
    r=next(x for x in S if x['case']==name and x['method']=='Reuse' and x['experiment'] in ['A','D'])
    caps.append(int(cap));observed.append(r['total_mean']);diagnosis.append(r['diagnostic_mean'])
plt.rcParams.update({'font.size':12,'axes.labelsize':13,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(7.1,4.2));x=np.arange(4)
for off,v,l in [(-.24,diagnosis,'Observed diagnosis'),(0,observed,'Observed reuse total'),(.24,caps,'Sufficient total cap')]:ax.bar(x+off,v,.24,label=l)
ax.set_xticks(x,[a for a,p in cases]);ax.set_yscale('log');ax.set_ylabel('Duels (log scale)');ax.legend();fig.tight_layout();fig.savefig(R/'figures/sufficient_budgets.pdf',bbox_inches='tight');fig.savefig(R/'figures/sufficient_budgets.png',dpi=160,bbox_inches='tight')
(R/'results/budgets.json').write_text(json.dumps([dict(case=a,cap=c,observed=o,diagnosis=d) for (a,_),c,o,d in zip(cases,caps,observed,diagnosis)],indent=2))
