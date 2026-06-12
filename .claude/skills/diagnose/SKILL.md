---
name: diagnose
description: Root-cause a failing or WRONG empirical result with a disciplined reproduce -> minimise -> hypothesise -> instrument -> fix loop, instead of guessing-and-poking. Use when the user says "why is my regression wrong", "this number changed", "my script errors out", "the result won't reproduce", "debug this", "this estimate looks wrong", or "it worked yesterday". Tuned for research code (Stata / Python / SAS): look-ahead leakage, merge-key collision, winsorize-order, missing/coercion, FE mis-specification, clustering/SE choices, weighting, collinearity/convergence, seeds, package/version drift, and SAS results landing in `.lst` while errors hide in `.log`. Use `--no-fix` to localize the root cause without editing shared or load-bearing files.
argument-hint: "[file, script, or short description of the symptom] [--no-fix]"
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash", "Task"]
effort: high
---

# /diagnose -- root-cause a wrong or failing result

Find *why* an analysis errors, returns the wrong number, or won't reconcile -- with a structured debugging loop rather than scattershot edits. Adapted from the `diagnose` pattern in [mattpocock/skills](https://github.com/mattpocock/skills), reshaped for empirical research code where the bug is usually a *silent* wrong number, not a crash.

The discipline: **never edit before you can reproduce, and never fix before you can explain.** A guessed fix that makes the symptom disappear without a named root cause is how a wrong number gets *laundered* into a published table.

## When to use

- A regression / estimate returns a value you can't explain, or one that changed when nothing should have.
- A script errors out and the stack trace (or the SAS `.log`) doesn't point at the real cause.
- A result "won't reproduce" -- a different number on re-run, on another machine (office PC vs home PC vs HPC), or after a package update.
- A replication claim fails [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) and you need to localize *which* step drifted.

**Diagnose is symptom-driven and single-target: ONE wrong number / ONE failing run.** Use a sibling instead when the job is different:

- [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) -- verify *all* numeric claims in a manuscript against current code (claim-driven, whole-paper). A FAILing claim hands off *to* `/diagnose` to localize the step; if you want to re-check every table number, start there.
- [`/review-code`](../review-code/SKILL.md) -- code-quality review with **no specific symptom**.
- [`/capture-environment`](../capture-environment/SKILL.md) -- snapshot the environment when version/seed drift is the suspect.

## Phases

### Phase 0 -- Pin the symptom (expected vs. actual)

State the bug as a falsifiable gap before touching anything:

- **Expected:** the value/behaviour you believe is correct, and *why* (a prior run, a paper table, a hand calculation, a theoretical sign).
- **Actual:** the value/error observed now, copied verbatim (full message, not a paraphrase).
- **Tolerance:** the threshold that separates "same" from "different", keyed to the source of *expected* -- prior run on the same machine -> machine-epsilon + display rounding; a published table -> rounding + small slack (~1e-3); a hand calculation -> ~0.01; a theoretical prediction -> an economic-significance band, not a decimal. Don't chase 1e-12 floating-point noise; don't wave away a 5% gap. (See [`replication-protocol.md`](../../rules/replication-protocol.md), "Tolerance Thresholds".)

If expected/actual can't be stated, the task is *understanding*, not diagnosis -- stop and clarify first.

> **Anti-laundering note** (from [`replication-protocol.md`](../../rules/replication-protocol.md) "If Mismatch"): the on-disk number is a *challenger*, not an oracle. A refactor may have broken a previously-correct table, so the *manuscript* number may be the right one and the code the buggy side. Frame it as "one of {paper, code} must change -- isolate which," never "make the code match the paper."

### Phase 1 -- Reproduce deterministically (get a reliable red)

A bug you can't reproduce on demand can't be fixed, only hidden.

1. Fix every source of nondeterminism: set the seed (`set seed` / `np.random.seed` / a passed `random_state`), pin the working directory, record the environment (Stata `version`, `pip freeze` / `conda env export`, SAS `&sysvlong`) -- lean on [`/capture-environment`](../capture-environment/SKILL.md).
2. Re-run the smallest unit that exhibits the bug and confirm it fails **every time**. An intermittent failure is its own hypothesis (uninitialised RNG, order-dependent merge, race in parallel/HPC array code) -- note it and carry it into Phase 3.

### Phase 2 -- Minimise to an MWE

Shrink until the bug sits in the open:

- **Data:** subset to the smallest rows/columns that still reproduce (often one firm, one period, a handful of rows / one `gvkey`).
- **Code:** strip the pipeline to the shortest path from input to wrong output; comment out everything the symptom survives without.
- Each removal that *keeps* the bug is information; each that *kills* it is a stronger signal -- record which.

