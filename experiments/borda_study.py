"""Execute the Borda-only study. Configurations and every seed are retained."""
import sys,json,gzip,platform,time,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from cobra.core import scores,validate
from cobra.simulation import simulate

def planted(k,gap,cycle=0.):
    p=np.full((k,k),.5);a=gap*(k-1)/k;p[0,1:]+=(a);p[1:,0]-=a
    if cycle:
        # Circulations have zero row sum, preserving EVERY Borda score.
        for i in range(0,k-2,3):
            for x,y in ((i,i+1),(i+1,i+2),(i+2,i)):
                p[x,y]+=cycle;p[y,x]-=cycle
    return validate(p)

def prepare_real():
    from prepare_data import load_rankings
    out=ROOT/'data'/'borda';out.mkdir(exist_ok=True)
    selected=[('Skating','00006-00000028.soc'),('ERS','00007-00000005.soi')]
    meta=[]
    for name,file in selected:
        p,m=load_rankings(ROOT/'data'/file);np.save(out/(name+'.npy'),p)
        m.update(name=name,file=file,matrix_sha256=hashlib.sha256(p.tobytes()).hexdigest())
        meta.append(m)
    (out/'metadata.json').write_text(json.dumps(meta,indent=2));return meta

def configurations():
    cases=[]
    def add(name,p,family,seeds=100,cap=100000):
        cases.append(dict(name=name,p=p.tolist(),family=family,seeds=seeds,cap=cap))
    for k in (3,5,10,20,50):add('K'+str(k),planted(k,.1),'A: scaling',100 if k<=10 else 30)
    for g in (.2,.1,.05,.02,.01):add('gap'+str(g),planted(5,g),'B: gaps',100 if g>=.05 else 30,100000 if g>=.05 else 200000)
    for k in (3,5,10):add('cycle'+str(k),planted(k,.1,.30),'C: structure')
    add('near_cycle',planted(3,.01,.30),'C: structure',30,200000)
    p=np.array([[.5,.51,.51],[.49,.5,.90],[.49,.10,.5]])
    add('disagreement',p,'C: structure')
    add('tie',np.array([[.5,.8,.2],[.2,.5,.8],[.8,.2,.5]]),'D: robustness',30,100000)
    for name in ('Skating','ERS'):
        add(name,np.load(ROOT/'data/borda'/f'{name}.npy'),'Implementation',30,500000)
    return cases

def main():
    import prepare_data
    prepare_real();cases=configurations();out=ROOT/'results';out.mkdir(exist_ok=True)
    modes=['fixed','uniform','cobra','random_pair','no_reuse','directional','pair_only']
    # All seven modes on small instances; larger cases retain the five core modes.
    config=dict(delta=.05,batch=128,modes=modes,cases=cases,seed_rule='2026000 + replication',
                python=sys.version,numpy=np.__version__,platform=platform.platform())
    (out/'config.json').write_text(json.dumps(config,indent=2));runs=[];start=time.perf_counter()
    for case in cases:
        p=np.array(case['p']); active=modes if len(p)<=10 and case['name']!='near_cycle' else modes[:5]
        for seed in range(case['seeds']):
            for mode in active:
                r=simulate(p,mode,2026000+seed,case['cap'],.05,128,[1000,10000,100000])
                r.update(case=case['name'],family=case['family']);runs.append(r)
        print(case['name'],len(runs),'runs',round(time.perf_counter()-start,1),'seconds',flush=True)
        (out/'runs.json.gz').write_bytes(gzip.compress(json.dumps(runs,separators=(',',':')).encode(),mtime=0))
    # Separate horizon-aware confidence experiment, not a relabeling of fixed-delta runs.
    hr=[]
    for h in (1000,10000,100000):
        for seed in range(30):
            for mode in ('uniform','cobra'):
                r=simulate(planted(3,.2),mode,3026000+seed,h,h**-2,128,[h]);r.update(case='horizon',horizon=h);hr.append(r)
    (out/'horizon.json.gz').write_bytes(gzip.compress(json.dumps(hr,separators=(',',':')).encode(),mtime=0))
    (out/'execution.json').write_text(json.dumps(dict(runs=len(runs),horizon_runs=len(hr),seconds=time.perf_counter()-start),indent=2))

if __name__=='__main__':main()
