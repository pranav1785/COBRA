"""Final-report dataset presentation; called by make_report.py."""
import numpy as np

def sections(meta,summary,checks,fig):
    out=[]
    for m in meta:
        name=m['name'];title="Figure-skating judges' rankings" if name=='Skating' else 'Electoral Reform Society election ballots'
        p=np.array(m['matrix']);matrix='\\begin{pmatrix}'+r'\\'.join('&'.join(f'{v:.4f}' for v in rr) for rr in p)+r'\end{pmatrix}'
        rows={method:next(r for r in summary if r['experiment']=='D' and r['case']==name and r['method']==method) for method in ['Restart','Reuse']}
        vals={method:np.mean([r['regret'] for r in checks if r['case']==name and r['method']==method]) for method in ['Restart','Reuse','RUCB']}
        complete=sum(r.get('complete',False) for r in checks if r['case']==name and r['method']=='Reuse')
        saving=100*(rows['Restart']['additional_mean']-rows['Reuse']['additional_mean'])/rows['Restart']['additional_mean']
        body=r'\FloatBarrier\section{Implementation: '+title+'}\n'
        body+=f"We apply the method to {'judges ranking competitors in 1998 figure-skating competitions' if name=='Skating' else 'ranked election ballots collected by the Electoral Reform Society'}, from PrefLib \\cite{{{'skate' if name=='Skating' else 'ers'}}}. The selected profile contains {m['voters']} voters and {m['full_k']} alternatives. Its original identifier is \\texttt{{{m['file']}}}. The full profile has a strict Condorcet winner (original candidate ID {m['full_cw']+1}). We do not claim that the complete profile is a no-Condorcet instance.\n\n"
        body+=r'\textbf{Construction of the implementation case.} We scan files and candidate triples lexicographically and retain the first strict three-cycle with a unique Borda winner. Selection uses the preference profile, not the simulated performance of either method. This produces a disclosed cyclic stress test rather than an estimate of the prevalence of cycles. '
        body+=f"The retained original candidate IDs are {', '.join(map(str,m['ids_one_based']))}, in that order. The observed pairwise matrix is\n\\[P={matrix}.\\]\n"
        if name=='ERS':
            body+=r'ERS ballots can be incomplete. We place unranked candidates jointly last, following the documented tied-completion convention. Each voter tie contributes half a win in either direction. A simulated duel is then binary, equivalent to independently drawing a voter and fairly breaking a tied comparison. The audit also found full ERS Set 5 without a strict Condorcet winner, but with pairwise ties; that full profile falls outside our uniform-separation theorem.\par'
        else:
            body+=r'The strict judge rankings yield a directed majority cycle on these three competitors, although the full competition retains a Condorcet winner. Sampling a pair uses the empirical fraction of judges preferring its row candidate.\par'
        body+=fig('implementation_'+name.lower(),f'{title}: additional duels needed for certification over 60 paired runs. Both methods share diagnosis and the fresh sample stream; Reuse has the additional shared-matrix stopping option. The curves include every run.','0.88')
        body+=f"\\textbf{{Results on this dataset.}} Mean additional duels were {rows['Restart']['additional_mean']:,.0f} for Restart and {rows['Reuse']['additional_mean']:,.0f} for Reuse, a {saving:.1f}\\% reduction. The common diagnosis cost averaged {rows['Reuse']['diagnostic_mean']:,.0f} duels. All 60 runs per method completed with the correct Borda target at the identification confidence budget.\n\n"
        body+=f"At horizon $T=300{{,}}000$, using the stricter horizon-calibrated budget, mean regret was {vals['Reuse']:,.0f} (Reuse), {vals['Restart']:,.0f} (Restart), and {vals['RUCB']:,.0f} (RUCB), with {complete}/20 Reuse runs completing. "
        body+=('The reduction in fresh sampling accompanies successful fallback in this case. ' if complete else 'The hybrid diagnoses remained unfinished: lower observed regret here is not evidence of successful fallback. ')
        body+=r'These are simulations conditional on an empirical matrix, not new human trials or held-out population predictions. Small voter samples, the intentional candidate restriction, and any tied-completion choice limit generalization.\par'
        out.append(body)
    return out
