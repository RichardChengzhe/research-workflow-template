---
paths:
  - "code/**/*.py"
  - "code/**/*.do"
  - "code/**/*.sas"
---

# Python, Stata & SAS Code Conventions

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
- Relative paths only: `Path("data/processed/file.dta")`
- Save figures with explicit dimensions: `fig.savefig(..., dpi=300, bbox_inches="tight")`

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

clear all
set more off
```

### Path Management
- ALL paths via globals from `00_run.do`: `"$processed"`, `"$figures"`, `"$tables"`
- NEVER hardcode absolute paths in individual scripts
- Use `cd "$data"` to change to data directory when needed

### Data Management
- `label variable` for all created variables
- `label data` with description
- `describe` and `summarize` key variables after transformations
- `assert` to verify expected sample sizes and variable ranges

### Estimation
- Use `eststo` / `esttab` for regression output tables
- Cluster standard errors at the appropriate level: `vce(cluster $cluster_var)`
- Store estimates: `estimates save "$results/model_name.ster", replace`
- Always report N, R-squared, and fixed effects

### Output
- Tables: `esttab using "$tables/table_name.tex", replace booktabs`
- Figures: `graph export "$figures/figure_name.pdf", replace`
- Set seed from params.do for any stochastic computation

### Logging
- Scripts are run via `run_all.sh` which captures logs to `output/logs/`
- Use `display` for key intermediate results
- Use `timer on/off` for performance-critical sections

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
- SAS exit codes are unreliable — the log is the only trustworthy indicator
- Use `%put NOTE:` for key intermediate results
