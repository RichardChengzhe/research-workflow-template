---
paths:
  - "code/**/*.py"
  - "code/**/*.do"
  - "code/**/*.sas"
  - "manuscript/**/*.tex"
  - "output/**"
---

# Quality Gates & Scoring Rubrics

> **Framing:** Thresholds are **advisory at the harness level**. The `/commit` skill runs `quality_score.py` and halts on failure until the user fixes or explicitly overrides. A **real git pre-commit hook** (`.githooks/pre-commit`, activated once via `./scripts/install-hooks.sh`) extends the same gates to *every* commit, so bypassing the skill no longer bypasses the review — unless you opt out with `SKIP_QUALITY_GATE=1` / `--no-verify`. "Gate" here means "checkpoint enforced by a skill or the pre-commit hook," not an unconditional harness-level block.

## Thresholds

- **80/100 = Commit** -- good enough to save
- **90/100 = PR** -- ready for review
- **95/100 = Excellence** -- publication-ready

## Python Scripts (.py)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Syntax/runtime errors | -100 |
| Critical | Hardcoded absolute paths | -20 |
| Critical | Missing import statements | -15 |
| Major | No docstring for functions | -5 |
| Major | Missing type hints on public functions | -3 |
| Major | Unused imports | -3 |
| Minor | Lines > 100 characters | -1 per occurrence |
| Minor | Missing `if __name__ == "__main__"` guard | -2 |

## Stata Do-Files (.do)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Syntax errors / does not run | -100 |
| Critical | Hardcoded absolute paths (not using globals) | -20 |
| Critical | Missing `clear all` / `set more off` at top | -10 |
| Major | Missing `log using` or not run via run_all.sh | -10 |
| Major | Missing `set seed` for stochastic computation | -10 |
| Major | No variable labels on created variables | -5 |
| Major | Missing `estout`/`esttab` for regression output | -5 |
| Minor | Missing script header (purpose, inputs, outputs) | -3 |
| Minor | Hardcoded values that should be in params.do | -3 |

## SAS Programs (.sas)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Syntax errors / does not run | -100 |
| Critical | Hardcoded passwords in script | -30 |
| Critical | Hardcoded absolute paths (not using macros) | -20 |
| Major | Missing script header (purpose, inputs, outputs) | -5 |
| Major | No error checking after key operations | -5 |
| Major | Missing `proc sort` before merge/BY processing | -5 |
| Major | `SELECT *` in production PROC SQL | -5 |
| Major | Missing observation count verification | -3 |
| Minor | Missing date formats on date variables | -2 |
| Minor | Missing variable labels | -2 |
| Minor | Commented-out dead code blocks | -1 |

## Manuscript (.tex)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | LaTeX compilation failure | -100 |
| Critical | Undefined citation | -15 |
| Critical | Missing table/figure reference | -10 |
| Major | Overfull hbox > 10pt | -5 |
| Major | Claim without citation | -5 |
| Major | Inconsistent notation | -3 |
| Minor | Informal language | -1 |
| Minor | Passive voice overuse | -1 |

## Dispositions (how a finding scores)

A reviewer/auditor assigns one disposition per finding. Three of them are fail-closed; one is a research-specific non-blocking state.

- **PASS** — within tolerance / no issue. No deduction.
- **FAIL** — a real defect (a deduction above) **or** a numeric/empirical claim that is outside tolerance with *no concrete named alternative* recorded. Blocks commit per the thresholds below. **Fabrication, an unmatched claim, or a vague/blank "unclear" note always stays FAIL** — never downgraded.
- **EXPLAINED** — a discrepancy or critique that is fully accounted for by a *concrete, named alternative specification* (e.g. never-treated vs not-yet-treated comparison group, conditional vs unconditional parallel trends, `reghdfe` vs `areg`/`reg` clustering df adjustment, an MC seed/reps difference, or a display-rounding gap). It is **surfaced** in the report (and meant to flow into a response-to-referees), but it does **not** block — the author has already recorded a defensible justification. EXPLAINED requires a named alternative in the note; a blank or hand-wavy note never downgrades a FAIL. (Mirrors the `status` semantics in [`replication-protocol.md`](replication-protocol.md).)

This disposition is what lets the domain-reviewer raise a *defensible alternative interpretation* without it being treated as an auto-FAIL, while keeping fabricated or unsupported claims hard-blocked.

## Enforcement (the /commit skill + an optional pre-commit hook)

- **Score < 80:** Halt within `/commit`. List blocking issues. The user may override with an explicit natural-language signal ("commit anyway" / "skip quality gate") and a reason — the override is logged in the commit body.
- **Score < 90:** Allow commit within `/commit`, warn. List recommendations.
- **EXPLAINED findings:** do not block. They are listed in the summary with their named alternative.
- **Direct `git commit`:** unenforced *until* you run `./scripts/install-hooks.sh`, which points `core.hooksPath` at the version-controlled `.githooks/pre-commit`. After that, every commit (skill or not) runs the surface-sync + quality (>=80) gates. Bypass sparingly with `SKIP_QUALITY_GATE=1` (quality only) or `git commit --no-verify` (all hooks); record the reason in the commit body.

## Quality Reports

Generated **only at merge time**. Use `templates/quality-report.md` for format.
Save to `quality_reports/merges/YYYY-MM-DD_[branch-name].md`.

## Tolerance Thresholds (Research)

| Quantity | Tolerance | Rationale |
|----------|-----------|-----------|
| Point estimates | 1e-6 | Numerical precision |
| Standard errors | 1e-4 | Clustering/bootstrap variation |
| Coverage rates | +/- 0.01 | MC variability |
| Sample sizes (N) | Exact match | No reason for difference |
