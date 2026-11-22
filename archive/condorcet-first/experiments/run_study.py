"""Reproducible Dir1 simulation. Run from any directory with Python 3.

Batching aggregates actual iid duels, not fractional observations. Certificates
are inspected after batches; both paired policies use identical checkpoints.
"""
from pathlib import Path
import itertools,json,math,hashlib,time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from numba import njit
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'report'/'results'; OUT.mkdir(parents=True,exist_ok=True)
FIG=ROOT/'report'/'figures';FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':12,'axes.labelsize':13,'legend.fontsize':11,'figure.figsize':(7.1,4.1),'savefig.bbox':'tight','pdf.fonttype':42})

def scores(p):return (p.sum(1)-.5)/(len(p)-1)
def cw(p):return next((i for i in range(len(p)) if all(p[i,j]>.5 for j in range(len(p)) if i!=j)),None)
def intervals(w,n,delta):
    k=len(w);m=k*(k-1)/2; nn=np.maximum(n,1)
    r=np.sqrt(np.log(4*m*nn**2/delta)/(2*nn));mu=np.divide(w,nn)
    lo=np.where(n>0,np.maximum(0,mu-r),0.);hi=np.where(n>0,np.minimum(1,mu+r),1.)
    np.fill_diagonal(lo,.5);np.fill_diagonal(hi,.5)
    return lo,hi
def certified(lo,hi):
    i=int(np.argmax(lo));return i if all(lo[i]>hi[j] for j in range(len(lo)) if j!=i) else None
def row_bounds(w,n,delta):
    lo,hi=intervals(w,n,delta);k=len(w)
    return (lo.sum(1)-.5)/(k-1),(hi.sum(1)-.5)/(k-1)
def cap_count(k,gap,delta):
    n=1
    while math.sqrt(math.log(4*k*n*n/delta)/(2*n))>gap/8:n*=2
    return n

def paired(p,seed,delta=.05,horizon=None,batch=2048):
    k=len(p);bs=scores(p); c=cw(p);target=c if c is not None else int(bs.argmax())
    gaps=(p[target]-.5) if c is not None else bs[target]-bs
    d=delta/3; h=.8*float(np.min(np.abs(p[np.triu_indices(k,1)]-.5)))
    assert h>0
    nb_gap=float(np.sort(bs)[-1]-np.sort(bs)[-2]); assert nb_gap>1e-10
    nd=math.ceil(math.log(4*k/d)/(2*h*h)); limit=horizon if horizon is not None else 10**12
    rng=np.random.default_rng(seed);fresh=np.random.default_rng(seed+10000000)
    w=np.zeros((k,k));n=np.zeros((k,k),dtype=np.int64);t=0;reg=0.;cache={}
    def duel(i,j,count):
        nonlocal t,reg
        z=int(rng.binomial(count,p[i,j]));w[i,j]+=z;w[j,i]+=count-z;n[i,j]+=count;n[j,i]+=count;t+=count;reg+=count*(gaps[i]+gaps[j])/2
        return z
    def test(i,j):
        key=tuple(sorted((i,j)))
        if key in cache:return cache[key]
        count=min(nd,limit-t)
        if count<=0:return None
        z=duel(i,j,count)
        if count<nd:return None
        win=i if z>count/2 else j
        cache[key]=win;return win
    q=0;diagnosis=None
    for j in range(1,k):
        z=test(q,j)
        if z is None:break
        q=z
    else:
        for j in range(k):
            if j==q:continue
            z=test(q,j)
            if z is None:break
            if z!=q:diagnosis='no_cw';break
        else:diagnosis='cw'
    diag=t;diagreg=reg
    def result(method,stop,rr,answer):
        totalreg=rr+(max(0,limit-stop)*(gaps[answer]) if answer is not None and horizon is not None else 0)
        return dict(method=method,seed=seed,diagnosis=diagnosis,diagnostic_duels=diag,additional_duels=stop-diag,total_duels=stop,regret=float(totalreg),answer=answer,correct=bool(answer==target) if answer is not None else False,complete=answer is not None,target=target,h=h,delta=delta,horizon=horizon,nd=nd)
    if diagnosis!='no_cw':
        ans=q if diagnosis=='cw' else None
        return [result(a,t,reg,ans) for a in ['Restart','Reuse']]
    count=np.zeros(k,dtype=np.int64);wins=np.zeros(k);cap=cap_count(k,nb_gap,d)
    saved={};lo,hi=row_bounds(w,n,d);ans=certified(lo,hi)
    if ans is not None:saved['Reuse']=result('Reuse',t,reg,ans)
    while t<limit and np.min(count)<cap:
        i=int(np.argmin(count));m=min(batch,cap-int(count[i]),limit-t)
        if m<=0:break
        js=[j for j in range(k) if j!=i]
        alloc=fresh.multinomial(m,np.ones(k-1)/(k-1));z=fresh.binomial(alloc,p[i,js])
        wins[i]+=int(z.sum());count[i]+=m
        for j,a,b in zip(js,alloc,z):
            w[i,j]+=b;w[j,i]+=a-b;n[i,j]+=a;n[j,i]+=a
            reg+=a*(gaps[i]+gaps[j])/2
        t+=m
        nn=np.maximum(count,1);r=np.sqrt(np.log(4*k*nn.astype(float)**2/d)/(2*nn));mu=wins/nn
        dl=np.where(count>0,np.maximum(0,mu-r),0.);du=np.where(count>0,np.minimum(1,mu+r),1.)
        direct=certified(dl,du)
        if 'Reuse' not in saved:
            ml,mu_=row_bounds(w,n,d)
            lower,upper=np.maximum(ml,dl),np.minimum(mu_,du)
            reuse=direct if np.any(lower>upper) else certified(lower,upper)
            if reuse is not None:saved['Reuse']=result('Reuse',t,reg,reuse)
        if direct is not None:
            saved['Restart']=result('Restart',t,reg,direct)
            if 'Reuse' not in saved:saved['Reuse']=result('Reuse',t,reg,direct)
            break
    for name in ['Restart','Reuse']:
        if name not in saved:saved[name]=result(name,t,reg,None)
    assert saved['Reuse']['additional_duels']<=saved['Restart']['additional_duels']
    return list(saved.values())

