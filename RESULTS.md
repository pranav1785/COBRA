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

All 17 unit/integration tests pass. Independent numerical checks cover all 8,560 records; no incorrect certificate was observed. The final PDF has 11-point text, a cover and contents, and 15 pages from introduction through references. Conclusions are mixed and instance-dependent, as the professor's rubric permits.
