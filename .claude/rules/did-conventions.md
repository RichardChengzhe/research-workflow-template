---
paths:
  - "code/**/*did*.do"
  - "code/**/*event*study*.do"
  - "code/**/*csdid*.do"
  - "code/**/*drdid*.do"
  - "code/**/*did*.py"
---

# DiD / Event-Study Conventions (Callaway-Sant'Anna practitioner standard)

Methodological standards for difference-in-differences and event-study work, after Callaway & Sant'Anna (2021), Sant'Anna & Zhao (2020), and Roth, Sant'Anna, Bilinski & Poe (2023, *"What's Trending in DiD?"*). The skill [`/did-event-study`](../skills/did-event-study/SKILL.md) implements this; this rule keeps any DiD work in the repo consistent with it.

**The governing principle: the paper and the original author code are the source of truth; translated wrappers and printed numbers are derived artifacts to be verified against them.** If a result looks implausible, debug the wrapper -- sample, weights, clustering, data construction, software engine, target mapping -- *before* interpreting it.

This is a Stata-first template. The Stata commands `csdid` (Rios-Avila, Sant'Anna & Callaway) and `drdid` are the working implementations; `csdid` exposes the `asinr` ("as in R") option precisely so its numbers reproduce the canonical R `did`/`DRDID` packages. Where a published paper's author code is in another language, *that* code is the truth for its numbers (see Verification).

## Data & coding -- HARD
- Data MUST be **LONG**: one row per unit-period. In Stata, `xtset id period` before estimation.
- `gvar` (group) = the **first period a unit is treated**; **never-treated coded EXACTLY `0`** (`csdid ..., gvar(first_treat)`).
- The id must be **time-invariant and numeric**, and **unique within each period**. Check panel balance before any balanced-panel estimation -- unbalanced or duplicate `(id,period)` data errors or silently changes the estimand (balancing drops attriters -> a different target).
- These estimators are **staggered-adoption / absorbing only** -- once treated, always treated. No reversal.
- `ATT(g,t)` is identified only for `t >= g`; `t < g` estimates are **pseudo-ATTs for pre-testing only** (valid only under no-anticipation).

## Estimator -- HARD
- **Doubly robust is the default:** `csdid y covariates, ivar(id) time(period) gvar(g) method(dripw)` (DR with inverse-probability-tilting PS + WLS outcome regression). The `method()` choice matters only when covariates are included.
- Simple 2x2 -> `drdid`; multi-period / staggered -> `csdid` (which calls the DR 2x2 engine internally per `ATT(g,t)`).
- Covariates must be **time-invariant / baseline** (time-varying -> use the base-period value; never condition on post-treatment / treatment-affected covariates -- "bad controls").
- A **TWFE event study** (`reghdfe y i.rel_time##treat, absorb(id period) cluster(id)`) is a *benchmark to compare against*, NOT the headline under staggered timing -- it is contaminated by forbidden comparisons (negative weights). For an interaction-weighted estimator robust to heterogeneity, use `eventstudyinteract` (Sun & Abraham 2021).

## Control group -- HARD
- **`notyettreated` is the default for staggered designs** (`csdid ..., notyet`) -- a larger, time-varying comparison that imposes stronger cross-group parallel trends ("no free lunch"); use never-treated for a clean 2xT design.
- **Never use already-treated units as controls** under heterogeneity (the source of "forbidden comparisons").

## Inference -- HARD
- Multiplier bootstrap with **uniform / simultaneous** bands for event-study plots: `csdid ..., wboot` then `csdid_plot` / `estat event` (>= 1000 reps; far more for publication). **Never** ship pointwise-only bands as the headline.
- `set seed` before any estimation -- inference is bootstrap-based.
- Cluster at the level treatment is independently assigned, normally the unit (`cluster(id)`); at most two clustering dimensions. **Few treated clusters** need a wild-cluster bootstrap (`boottest` after the TWFE benchmark; `csdid`'s `wboot`).
- Report design-relevant weights, and report results weighted *and* unweighted.

## Aggregation & reporting -- HARD
- **Always aggregate;** never present the full `ATT(g,t)` matrix as the result. Use `estat` after `csdid`: `estat simple` is **discouraged as the headline** (overweights early-treated).
- Headline = **Overall ATT** from `estat group` (group-aggregated); dynamics = `estat event`; per-period = `estat calendar`.
- Event-study plots show **both** simultaneous and pointwise bands. Map every table/figure to its generating script + line.

## Diagnostics -- HARD (none skippable)
- **Pre-trends is a PRE-TEST, not a test** -- *evidence on credibility*, never proof. Do **NOT** pre-test with a TWFE event study (it can reject PT under selective timing even when it holds); use the `ATT(g,t)` pre-test from `csdid` (`estat pretrend` / the `t < g` coefficients).
- **Sensitivity is robustness, not a gate:** report **HonestDiD** (Rambachan & Roth) breakdown values -- available in Stata via the `honestdid` package, which post-processes a `csdid`/event-study estimate. Parallel trends is **not** invariant to levels vs logs -- check functional-form sensitivity explicitly.
- Confirm the `csdid` regression-adjustment variant matches the TWFE event study in simple cases, so divergence is attributable to *design* (negative weights), not a coding bug.

## Continuous / dose treatment
- For a continuous dose, the design is changing fast (Callaway, Goodman-Bacon & Sant'Anna). Use the dose-response tooling carefully; the dose covariate must carry its **real** pre-treatment value (**not 0**). Treat any continuous-dose result as more fragile and document the estimand.

## Verification -- HARD
- **The canonical R packages (`did`/`DRDID`) are the estimator benchmark.** A Stata (`csdid`/`drdid` with `asinr`) or Python port must reproduce R to `abs_diff < 1e-6` on the point estimate AND the analytic SE (bootstrap-SE and cosmetic graphing differences excepted).
- **Replicating a published paper is a separate check:** translate from, and verify against, *that paper's* original author code (often Stata) -- there, the paper's author code is the truth for its numbers. Benchmark against the actual `esttab`/`outreg2` outputs, not printed numbers; match to `1e-6`, loosening only deliberately and documented.
- "Replication first -- match original numbers before extending." See [`replication-protocol.md`](replication-protocol.md).

## Pitfalls -- DON'T
- Read pre-trends (or anything) off **dynamic TWFE** event-study coefficients under staggered timing.
- Use **already-treated** units as controls.
- **Over-read pre-trends** -- condition the analysis on "passing" a pre-test, or treat passing as proof of PT.
- Wrong **clustering** level (cluster where treatment is independently assigned).
- Ignore **functional form** -- PT in levels != PT in logs.
- Present a **simple/unweighted aggregate** or the raw `ATT(g,t)` matrix as the headline.
- Condition on **post-treatment / treatment-affected covariates** ("bad controls").
- Interpret an implausible number before **debugging the wrapper**.

## Cross-references
- [`.claude/skills/did-event-study/SKILL.md`](../skills/did-event-study/SKILL.md) -- the pipeline.
- [`replication-protocol.md`](replication-protocol.md) -- match original numbers first.
- [`inference-robustness.md`](inference-robustness.md) -- multiple-testing and spec-robustness battery around the DiD estimate.
- [`python-stata-conventions.md`](python-stata-conventions.md) -- coding standards for the `.do`/`.py` scripts.
- Canonical resources: <https://psantanna.com/did-resources/> (the JEL Practitioner's Guide, *What's Trending*, the packages).
