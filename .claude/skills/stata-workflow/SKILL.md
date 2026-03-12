---
name: stata-workflow
description: Use when working with Stata .do files for empirical finance/accounting research. Covers panel data, reghdfe, esttab, merge workflows, variable construction, and debugging. Triggers - reghdfe, xtreg, xtset, esttab, eststo, merge, append, panel data, fixed effects, clustered standard errors.
allowed-tools: ["Read", "Bash", "Glob", "Grep"]
---

# Stata Workflow for Empirical Finance/Accounting Research

## Overview

Expert guidance on Stata programming for empirical research in finance and accounting. Prioritizes reproducibility, efficiency, and publication-quality output.

## Panel Data Setup

Standard panel setup pattern:

```stata
use "data.dta", clear
xtset firmid yearq          // or: xtset gvkey fyear
```

Always verify panel structure:
- `xtdescribe` to check gaps
- `duplicates report firmid yearq` before xtset
- `tsset` for time-series operators (L. F. D. S.)

## Regression Specifications

### reghdfe (preferred for high-dimensional FE)

```stata
reghdfe depvar treatment controls, absorb(firmid yearq) cluster(firmid)
```

Key options:
- `absorb(firmid yearq)` — firm and time FE
- `absorb(firmid industry#yearq)` — firm FE + industry-by-year FE
- `cluster(firmid)` — cluster at firm level
- `cluster(firmid yearq)` — two-way clustering

### Interaction terms

```stata
reghdfe y c.x1##c.x2 controls, absorb(fe) cluster(cl)
// Or manually:
gen x1_x2 = x1 * x2
reghdfe y x1 x2 x1_x2 controls, absorb(fe) cluster(cl)
```

### Instrumental variables

```stata
ivreghdfe depvar controls (endogvar = instrument), absorb(fe) cluster(cl)
// First stage F-stat reported automatically
```

## Output Formatting

### esttab (preferred)

```stata
eststo clear
eststo: reghdfe y x1 controls1, absorb(firmid yearq) cluster(firmid)
eststo: reghdfe y x1 controls2, absorb(firmid yearq) cluster(firmid)
eststo: reghdfe y x1 controls3, absorb(firmid industry#yearq) cluster(firmid)

esttab using "table.tex", replace ///
    b(%9.3f) se(%9.3f) ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    r2 N ///
    title("Main Results") ///
    mtitles("(1)" "(2)" "(3)") ///
    drop(_cons) ///
    booktabs ///
    label
```

### Adding custom rows (FE indicators, etc.)

```stata
esttab using "table.tex", replace ///
    indicate("Firm FE = *firmid*" "Year FE = *yearq*") ///
    // OR manually:
    stats(N r2 firmfe yearfe, ///
        labels("Observations" "R-squared" "Firm FE" "Year FE") ///
        fmt(%9,0gc %9.3f 0 0))
```

## Variable Construction

### Winsorizing

```stata
// At 1st and 99th percentiles
winsor2 varlist, cuts(1 99) replace
// Or by group:
bysort yearq: winsor2 varlist, cuts(1 99) replace
```

### Lags and leads (requires xtset)

```stata
gen lag_x = L.x          // one-period lag
gen lead_x = F.x         // one-period lead
gen delta_x = D.x        // first difference
gen lag2_x = L2.x        // two-period lag
```

### Scaled variables

```stata
gen roa = ni / at                     // return on assets
gen bm = ceq / (csho * prcc_f)       // book-to-market
gen leverage = (dltt + dlc) / at      // leverage
gen size = ln(csho * prcc_f)          // log market cap
```

## Merge Workflows

### CRSP-Compustat merge pattern

```stata
// Start with Compustat
use "compustat_funda.dta", clear
// Merge linking table
merge m:1 gvkey using "ccmxpf_lnkhist.dta"
keep if _merge == 3
drop _merge
// Keep valid links
keep if linktype == "LU" | linktype == "LC"
keep if linkprim == "P" | linkprim == "C"
// Merge CRSP
merge 1:1 permno date using "crsp_msf.dta"
```

### Always check merges

```stata
tab _merge
// Document merge rates in comments
// _merge==1: master only, _merge==2: using only, _merge==3: matched
```

## Common Debugging

- **r(111)**: variable not found — check spelling, check if data loaded
- **r(198)**: variable already defined — drop or rename first
- **r(459)**: not sorted — `sort varlist` or `bysort varlist:`
- **r(2000)**: no observations — check `if` conditions, check merge
- **type mismatch in merge**: `tostring`/`destring` to align types
- **singleton observations dropped**: normal with reghdfe, document count

## Best Practices

- Always use `version 17` (or your version) at top of .do file
- Set `set more off` and `clear` at start (NOT `clear all` if called from master)
- Use `compress` before saving to reduce file size
- Use `label variable` for all constructed variables
- Log output: `log using "filename.log", replace`
- Use `tempfile` and `tempvar` for intermediate objects
- Comment liberally with `//` and `///` for line continuation
- Use `assert` statements to verify data integrity
