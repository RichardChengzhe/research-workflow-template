---
paths:
  - "code/**/*.do"
  - "code/**/*.py"
  - "code/**/*.sas"
---

# Inference & Robustness (multiple testing + researcher degrees of freedom)

Advisory standards for the inference choices that decide whether a result survives a sharp referee -- consolidated so they do not live only as a one-line objection. Applies to empirical analysis scripts; the manuscript-side check is in [`/review-paper`](../skills/review-paper/SKILL.md) and the design-side commitment in [`/preregister`](../skills/preregister/SKILL.md).

## Multiple hypothesis testing

When a paper tests **many hypotheses** (several outcomes, subgroups, treatment arms, or specifications), unadjusted p-values overstate significance. Decide the correction **by what you control and pre-register the family**:

- **Family-wise error rate (FWER)** -- control the probability of *any* false rejection. Use when even one false positive is costly (a headline claim).
  - **Romano-Wolf** stepdown (resampling, exploits cross-equation dependence -- far less conservative than Bonferroni; Stata `rwolf`/`rwolf2`) is the modern default for a small family.
  - Holm-Bonferroni as a distribution-free fallback; plain Bonferroni only for a tiny family.
- **False discovery rate (FDR)** -- control the *expected share* of false rejections among rejections. Use for **many** hypotheses where some false positives are acceptable (screening, heterogeneity scans).
  - Benjamini-Hochberg; **Anderson (2008) sharpened two-stage q-values** are the standard in applied micro (Anderson distributes `fdr_sharpened_qvalues.do` / `minq.ado`; the World Bank "Multiple Hypothesis Testing commands in Stata" post catalogs the current options -- verify the exact command name against its live docs before use).
- **Pre-register the family and the correction** (the unit of correction is a researcher degree of freedom). Report both unadjusted and adjusted; never pick the family that makes the result survive.

## Standard-error / clustering choices

- Cluster at the level treatment is independently assigned (Cameron, Gelbach & Miller). **Multi-way clustering** (e.g. firm and time) via `reghdfe ..., vce(cluster firm time)` / `vce(cluster id##period)` when shocks are correlated along two dimensions. Report whether the headline survives one-way vs two-way.
- Time-series / autocorrelated errors: Newey-West (`newey ..., lag(k)`), with the lag length stated and justified.
- **Few clusters** break the cluster-robust asymptotics: use a wild-cluster bootstrap (`boottest` after the estimate) and report it as the inference of record, not an afterthought.

## Researcher degrees of freedom / specification robustness

A single specification is a point on a garden of forking paths. Make the robustness explicit:

- **Show the specification is not cherry-picked** -- a specification / multiverse curve (sweep the defensible covariate sets, sample restrictions, functional forms; report the *distribution* of estimates, not one).
- **Leave-one-out / influential observations** -- confirm the result is not driven by a few units or one cluster.
- **Inference robustness** -- alternative clustering levels, wild-cluster bootstrap with few clusters, randomization inference where the design supports it.
- For **DiD specifically**, the robustness battery is the diagnostic + sensitivity suite in [`did-conventions.md`](did-conventions.md) (HonestDiD / functional-form sensitivity), not a TWFE pre-test.

## Simulation / Monte Carlo (if used)

If a result rests on a simulation, report **Monte Carlo standard error (MCSE)** for every reported simulated quantity (bias, coverage, rejection rate). A simulated number without its MCSE is not interpretable -- "coverage is 0.94" means nothing without the +/- from the number of replications.

## Reporting

- State the **family** and the **correction method** up front; report unadjusted *and* adjusted p-values/q-values.
- A robustness check that only ever confirms the headline is theatre -- report the spec where the result *weakens*, and interpret it.

## Cross-references
- [`.claude/skills/review-paper/SKILL.md`](../skills/review-paper/SKILL.md) -- manuscript-side inference review.
- [`.claude/skills/preregister/SKILL.md`](../skills/preregister/SKILL.md) -- commit the family and correction in advance.
- [`.claude/skills/power-analysis/SKILL.md`](../skills/power-analysis/SKILL.md) -- detectable-effect sizing.
- [`did-conventions.md`](did-conventions.md) -- the DiD-specific robustness suite.
