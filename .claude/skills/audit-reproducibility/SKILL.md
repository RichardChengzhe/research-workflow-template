---
name: audit-reproducibility
description: Enforce the replication-protocol.md rule by cross-checking numeric claims in a manuscript against the actual Stata / Python / SAS outputs. Report PASS/FAIL/EXPLAINED per claim against tolerance thresholds. Use before submission and before releasing a replication package.
argument-hint: "[manuscript path] [outputs-dir] (outputs-dir defaults to output/)"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Task"]
effort: high
---

# Audit Reproducibility

Compare numeric claims in a manuscript (point estimates, t-statistics / standard errors, p-values, counts) against the actual outputs produced by the analysis pipeline. Report PASS / FAIL / EXPLAINED per claim against the tolerance thresholds defined in [`.claude/rules/replication-protocol.md`](../../rules/replication-protocol.md).

**Core principle:** If the paper says the treatment coefficient is `-1.632 (t = -2.79)` and the code produces `-1.628 (t = -2.75)`, we verify — **numerically** — that the difference is within the documented tolerance. No more "looks close enough" eyeballing.

## When to use

- **Before submission.** Catches the "I updated the analysis but forgot to update Table 3" bug.
- **Before releasing a replication package.** Verifies the code actually reproduces the paper ([`/replication-package`](../replication-package/SKILL.md) gates on this).
- **After a major revision.** Ensures the paper still matches the latest code.
- **Quality-gate in `/commit`.** Pair with a pre-commit invocation on manuscript + analysis changes.

## Inputs