def matrix(ab=.6,bc=.7,ca=.65):return np.array([[.5,ab,1-ca],[1-ab,.5,bc],[ca,1-bc,.5]])
def real_cases():
    selected=[]
    for prefix,audit in [('00006','audit.json'),('00007','ers_audit.json')]:
        records=json.loads((ROOT/'data'/audit).read_text())
        found=False
        for rec in sorted(records,key=lambda x:x['file']):
            p=np.load(ROOT/'data'/(Path(rec['file']).stem+'.npy'))
            for inds in itertools.combinations(range(len(p)),3):
                q=p[np.ix_(inds,inds)];b=scores(q)
                if cw(q) is None and np.min(np.abs(q[np.triu_indices(3,1)]-.5))>0 and np.sort(b)[-1]-np.sort(b)[-2]>1e-9:
                    name='Skating' if prefix=='00006' else 'ERS'
                    np.save(OUT/(name+'_matrix.npy'),q)
                    meta=dict(name=name,file=rec['file'],indices_zero_based=list(inds),ids_one_based=[x+1 for x in inds],full_k=len(p),full_cw=cw(p),voters=rec['voters'],matrix=q.tolist(),borda=b.tolist(),source=rec.get('source'),selection='First lexicographic strict three-cycle with unique Borda winner across files and candidate triples; outcomes not consulted.')
                    selected.append((name,q,meta));found=True;break
            if found:break
        assert found,prefix
    (OUT/'real_metadata.json').write_text(json.dumps([z[2] for z in selected],indent=2))
    return selected

def rucb_reference(p,seed,T,checkpoints):
    rng=np.random.default_rng(seed);k=len(p);w=np.zeros((k,k));reg=0.;B=None;out={};b=scores(p);c=cw(p);g=p[c]-.5 if c is not None else b.max()-b
    for t in range(1,T+1):
        n=w+w.T;u=np.divide(w,n,out=np.ones_like(w),where=n>0)+np.sqrt(np.divide(.51*np.log(t),n,out=np.zeros_like(w),where=n>0));u[n==0]=2;np.fill_diagonal(u,.5)
        C=np.flatnonzero(np.all(u>=.5,axis=1))
        if B is not None and B not in C:B=None
        if len(C)==0:a=int(rng.integers(k))
        elif len(C)==1:a=int(C[0]);B=a
        elif B is None:a=int(rng.choice(C))
        elif rng.random()<.5:a=B
        else:a=int(rng.choice(C[C!=B]))
        ds=np.flatnonzero(u[:,a]==u[:,a].max())
        if len(ds)>1:ds=ds[ds!=a]
        j=int(rng.choice(ds));reg+=(g[a]+g[j])/2
        if a!=j:
            if rng.random()<p[a,j]:w[a,j]+=1
            else:w[j,a]+=1
        if t in checkpoints:out[t]=float(reg)
    return out

