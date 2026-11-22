"""Audit every retained numeric record and independently recompute summaries."""
from pathlib import Path
import gzip,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from cobra.core import scores

def main():
    cfg=json.loads((ROOT/'results/config.json').read_text());cases={c['name']:c for c in cfg['cases']}
    runs=json.loads(gzip.decompress((ROOT/'results/runs.json.gz').read_bytes()));keys=set();certwrong=[]
    for r in runs:
        c=cases[r['case']];p=np.array(c['p']);b=scores(p);n=np.array(r['counts'])
        key=(r['case'],r['mode'],r['seed']);assert key not in keys;keys.add(key)
        assert np.array_equal(n,n.T) and np.all(n.diagonal()==0)
        assert n.sum()==2*r['duels'] and 0<r['duels']<=c['cap']
        expected=float(np.sum(n*(b.max()-(b[:,None]+b[None,:])/2))/2)
        assert np.isclose(expected,r['regret'],atol=1e-7)
        assert r['correct']==bool(np.isclose(b[r['estimate']],b.max(),atol=1e-12,rtol=0))
        if r['certified'] and not r['correct']:certwrong.append(key)
        if not r['certified']:assert r['duels']==r['cap']
    summary=json.loads((ROOT/'results/summary.json').read_text())
    for s in summary:
        rr=[r for r in runs if r['case']==s['case'] and r['mode']==s['mode']]
        assert len(rr)==s['seeds'];assert np.isclose(np.mean([r['duels'] for r in rr]),s['mean'])
        assert sum(r['certified'] for r in rr)==s['certified']
    # Validate score-preserving circulations and all intended gaps.
    for c in cases.values():
        b=scores(np.array(c['p']))
        if c['name'].startswith('gap'):assert np.isclose(np.sort(b)[-1]-np.sort(b)[-2],float(c['name'][3:]))
    hr=json.loads(gzip.decompress((ROOT/'results/horizon.json.gz').read_bytes()))
    p=np.full((3,3),.5);p[0,1:]+=.2*2/3;p[1:,0]-=.2*2/3;b=scores(p)
    for r in hr:
        n=np.array(r['counts']);assert r['delta']==r['horizon']**-2
        assert n.sum()==2*r['duels'] and r['duels']<=r['horizon']
        expected=float(np.sum(n*(b.max()-(b[:,None]+b[None,:])/2))/2)
        assert np.isclose(expected,r['regret'],atol=1e-7)
        expected_final=expected+(r['horizon']-r['duels'])*(b.max()-b[r['estimate']])
        assert np.isclose(expected_final,r['trace'][-1]['regret'],atol=1e-7)
        if r['certified'] and not r['correct']:certwrong.append(('horizon',r['mode'],r['seed'],r['horizon']))
    wr=json.loads(gzip.decompress((ROOT/'results/weight_runs.json.gz').read_bytes()))
    ws=json.loads((ROOT/'results/weight_summary.json').read_text())
    for r in wr:
        p=np.array(cases[r['case']]['p']);b=scores(p);n=np.array(r['counts'])
        assert n.sum()==2*r['duels'] and np.array_equal(n,n.T)
        expected=float(np.sum(n*(b.max()-(b[:,None]+b[None,:])/2))/2)
        assert np.isclose(expected,r['regret'],atol=1e-7)
        if r['certified'] and not r['correct']:certwrong.append(('weight',r['case'],r['leader_weight'],r['seed']))
    for g in ws['summary']:
        rr=[r for r in wr if r['case']==g['case'] and r['leader_weight']==g['weight']]
        assert len(rr)==g['seeds'];assert np.isclose(np.mean([r['duels'] for r in rr]),g['mean'])
        assert sum(r['certified'] for r in rr)==g['certified']
    result=dict(records=len(runs),horizon_records=len(hr),weight_records=len(wr),groups=len(summary),wrong_certificates=certwrong,all_numeric_checks_passed=True)
    (ROOT/'results/validation.json').write_text(json.dumps(result,indent=2));print(result)

if __name__=='__main__':main()
