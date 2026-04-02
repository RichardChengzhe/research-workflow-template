---
paths:
  - "code/**/*.py"
  - "code/**/*.do"
  - "code/**/*.sas"
  - "manuscript/**/*.tex"
  - "output/**"
---

# Quality Gates & Scoring Rubrics

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

## Enforcement

- **Score < 80:** Block commit. List blocking issues.
- **Score < 90:** Allow commit, warn. List recommendations.
- User can override with justification.

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
