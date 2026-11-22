"""Policies see counts and feedback only; true probabilities live in simulation.py."""
import numpy as np

def validate(p):
    p=np.asarray(p,float)
    if p.ndim!=2 or p.shape[0]!=p.shape[1] or len(p)<2: raise ValueError('K >= 2 square matrix required')
    if not np.isfinite(p).all() or np.any((p<0)|(p>1)) or not np.allclose(p+p.T,1) or not np.allclose(np.diag(p),.5): raise ValueError('Invalid reciprocal preference matrix')
    return p

def scores(p):
    p=validate(p); return (p.sum(1)-.5)/(len(p)-1)

def radius(n,objects,delta):
    n=np.asarray(n); nn=np.maximum(n,1)
    return np.sqrt(np.log(4*objects*nn.astype(float)**2/delta)/(2*nn))

def bounds(w,n,objects,delta):
    nn=np.maximum(n,1); mu=w/nn; r=radius(n,objects,delta)
    return np.where(n>0,np.maximum(0,mu-r),0.),np.where(n>0,np.minimum(1,mu+r),1.)

def certificate(lo,hi):
    i=int(np.argmax(lo)); return i if lo[i]>np.max(np.delete(hi,i)) else None

class Learner:
    """Block-frozen policy, batch size supplied by runner (not outcome dependent).

    COBRA schedules three safe blocks then one informative block. All decisions
    are functions of feedback and private randomness; neither P nor gaps enter.
    'no_reuse' keeps a shadow matrix for IDENTICAL allocation, but uses only direct
    intervals to stop. 'directional' discards reverse-pair evidence for bounds.
    """
    def __init__(self,k,mode='cobra',delta=.05):
        if k<2 or not 0<delta<1: raise ValueError('Invalid K or confidence')
        if mode not in ('fixed','uniform','cobra','random_pair','no_reuse','directional','pair_only'): raise ValueError(mode)
        self.k=k;self.mode=mode;self.delta=delta;self.block=0
        self.w=np.zeros((k,k));self.n=np.zeros((k,k),dtype=np.int64)
        self.dw=np.zeros((k,k));self.dn=np.zeros((k,k),dtype=np.int64)
        self.s=np.zeros(k);self.c=np.zeros(k,dtype=np.int64)
    def pair_bounds(self,directional=False):
        w,n=(self.dw,self.dn) if directional else (self.w,self.n)
        m=self.k*(self.k-1) if directional else self.k*(self.k-1)//2
        lo,hi=bounds(w,n,m,self.delta/2)
        np.fill_diagonal(lo,.5);np.fill_diagonal(hi,.5)
        return lo,hi
    def score_bounds(self):
        # Baselines spend all delta on direct means; reuse controls split equally.
        d=self.delta if self.mode in ('uniform','fixed') else self.delta/2
        lo,hi=bounds(self.s,self.c,self.k,d)
        if self.mode in ('cobra','random_pair','directional','pair_only'):
            pl,pu=self.pair_bounds(self.mode=='directional');k=self.k
            lo=np.maximum(lo,(pl.sum(1)-.5)/(k-1));hi=np.minimum(hi,(pu.sum(1)-.5)/(k-1))
        return lo,hi
    def estimate(self):
        if self.mode in ('uniform','fixed','no_reuse'):
            return np.divide(self.s,self.c,out=np.full(self.k,.5),where=self.c>0)
        mu=np.divide(self.w,self.n,out=np.full_like(self.w,.5),where=self.n>0)
        return (mu.sum(1)-.5)/(self.k-1)
    def select(self,rng):
        safe=self.mode in ('fixed','uniform') or (self.mode!='pair_only' and self.block%4!=3)
        if safe:return ('safe',int(np.argmin(self.c)),None)
        if self.mode=='random_pair':
            i=int(rng.integers(self.k));j=int(rng.integers(self.k-1));j+=j>=i
            return ('pair',i,j)
        # Shadow allocation is deliberately independent of stopping ablations.
        pl,pu=self.pair_bounds(); mu=np.divide(self.w,self.n,out=np.full_like(self.w,.5),where=self.n>0)
        est=(mu.sum(1)-.5)/(self.k-1); a=int(est.argmax())
        upper=(pu.sum(1)-.5)/(self.k-1);upper[a]=-np.inf; b=int(upper.argmax())
        width=pu-pl; weight=np.zeros_like(width)
        weight[a,:]=1;weight[:,a]=1;weight[b,:]=1;weight[:,b]=1
        weight[a,b]=weight[b,a]=2;np.fill_diagonal(weight,0)
        contribution=np.triu(weight*width,1);best=contribution.max()
        choices=np.argwhere((contribution==best)&np.triu(np.ones_like(width,dtype=bool),1))
        i,j=choices[int(rng.integers(len(choices)))];return ('pair',int(i),int(j))
    def update(self,i,j,n,w,safe=False):
        if i==j: raise ValueError('Exploration must compare distinct arms')
        if not 0<=w<=n: raise ValueError('Invalid feedback')
        self.n[i,j]+=n;self.n[j,i]+=n;self.w[i,j]+=w;self.w[j,i]+=n-w
        self.dn[i,j]+=n;self.dw[i,j]+=w
        if safe:self.c[i]+=n;self.s[i]+=w

