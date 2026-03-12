---
name: stata-execution
description: Use when executing Stata .do files on Windows. Covers batch execution, MCP Stata tool, common syntax pitfalls, and debugging. Triggers - "run Stata", "do file", ".do", "reghdfe", "esttab", Stata errors.
argument-hint: "[script_name.do]"
allowed-tools: ["Read", "Bash", "Glob", "Grep"]
---

# Stata Execution on Windows -- Pitfalls & Best Practices

## Stata Installation & Documentation

<!-- CUSTOMIZE: Update paths for your Stata installation -->
- **Executable:** `C:\Program Files\Stata18\StataMP-64.exe`
- **PDF Docs:** `C:\Program Files\Stata18\docs\` (36 manuals)
- **Key manuals for econometrics:**
  - `r.pdf` — Base reference (regress, predict, test, margins, etc.)
  - `xt.pdf` — Panel data (xtreg, xtset, xtdescribe)
  - `ts.pdf` — Time series
  - `causal.pdf` — Causal inference (DiD, treatment effects)
  - `u.pdf` — User's Guide (data management, programming, Mata basics)
  - `st.pdf` — Survival analysis
  - `me.pdf` — Multilevel/mixed effects
  - `p.pdf` — Programming (macros, programs, ado files)
  - `m.pdf` — Mata reference
  - `tables.pdf` — Tables and collection framework

**Token-efficient doc lookup:** Use `pdftotext` + `grep` to search manuals without loading them:
```bash
# Search a specific manual
pdftotext "/c/Program Files/Stata18/docs/r.pdf" - | grep -n -i "regress"

# Search all manuals for a command
for f in "/c/Program Files/Stata18/docs/"*.pdf; do
  result=$(pdftotext "$f" - 2>/dev/null | grep -l -i "xtset" 2>/dev/null)
  [ -n "$result" ] && echo "$(basename "$f"): match"
done

# Extract specific pages to read
pdftotext -f 50 -l 55 "/c/Program Files/Stata18/docs/xt.pdf" -
```

## How to Execute Stata Scripts

### Option A: PowerShell batch mode (full end-to-end runs)

```powershell
# MUST use -Wait or Stata detaches and shell returns immediately
Start-Process -FilePath 'C:\Program Files\Stata18\StataMP-64.exe' `
    -ArgumentList '/e do "F:\path with spaces\script.do"' `
    -Wait -NoNewWindow