@njit(cache=True)
def rucb_fast(p,seed,T,checkpoints):
    np.random.seed(seed);k=len(p);w=np.zeros((k,k));g=np.zeros(k);bs=(p.sum(axis=1)-.5)/(k-1);c=-1
    for i in range(k):
        ok=True
        for j in range(k):
            if i!=j and p[i,j]<=.5:ok=False
        if ok:c=i
    for i in range(k):g[i]=p[c,i]-.5 if c>=0 else bs.max()-bs[i]
    out=np.zeros(len(checkpoints));ci=0;reg=0.;B=-1
    for t in range(1,T+1):
        u=np.full((k,k),2.);C=np.empty(k,np.int64);nc=0
        for i in range(k):
            for j in range(k):
                n=w[i,j]+w[j,i]
                if i==j:u[i,j]=.5
                elif n>0:u[i,j]=w[i,j]/n+math.sqrt(.51*math.log(t)/n)
            if np.min(u[i,:])>=.5:C[nc]=i;nc+=1
        if B>=0:
            present=False
            for z in range(nc):
                if C[z]==B:present=True
            if not present:B=-1
        if nc==0:a=np.random.randint(k)
        elif nc==1:a=C[0];B=a
        elif B<0:a=C[np.random.randint(nc)]
        elif np.random.random()<.5:a=B
        else:
            options=np.empty(k,np.int64);no=0
            for z in range(nc):
                if C[z]!=B:options[no]=C[z];no+=1
            a=options[np.random.randint(no)]
        mx=np.max(u[:,a]);ds=np.empty(k,np.int64);nd=0
        for j in range(k):
            if u[j,a]==mx:ds[nd]=j;nd+=1
        if nd>1:
            count=0
            for z in range(nd):
                if ds[z]!=a:ds[count]=ds[z];count+=1
            nd=count
        j=ds[np.random.randint(nd)];reg+=(g[a]+g[j])/2
        if a!=j:
            if np.random.random()<p[a,j]:w[a,j]+=1
            else:w[j,a]+=1
        if ci<len(checkpoints) and t==checkpoints[ci]:out[ci]=reg;ci+=1
    return out

def rucb(p,seed,T,checkpoints):
    values=rucb_fast(p,seed,T,np.array(checkpoints,dtype=np.int64))
    return {t:float(v) for t,v in zip(checkpoints,values)}

def summarize(records):
    groups={}
    for r in records:groups.setdefault((r['experiment'],r['case'],r['method'],r.get('horizon')),[]).append(r)
    summary=[]
    for (ex,case,method,T),rs in groups.items():
        a=np.array([r['additional_duels'] for r in rs]);rr=np.array([r['regret'] for r in rs]);total=np.array([r['total_duels'] for r in rs])
        summary.append(dict(experiment=ex,case=case,method=method,horizon=T,runs=len(rs),additional_mean=float(a.mean()),additional_se=float(a.std(ddof=1)/np.sqrt(len(a))) if len(a)>1 else 0,total_mean=float(total.mean()),regret_mean=float(rr.mean()),regret_se=float(rr.std(ddof=1)/np.sqrt(len(rr))) if len(rr)>1 else 0,complete=sum(r['complete'] for r in rs),correct=sum(r['correct'] for r in rs),diagnostic_mean=float(np.mean([r['diagnostic_duels'] for r in rs]))))
    return summary

