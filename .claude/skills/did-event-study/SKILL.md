---
name: did-event-study
description: Run a staggered difference-in-differences / event-study analysis to the Callaway–Sant'Anna practitioner standard — a Stata-first thin wrapper over the canonical packages (csdid / drdid, eventstudyinteract, honestdid; reghdfe TWFE benchmark-only), enforcing the doubly-robust default, a mandatory diagnostic + sensitivity suite, uniform-band inference, replicate-and-verify-against-source discipline, and a graded credibility verdict. Use when user says "run a DiD", "event study", "staggered adoption", "Callaway Sant'Anna", "csdid", "Sun Abraham", "did with multiple periods", or points at panel data with a treatment-timing variable. NEVER reimplements an estimator.
argument-hint: "[data path] [--outcome --unit --time --gvar] [--control nevertreated|notyettreated] [--continuous] [--r]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash"]
effort: high
---

# /did-event-study — DiD / event study, Callaway–Sant'Anna practitioner standard (Stata-first)

This is a **thin orchestrator over the canonical Stata packages** — it never reimplements an estimator. It walks the practitioner workflow from *Difference-in-Differences with Multiple Time Periods* (Callaway & Sant'Anna 2021), the *Doubly Robust DiD* estimators (Sant'Anna & Zhao 2020), and the *"What's Trending in DiD?"* synthesis (Roth, Sant'Anna, Bilinski & Poe 2023), and it follows the **replicate-and-verify-against-source** discipline.

> **Actor → Critic.** The skill is the *Actor*: it runs the packages and the diagnostics. It then puts on the *Critic* hat for **Phase 8 — a graded credibility verdict**, never a binary "passes." A mismatch with a pre-test is *evidence on credibility*, not a gate. (This actor/critic + mandatory-diagnostic + graded-credibility shape mirrors [`.claude/rules/orchestrator-protocol.md`](../../rules/orchestrator-protocol.md) and the verification posture of [`/audit-reproducibility`](../audit-reproducibility/SKILL.md).)

> **Read first:** [`.claude/rules/did-conventions.md`](../../rules/did-conventions.md) — the HARD standards this skill enforces (data coding, DR default, control group, inference, aggregation, verification, and the pitfalls to avoid). Then the canonical resources in §Resources.

**This template is Stata-first.** The working implementations are `csdid` (Rios-Avila, Sant'Anna & Callaway — Callaway–Sant'Anna `ATT(g,t)`), `drdid` (the 2×2 engine), `eventstudyinteract` (Sun & Abraham interaction-weighted estimator), and `honestdid` (Rambachan & Roth sensitivity). `reghdfe` provides the TWFE event-study **benchmark only**. The methodological defaults (`notyettreated` control, HonestDiD led by relative-magnitudes `Mbar`, DR default, TWFE benchmark-only) follow the Callaway–Sant'Anna practitioner standard codified in `did-conventions`.

## When to use

- Staggered or 2×T adoption with panel or repeated cross-sections; a binary absorbing treatment, or a **continuous dose**.
- Any time someone reaches for a TWFE event study under staggered timing — route here instead.

## When NOT to use

- A single 2×2 with one pre / one post and no covariates is a one-liner — still use `drdid`, but you don't need the full pipeline.
- Reversible / switching treatments (units turning on **and** off): these estimators assume absorbing treatment. Stop and reconsider the design.

## Workflow (fixed order)

### Phase 0 — Reproducibility setup (gate before any estimation)
- `set seed` (and `set sortseed`) is **REQUIRED** — all inference is bootstrap-based. Pick one and pin it; record it via [`/capture-environment`](../capture-environment/SKILL.md).
- Pin software (`version NN` at the top of the `.do`; install `csdid drdid eventstudyinteract honestdid reghdfe ftools` and list them). No hard-coded machine paths — Stata paths via globals from `00_run.do` (the `git-guardrails` hook blocks hardcoded paths in `.do`/`.py`).
- One master script runs the pipeline end-to-end (`./run_all.sh "<your_did>.do"`).

### Phase 1 — Design / estimand
- Reshape to **LONG**: one row per unit-period; `xtset id period` before estimation.
- Required columns: outcome `y`, time `period` (`time()`), a **time-invariant numeric** unit id `id` (`ivar()`), and `gvar` = group = **first period treated**; **never-treated coded EXACTLY `0`**.
- Tabulate the roll-out (share of units/population by cohort) to make the design explicit: **2×2 → 2×T → staggered G×T**.
- Pick the estimand up front. The recommended single summary is the **Overall ATT** from `estat group` (group-aggregated); dynamics via `estat event`.

### Phase 2 — Estimator selection
Follow the decision logic in §Estimator selection. Output: which estimator, `method()` (DR/IPW/OR), `control_group`, panel vs RC, covariates yes/no.

### Phase 3 — Estimation (drive the package; do not reimplement)

- **2×2 (one pre / one post):**
  ```stata
  drdid y covs, ivar(id) time(period) tr(treat) drimp
  ```
  IPW-only: `drdid ..., ipw`; OR-only: `drdid ..., reg`.
  - **Pre-flight:** the panel form requires `id` **unique within each period** AND a **balanced** panel. Real datasets often aren't — check first:
    ```stata
    duplicates report id period          // must be 0 duplicate (id,period)
    xtset id period
    xtdescribe                            // confirms balance; unbalanced => see below
    ```
  - **If unbalanced** (the common case): either balance the panel (keep ids present in all periods) — but that is a **different estimand** (the balanced subpopulation), so record it as a named alternative (`EXPLAINED` in the audit), e.g. "full-sample 2×2 = 2.914; balanced-panel DR = 2.972 (19 attriters dropped)"; or treat the waves as repeated cross-sections. DR with **no covariates reduces to the simple 2×2** — `drdid` earns its keep once covariates are added.
- **Staggered / multi-period (G×T or 2×T) — the workhorse:**
  ```stata
  csdid y covs, ivar(id) time(period) gvar(gvar) ///
        method(dripw)        /// doubly robust DEFAULT (only used when covs present)
        notyet               /// not-yet-treated control (staggered); omit for never-treated
        wboot reps(1000) rseed(12345)   // publication: reps(>=10000)
  estat group                // headline Overall ATT
  estat event                // dynamic event-study coefficients
  csdid_plot                 // event-study figure (simultaneous + pointwise bands)
  ```
  `csdid` builds every `ATT(g,t)` from a clean `drdid` 2×2 — that is *why* it avoids the forbidden already-treated-as-control comparisons that bias TWFE. Covariates must be **time-invariant / baseline** (never post-treatment "bad controls").
- **Sun–Abraham (interaction-weighted), heterogeneity-robust event study:**
  ```stata
  eventstudyinteract y rel_t_dummies, cohort(gvar) control_cohort(never_treated) ///
        absorb(id period) vce(cluster id)
  ```
  Use Sun & Abraham (2021) when you want an event study robust to heterogeneous dynamic effects without the full `ATT(g,t)` matrix.
- **TWFE event study — a benchmark/sanity-check, never the headline under heterogeneity:**
  ```stata
  reghdfe y ib(last_pre).rel_time##i.treat, absorb(id period) vce(cluster id)
  ```
  Confirm `csdid`'s regression-adjustment variant (`method(reg)`) matches it in simple cases (SEs differ only because of the bootstrap) so any divergence is attributable to *design* (negative weights), not a coding bug.
- **Continuous dose:** the design is changing fast (Callaway, Goodman-Bacon & Sant'Anna). Use the dose-response tooling carefully; the dose covariate must carry its **real** pre-treatment value (**not 0**), `gvar = 0` for never-treated. Treat any continuous-dose result as more fragile and document the estimand.
- **R parallel (optional, `--r`):** R is **not** the primary stack here, but the canonical `did::att_gt` / `fixest::sunab` packages are a useful cross-check. `csdid`'s `asinr` option exists precisely so its numbers reproduce R's `did`/`DRDID` to `1e-6` — if you run R, hold it and Stata to that tolerance (point estimate + analytic SE; bootstrap-SE and cosmetic graphing differences excepted).

### Phase 4 — Mandatory diagnostics (none skippable)
1. **Pre-trends (a PRE-TEST, not a test):** read pre-treatment `ATT(g,t)` for `t<g` from `estat pretrend` and the event-study `e<0 ≈ 0` (with `e = -1 ≈ 0` under a universal/long base period). Passing is *evidence on credibility*, **not proof** PT holds where you need it. **Do NOT pre-test with a TWFE event study** — under selective timing it can reject PT even when it holds.
2. **Event study:** `estat event` → `csdid_plot` (red = pre pseudo-ATTs, blue = post; fix the y-axis so panels compare). Pseudo-ATTs are valid only under no-anticipation.
3. **Negative-weights / forbidden-comparison check:** satisfied *by design* via `csdid`/`eventstudyinteract`; flag negative TWFE weights as the reason to prefer the `ATT(g,t)` building block (the Goodman-Bacon decomposition / `bacondecomp` makes this concrete).
4. **DR overlap:** inspect propensity-score overlap (trim extreme PS; `csdid` reports the PS model — confirm it converged and overlap is not knife-edge).

### Phase 5 — Sensitivity (ROBUSTNESS, never a pass/fail pre-test)
- **HonestDiD (Rambachan & Roth)** — **lead with the relative-magnitudes `Mbar` breakdown** (headline), also report smoothness `M`. In Stata the `honestdid` package post-processes a `csdid` event-study estimate:
  ```stata
  csdid y covs, ivar(id) time(period) gvar(gvar) notyet agg(event)
  honestdid, pre(1/4) post(5/9) mvec(0(0.5)2)     // relative-magnitudes Mbar breakdown
  ```
  Report the breakdown `Mbar` (the largest violation under which the result still rules out 0). *(The original HonestDiD reference implementation is R; the Stata `honestdid` package wraps it. If you prefer the R path, `HonestDiD::createSensitivityResults_relativeMagnitudes()` on the event-study influence function gives the same breakdown — but the Stata twin above is the primary path here.)*
- **Functional-form sensitivity:** parallel trends is **not** invariant to levels vs logs — check the result under both, and reason about which time-varying confounders could break PT. *(Roth & Sant'Anna's `didFF` diagnostic — implied counterfactual density of Y(0) dipping below 0 ⇒ PT-for-all-functional-forms violated — is R-only; if you have R available run it as a parallel check, otherwise do the levels-vs-logs comparison in Stata and argue the functional form substantively.)*
- **Formal sensitivity should be standard practice.** Pair it with substantive reasoning about the size of a plausible violation.

### Phase 6 — Inference
- Multiplier bootstrap with **uniform / simultaneous** bands: `csdid ..., wboot` then `estat event` / `csdid_plot`. `reps(>=10000)` for publication. **Never** ship pointwise-only bands as the headline.
- Cluster at the level treatment is independently assigned, normally the unit (`cluster(id)`); at most two clustering dimensions. **Few treated clusters** need a wild-cluster bootstrap (`csdid`'s `wboot`; `boottest` after the TWFE benchmark).
- Report design-relevant weights, and report results weighted *and* unweighted.

### Phase 7 — Aggregation & reporting
- `estat event` for the event study; `estat group` for the headline **Overall ATT**; `estat calendar` per period. **Avoid `estat simple` as the headline** (overweights early-treated).
- Report the `e ∈ {0,…,K}` average with its CI, BOTH simultaneous and pointwise bands on the plot, and map **every coefficient/figure to its generating script + line** (the `RESULTS_PROVENANCE.md` / passport map).

### Phase 8 — Credibility verdict (graded, honest — the Critic)
Synthesize the diagnostics into a **graded** verdict (Strong / Moderate / Weak / Not-credible) with explicit reasons — never a binary "passes":
- **Design** — `gvar` coded right (`0` = never-treated)? absorbing treatment? clean control group exists?
- **Pre-trends** — Wald p + visual `e<0 ≈ 0` (state: evidence, not proof).
- **Sensitivity** — HonestDiD breakdown `Mbar`; levels-vs-logs (or `didFF` if run).
- **Overlap** — DR/PS overlap acceptable; trimming not heavily binding.
- **Inference** — uniform bands; seed set; weights reported both ways.

## Estimator selection

```
Continuous dose?            → dose-response tooling (real pre-treatment dose, gvar=0 = never)
else 2 groups × 2 periods?  → drdid y covs, ivar(id) time(t) tr(d) drimp
else many periods/cohorts?  → csdid (wraps drdid per ATT(g,t))   [workhorse]
heterogeneity-robust ES?    → eventstudyinteract (Sun–Abraham)
repeated cross-sections?    → csdid / drdid without the panel option
```
- **Doubly-robust is the default** (`method(dripw)`: IPW propensity score + outcome regression — doubly robust for *inference*). `method()` matters only with covariates.
- **Control group:** **`notyettreated` is the default for staggered G×T** (a larger, time-varying comparison; it imposes stronger cross-group PT — "no free lunch"); use never-treated for a clean 2×T design or when a credible never-treated pool is the right comparison. **Never use already-treated units as controls** under heterogeneity.
- **Under limited overlap**, prefer OR/regression-adjustment over DR.
- **Heterogeneity-robust estimators usually agree** (CS, Sun–Abraham, BJS, dCDH) — the first-order priority is a transparent target parameter + transparent comparison group, not agonizing over the package. `csdid` (Callaway–Sant'Anna) stays the workhorse default.

## Verification / replication standard
- Translate **from**, and verify **against**, the **original author code** — benchmark against the actual `esttab`/`outreg2` outputs, not printed paper numbers.
- **Match the source to `abs_diff < 1e-6`** on BOTH point estimate AND SE; loosen only deliberately and document the scope. "Replication first — match original numbers before extending." See [`replication-protocol.md`](../../rules/replication-protocol.md).
- Mandatory infra: `version` pin, globals (no hardcoded paths), `set seed`, one master script, machine-readable outputs (the `esttab` `.tex`, a `.csv` of coefficients, a per-analysis `verification.csv`).
- **Cross-software check:** `csdid ..., asinr` reproduces R's `did`/`DRDID` to `1e-6` (point + analytic SE); any Python (`csdid`/`differences`) port is held to the same. *(Distinct from replicating a published paper, where that paper's original author code — often Stata — is the truth for its numbers.)*

## Resources (canonical, public)
- **did-resources hub:** <https://psantanna.com/did-resources/> — the curated list (the JEL Practitioner's Guide, *What's Trending*, the DiD checklist, all packages). **Lead here.**
- **Stata packages:** `csdid` + `drdid` (`ssc install csdid drdid`) · `eventstudyinteract` (Sun–Abraham) · `honestdid` · `bacondecomp` · `boottest` · `reghdfe`.
- **R parallels (optional):** `did` <https://bcallaway11.github.io/did/> · `DRDID` <https://psantanna.com/DRDID/> · `fixest::sunab` · `HonestDiD` · `didFF`.
- **Papers:** Callaway & Sant'Anna (2021) <https://doi.org/10.1016/j.jeconom.2020.12.001> · Sant'Anna & Zhao (2020) <https://doi.org/10.1016/j.jeconom.2020.06.003> · Sun & Abraham (2021) <https://doi.org/10.1016/j.jeconom.2020.09.006> · Roth & Sant'Anna (2023, *Econometrica*) <https://doi.org/10.3982/ECTA19402> · Rambachan & Roth (2023, HonestDiD).

## Output
Write to `output/` (tables → `output/tables/`, figures → `output/figures/`, intermediate `.ster` → `output/results/`): the master `.do`, the `ATT(g,t)` + aggregations, the event-study figure (simultaneous + pointwise bands), the HonestDiD sensitivity, a `verification.csv`, and a `did_credibility_verdict.md` (the Phase 8 graded verdict + every table→script:line map).

## Exit behavior
- Exit 0 with the graded verdict. A **Not-credible** verdict or a failed source-verification (`abs_diff ≥ 1e-6`) is surfaced prominently — never silently passed.
- Pairs with [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) (numeric claims ↔ outputs) and [`/replication-package`](../replication-package/SKILL.md) (the deposit).

## What this skill does NOT do
- **Reimplement any estimator** — it drives the packages; if a number looks implausible, debug the wrapper / sample / weights / clustering / data construction / engine **before** interpreting it.
- **Handle reversible treatments**, or use TWFE as the headline under staggered timing.
- **Replace your judgment** — the credibility verdict is advisory; you are the auditor.

## Flags
- `--outcome` `--unit` `--time` `--gvar` — map columns to `y`/`id`/`period`/`gvar`.
- `--control` `<nevertreated|notyettreated>` — comparison group (default per §Estimator selection).
- `--continuous` — continuous-dose mode (real pre-treatment dose).
- `--r` — also run the R twin (`did`/`fixest::sunab`) for the dual-software cross-check (optional; Stata is the primary path).

## Cross-references
- [`.claude/rules/did-conventions.md`](../../rules/did-conventions.md) — the enforceable standards this skill implements.
- [`.claude/rules/inference-robustness.md`](../../rules/inference-robustness.md) — multiple-testing + spec-robustness battery around the DiD estimate.
- [`.claude/skills/audit-reproducibility/SKILL.md`](../audit-reproducibility/SKILL.md) · [`.claude/skills/replication-package/SKILL.md`](../replication-package/SKILL.md) · [`.claude/skills/power-analysis/SKILL.md`](../power-analysis/SKILL.md).
