"""Recompute published summaries and replay representative original runs."""
from pathlib import Path
import json,gzip,sys,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from cobra.simulation import simulate

def main():
    cfg=json.loads((ROOT/'results/config.json').read_text());cases={x['name']:x for x in cfg['cases']}
    runs=json.loads(gzip.decompress((ROOT/'results/runs.json.gz').read_bytes()))
    groups=json.loads((ROOT/'results/summary.json').read_text());checked=0
    for g in groups:
        rr=[r for r in runs if r['case']==g['case'] and r['mode']==g['mode']];v=np.array([r['duels'] for r in rr])
        for name,value in [('mean',v.mean()),('sd',v.std(ddof=1)),('median',np.median(v)),('q25',np.quantile(v,.25)),('q75',np.quantile(v,.75)),('accuracy',np.mean([r['correct'] for r in rr]))]:assert np.isclose(g[name],value)
        assert g['certified']==sum(r['certified'] for r in rr);checked+=1
    replay=[]
    for case in ('K3','K5','cycle3','disagreement','Skating','ERS'):
        c=cases[case]
        for mode in ('fixed','uniform','cobra','random_pair','no_reuse'):
            old=next(r for r in runs if r['case']==case and r['mode']==mode and r['seed']==2026000)
            new=simulate(np.array(c['p']),mode,old['seed'],old['cap'],old['delta'],old['batch'],[1000,10000,100000])
            for key in ('duels','counts','regret','certified','estimate','correct','trace'):assert old[key]==new[key],(case,mode,key)
            replay.append(dict(case=case,mode=mode,seed=old['seed'],matched=True))
    # Censored means, certification and accuracy in the PDF all derive from these groups.
    data=dict(summary_groups_recomputed=checked,primary_records=len(runs),representative_replays=replay,
              default_weight_replays=json.loads((ROOT/'results/weight_summary.json').read_text())['replayed_original_runs'],
              matched_fields=['duels','counts','regret','certified','estimate','correct','trace'],
              excluded_field='cpu_seconds is elapsed time and varies between runs',all_checks_passed=True)
    (ROOT/'results/reproducibility.json').write_text(json.dumps(data,indent=2));print('Recomputed',checked,'groups and exactly replayed',len(replay),'representative runs')

if __name__=='__main__':main()