def savefig(name):plt.tight_layout();plt.savefig(FIG/(name+'.pdf'));plt.savefig(FIG/(name+'.png'),dpi=160);plt.close()
def main():
    started=time.time();records=[];real=real_cases();cases={'Cycle':matrix(),'Near boundary':matrix(.55,.75,.51),'CW agreement':matrix(.7,.65,.3),'CW disagreement':matrix(.55,.75,.4)}
    for ex,items,seeds in [('A',[(a,cases[a]) for a in ['Cycle','Near boundary']],60),('D',[(a,p) for a,p,_ in real],60)]:
        for name,p in items:
            print('Running',ex,name,flush=True)
            for s in range(seeds):
                for r in paired(p,1000+s):r.update(experiment=ex,case=name);records.append(r)
    for ca in [.51,.53,.57,.65]:
        for bc in [.68,.75,.85]:
            p=matrix(.55,bc,ca)
            if np.sort(scores(p))[-1]-np.sort(scores(p))[-2]<.005:continue
            name=f'{ca:.2f},{bc:.2f}'
            for s in range(30):
                for r in paired(p,2000+s):r.update(experiment='B',case=name,ca=ca,bc=bc);records.append(r)
    horizons=[10000,30000,100000,300000]
    for name in ['Cycle','CW agreement','CW disagreement']:
        p=cases[name];print('Regret',name,flush=True)
        for T in horizons:
            for s in range(20):
                for r in paired(p,3000+s,delta=T**-2,horizon=T,batch=256):r.update(experiment='C',case=name);records.append(r)
        for s in range(8):
            curve=rucb(p,4000+s,max(horizons),horizons)
            for T,val in curve.items():records.append(dict(experiment='C',case=name,method='RUCB',seed=s,horizon=T,additional_duels=0,total_duels=T,diagnostic_duels=0,regret=val,answer=None,correct=False,complete=False))
    (OUT/'runs.json').write_text(json.dumps(records,indent=2));summary=summarize(records);(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    # Main paired comparison, confidence intervals are across independent seeds.
    fig,ax=plt.subplots();labels=['Cycle','Near boundary']+[z[0] for z in real];x=np.arange(len(labels));width=.34
    for j,method in enumerate(['Restart','Reuse']):
        rows=[next(r for r in summary if r['case']==name and r['method']==method and r['experiment'] in ['A','D']) for name in labels]
        ax.bar(x+(j-.5)*width,[r['additional_mean'] for r in rows],width,yerr=[1.96*r['additional_se'] for r in rows],label=method,capsize=3)
    ax.set_xticks(x,labels);ax.set_yscale('symlog',linthresh=1000);ax.set_ylabel('Additional duels after diagnosis');ax.legend();savefig('additional_duels')
    fig,ax=plt.subplots()
    for bc in [.68,.75,.85]:
        vals=[];errs=[];xs=[]
        for ca in [.51,.53,.57,.65]:
            name=f'{ca:.2f},{bc:.2f}';rs=[r for r in records if r['experiment']=='B' and r['case']==name];a={r['seed']:r['additional_duels'] for r in rs if r['method']=='Restart'};b={r['seed']:r['additional_duels'] for r in rs if r['method']=='Reuse'}
            if not a:continue
            v=np.array([100*(a[s]-b[s])/a[s] for s in a]);xs.append(ca-.5);vals.append(v.mean());errs.append(1.96*v.std(ddof=1)/np.sqrt(len(v)))
        ax.errorbar(xs,vals,yerr=errs,marker='o',capsize=3,label=f'p(B beats C)={bc:.2f}')
    ax.set_xlabel('C-over-A margin');ax.set_ylabel('Mean paired additional-duel saving (%)');ax.legend();savefig('sensitivity')
    for name in ['Cycle','CW agreement','CW disagreement']:
        fig,ax=plt.subplots()
        for method in ['Restart','Reuse','RUCB']:
            rows=sorted([r for r in summary if r['experiment']=='C' and r['case']==name and r['method']==method],key=lambda r:r['horizon'])
            ax.errorbar([r['horizon'] for r in rows],[r['regret_mean'] for r in rows],yerr=[1.96*r['regret_se'] for r in rows],marker='o',capsize=3,label=method)
        ax.set_xscale('log');ax.set_xlabel('Horizon T (log scale)');ax.set_ylabel('Cumulative hierarchical regret');ax.legend();savefig('regret_'+name.replace(' ','_'))
    fig,axes=plt.subplots(1,2,figsize=(7.1,3.3))
    for ax,(name,p,meta) in zip(axes,real):
        im=ax.imshow(p,vmin=0,vmax=1,cmap='RdBu');ax.set_xticks(range(3),[str(i) for i in meta['ids_one_based']]);ax.set_yticks(range(3),[str(i) for i in meta['ids_one_based']]);ax.set_title(name)
        for i in range(3):
            for j in range(3):ax.text(j,i,f'{p[i,j]:.3f}',ha='center',va='center',fontsize=12)
        ax.set_xlabel('Opponent ID');ax.set_ylabel('Row candidate ID')
    savefig('real_matrices')
    # Cumulative fresh-duel requirements, not only successful-run averages.
    fig,ax=plt.subplots()
    for name,p,_ in real:
        for method,style in [('Restart','--'),('Reuse','-')]:
            vals=np.sort([r['additional_duels'] for r in records if r['experiment']=='D' and r['case']==name and r['method']==method]);ax.step(vals,np.arange(1,len(vals)+1)/len(vals),where='post',linestyle=style,label=f'{name}: {method}')
    ax.set_xlabel('Additional duels');ax.set_ylabel('Fraction certified');ax.legend();savefig('real_ecdf')
    (OUT/'runtime.json').write_text(json.dumps(dict(seconds=time.time()-started,n_records=len(records),numpy=np.__version__,seed_ranges=[1000,2000,3000,4000],batch=2048)))
    print('Finished',len(records),'records in',time.time()-started,flush=True)
if __name__=='__main__':main()