The MWE is the deliverable even if the fix is later trivial: it's what makes the root cause undeniable.

### Phase 3 -- Hypothesise (enumerate, then rank)

List candidate causes *before* testing any -- a written list beats poking because it prevents fixating on the first idea. For empirical-finance code, walk the usual suspects (all of these run cleanly with **no error message** -- they are silent-wrong-number bugs):

- **Look-ahead / leakage** -- a characteristic merged at time t that was not knowable until t+1 (a 10-K signal aligned to the filing *period* not the *availability* date; a forward-filled fundamental; standardizing with a full-sample mean/sd that peeks at the future). The tell: an "too good" in-sample fit or a sign that only appears with contemporaneous alignment.
- **Joins & shape (merge-key collision)** -- a many-to-many `merge` inflating rows; duplicate keys; merging on a *recoded* id (an `egen group` id that is build-specific) instead of the stable key (`gvkey_str` / `cik` / `permno`); an unbalanced panel where balance was assumed.
- **Winsorize / transform order** -- winsorizing (or standardizing, or deflating) *before* the sample filter vs *after*; winsorizing pooled vs by-period; a treatment/rank measure built on the broad population then sub-set (inflates the rate via selection). Order changes the number silently.
- **Types & coercion** -- a numeric read as string; integer overflow (a numeric `gvkey` in a too-small int type wraps); a date parsed wrong; `1/0` <-> `TRUE/FALSE`; Stata extended missing `.a-.z` treated as data.
- **Missingness** -- `NA`/`.` dropped silently; an `na.rm`/`missing` flag flipping a mean; listwise deletion changing the sample mid-pipeline.
- **Specification (FE / SE)** -- wrong clustering level; fixed effects absorbed twice (e.g. firm FE *and* a firm-level control); a lag/lead off by one; `reghdfe absorb()` vs an explicit dummy giving different residual DoF.
- **Bad controls & colliders** -- a control that is post-treatment, a mediator on the causal path, or a descendant of treatment (adding it *induces* bias, invisibly). The tell: a coefficient that moves the "wrong way" or shrinks implausibly when a control enters. (See [`inference-robustness.md`](../../rules/inference-robustness.md).)
- **Numerical stability & convergence** -- an optimizer that didn't converge (check the convergence flag, not just the estimates), a singular/near-singular Hessian, collinearity (a dropped column, high VIF), tolerance too loose.
- **Weighting & aggregation** -- weights silently dropped/truncated; Stata `[fw=]` vs `[pw=]` vs `[aw=]` confused (a frequent silent bug); a weight applied *after* rather than *before* a transform.
- **Environment / log trap** -- a package/Stata version bump that changed a default; a seed that moved; **a SAS step whose results went to the `.lst` while an `ERROR:` sits unread in the `.log`** (a clean exit code can hide a hard error -- always `grep -c "^ERROR" *.log`).

