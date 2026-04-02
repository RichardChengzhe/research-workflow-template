---
paths:
  - "code/**"
  - "manuscript/**"
  - "output/**"
---

# Task Completion Verification Protocol

**At the end of EVERY task, Claude MUST verify the output works correctly.** This is non-negotiable.

## For Stata .do Files:
1. Run via `./run_all.sh "script_name.do"`
2. Read the log file in `output/logs/`
3. Check for errors, warnings, unexpected output
4. Verify output files (.dta, .tex, .pdf, .ster) were created with non-zero size
5. Spot-check estimates for reasonable magnitude
6. Report verification results

## For Python Scripts:
1. Run `python code/python/script_name.py`
2. Check exit code (0 = success)
3. Verify output files were created
4. Check for warnings in stdout/stderr
5. Report verification results

## For SAS .sas Files:
1. Run via `./run_all.sh "script_name.sas"`
2. Read the log file in `output/logs/`
3. Search for `ERROR:` lines (any = failure)
4. Check `WARNING:` lines and evaluate significance
5. Verify observation counts in `NOTE:` lines match expectations
6. Verify output files (.sas7bdat, .csv, .xlsx, .dta) were created with non-zero size
7. Note: SAS exit codes are unreliable — the log is authoritative
8. If script uses WRDS (`rsubmit`): remind user to approve Duo push on phone
9. Report verification results

## For LaTeX Manuscript:
1. Compile with `latexmk -pdf manuscript/main.tex`
2. Check for errors and warnings
3. Grep for undefined citations
4. Grep for overfull hbox warnings
5. Verify PDF was generated
6. Report verification results

## For Output Tables:
1. Verify the .tex file exists and has content
2. Check that it compiles within the manuscript
3. Spot-check a few values against the Stata/Python log

## Common Pitfalls:
- **Assuming success**: Always verify output files exist AND contain correct content
- **Stale outputs**: After modifying a script, re-run it before verifying
- **Log location**: Logs go to `output/logs/`, not the script directory

## Verification Checklist:
```
[ ] Output file created successfully
[ ] No compilation/execution errors
[ ] Log file reviewed for warnings
[ ] Output values are reasonable
[ ] Reported results to user
```
