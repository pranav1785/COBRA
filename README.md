# COBRA — Confidence-Optimized Borda Ranking Algorithm

DA5453, Learning from Human Preferences, IIT Madras.
Pranav Bhatnagar (ED23B037) and Praveen Kumar S (ED23B038).

This is the **Borda-only redesign**. There is no Condorcet diagnosis or objective switching in the active pipeline. The question is whether adaptive comparison allocation and valid reuse beat a strong, confidence-stopping uniform-opponent baseline. The answer is instance-dependent; negative savings and capped runs are included.

## Method and guarantee

COBRA stores reciprocal pair statistics, averages simultaneous pair confidence bounds into Borda bounds, and intersects them with designated uniform-opponent bounds. Three safe sampling blocks alternate with one leader/rival weighted-uncertainty block. The policy receives feedback only, never the true preference matrix or gap. A strict separated-interval certificate is required; a budget-limited empirical answer is explicitly uncertified.

The report proves simultaneous correctness and a conservative safeguard bound of order `K / gap² * log(K / (delta * gap))`, plus block overhead. With a supplied horizon and `delta=T^-2`, explore-then-self-exploit gives the stated gap-dependent logarithmic finite-horizon regret bound. The adaptive heuristic has no sharper theorem here. Exact Borda ties have no finite strict-winner guarantee. These are standard confidence mechanisms combined for a course investigation, not a publication-level novelty claim.

## Contents

- `cobra/core.py`: feedback-only policies, bounds, certificates.
- `cobra/simulation.py`: independent stationary duel simulator and Borda regret.
- `baselines/`: documentation of fixed/uniform modes implemented in the shared core.
- `experiments/borda_study.py`: all fixed-seed synthetic, full-profile real, and horizon experiments.
- `experiments/prepare_data.py`: strict-ranking parser and optional source download.
- `experiments/analyse_borda.py`: numeric summaries, paired bootstrap intervals, plots.
- `tests/test_borda.py`: deterministic and integration checks.
- `results/`: compressed raw per-seed runs, full configurations, summaries, versions.
- `data/borda/`: full empirical matrices and metadata. The two selected original ranking files are included; no large raw collection is needed.
- `figures/`: vector PDF figures.
- `report/main.tex`, `report/references.bib`, `report/main.pdf`: complete report.
- `archive/condorcet-first/`: previous report, source, experiments and results, preserved as historical work with a different objective. Do not use its theorems or plots to describe the new algorithm.

## Reproduce

Tested with Python 3.13.1; numerical package versions are pinned in `requirements.txt` and recorded in `results/config.json`.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python experiments/prepare_data.py
python experiments/borda_study.py
python experiments/analyse_borda.py
python experiments/validate_borda.py
python report/build_borda_report.py
```

Build the PDF from the `report` directory using a BibTeX-capable LaTeX installation:

```bash
tectonic main.tex
```

Alternatively use `pdflatex main`, `bibtex main`, and `pdflatex main` twice. The report uses standard LaTeX packages and figures in `../figures`. Rebuilding from raw runs needs only analysis and report generation, not new simulations. Runtime numbers depend on the machine and load.

## Experimental interpretation

The main cost is mean `min(certification_time, cap)` across **all** seeds. An uncertified run contributes its full cap. This is a restricted mean, not an estimate of uncapped stopping time. Empirical recommendation accuracy is reported separately from certification. All objectives and all regret use Borda scores. The fixed-budget baseline is not used to manufacture sample savings from adaptive stopping; the denominator is Uniform + stop.

Algorithms share confidence targets and block sizes. Matched shadow-allocation ablations share identical feedback until the earlier stopping point; other policies use separate random generators with matched seed indices, without claiming exact common pair-outcome streams. Pairwise reverse evidence is one outcome viewed in two rows, not two independent observations. The directional ablation uses the ordered-pair union correction. The direct-only ablation retains the shadow matrix for allocation but disables its certificate.

Real datasets are PrefLib Worldjunior Ladies Free Skate (24 alternatives, nine judges, full matrix) and ERS Set 5 (26 candidates, 104 ballots, full matrix). Unranked candidates are jointly last; tied voter preferences contribute half. Evaluations simulate new Bernoulli outcomes from empirical probabilities, not new human responses. No smoothing or three-arm subset selection is used.

The three-arm planted case provides a small positive result. Larger planted cases show that uniform stopping can be cheaper. Read the report and `results/summary.json` for exact values, certification rates, negative findings and caps.

## History

The starting remote was `main` at `9ea4ce7ccac4eb9d6f251cd617cf863ebb843ac2`. There was no local git checkout; all existing local files were preserved before redesign. The update uses a normal child commit and does not rewrite history. The verified final commit is supplied with the deliverables.
