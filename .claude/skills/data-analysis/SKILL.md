---
name: data-analysis
description: End-to-end data analysis workflow using Python and Stata, from exploration through regression to publication-ready tables and figures
disable-model-invocation: true
argument-hint: "[dataset path or description of analysis goal]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
---

# Data Analysis Workflow

Run an end-to-end data analysis using Python and/or Stata: load, explore, analyze, and produce publication-ready output.

**Input:** `$ARGUMENTS` -- a dataset path (e.g., `data/processed/analysis_sample.dta`) or a description of the analysis goal (e.g., "regress bond spreads on DC investment with state fixed effects").

---

## Constraints

- **Follow code conventions** in `.claude/rules/python-stata-conventions.md`
- **Save Stata scripts** to `code/stata/` with descriptive names
- **Save Python scripts** to `code/python/` with descriptive names
- **Save all outputs** (figures, tables, results) to `output/`
- **Run code-reviewer** on the generated script before presenting results
- **Use globals from 00_run.do** for all Stata paths

---

## Workflow Phases

### Phase 1: Setup and Data Loading

1. Read `.claude/rules/python-stata-conventions.md` for project standards
2. Read `code/stata/params.do` for research parameters
3. Create script with proper header (purpose, inputs, outputs)
4. Load and inspect the dataset

### Phase 2: Exploratory Data Analysis

Generate diagnostic outputs:
- **Summary statistics:** Variable types, means, missing rates
- **Distributions:** Histograms for key continuous variables
- **Relationships:** Scatter plots, correlation matrices
- **Time patterns:** If panel data, plot trends over time
- **Group comparisons:** If treatment/control, compare pre-treatment means

Save all diagnostic figures to `output/figures/`.

### Phase 3: Main Analysis

Based on the research question:
- **Stata:** Use `reghdfe` for panel data with high-dimensional FEs
- **Python:** Use `linearmodels` or `statsmodels` for panel regression
- **Standard errors:** Cluster at the appropriate level (from params.do)
- **Multiple specifications:** Start simple, progressively add controls
- **Effect sizes:** Report standardized effects alongside raw coefficients

### Phase 4: Publication-Ready Output

**Tables (Stata):**
- Use `eststo` / `esttab` for regression tables
- Include all standard elements: coefficients, SEs, significance stars, N, R-squared
- Export as `.tex` for LaTeX inclusion

**Tables (Python):**
- Use `stargazer` or manual LaTeX formatting
- Export as `.tex` and `.csv`

**Figures:**
- Python: `matplotlib` + `seaborn` with consistent style
- Stata: `graph export` as PDF
- Set explicit dimensions and 300 DPI for raster formats
- Save as PDF (vector) for manuscript inclusion

### Phase 5: Save and Review

1. Save all outputs to appropriate `output/` subdirectories
2. Run the code-reviewer agent on the generated script
3. Address any Critical or High issues from the review

---

## Important

- **Reproduce, don't guess.** If the user specifies a regression, run exactly that.
- **Show your work.** Print summary statistics before jumping to regression.
- **Check for issues.** Look for multicollinearity, outliers, perfect prediction.
- **Use relative paths.** All paths via globals (Stata) or relative (Python).
- **No hardcoded values.** Use variables from params.do for sample restrictions.
