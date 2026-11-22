# COBRA: Condorcet-Or-Borda Reuse Algorithm

Authors supplied by the team: Pranav Bhatnagar (ED23B037), Praveen Kumar S (ED23B038).

The full report is report/main.tex, compiled to report/main.pdf. A final delivery copy is in output/pdf/. The older dir1_approach.pdf is only the preliminary proposal.

## Reproduce

Python 3.13 was used. Install numpy, matplotlib, requests, numba, scipy and pymupdf (the latter two are used for analysis/review rather than the core simulator).

1. python experiments/audit_datasets.py
2. python experiments/fetch_ers.py
3. python experiments/verify.py
4. python experiments/run_study.py
5. python report/real_regret_check.py
6. python report/plot_budgets.py
7. python report/make_report.py
8. Compile report/main.tex from report/ with Tectonic or a standard LaTeX installation. Bibliography is embedded; no BibTeX is required.

Run the scripts from any working directory: paths are relative to the scripts, except compilation which should run from report/ for figure resolution. Downloading data requires internet access. PrefLib source URLs are recorded in audit JSON. The archive contains selected derived matrices and metadata; raw public profiles are downloaded separately by the scripts. ERS incomplete rankings are completed with unranked alternatives tied last, and pairwise voter ties contribute half a win.

## Important interpretation

- The target is Condorcet if it exists, Borda otherwise. This differs from optimizing Borda universally.
- The proof assumes known positive gap lower bounds, known horizon, fixed probabilities and fresh independent binary observations. The learner receives oracle-informed lower bounds in simulation; this is not a practical unknown-gap guarantee.
- Confidence intervals for matrix reuse and direct scores are time-uniform. Diagnostic majority tests use separately calibrated fresh blocks.
- Both paired methods share diagnosis, future draws, checkpoints and caps. Reuse only adds an optional valid early certificate.
- Batching aggregates actual multinomial opponent assignments and binomial outcomes; all physical duels are counted.
- Experiments A/B/D use fixed confidence .05. Only experiment C and the extra real regret check use horizon-calibrated T^-2 confidence, as required for the stated expected-regret theorem.
- The selected real cases are cycle restrictions from two ranking collections. Both selected full profiles have a Condorcet winner. The restriction rule is disclosed and is not a prevalence estimate.
- No claim of new published research, held-out population accuracy or universal superiority is made.

## Outputs

report/results/runs.json: all 1776 main-study method/run/horizon outcomes. RUCB completion flags are not meaningful because it does not implement the hybrid stopping criterion.

report/results/summary.json: seeded means, standard errors, correctness, completion and duel counts.

report/results/real_regret.json: additional short-horizon checks on the two selected real subsets.

report/results/budgets.json: conservative sufficient exploration caps and measured costs.

report/figures/: vector PDF plots and PNG previews, including supplementary agreement and real-completion plots not stacked into the main report.

experiments/verify.py: exhaustive strict four-arm tournament checks and seeded stochastic pairing checks. The readable RUCB implementation and accelerated Numba version are both in run_study.py; their random generators differ, so individual seeds do not generate identical trajectories.

Before submission, the named team should independently read the proof, inspect results and verify their identifying details. The report documents AI assistance without asserting unperformed human checks.
