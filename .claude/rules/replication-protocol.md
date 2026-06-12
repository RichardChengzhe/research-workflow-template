---
paths:
  - "code/**/*.do"
  - "code/**/*.py"
  - "code/**/*.sas"
---

# Replication-First Protocol

**Core principle:** Replicate original results to the dot BEFORE extending.

**Producer stance:** You are not only *consuming* a replication — you are *producing* one that an AEA Data Editor, a referee, or future-you can run with a single command from a clean shell, with the environment pinned. Build for that audience from Phase 1 (see Phase 5).

---

## Phase 1: Inventory & Baseline

Before writing any code:

- [ ] Read the paper's replication README
- [ ] Inventory replication package: language, data files, scripts, outputs
- [ ] Record gold standard numbers from the paper:

```markdown
## Replication Targets: [Paper Author (Year)]

| Target | Table/Figure | Value | SE/CI | Notes |
|--------|-------------|-------|-------|-------|
| Main ATT | Table 2, Col 3 | -1.632 | (0.584) | Primary specification |
```

- [ ] Store targets in `quality_reports/replication_targets.md`

---

## Phase 2: Translate & Execute

- [ ] Follow `python-stata-conventions.md` for all coding standards
- [ ] Translate line-by-line initially -- don't "improve" during replication
- [ ] Match original specification exactly (covariates, sample, clustering, SE computation)
- [ ] Save all intermediate results (.dta, .ster, .pkl)
- [ ] Run every script via `./run_all.sh` so a log lands in `output/logs/` (the log is the evidence the step ran)

### Common Pitfalls

| Original | Our Code | Trap |
|----------|----------|------|
| `reg y x, cluster(id)` | Same Stata | Verify df adjustment matches |
| `areg y x, absorb(id)` | `reghdfe y x, absorb(id)` | Check demeaning method matches |
| Python `statsmodels` | Stata `reg` | Default SE computation differs |
| `bootstrap, reps(999)` | Match exactly | Match seed, reps, and bootstrap type |

---

## Phase 3: Verify Match

### Tolerance Thresholds

| Type | Tolerance | Rationale |
|------|-----------|-----------|
| Integers (N, counts) | Exact match | No reason for any difference |
| Point estimates | < 0.01 | Rounding in paper display |
| Standard errors | < 0.05 | Bootstrap/clustering variation |
| P-values | Same significance level | Exact p may differ slightly |
| Percentages | < 0.1pp | Display rounding |

### If Mismatch

**Do NOT proceed to extensions.** Isolate which step introduces the difference, check common causes (sample size, SE computation, default options, variable definitions), and document the investigation even if unresolved.

**The mismatch does not presume the code is correct.** The on-disk output is a *challenger*, not an oracle — a refactor may have broken a previously-correct table, so the *manuscript* number may be the right one and the code the stale/buggy side. Frame it as "one of {paper, code} must change — isolate which," never "revert the code to match the paper."

**A defensible alternative is not a failure.** If the gap is explained by a *concrete, named alternative specification* (e.g. never-treated vs not-yet-treated comparison group, conditional vs unconditional parallel trends, `reghdfe` vs `reg`/`areg` clustering df, MC seed/reps, display rounding), record that named alternative and mark the target **EXPLAINED** rather than FAIL — see the `status` semantics below. A blank or vague note ("unclear") never downgrades a FAIL.

### Replication Report

Save to `quality_reports/replication_report.md`:

```markdown
# Replication Report: [Paper Author (Year)]
**Date:** [YYYY-MM-DD]
**Original language:** [Stata/R/etc.]
**Our code:** [script path]

## Summary
- **Targets checked / Passed / Failed / Explained:** N / M / K / E
- **Overall:** [REPLICATED / PARTIAL / FAILED]

## Results Comparison

| Target | Paper | Ours | Diff | Status |
|--------|-------|------|------|--------|

## Discrepancies (if any)
- **Target:** X | **Investigation:** ... | **Resolution / named alternative:** ...

## Environment
- Stata version, key packages (with versions), Python version, data source
```

---

## Phase 4: Only Then Extend

After replication is verified (all targets PASS or EXPLAINED):

- [ ] Commit replication script: "Replicate [Paper] Table X -- all targets match"
- [ ] Now extend with project-specific modifications
- [ ] Each extension builds on the verified baseline

---

## Phase 5: Producing a Replication Package

Whether replicating someone else's paper or shipping your own, the deliverable an AEA Data Editor / referee checks has a fixed shape:

- **One-command reproduction.** A single entry point regenerates every output the paper cites — for this template that is `./run_all.sh` driving the pipeline order in `pipeline.md` (e.g. `04_analysis.do` / `00_run.do`). For a pure-Stata package, a `99_run_all.do` that `do`-s each numbered script in order serves the same purpose.
- **Numbered, ordered scripts.** Run order must be unambiguous from filenames or from `pipeline.md`.
- **No hard-coded paths.** All paths via Stata globals from `00_run.do`, or Python `pathlib.Path` relative to the repo root.
- **Captured logs.** `output/logs/` holds the captured stdout for each step (run via `run_all.sh`).
- **License + README** at repo root: data source, computational requirements, run instructions.

### Environment pinning (mandatory)

Reproducibility requires recording the *exact* environment, not just the code:

- **Stata:** pin `version NN` at the top of `.do` files; capture installed package versions once (e.g. a small subroutine that logs `about`, `which reghdfe`, `which estout`, `which ivreg2` to `output/logs/sessionInfo.txt`), and list every `ssc install` in the install step.
- **Python:** record `python --version` and a pinned `requirements.txt` (or the conda env export) alongside the package.
- **SAS:** record the SAS version and any WRDS macros `%include`-d; note which steps require WRDS/Duo.

This is what gives the referee / future-you the package versions actually used.

---

## Claims Provenance (passport)

For numeric-claim provenance — recording, per verified number in the manuscript, the exact script invocation and output file that produced it — use the per-paper passport described in [`manuscript-overleaf-sync.md`](manuscript-overleaf-sync.md) and `templates/passport-template.yaml` (when present). The passport reuses the same disposition vocabulary as Phase 3:

- **PASS** — last audit confirmed within tolerance.
- **FAIL** — outside tolerance **and** no concrete named alternative recorded. Blocks `/commit` for the affected files unless explicit override. An UNMATCHED claim always stays FAIL.
- **EXPLAINED** — outside tolerance, **but** the note records a *specific named alternative specification* that accounts for the gap. Surfaced (and meant to flow into a response-to-referees); does **not** block.
- **STALE** — the `source_file` or `output_file` changed after `last_verified_on`; re-audit to refresh.
- **UNVERIFIED** — added to the manuscript but never run through the numeric audit; should not appear in a submission-ready package.

Keep the scope narrow: the passport handles numeric claims with code provenance; citation/named-entity claims are handled separately by the claim-verification path. Both run.
