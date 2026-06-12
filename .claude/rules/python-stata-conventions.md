---
paths:
  - "code/**/*.py"
  - "code/**/*.do"
  - "code/**/*.sas"
---

# Python, Stata & SAS Code Conventions

**Reproducibility is the default, not a feature.** A script should be runnable from a clean shell with no manual intervention, and end in the same state regardless of how many times it runs.

## Python Standards

### Structure
- PEP 8 compliance (use `black` formatter if available)
- Type hints on all public function signatures
- Docstrings for all functions (Google style)
- `if __name__ == "__main__":` guard for scripts

### Header
```python
"""
[Step NN]: [Descriptive Title]

Purpose: [What this script does]
Inputs:  [Data files read]
Outputs: [Files created]
Dependencies: [Upstream scripts]
"""
```

### Data & Analysis
- Use `pandas` for data manipulation, `numpy` for numerics
- Use `statsmodels` or `linearmodels` for regression
- Use `matplotlib` + `seaborn` for figures (set style globally)
- Relative paths only via `pathlib.Path` relative to repo root: `Path("data/processed/file.dta")`
- Save figures with explicit dimensions: `fig.savefig(..., dpi=300, bbox_inches="tight")`
- Pin the environment: record `python --version` + a pinned `requirements.txt` (or conda env export) so the package is reproducible.

### Output
- Tables: export as `.tex` (LaTeX) and `.csv` (inspection)
- Figures: export as `.pdf` (vector) for manuscript inclusion
- Log key results to stdout for log capture

## Stata Standards

### Preamble (every .do file)
```stata
* ==============================================================================
* [Step NN]: [Descriptive Title]
*
* Purpose: [What this script does]
* Inputs:  [Data files read]
* Outputs: [Files created]
* Dependencies: [Upstream scripts]
* ==============================================================================

version 18              // pin Stata semantics — new versions silently change defaults
clear all               // no leftover state from a prior session
set more off            // don't pause for keystrokes
set seed 12345          // pin RNG for any random op (from params.do)
set sortseed 12345      // pin sort stability across versions
cap log close _all      // pre-emptively close any log a prior session left open
```

End every `.do` file with `exit, clear STATA` — an explicit clean exit that also suppresses the batch-mode completion modal on Windows.

Why each line matters:
- **`version 18`** — explicit semantics. New Stata versions can silently change defaults (e.g. `reghdfe` clustering df-adjustment); pinning is the only defence.
- **`set seed` + `set sortseed`** — every random op *and* every `sort` is deterministic. Take the seed value from `params.do`.
- **`cap log close _all`** — belt-and-suspenders against a leftover open log.

### Path Management
- ALL paths via globals from `00_run.do`: `"$processed"`, `"$figures"`, `"$tables"`, `"$results"`
- NEVER hardcode absolute paths in individual scripts
- Use `cd "$data"` to change to data directory when needed

### Data Management
- `label variable` for all created variables
- `label data` with description
- `describe` and `summarize` key variables after transformations
- `assert` to verify expected sample sizes and variable ranges
- `merge 1:1 id using foo, assert(3)` — fail loud on mismatched keys; never merge without checking `_merge`
- **Missing-value trap:** Stata treats `.` as `+∞` in inequality comparisons. Write `if x > 5 & x != .` when you mean non-missing-and-greater-than-5
- Prefer `bysort id: egen y = total(x)` over the deprecated `egen sum()`
- Generate-then-inspect before destructive edits: `gen new_var = ...` and check before any `drop`/`replace` on observed data

### Estimation
- Use `eststo` / `esttab` for regression output tables
- Cluster standard errors at the level of treatment assignment (or the highest plausible level of dependence): `vce(cluster $cluster_var)`. Never use bare `, robust` without justification.
- `reghdfe` is preferred for high-dimensional FE and gives explicit df adjustment — but check it against `areg`/`reg ... , cluster()` in edge cases; the `version` pin is only partial defence.
- Store estimates: `estimates save "$results/model_name.ster", replace`
- Always report N, R-squared, and fixed effects

### Tables — `\input{}`, never hand-format
Any table that appears in the paper must be produced by `esttab` and pulled into LaTeX with `\input{}`, so the cell values come from the actual estimation and update mechanically on every run:
```stata
esttab m1 m2 using "$tables/tab_main.tex", replace ///
    booktabs label                              /// use the variable labels you set
    b(3) se(2)                                  /// 3-decimal coeffs, SE/t in parens
    star(* 0.10 ** 0.05 *** 0.01)              /// econ convention (AER/QJE/JPE/ECMA)
    stats(N r2, fmt(%9.0fc %9.3f) labels("Observations" "R-squared")) ///
    nonotes addnote("Standard errors clustered at <level>.")
```
Then in the manuscript: `\input{../output/tables/tab_main.tex}`. **Never hand-edit numbers into a LaTeX table** — that breaks the link to the estimation. Document the significance-stars convention in the table note even though it is "obvious"; referees read notes. (Default two-tailed; one-tailed is rare in published work and must be justified.)

### Figures
```stata
graph export "$figures/figure_name.pdf", replace as(pdf)   // vector, for the paper
graph export "$figures/figure_name.png", replace width(2000) // raster, for slides
```
Don't rely on the auto-generated `.gph` — it is not portable across Stata versions.

### Logging & environment capture
- Scripts are run via `run_all.sh`, which captures logs to `output/logs/`
- Use `display` for key intermediate results; `timer on/off` for performance-critical sections
- Capture package versions once (e.g. in `00_run.do` or a dedicated subroutine) so the environment is reproducible:
```stata
log using "$logs/sessionInfo.txt", text replace
about
which reghdfe
which estout
which ivreg2
log close
```
List every `ssc install` in the install/setup step so a clean machine can be provisioned. An AEA Data Editor and future-you both need the package versions actually used.

## SAS Standards

### Header (every .sas file)
```sas
/* ==============================================================================
 * [Step NN]: [Descriptive Title]
 *
 * Purpose: [What this script does]
 * Inputs:  [Data files/libraries read]
 * Outputs: [Datasets/files created]
 * Dependencies: [Upstream scripts, WRDS access needed?]
 * ============================================================================== */
```

### Path & Credential Management
- Use macro variables for project paths: `%let projroot = ...;`
- Libnames via macros: `libname raw "&projroot/data/raw";`
- NEVER hardcode passwords — use autoexec.sas (gitignored) or environment variables
- NEVER hardcode absolute paths in production scripts

### WRDS Connection
- Use `rsubmit`/`endrsubmit` for remote execution
- Use `proc upload`/`proc download` for file transfer
- Reference WRDS macros via `%include '/wrds/...'` on the remote server
- Always `signoff` when done

### Data Management
- PROC SQL: always name columns explicitly (no `SELECT *` in production)
- PROC SORT NODUPKEY before merge BY variables
- Verify observation counts after key operations: `proc sql; select count(*) from ...;`
- Handle SAS missing values explicitly (missing < any number)
- Use `label` statements for created variables
- Format dates: `format datadate date9.;`

### Output
- CSV: `proc export dbms=csv putnames=yes;`
- Excel: `proc export dbms=xlsx replace;`
- Stata: `proc export dbms=stata replace;`
- SAS datasets for intermediate results in `data/processed/`

### Logging
- Run via `run_all.sh` which captures the SAS log to `output/logs/`
- ALWAYS check the log for `ERROR:` and `WARNING:` lines
- SAS exit codes are unreliable — the log is the only trustworthy indicator. On WRDS, remember some output lands in `.lst`, not `.log`.
- Use `%put NOTE:` for key intermediate results