```

**Key points:**
- `-Wait` is CRITICAL: without it, Stata launches as detached GUI and shell returns exit 0 immediately
- Paths with spaces MUST be double-quoted inside the ArgumentList string
- Creates `scriptname.log` in the **current working directory** (NOT the script directory)
- Exit code 0 always (Stata `/e` mode); check the `.log` for `r(NNN);` errors

### Option B: MCP Stata tool (interactive exploration)

- Direct `stata_run_selection` commands work and persist file writes
- `do "script.do"` via MCP **echoes the script but does NOT execute it** -- avoid this
- Use for: verifying individual regressions, debugging, quick data checks
- Set globals manually before running sections:

```stata
global root "F:/path/to/project"
global processed "$root/data/processed"
global tables    "$root/output/tables"
global figures   "$root/output/figures"
global results   "$root/output/results"
```

### Option C: Git Bash (run_all.sh)

MSYS/Git Bash path mangling converts `/e` to `E:/`. Fix:

```bash
MSYS_NO_PATHCONV=1 "$STATA_PATH" /e do "$script_path"
```

Note: Stata still detaches (returns immediately). The `tee` captures nothing because `/e` writes to its own log file, not stdout.

## Syntax Pitfalls

### 1. Block comments inside line comments -- CRITICAL

`/*` ALWAYS opens a block comment, even inside a `*` line comment:

```stata
* BAD:  output/results/*.ster    <-- /* opens unclosed block comment!
* GOOD: output/results/[model].ster
* GOOD: output/results/all .ster files
```

The `/*` block comment parser takes precedence over `*` line comments. An unclosed `/*` swallows the entire rest of the file -- the script echoes but never executes.

### 2. `clear` vs `clear all`

- `clear all` -- clears data, globals, programs, mata, EVERYTHING
- `clear` -- clears data only, preserves globals

Scripts called from a master do-file (e.g., `00_run.do`) MUST use `clear` to preserve globals. Add a globals guard for standalone execution:

```stata
clear
set more off

* Set globals if not already defined (standalone execution)
if "$processed" == "" {
    * CUSTOMIZE: add your username and root path
    if "`c(username)'" == "[YOUR_USERNAME]" {
        global root "[YOUR_PROJECT_ROOT]"
    }
    global processed "$root/data/processed"
    global tables    "$root/output/tables"
    global figures   "$root/output/figures"
    global results   "$root/output/results"
}
```

### 3. esttab pitfalls

**Mutually exclusive options:** `se()`, `ci()`, `p()`, `z()`, `aux()` are MUTUALLY EXCLUSIVE:

```stata
* BAD:  b(4) se(4) ci(4)  --> "only one allowed of z, se, p, ci, and aux()"
* GOOD: b(4) se(4)        --> for regression tables
* GOOD: b(4) ci(4)        --> for event study coefficient exports
```

**Duplicate Observations row:** Using `scalars("N_full Observations" ...)` creates TWO Observations rows — one from the `N_full` scalar, one from esttab's default `e(N)`. Fix: add `noobs` to suppress the automatic row:

```stata
* BAD: duplicate Observations rows in output
esttab ... , scalars("N_full Observations" "r2_a Adj. R2")

* GOOD: single formatted Observations row
esttab ... , noobs scalars("N_full Observations" "r2_a Adj. R2")
```

### 4. Two-way clustering language

Cameron-Gelbach-Miller two-way clustering:
- SAY: "Two-way clustering: issuer and year-month"
- NOT: "issuer x year-month" (misleadingly implies interaction)

```stata
* Two-way clustering in reghdfe:
reghdfe y x, absorb(fe1 fe2) cluster(dim1 dim2)
* reghdfe interprets two variables as CGM two-way clustering
```

### 5. Winsorization with winsor2

Always winsorize continuous variables before estimation. Use `winsor2` with
`_w` suffix (default, no `replace`) to preserve originals:

```stata
* Generate _w variables; originals kept intact
winsor2 spread issue_amt ttm, cuts(1 99)
* Creates: spread_w, issue_amt_w, ttm_w

* Use _w variables in regressions and summary statistics
reghdfe spread_w post_treatment ln_size_w ln_ttm_w, absorb(fe1 fe2) cluster(cl)
```

**Convention:** Never use `winsor2 ..., replace`. Always keep originals and
use `_w` suffix variables in all downstream estimation and summary stats.

### 6. Factor notation in ppmlhdfe

`ppmlhdfe` does NOT support `ib()` factor notation for event-time dummies. Create manual dummy variables instead:

```stata
forvalues t = -5/5 {
    if `t' == -1 continue
    local tname = cond(`t' < 0, "m" + string(abs(`t')), "p" + string(`t'))
    gen byte et_`tname' = (event_time == `t') if event_time != .
    replace et_`tname' = 0 if et_`tname' == .
}
```

### 7. Memory management in long scripts

Many `reghdfe` calls accumulate stored estimates and mata matrices. Eventually hits `r(3900)` — "unable to allocate" memory error. Fix: drop unneeded estimates and clear mata between major sections:

```stata
* Save estimates to .ster files first, then free memory
foreach est in a1_model b2_model c3_model {
    capture estimates drop `est'
}
mata: mata clear

* Restore from .ster later if needed (e.g., for comparison tables)
estimates use "$results/a1_model.ster"
estimates store a1_model
```

## Debugging Batch Mode

1. **Script echoes but doesn't execute**: Check for `/*` inside `*` comments in the file header
2. **"file not found" error**: Path has spaces but isn't quoted
3. **No output files created, exit 0**: Stata detached; use `-Wait` in PowerShell
4. **Empty log file (run_all.sh)**: MSYS mangled `/e` to `E:/`; add `MSYS_NO_PATHCONV=1`
5. **Globals empty after script starts**: Script uses `clear all` instead of `clear`