- `$0` — path to the manuscript (`.tex`, `.md`, `.pdf`). Required. For this template the authoritative source is `manuscript/main.tex` and the per-table `\input{}` files under `output/tables/`.
- `$1` — path to the outputs directory. Defaults to `output/` (the template's `output/tables/`, `output/results/`, `output/logs/`). Recognised alternatives: any directory the user-specified outputs live in.

## Workflow

### Phase 0: Pre-flight

1. Read [`replication-protocol.md`](../../rules/replication-protocol.md) for the tolerance thresholds currently in effect.
2. Verify the outputs directory exists and is non-empty. If empty or stale (older than the manuscript), prompt the user to re-run their pipeline (e.g., `./run_all.sh "04_analysis.do"`) before auditing.
3. Ensure a `sessionInfo.txt` or equivalent environment capture exists in `output/logs/` (produced by [`/capture-environment`](../capture-environment/SKILL.md)).

### Phase 1: Extract claims from the manuscript

Parse the manuscript for numeric claims. Patterns to match (this template reports **t-statistics in parentheses**, not SEs — see [`manuscript-overleaf-sync.md`](../../rules/manuscript-overleaf-sync.md)):

- **Coefficient + t-stat**: `$\beta = -0.0123$ (-3.45)`, `0.342$^{***}$ (3.76)`, a starred coefficient with a parenthesized t below it
- **Table cells**: `& -0.0123$^{***}$ & (-3.45) &` in LaTeX table environments (the `\input{output/tables/...}` file)
- **Counts**: `our sample of 120{,}000 firm-months`, `$N = 120{,}000$`
- **Summary stats**: `mean = 0.423`, `SD = 0.087`
- **P-values / Wald**: `p < 0.01`, `Wald $p = 0.003$`

Record each claim as a tuple:

```
{
  claim_id: "Table2_col3_treatment",
  location: "Table 2, Column 3, row 'Treatment'",
  kind: "point_estimate" | "t_statistic" | "standard_error" | "p_value" | "count" | "percentage",
  reported_value: -1.632,
  uncertainty: -2.79,               # t-stat for a coefficient row (or SE if the table uses SEs)
  significance_stars: 3,            # 0-3 or None
  raw_context: "the treatment effect of -1.632 (t = -2.79) indicates..."
}
```

Write the extracted claims to `quality_reports/reproducibility_claims_[manuscript-name].json` so the user can review the extraction before audit.

### Phase 2: Extract results from outputs

Scan `$1` for corresponding values. Priority order for this template:

1. **`esttab` `.tex` tables** under `output/tables/` — parse LaTeX table cells directly; match on column headers + row labels. This is the **strongest provenance signal**: the cell value comes mechanically from the `.do` file's `esttab` call.
2. **`.csv` summary files** under `output/tables/` or `output/results/` — pandas/`insheet` parse, key-value lookup.
3. **Stata `.ster` estimates / saved `e()` results** — re-load with `estimates use` and read the coefficient/`r(table)` (a tiny `.do` can `estimates use ... ; matrix list r(table)` and write the cell to a temp file).
4. **`.log` / `.smcl` files** (Stata `reghdfe`/`csdid` output) under `output/logs/` — regex extraction of the coefficient block.
5. **`.lst` files** (SAS printed output) — **SAS results land in `.lst`, not `.log`**; regex the relevant `proc` output.
6. **`.dta` / `.parquet`** — read via Python (`pyreadstat.read_dta`, `pandas.read_parquet`) for a stored scalar.

Record each extracted result:

```
{
  source: "output/tables/tab2.tex",
  lookup_key: "col (3), row 'Treatment'",
  value: -1.628,
  uncertainty: -2.75,
  p_value: 0.006
}
```

### Phase 3: Match claims to results

Use fuzzy heuristics when exact labels don't match:

- Name similarity (`"treatment effect"` ~ `"ATT"` ~ `"treated"` ~ the table row label)
- Magnitude similarity (if two candidates have values within 10% of the reported, prefer the one with closer t-stat)
- Context hints from the claim's `raw_context` field (table number, panel, column, row label)
- The `\input{output/tables/tabN.tex}` ↔ regression-call mapping in the producing `.do` is the most reliable match — trace it.

For every claim, produce a match candidate with a confidence score. Claims below 0.7 confidence get flagged as "UNMATCHED — manual review needed" rather than silently passing.

### Phase 4: Tolerance check

For each matched claim, apply the thresholds from `replication-protocol.md`:

| Kind | Tolerance | Example |
|---|---|---|
| Integers (N, counts) | Exact | 120,000 must equal 120,000 |
| Point estimates | `abs(reported - computed)` < 0.01 | -0.0123 vs -0.0122 → diff = 0.0001 → PASS |
| t-statistics / SEs | within the protocol's SE band | t = -3.45 vs -3.41 → PASS |
| P-values | Same significance level | p<0.01 and p<0.01 → PASS; p<0.01 and p=0.03 → FAIL |
| Percentages | ±0.1pp | 42.3% vs 42.35% → PASS |

Respect any **tolerance overrides** the user has written into their `replication-protocol.md` fork (they may loosen for bootstrap/MC noise or tighten for administrative data).

### Phase 4b: Disposition — PASS / FAIL / EXPLAINED / UNMATCHED

A tolerance check resolves to one of four dispositions:

- **PASS** — within tolerance.
- **FAIL** — outside tolerance, with no defensible alternative recorded. **Blocks** (exit 1).
- **EXPLAINED** — outside tolerance, **but** the author has recorded a *concrete, named alternative specification* that accounts for the gap (see the downgrade rule). Surfaced in the report and carried into a response-to-referees; does **not** block.
- **UNMATCHED** — no computed counterpart found (Phase 3 confidence < 0.7). Never auto-downgradable.

**A mismatch is not automatically a failure.** In applied work the most common out-of-tolerance result is a *defensible alternative spec*, not a bug — `reghdfe` vs `reg`/`areg` clustering df, never-treated vs not-yet-treated comparison group, conditional vs unconditional parallel trends, a different bootstrap seed/reps, AR(1) prediction-error shock vs a simple ΔZ change, or display rounding. The skill's job is to *stage the disagreement* for a human auditor, not to pronounce the code right and the paper wrong. (The df-adjustment note in "Stata-specific notes" below is the canonical example of a named alternative.)

**The manuscript is not the oracle.** When the computed value disagrees with the manuscript, do not presume the code is correct and the paper stale — nor the reverse. A refactor may have broken a previously-correct table (the *on-disk output* is the buggy one), or the paper may carry an old number. The computed value is a **challenger**, not ground truth. Report a mismatch as "one of {paper, code} must change — isolate which," never "revert the code to match the paper." This prevents the trap of reverting a genuine bug-fix just to make the paper 'reproduce.'

#### Downgrade rule: FAIL → EXPLAINED

A FAIL may be downgraded to EXPLAINED **only** when a *specific named alternative* is recorded for that exact claim — in the passport entry's `notes:` field (passport mode) or the audit report's author-note column (default mode). Example of a valid note:

> "never-treated vs not-yet-treated comparison group; under not-yet-treated the published value is −1.19, within rounding of the script's −1.187. CODE-CORRECTED pending."

The author is the **auditor**: the skill stages the two-sided comparison (reported value *and* computed value, both shown); the human writes the one-line named alternative; the skill records it and thereafter respects it. Tag the resolution `PAPER-CORRECTED`, `CODE-CORRECTED`, or `DEFENSIBLE-ALTERNATIVE`.

**Hard floor — never downgradable to EXPLAINED:**
- A blank note, "unclear", "looks fine", or any note that does not *name a concrete alternative spec*.
- An **UNMATCHED** claim (no computed counterpart to compare against).
- A flat numerical contradiction with no alternative offered.

(Citation/existence claims are out of scope here — [`/verify-claims`](../verify-claims/SKILL.md) owns those, and applies the same named-alternative softening on its side.)

#### Repeated EXPLAINED is a signal (two-strikes)

Reuse the two-strikes rule from [`summary-parity.md`](../../rules/summary-parity.md): if the **same** claim is downgraded to EXPLAINED in **two consecutive audits** without ever being corrected to PASS (the author keeps invoking the alternative but never updates paper or code), stop treating it as quietly resolved. Surface it prominently in Phase 5 — *"this contested number has been EXPLAINED twice but never corrected"* — so a standing disagreement can't hide behind a recorded note indefinitely. In passport mode, detect this by comparing the current `status`/`notes` against the prior audit's.

### Phase 5: Report

Write `quality_reports/reproducibility_audit_[manuscript-name].md`:

```markdown
# Reproducibility Audit: [Manuscript Title]

**Date:** [YYYY-MM-DD]
**Manuscript:** [path]
**Outputs directory:** [path]
**Tolerance source:** .claude/rules/replication-protocol.md

## Summary

| Status | Count |
|---|---|
| PASS | N |
| FAIL (diff > tolerance, no named alternative) | M |
| EXPLAINED (out of tolerance, named alternative recorded) | E |
| UNMATCHED (manual review) | K |
| **Overall verdict** | **PASS / FAIL** (FAIL iff M > 0; EXPLAINED does not fail the audit) |

## PASS (all within tolerance)
| Claim | Reported | Computed | Diff | Tolerance |
|---|---|---|---|---|
| Table2_col3_treatment | -1.632 (-2.79) | -1.628 (-2.75) | 0.004 / 0.04 | 0.01 / band |

## FAIL (outside tolerance — BLOCKER)
| Claim | Reported | Computed | Diff | Tolerance | Location in paper | Author note (name a concrete alternative to downgrade → EXPLAINED) |
|---|---|---|---|---|---|---|

## EXPLAINED (out of tolerance; defensible named alternative recorded — non-blocking, carry into response-to-referees)
| Claim | Reported | Computed | Named alternative (why the gap is defensible) | Resolution |
|---|---|---|---|---|
| Table3_TreatPost | -1.187 | -1.19 | never-treated vs not-yet-treated comparison group | DEFENSIBLE-ALTERNATIVE |

## UNMATCHED (manual review)
| Claim | Raw context | Candidate sources |
|---|---|---|

## Environment
[sessionInfo excerpt]

## Next steps
1. Resolve each FAIL row — either correct the manuscript, rerun the analysis, or (if the gap is a defensible alternative spec) record a concrete named alternative to downgrade it to EXPLAINED.
2. Review UNMATCHED rows — add explicit lookup keys or widen the search scope.
3. Review EXPLAINED rows before submission — each should map to a sentence in the response-to-referees.
4. After zero FAILs (EXPLAINED rows allowed), the paper is replication-ready.
```

## Exit behavior

- **All PASS (or PASS + EXPLAINED):** exit 0, summary printed.
- **Any FAIL:** exit 1, summary printed to stderr. This makes the skill usable as a `/commit` pre-commit gate — see `replication-protocol.md` for the enforcement pattern. **EXPLAINED rows do NOT count as FAIL and never trigger exit 1** — they are surfaced, not blocking. The gate keeps its full teeth for genuine FAILs (no named alternative) and for fabricated/UNMATCHED claims.
- **UNMATCHED > 0 (with 0 FAIL):** exit 0 with warning — user must manually review.

## Source-language coverage

The skill compares manuscript claims against outputs in three source-language ecosystems:

| Source | Default outputs dir | Read-output via | Common claim sources |
|---|---|---|---|
| **Stata** (default) | `output/tables/`, `output/results/`, `output/logs/` | parse `esttab` `.tex`; `estimates use` for `.ster`; `pyreadstat.read_dta` for `.dta` scalars | `esttab` `.tex` / `.csv` / `.smcl`/`.log` values / `.ster` |
| **Python** | `output/tables/`, `output/results/` | `pandas.read_parquet`, `pickle.load`, `pandas.read_csv` | `.parquet` / `.pickle` / `.csv` |
| **SAS** | `output/` (SAS prints to `.lst`) | regex `.lst`; `pyreadstat.read_sas7bdat` for stored datasets | `.lst` printed output / `.sas7bdat` |

**Stata-specific notes:**

- Manuscript cell `\input{output/tables/main_results.tex}` is the strongest provenance signal — the cell value comes mechanically from the `.do` file. Match the location in the `.tex` to the `eststo`/`esttab` call in the producing script (e.g. `04_analysis.do`).
- Clustering df adjustments can differ between `reghdfe` and base `reg, cluster()`. If a t-stat/SE mismatches at the 2nd decimal, the tolerance in `replication-protocol.md` covers it; if it mismatches at the 1st decimal, investigate the df adjustment — this is the canonical *named alternative* (record it, downgrade FAIL → EXPLAINED).
- This template reports **t-statistics in parentheses**. When the manuscript shows a t and the output a SE (or vice versa), reconstruct t = coef/SE before comparing — do not flag a "mismatch" that is really a t-vs-SE units difference.

**SAS-specific note:** SAS exit codes are unreliable and **results print to `.lst`, not `.log`** — read the `.lst` for the numeric output and the `.log` only for `ERROR:`/`WARNING:` lines. A SAS step can "succeed" (exit 0) while the `.log` holds an error and the `.lst` is empty.

## Passport-mode

When `quality_reports/passports/<paper-slug>.yaml` exists, the skill operates in **passport mode**: instead of emitting a one-shot report, it **reads, updates, and rewrites** the passport file in place.

- For each `claims:` entry in the passport, perform the same numeric audit as the default mode (extract reported value from manuscript at `location`, locate computed value at `source_file:source_line` / `output_file:output_field`, compare against `tolerance:`).
- After each claim is audited, update `status` in place:
  - PASS → claim within tolerance.
  - FAIL → claim outside tolerance **and** the entry's `notes` does not name a concrete alternative. Record the discrepancy (reported vs computed) in `notes`. Blocks (exit 1).
  - EXPLAINED → claim outside tolerance **but** the entry's `notes` already records a *specific named alternative spec* (not blank, not "unclear"). The skill reads `notes` on its next run and resolves the same out-of-tolerance claim to EXPLAINED instead of FAIL — surfaced, non-blocking. The hard floor still applies: an UNMATCHED claim or a note without a named alternative stays FAIL.
  - STALE → if `source_file` or `output_file` modification time is later than `last_verified_on`, mark STALE and re-run the audit logic (after the rerun, status becomes PASS / FAIL / EXPLAINED — STALE is transient).
- Update `last_verified_on` and `last_verified_by: "/audit-reproducibility"` per claim.
- Update `paper.last_audit` at the top level.

If a claim in the manuscript is detected that has no matching passport entry, emit an UNVERIFIED warning — the author should add it (passport scope is author-curated, not auto-populated, to avoid bad inferences).

Passport mode does NOT delete passport entries. If a claim disappears from the manuscript, the passport entry remains with a STALE status — the author decides whether to delete (claim retracted) or update the entry's `location` (claim moved).

See [`.claude/rules/replication-protocol.md`](../../rules/replication-protocol.md) "Claims Provenance (passport)" for the full schema and integration points (`/commit`, `/review-paper`).

## Cross-references

- [`.claude/rules/replication-protocol.md`](../../rules/replication-protocol.md) — the tolerance contract + passport schema + the "manuscript is not the oracle" framing.
- [`templates/passport-template.yaml`](../../../templates/passport-template.yaml) — starter file to copy for a new paper.
- [`.claude/skills/review-paper/SKILL.md`](../review-paper/SKILL.md) — content review; pair with this skill for a full pre-submission audit.
- [`.claude/skills/capture-environment/SKILL.md`](../capture-environment/SKILL.md) · [`.claude/skills/disclosure-check/SKILL.md`](../disclosure-check/SKILL.md) — environment capture + restricted-data screening downstream.
- [`.claude/skills/replication-package/SKILL.md`](../replication-package/SKILL.md) — gates on this skill before assembling the AEA DCAS deposit.
- [`.claude/rules/summary-parity.md`](../../rules/summary-parity.md) — the two-strikes rule reused for repeated-EXPLAINED.

## What this skill does NOT do

- **Re-run your analysis.** The skill compares CURRENT outputs against manuscript claims. If the outputs are stale, re-run your pipeline first (the pre-flight phase will warn).
- **Catch wrong specifications.** A regression that runs cleanly and produces a reproducible `-0.0123` is reproducible. Whether `-0.0123` is the RIGHT estimand is a `/review-paper` / domain-reviewer question.
- **Check external package versions.** The `sessionInfo.txt` capture lets a reviewer see the env; pinning versions is on the user (via `/capture-environment`).
