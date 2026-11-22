"""Generate the final report from verified study outputs; no invented numbers."""
from pathlib import Path
import json,gzip,shutil
ROOT=Path(__file__).resolve().parents[1]

def main():
    summary=json.loads((ROOT/'results/summary.json').read_text());savings=json.loads((ROOT/'results/savings.json').read_text())
    meta=json.loads((ROOT/'data/borda/metadata.json').read_text());exe=json.loads((ROOT/'results/execution.json').read_text())
    def s(c,m):return next(x for x in summary if x['case']==c and x['mode']==m)
    def sv(c):return next(x for x in savings if x['case']==c)
    rows=[]
    for c in ['K3','K5','K10','K20','K50','gap0.2','gap0.05','gap0.02','gap0.01','cycle3','cycle5','near_cycle','disagreement','tie','Skating','ERS']:
        a,b=s(c,'uniform'),s(c,'cobra');v=sv(c)
        rows.append(f"{c.replace('_',r'\_')} & {a['mean']:,.0f} & {b['mean']:,.0f} & {a['certified']}/{a['seeds']} & {b['certified']}/{b['seeds']} & {v['saving']:+.1f} \\")
    table='\n'.join(rows)
    abrows=[]
    labels={'uniform':'Uniform + stop','cobra':'COBRA','random_pair':'Random adaptive block','no_reuse':'Direct-only certificate','directional':'Forward evidence only','pair_only':'No safeguard'}
    for m,l in labels.items():
        x=s('cycle3',m);abrows.append(f"{l} & {x['mean']:,.0f} & {x['sd']:,.0f} & {x['certified']}/{x['seeds']} & {100*x['accuracy']:.0f}\\% \\")
    realrows=[]
    for x in meta:realrows.append(f"{x['name']} & {x['k']} & {x['voters']} & {x['cycles']} & {x['borda_winner']} & {x['gap']:.4f} \\")
    performance=[]
    for c in ('Skating','ERS'):
        for m in ('uniform','cobra'):
            x=s(c,m);performance.append(f"{c}: {labels[m]} & {x['certified']}/{x['seeds']} & {100*x['accuracy']:.1f}\\% & {x['cpu']:.2f} \\")
    intervals=[]
    for c in ('K3','K5','K10','cycle3','cycle5','Skating','ERS'):
        x=sv(c);intervals.append(f"{c} & {x['saving']:+.1f} & [{x['ci'][0]:+.1f}, {x['ci'][1]:+.1f}] \\")
    weights=json.loads((ROOT/'results/weight_summary.json').read_text());weightrows=[]
    for c in ('cycle3','K5'):
        entries=[next(x for x in weights['summary'] if x['case']==c and x['weight']==w) for w in (1,2,4)]
        weightrows.append(f"{c} & {entries[0]['mean']:,.0f} & {entries[1]['mean']:,.0f} & {entries[2]['mean']:,.0f} & 100/100 \\")
    assert all(x['certified']==100 and x['accuracy']==1 for x in weights['summary'])
    weightfinding='Weights 2 and 4 give identical mean comparison costs in these tests; weight 1 uses '
    for c in ('cycle3','K5'):
        x=next(x for x in weights['contrasts'] if x['case']==c and x['weight']==1)
        weightfinding+=f"{x['extra_cost_vs_weight2']:.1f}\\% more comparisons on {c} (95\\% paired bootstrap interval {x['ci'][0]:.1f}--{x['ci'][1]:.1f}\\%); "
    weightfinding=weightfinding.rstrip('; ')+'. This limited robustness check does not establish an optimal weight or remove the five-arm regression against Uniform.'
    substitutions={'@@TABLE@@':table,'@@ABTABLE@@':'\n'.join(abrows),'@@REALTABLE@@':'\n'.join(realrows),'@@PERFORMANCE@@':'\n'.join(performance),'@@CITABLE@@':'\n'.join(intervals),'@@WEIGHTS@@':'\n'.join(weightrows),'@@RUNS@@':str(exe['runs']),'@@HRUNS@@':str(exe['horizon_runs']),'@@MINUTES@@':f"{exe['seconds']/60:.1f}",
                   '@@S3@@':f"{sv('K3')['saving']:.1f}",'@@S5@@':f"{sv('K5')['saving']:.1f}",'@@S10@@':f"{sv('K10')['saving']:.1f}",
                   '@@CPUU@@':f"{s('K10','uniform')['cpu']:.3f}",'@@CPUC@@':f"{s('K10','cobra')['cpu']:.3f}",
                   '@@SCERT@@':f"{s('Skating','cobra')['certified']}/30",'@@ECERT@@':f"{s('ERS','cobra')['certified']}/30"}
    text=(ROOT/'report/borda_template.tex').read_text(encoding='utf-8')
    substitutions['@@WEIGHTFINDING@@']=weightfinding
    # Normalize row terminators explicitly (two literal TeX backslashes).
    for key in ('@@TABLE@@','@@ABTABLE@@','@@REALTABLE@@','@@PERFORMANCE@@','@@CITABLE@@','@@WEIGHTS@@'):
        substitutions[key]='\n'.join(line.rstrip(chr(92))+chr(92)*2 for line in substitutions[key].splitlines())
    for key,value in substitutions.items():text=text.replace(key,value)
    assert '@@' not in text
    (ROOT/'report/main.tex').write_text(text,encoding='utf-8')
    print('Report source generated from',exe['runs'],'runs')

if __name__=='__main__':main()
