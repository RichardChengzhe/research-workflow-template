---
paths:
  - "code/**/*.do"
  - "code/**/*.py"
  - "code/**/*.sas"
  - "manuscript/**/*.tex"
  - "output/**"
  - "slides/**/*.tex"
---

# Content Invariants (INV-1 through INV-12)

Numbered non-negotiable rules for content produced in this repository. Critic agents, reviewers, and audit agents should cite invariants by number (e.g., "violates INV-3") when flagging issues. These complement the scored deductions in [`quality-gates.md`](quality-gates.md): the rubric scores severity, the invariants name the specific contract.

## Code invariants (.do / .py / .sas)

- **INV-1: No hardcoded absolute paths.** No `/Users/...`, `C:\...`, `~` expansion, or machine-specific roots in committed code. Stata uses globals from `00_run.do` (`$processed`, `$tables`); Python uses `pathlib.Path` relative to the repo root; SAS uses `%let` macro roots and libname macros. Credentials live in gitignored `autoexec.sas` / environment variables, never inline.
- **INV-2: Seed once, at the top.** Any script with a stochastic step (bootstrap, simulation, random sample, train/test split) sets the seed exactly once near the top, before any random draw -- `set seed` (Stata, from `params.do`), `np.random.seed(...)` / a seeded `Generator` (Python). Never re-seed inside a loop or a function.
- **INV-3: Research parameters are single-sourced.** Sample windows, winsorization cutoffs, treatment dates, FE specifications, and estimation choices live in one place (`params.do` or an equivalent config), not scattered as magic numbers across scripts. Changing a parameter there must change all downstream analysis -- warn before editing it.
- **INV-4: Log is authoritative for SAS, output files for all.** A SAS run is judged by its log (`ERROR:` / `WARNING:` / `NOTE:` observation counts), never by its exit code. Every script's claimed output files must exist with non-zero size before the task is called done.

## Manuscript & output invariants (.tex / output/**)

- **INV-5: t-statistics in parentheses, never standard errors.** Regression tables report the coefficient on top and the t-statistic in parentheses below it, with stars `*` p<0.10, `**` p<0.05, `***` p<0.01. Be explicit in the table notes about what the parenthetical is; do not silently mix SEs and t-stats across tables.
- **INV-6: Every number in the prose traces to a generating script.** A coefficient, N, or p-value stated in the manuscript must be reproducible from a named script + table output. Map table/figure to its generating script and line (a results-provenance note). Numbers that cannot be traced are bugs, not prose.
- **INV-7: Notation parity across artifacts.** Every symbol, variable name, and subscript used in the manuscript, the slides, and the table labels must be identical across them. Notation drift between the paper and its slide deck (or between two tables) is a critical bug.
- **INV-8: Single canonical bibliography.** One `.bib` file is the source of truth (configure its name/path in `CLAUDE.md`). No per-section or per-table `.bib` files. All `\cite{}` keys must resolve against that one file; every cited key must exist and every reference should be cited.

## Slide invariants (Beamer, kept)

- **INV-9: No `\pause` or overlays.** Beamer `\pause`, `\only`, `\visible`, `\onslide`, `\uncover` are forbidden. Use multiple slides for progressive builds, color for emphasis. See [`no-pause-beamer.md`](no-pause-beamer.md) for rationale.
- **INV-10: Max 2 colored boxes per slide.** Overusing callout / definition / alert boxes creates "box fatigue." Two per slide maximum.
- **INV-11: Motivation before formalism.** Every definition or estimating equation is preceded by a motivating example, intuition, or real-world question. No unmotivated math on a slide.

## Figure invariant

- **INV-12: Vector figures at publication resolution.** Figures for the manuscript are vector PDF (or >= 300 DPI raster where vector is impossible); figures embedded in slides match the deck background. Apply a consistent project plotting style (set globally in Python via a `matplotlib`/`seaborn` style, or in a shared Stata graph scheme) -- no default gray-background plots in any committed figure.

## Cross-references

- [`quality-gates.md`](quality-gates.md) -- scored severity for these violations.
- [`python-stata-conventions.md`](python-stata-conventions.md) -- the full coding standard behind INV-1 through INV-4.
- [`no-pause-beamer.md`](no-pause-beamer.md) -- INV-9 rationale.
- [`cross-artifact-review.md`](cross-artifact-review.md) -- enforces INV-6/INV-7 across the paper-code dependency graph.