For a genuinely ambiguous bug, fan out the top competing hypotheses to parallel `Task` subagents (one per hypothesis, forked context), each instructed to *try to confirm its own cause on the MWE* and report back -- the loop-first analogue of asking three colleagues at once (see [`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md)).

### Phase 3b -- Reduce the hypotheses (so you don't launder a guess)

Each hypothesis (whether tested by hand or by a fan-out `Task`) returns `{hypothesis, evidence for, evidence against, confidence, one-line conclusion}`. Then:

- **One clear winner** (high confidence, others refuted) -> proceed to Phase 4 to confirm the mechanism.
- **A near-tie** (top two within ~20 percentage points) -> do *not* pick one; go to Phase 4 instrumentation to discriminate.
- **None above ~50%** -> report ambiguity and ask the user; do not edit on a coin-flip.

### Phase 4 -- Instrument & localize (bisect, don't stare)

Test the ranked hypotheses cheaply:

- **Bisect the pipeline** -- check the intermediate value at the midpoint of the data flow; the bug is upstream or downstream of it. Repeat. Binary search finds the offending line in `log2(n)` steps, not `n`.
- **Bisect history** -- if it "worked yesterday", compare against the last-good commit/output to pin the change that introduced it. (`git bisect` is fine here -- it never discards work; the destructive git commands are blocked by [`git-guardrails.py`](../../hooks/git-guardrails.py), this is not one of them.)
- **Instrument with diagnostic primitives**, not guesses -- at each stage inspect:
  - **Stata:** `describe`/`codebook` for types; `count` and `count if missing(x)`; `tab v, missing` to catch a dropped level; `isid gvkey_str mdate` *before and after* every `merge`/`reshape`; `assert _merge==3` (or the expected match pattern); `_N` before vs after a transform.
  - **Python/pandas:** `df.dtypes`; `df.isnull().sum()`; `len(df)` before/after; `df.duplicated(keys).sum()`; `df.merge(..., validate="1:1")` to make a bad join *raise*.
  - **SAS:** `grep -c "^ERROR" *.log` first (the log trap); `proc contents`; obs counts in the `.log` `NOTE:` lines before/after each `data`/`proc sql` step; a `proc sql` self-join check for duplicate keys.

  **The stage where a row count drops/inflates unexpectedly, a level vanishes, `_merge` is not all 3, or correlation jumps is the culprit stage.**

End Phase 4 with a one-sentence root cause naming the exact line/step and mechanism.

### Phase 5 -- Fix & verify (then guard against regression)

**Confidence gate (the anti-laundering rule):** do not apply a fix unless the root cause is named **and** its mechanism is explicit. If Phase 3b left a near-tie, behave as `--no-fix`: report the candidates and ask. Editing research code on an unproven hypothesis is exactly the laundering this skill exists to prevent.

Unless `--no-fix` is set:

1. Apply the **minimal** fix at the root cause -- not a downstream patch that masks it (prefer fixing the bad merge over filtering its duplicate rows afterward; prefer fixing the alignment over dropping the leaked column).
2. Re-run the MWE -> confirm `actual == expected` within the Phase-0 tolerance.
3. Re-run the **full** unit and any dependent step -> confirm the fix didn't move another number. If the result feeds a manuscript claim, re-check it (cross-ref the claim passport in [`/audit-reproducibility`](../audit-reproducibility/SKILL.md)).
4. Note a **prevention** -- the assertion/check that would have caught this earlier. One concrete guard per bug class:

   | Bug class | One-line guard |
   |---|---|
   | Look-ahead / leakage | align on the *availability* date; standardize with an as-of (real-time) mean/sd, never full-sample |
   | Joins & shape | `isid gvkey_str mdate` pre-merge; `assert _merge==3` / pandas `validate="1:1"` |
   | Winsorize / transform order | construct rank/treatment/winsor **after** all merges and sample filters ([`python-stata-conventions.md`](../../rules/python-stata-conventions.md)) |
   | Types & coercion | `assert !missing(real(x))` after read; key id stored as string (`gvkey_str`) |
   | Missingness | explicit missing handling; `assert sum(missing(x))==0` where none expected |
   | Specification | one FE source per dimension; never absorb a dimension you also control for |
   | Weighting | assert the weight type (`[pw=]` vs `[aw=]`) matches intent; `assert !missing(w)` |
   | SAS log trap | `grep -c "^ERROR" *.log` gate after every run; treat a clean exit code as necessary not sufficient |

   Propose the guard; don't silently install a test suite.

With `--no-fix`, stop after the root cause is named and report it for the user to fix by hand.

## Worked example (Stata: a merge-key collision)

A Treat × Post panel coefficient jumped from `-0.0123` to `-0.0071` after a data refresh; nothing in the spec changed.

```stata
* Phase 1 -- reproduce: set seed 1234; same .do, same number every run. Red is stable.

* Phase 2 -- MWE: one industry, two months still shows the jump.
*           Strip to: use panel -> merge covars -> reghdfe. Bug survives the merge step.

* Phase 4 -- instrument: counts before/after the merge
count                                            //  120,000  (expected)
merge m:1 gvkey mdate using "covars", keep(3)    //  ...
count                                            //  122,329  <-- inflated! many-to-many

* Root cause: the refresh assigned a fresh `egen group` numeric `gvkey` per build,
* so the SAME numeric id now maps to a DIFFERENT firm across the two files; the m:1
* merge fans out the mismatched ids, 120,000 -> 122,329 (+2,329 rows), re-weighting
* the estimate. The stable key (gvkey_str) was right there and unused.

* Phase 5 -- minimal fix at the root (merge on the STABLE key), NOT a downstream drop:
merge m:1 gvkey_str mdate using "covars", keep(3)
* re-run: coefficient back to -0.0123 within tolerance; full pipeline re-checked, no other number moved.

* Prevention (Joins & shape guard):
isid gvkey_str mdate
assert _merge==3
```

(The same bug class in Python: `df.merge(covars, on=["gvkey_str","mdate"], validate="m:1")` -- the `validate` makes a bad join *raise* instead of silently inflating.)

## Output / report format

Write a short diagnosis to `quality_reports/diagnoses/YYYY-MM-DD_<slug>.md` (create the directory first: `mkdir -p quality_reports/diagnoses`). These reports may contain **real data values and file paths -- they are project-internal**, like session logs; keep them out of any public replication package. Include:

- **Symptom:** expected vs. actual (+ tolerance).
- **MWE:** the minimal input/code that reproduces it.
- **Root cause:** the exact line/step and mechanism.
- **Fix:** the diff applied (or, with `--no-fix`, the recommended change).
- **Verification:** MWE + full-run re-check results.
- **Prevention:** the guard that would have caught it.

Plus a chat summary leading with the one-line root cause.

## Cross-language notes

The usual-suspects model is illustrated in Stata above, but the bug *classes* are language-neutral; the diagnostic idioms differ:

- **Stata** -- `tab v, missing` and explicit `.`/`.a-.z` extended missing; `set seed`; `version`; `isid`/`assert _merge==3`; weights `[fw=]` vs `[pw=]` vs `[aw=]` is a frequent silent bug. Pair with the project's Stata execution conventions.
- **Python** -- `df.isnull().sum()`; `numpy.nan` is not `None`; pandas vs numpy NaN handling differ; `np.random.seed()` / a passed `random_state`; `merge(..., validate=...)`; `pip freeze`.
- **SAS** -- the **`.lst` vs `.log` trap** is the headline: print output goes to the `.lst`, but a hard `ERROR:` may sit in the `.log` while the job still exits clean -- always `grep -c "^ERROR" *.log` (see the [`/sas`](../sas/SKILL.md) skill's log-reading section). `&sysvlong` for the version; obs counts in `NOTE:` lines before/after each step.

(Forkers in other fields: the structural classes -- Look-ahead, Joins, Order-of-operations, Missingness, Environment -- are discipline-neutral; the econometric suspects above are the worked instance.)

## Exit behavior

| Outcome | Action |
|---|---|
| Root cause **NAMED** (high confidence), fix applied, re-verified | report root cause + diff + prevention |
| `--no-fix` | stop at a named root cause; write the report, make **no** edit to source |
| **Phase 0 blocked** (no statable expected/actual) | halt, ask for the expected value -- diagnosis needs a target |
| **Phase 1 blocked** (cannot reproduce / nondeterminism) | report the nondeterminism *as* the finding (it is the bug class) + how to make the analysis deterministic; do not edit blindly |
| Phase 3b **near-tie / <50%** | report the competing hypotheses and ask the user; do not apply a fix |

## Flags

- `--no-fix` -- Diagnose only: run through naming the root cause (Phases 0-4) and write the report, but make **no** edit to source. Use when you want to apply the fix yourself, or when the file is shared/load-bearing (e.g. `params.do`, the master pipeline) and an automated edit is inappropriate.

## Cross-references

- [`.claude/skills/review-code/SKILL.md`](../review-code/SKILL.md) -- code-quality review with no specific symptom (diagnose is symptom-driven).
- [`.claude/skills/audit-reproducibility/SKILL.md`](../audit-reproducibility/SKILL.md) -- verify all numeric claims against code; diagnose localizes a *single* failing one (and is the natural hand-off from a FAIL).
- [`.claude/skills/capture-environment/SKILL.md`](../capture-environment/SKILL.md) -- snapshot the environment when version/seed drift is the suspect.
- [`.claude/skills/sas/SKILL.md`](../sas/SKILL.md) -- SAS execution + the `.lst`/`.log` log-reading discipline.
- [`.claude/rules/replication-protocol.md`](../../rules/replication-protocol.md) -- the tolerance contract that defines "same number", and the "If Mismatch" hand-off to this skill.
- [`.claude/rules/orchestrator-protocol.md`](../../rules/orchestrator-protocol.md) -- the fan-out primitive used for competing-hypothesis testing in Phase 3.

## What this skill does NOT do

- **Review code with no symptom** -- that is [`/review-code`](../review-code/SKILL.md). Diagnose needs an expected-vs-actual gap to chase.
- **Re-audit every claim in a paper** -- that is [`/audit-reproducibility`](../audit-reproducibility/SKILL.md). Diagnose fixes one bug deeply.
- **Build a test suite** -- it proposes the single guard that would have caught *this* bug; standing test infrastructure is separate dev work.
- **Commit the fix** -- branching / committing is [`/commit`](../commit/SKILL.md)'s job.
