"""Exact iid batched simulation; no fractional duel counts or oracle selection."""
import time
import numpy as np
from .core import Learner,scores,validate,certificate

def regret(p,i,j):
    b=scores(p);return float(b.max()-(b[i]+b[j])/2)

def simulate(p,mode,seed,cap=100000,delta=.05,batch=128,checkpoints=(),leader_weight=2.,audit=False):
    p=validate(p);k=len(p);b=scores(p); winners=np.flatnonzero(np.isclose(b,b.max(),atol=1e-12,rtol=0))
    # Distinct streams: selection and outcomes. Matched variants start identically.
    rng=np.random.default_rng(seed); feedback=np.random.default_rng(seed+1000000)
    learner=Learner(k,mode,delta,leader_weight);t=0;r=0.;cert=None;trace=[];blocks=[];start=time.perf_counter()
    checkpoints=sorted(set([x for x in checkpoints if 0<x<=cap]+[cap]));ci=0
    while t<cap:
        action,i,j=learner.select(rng);n=min(batch,cap-t,checkpoints[ci]-t)
        if action=='safe':
            opponents=rng.multinomial(n,np.full(k-1,1/(k-1)));jlist=[x for x in range(k) if x!=i]
            for j,nj in zip(jlist,opponents):
                if nj:
                    w=int(feedback.binomial(int(nj),p[i,j]));learner.update(i,j,int(nj),w,True)
                    r+=int(nj)*float(b.max()-(b[i]+b[j])/2)
        else:
            w=int(feedback.binomial(n,p[i,j]));learner.update(i,j,n,w)
            r+=n*float(b.max()-(b[i]+b[j])/2)
        if audit:blocks.append(dict(index=learner.block,action=action,start=t,length=n,designated=i if action=='safe' else None,direct_counts=learner.c.tolist()))
        t+=n;learner.block+=1
        lo,hi=learner.score_bounds();found=certificate(lo,hi)
        if mode!='fixed' and found is not None:cert=found
        if t==checkpoints[ci] or cert is not None:
            estimate=cert if cert is not None else int(learner.estimate().argmax())
            trace.append(dict(t=t,regret=r,correct=bool(estimate in winners),certified=cert is not None,
                              uncertainty=float(np.max(hi-lo))))
            if t==checkpoints[ci]:ci+=1
        if cert is not None:break
    elapsed=time.perf_counter()-start
    estimate=cert if cert is not None else int(learner.estimate().argmax())
    # Completion implies self-duels, contributing zero iff certificate is correct.
    for h in checkpoints:
        if h>t:trace.append(dict(t=h,regret=r+(h-t)*float(b.max()-b[estimate]),correct=bool(estimate in winners),certified=True,uncertainty=float(np.max(hi-lo))))
    result=dict(mode=mode,seed=seed,delta=delta,batch=batch,cap=cap,duels=t,certified=cert is not None,
                estimate=estimate,correct=bool(estimate in winners),regret=r,cpu_seconds=elapsed,
                trace=trace,counts=learner.n.tolist())
    if audit:result['blocks']=blocks
    return result
