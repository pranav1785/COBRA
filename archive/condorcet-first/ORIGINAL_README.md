# COBRA

## Condorcet-Or-Borda Reuse Algorithm

**Pranav Bhatnagar — ED23B037**  
**Praveen Kumar S — ED23B038**

A Condorcet-first preference learner with a Borda fallback. The study asks whether comparisons collected during Condorcet diagnosis reduce the additional duels needed to certify a Borda winner.

- [Final report](report/main.pdf)
- [LaTeX source](report/main.tex)
- [Experiment code](experiments/run_study.py)
- [Detailed study notes](README_STUDY.md)
- [Measured results](report/results)

The report contains the correctness argument, explicit finite-horizon regret assumptions, paired synthetic experiments, and disclosed cyclic restrictions from PrefLib skating and ERS profiles. It does not claim unknown-gap guarantees or population-level validation.

The main run records are losslessly compressed in `report/results/runs.json.gz`; the report generator reads either that file or an uncompressed `runs.json`. Raw original voter files are downloaded by the supplied scripts rather than redistributed here.
