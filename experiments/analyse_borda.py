"""Tables/figures derive exclusively from retained numeric runs."""
from pathlib import Path
import json,gzip,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results';FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':12,'axes.labelsize':12,'legend.fontsize':10,'figure.figsize':(7.2,3.7),'savefig.bbox':'tight','pdf.fonttype':42})
LABEL={'uniform':'Uniform + stop','cobra':'COBRA','random_pair':'COBRA random pair','no_reuse':'No reuse certificate','directional':'Forward evidence only','pair_only':'No safeguard','fixed':'Fixed budget'}
COL={'uniform':'#3465a4','cobra':'#b62c2c','random_pair':'#488c46','no_reuse':'#8b5aa7','directional':'#c47c15','pair_only':'#777777','fixed':'#999999'}
def save(name):plt.tight_layout();plt.savefig(FIG/(name+'.pdf'));plt.savefig(FIG/(name+'.png'),dpi=160);plt.close()
def main():
    runs=json.loads(gzip.decompress((OUT/'runs.json.gz').read_bytes()));config=json.loads((OUT/'config.json').read_text());summary=[]
    for case in config['cases']:
        for mode in config['modes']:
            rr=[r for r in runs if r['case']==case['name'] and r['mode']==mode]
            if not rr:continue
            n=np.array([r['duels'] for r in rr]);d=dict(case=case['name'],mode=mode,seeds=len(rr),cap=case['cap'],mean=float(n.mean()),sd=float(n.std(ddof=1)),median=float(np.median(n)),q25=float(np.quantile(n,.25)),q75=float(np.quantile(n,.75)),certified=sum(r['certified'] for r in rr),accuracy=float(np.mean([r['correct'] for r in rr])),cpu=float(np.mean([r['cpu_seconds'] for r in rr])))
            summary.append(d)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    savings=[];rng=np.random.default_rng(879)
    for case in config['cases']:
        a=sorted([r for r in runs if r['case']==case['name'] and r['mode']=='uniform'],key=lambda x:x['seed'])
        b=sorted([r for r in runs if r['case']==case['name'] and r['mode']=='cobra'],key=lambda x:x['seed'])
        x=np.array([r['duels'] for r in a]);y=np.array([r['duels'] for r in b]);idx=rng.integers(len(x),size=(3000,len(x)))
        boot=100*(x[idx].mean(1)-y[idx].mean(1))/x[idx].mean(1)
        savings.append(dict(case=case['name'],saving=float(100*(x.mean()-y.mean())/x.mean()),ci=np.quantile(boot,[.025,.975]).tolist(),paired_duel_difference=float(np.mean(x-y))))
    (OUT/'savings.json').write_text(json.dumps(savings,indent=2))
    def find(c,m):return next(r for r in summary if r['case']==c and r['mode']==m)
    # Scaling and gap plots: cap includes unfinished runs, never drop failures.
    for filename,names,x,label,logx in [('scaling',['K'+str(k) for k in (3,5,10,20,50)],[3,5,10,20,50],'Number of arms K',True),('gaps',['gap'+str(g) for g in (.2,.1,.05,.02,.01)],[.2,.1,.05,.02,.01],'True Borda gap (evaluation only)',True)]:
        for m in ('uniform','cobra','random_pair'):
            y=[find(c,m)['mean'] for c in names];se=[find(c,m)['sd']/np.sqrt(find(c,m)['seeds']) for c in names]
            plt.errorbar(x,y,yerr=1.96*np.array(se),marker='o',label=LABEL[m],color=COL[m],capsize=3)
        if logx:plt.xscale('log')
        plt.yscale('log');plt.xlabel(label);plt.ylabel('Mean min(certification duels, cap)');plt.legend();save(filename)
    names=['K3','K5','cycle3','cycle5','disagreement','Skating','ERS'];x=np.arange(len(names));width=.25
    for q,m in enumerate(('uniform','cobra','random_pair')):
        plt.bar(x+(q-1)*width,[find(c,m)['mean'] for c in names],width,label=LABEL[m],color=COL[m])
    plt.yscale('log');plt.xticks(x,names,rotation=15);plt.ylabel('Restricted mean total duels');plt.legend();save('summary')
    # Full per-seed distributions expose regressions.
    c='cycle3';modes=['uniform','cobra','random_pair','no_reuse','directional','pair_only']
    plt.boxplot([[r['duels'] for r in runs if r['case']==c and r['mode']==m] for m in modes],tick_labels=[LABEL[m] for m in modes],showfliers=False)
    plt.xticks(rotation=18,ha='right');plt.ylabel('Total duels (cycle3)');save('ablation')
    for m in ('fixed','uniform','cobra','random_pair'):
        rr=[r for r in runs if r['case']=='cycle3' and r['mode']==m]
        x=[1000,10000,100000];acc=[];cert=[]
        for h in x:
            tr=[min((v for v in r['trace'] if v['t']>=h),key=lambda v:v['t']) for r in rr]
            acc.append(np.mean([v['correct'] for v in tr]));cert.append(np.mean([v['certified'] for v in tr]))
        plt.plot(x,acc,'o-',label=LABEL[m],color=COL[m])
    plt.xscale('log');plt.ylim(0,1.03);plt.xlabel('Comparison budget');plt.ylabel('Empirical Borda winner accuracy');plt.legend();save('accuracy')
    for m in ('uniform','cobra','random_pair'):
        rr=[r for r in runs if r['case']=='cycle3' and r['mode']==m];x=[1000,10000,100000]
        y=[];se=[]
        for h in x:
            z=np.array([next(v['regret'] for v in r['trace'] if v['t']==h) for r in rr]);y.append(z.mean());se.append(z.std(ddof=1)/np.sqrt(len(z)))
        plt.errorbar(x,y,yerr=1.96*np.array(se),marker='o',label=LABEL[m],color=COL[m],capsize=3)
    plt.xscale('log');plt.xlabel('Horizon (fixed delta = 0.05)');plt.ylabel('Cumulative strong Borda regret');plt.legend();save('regret')
    hr=json.loads(gzip.decompress((OUT/'horizon.json.gz').read_bytes()))
    for m in ('uniform','cobra'):
        hs=[1000,10000,100000];y=[np.mean([r['trace'][-1]['regret'] for r in hr if r['mode']==m and r['horizon']==h]) for h in hs]
        plt.plot(hs,y,'o-',label=LABEL[m],color=COL[m])
    plt.xscale('log');plt.xlabel('Known horizon T; confidence delta = T^-2');plt.ylabel('Mean strong Borda regret');plt.legend();save('horizon')
    # Matched seed counts before either has stopped: cap=10000 runs are rerun.
    sys.path.insert(0,str(ROOT));from cobra.simulation import simulate
    p=np.array(next(c['p'] for c in config['cases'] if c['name']=='cycle5'))
    fig,axs=plt.subplots(1,2,figsize=(7.2,3.2))
    for ax,m in zip(axs,('cobra','random_pair')):
        r=simulate(p,m,2026000,10000);n=np.array(r['counts']);im=ax.imshow(n,cmap='Blues',vmin=0,vmax=3000);ax.set_title(LABEL[m]);ax.set_xticks(range(5),range(1,6));ax.set_yticks(range(5),range(1,6));ax.set_xlabel('Arm');ax.set_ylabel('Arm')
    fig.colorbar(im,ax=axs.ravel().tolist(),label='Duels per unordered pair',fraction=.04,pad=.03)
    fig.savefig(FIG/'heatmap.pdf',bbox_inches='tight');fig.savefig(FIG/'heatmap.png',dpi=160,bbox_inches='tight');plt.close(fig)
    # Runtime is measured policy+simulation, not human query latency.
    for m in ('uniform','cobra'):
        ns=['K3','K5','K10','K20','K50'];plt.plot([3,5,10,20,50],[1e6*find(c,m)['cpu']/find(c,m)['mean'] for c in ns],'o-',label=LABEL[m],color=COL[m])
    plt.xlabel('Number of arms K');plt.ylabel('Microseconds / simulated duel');plt.legend();save('runtime')
    for c,style in [('Skating','-'),('ERS','--')]:
        for m in ('uniform','cobra'):
            rr=[r for r in runs if r['case']==c and r['mode']==m];hs=[1000,10000,100000,500000]
            yy=[np.mean([next(v['regret'] for v in r['trace'] if v['t']==h) for r in rr]) for h in hs]
            plt.plot(hs,yy,marker='o',linestyle=style,color=COL[m],label=c+': '+LABEL[m])
    plt.xscale('log');plt.xlabel('Comparison horizon');plt.ylabel('Mean cumulative strong Borda regret');plt.legend();save('real_regret')
    # Schematic describes feedback separation.
    fig,ax=plt.subplots(figsize=(7.2,2.3));ax.axis('off')
    labels=['3 safe blocks\nuniform opponents','1 adaptive block\nleader/rival uncertainty','Shared W, N\nreciprocal pair bounds','Intersect direct + row bounds\ncertificate or continue']
    pos=[(.18,.75),(.75,.75),(.18,.18),(.75,.18)]
    for xy,s in zip(pos,labels):ax.text(*xy,s,ha='center',va='center',bbox=dict(boxstyle='round,pad=.5',fc='#edf2f7',ec='#3465a4'),fontsize=11)
    for a,b in [(pos[0],pos[2]),(pos[1],pos[2]),(pos[2],pos[3])]:ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color='#555',shrinkA=28,shrinkB=36))
    ax.set_xlim(-.05,1.05);ax.set_ylim(-.12,1.05);save('schematic')
    print('Analysed',len(runs),'runs;',len(summary),'groups;',len(hr),'horizon runs')

if __name__=='__main__':main()
