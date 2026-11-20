"""Draw the two real-dataset implementation figures from recorded paired runs."""
from pathlib import Path
import gzip,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent
raw=R/'results/runs.json'
runs=json.loads(raw.read_text() if raw.exists() else gzip.decompress(raw.with_suffix('.json.gz').read_bytes()))
plt.rcParams.update({'font.size':12,'axes.labelsize':13,'legend.fontsize':11,'pdf.fonttype':42})
for name in ['Skating','ERS']:
    fig,ax=plt.subplots(figsize=(7.1,3.2));maximum=1
    for method,style in [('Restart','--'),('Reuse','-')]:
        values=np.sort([r['additional_duels'] for r in runs if r['experiment']=='D' and r['case']==name and r['method']==method])
        maximum=max(maximum,values.max())
        ax.step(values,np.arange(1,len(values)+1)/len(values),where='post',linestyle=style,label=method)
    ax.set_xlim(-.03*maximum,1.03*maximum);ax.set_ylim(0,1.04)
    ax.set_xlabel('Additional duels after diagnosis');ax.set_ylabel('Fraction certified');ax.legend()
    fig.tight_layout();fig.savefig(R/('figures/implementation_'+name.lower()+'.pdf'),bbox_inches='tight');plt.close(fig)

