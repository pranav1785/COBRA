# Final research summary

COBRA now means **Confidence-Optimized Borda Ranking Algorithm**. It targets the Borda winner from the first duel; the previous Condorcet-diagnosis objective is archived.

The active method combines a reciprocal comparison matrix, simultaneous pair intervals, row-average Borda intervals, and designated uniform-opponent intervals. Three uniform blocks safeguard each adaptive weighted-uncertainty block. It never receives true scores, probabilities or gaps.

## Executed study

8,380 primary runs, seven methods/ablations on inexpensive instances and five core methods on larger instances, plus 180 separately executed known-horizon runs. The study varies K through 50, true Borda gaps from .20 to .01, score-preserving preference cycles, a Condorcet/Borda-disagreement instance, exact ties, and two full human-ranking profiles. Raw numeric records, seeds, caps, versions, CPU time, comparison allocations, accuracy, certificates and Borda regret are retained.

## Findings

- On the three-arm cycle, COBRA uses 14,144 mean duels versus 15,175 for confidence-stopping Uniform: **6.8% saving**, paired bootstrap interval approximately **[2.5%, 10.8%]**.
- On the matched allocation without the shared certificate, the mean is 20,196 duels. Reuse helps substantially under that allocation; its benefit must not be confused with total savings against Uniform.
- Replacing adaptive blocks by random pairs gives 14,522 mean duels on that cycle. This smaller difference does not establish broad superiority for the adaptive heuristic.
- On planted five- and ten-arm instances with Borda gap .1, COBRA uses **31.6% and 36.7% more comparisons**, respectively. The planted three-arm 2.9% saving has an interval including zero.
- Both full real matrices—24-alternative skating and 26-candidate ERS—reach the 500,000-duel cap without certification for either main method. Both recommend the empirical Borda maximizer in 30/30 seeds. This is recommendation accuracy, not successful certified identification.
- At that common real-data horizon, mean Borda regret is lower for COBRA: skating approximately 203,748 versus 245,252; ERS 51,246 versus 58,367. Different pair allocations can change regret without changing capped identification cost.
- Small-gap and tie experiments are retained, including inconclusive runs. Degenerate zero savings at a shared cap do not establish equal uncapped sample complexity.
- Matrix confidence maintenance has greater CPU overhead than the simple baseline.

## Mathematical result and limits

The report proves fixed-count uniform concentration, count-uniform confidence coverage under adaptive pair sampling, row-bound validity, and certificate correctness. The implemented safeguard supports a high-probability sample bound of order `K / gap² * log(K / (delta * gap))`, with explicit block/checkpoint overhead. Exploration followed by certified self-exploitation gives expected regret at most `min(T,N0)+T*delta`. Choosing a supplied horizon's `delta=T^-2` gives the stated gap-dependent logarithmic finite-horizon bound.

This guarantee covers the implemented method through its safeguard. It does not prove an adaptive-specific improvement, a gap-free bound, or an anytime logarithmic expected-regret result. Exact ties have no strict-winner termination guarantee. Standard Borda learning, concentration and active-ranking ideas are credited; publication-level novelty is not claimed.

All 21 unit/integration tests pass, including a safeguard audit over 108 parameter combinations. Independent numerical checks cover the 8,560 original study records plus 600 sensitivity records; no incorrect certificate was observed. The reproducibility audit recomputes all 116 original summary groups and exactly replays 30 representative runs. Another 200 default-weight reruns match the original trajectories exactly, excluding elapsed time. The final PDF has 11-point text, a cover and contents, and 15 pages from introduction through references.

## Weight sensitivity and submission revision

On cycle3, weights 1, 2 and 4 use 14,670, 14,144 and 14,144 mean comparisons. On planted K5, they use 37,177, 35,682 and 35,682. Every cell certifies 100/100 correct winners. Weight 1's additional cost relative to weight 2 is 3.7% on cycle3 (paired bootstrap interval about [-0.4%, 7.9%]) and 4.2% on K5 ([0.8%, 7.7%]). The cycle3 contrast is not resolved at the nominal 95% level. Weights 2 and 4 yield identical stopping counts in all 200 matched trials, but one has different allocation/regret fields; equality of full trajectories is not claimed. The experiment does not establish an optimal weight or remove the complete algorithm's five-arm regression against Uniform.

The revised report adds both methods' certification rates to Table 1, explicit explanations of growing row-bound uncertainty and displaced direct samples, real-life election/judging motivation, clearer finite-horizon assumptions, and separate interpretations of allocation, reuse, and total-cost ablations. Shared cap hits remain an unresolved ordering, not evidence of equal sample efficiency.
