"""Controlled weights 1,2,4, matching the original cycle3 and K5 runs."""
import sys,json,gzip,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from cobra.simulation import simulate

def main():
    cfg=json.loads((ROOT/'results/config.json').read_text());original=json.loads(gzip.decompress((ROOT/'results/runs.json.gz').read_bytes()))
    cases=[c for c in cfg['cases'] if c['name'] in ('cycle3','K5')];runs=[];summary=[];start=time.perf_counter();replayed=0
    for c in cases:
        for weight in (1,2,4):
            rr=[]
            for s in range(100):
                r=simulate(np.array(c['p']),'cobra',2026000+s,c['cap'],.05,128,[1000,10000,100000],leader_weight=weight)
                r.update(case=c['name'],leader_weight=weight);rr.append(r);runs.append(r)
                if weight==2:
                    old=next(x for x in original if x['case']==c['name'] and x['mode']=='cobra' and x['seed']==r['seed'])
                    for key in ('duels','certified','estimate','correct','regret','counts','trace'):assert r[key]==old[key],(c['name'],s,key)
                    replayed+=1
            n=np.array([r['duels'] for r in rr]);summary.append(dict(case=c['name'],weight=weight,seeds=len(rr),mean=float(n.mean()),sd=float(n.std(ddof=1)),certified=sum(x['certified'] for x in rr),accuracy=float(np.mean([x['correct'] for x in rr]))))
            print(c['name'],weight,summary[-1],flush=True)
    contrasts=[];rng=np.random.default_rng(341)
    for c in cases:
        base=np.array([r['duels'] for r in runs if r['case']==c['name'] and r['leader_weight']==2])
        for w in (1,4):
            x=np.array([r['duels'] for r in runs if r['case']==c['name'] and r['leader_weight']==w]);idx=rng.integers(100,size=(3000,100));boot=100*(x[idx].mean(1)-base[idx].mean(1))/base[idx].mean(1)
            contrasts.append(dict(case=c['name'],weight=w,extra_cost_vs_weight2=float(100*(x.mean()-base.mean())/base.mean()),ci=np.quantile(boot,[.025,.975]).tolist()))
    identical=0
    for c in cases:
        for seed in range(2026000,2026100):
            a=next(r for r in runs if r['case']==c['name'] and r['seed']==seed and r['leader_weight']==2)
            b=next(r for r in runs if r['case']==c['name'] and r['seed']==seed and r['leader_weight']==4)
            identical+=all(a[key]==b[key] for key in ('duels','counts','regret','certified','estimate','correct','trace'))
    (ROOT/'results/weight_runs.json.gz').write_bytes(gzip.compress(json.dumps(runs,separators=(',',':')).encode(),mtime=0))
    (ROOT/'results/weight_summary.json').write_text(json.dumps(dict(summary=summary,contrasts=contrasts,replayed_original_runs=replayed,identical_weight2_weight4_runs=identical,config=dict(weights=[1,2,4],seeds=list(range(2026000,2026100)),cap=100000,delta=.05,batch=128,checkpoints=[1000,10000,100000],cases=cases),seconds=time.perf_counter()-start),indent=2))

if __name__=='__main__':main()
