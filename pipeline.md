# Pipeline

**Project:** [YOUR PROJECT NAME]
**Last Updated:** [DATE]

---

## Path Conventions

### Working Directory Structure

```
project-root/
├── data/           <- Validated data files
│   ├── raw/        <- Untouched source data (READ-ONLY)
│   └── processed/  <- Created by scripts
├── code/
│   ├── stata/      <- Stata .do files (numbered pipeline steps)
│   └── python/     <- Python scripts
├── output/         <- ALL generated outputs
│   ├── logs/       <- Execution logs (from run_all.sh)
│   ├── figures/    <- Plots for manuscript
│   ├── tables/     <- LaTeX tables, CSV summaries
│   └── results/    <- Intermediate estimation results (.ster, .pkl)
├── manuscript/     <- LaTeX manuscript
└── session_logs/   <- AI session documentation
```

### Script Path Rules

**Data input (Stata):**
```stata
cd "$data"
use "processed/analysis_file.dta"
```

**Output paths (Stata):**
```stata
graph export "$figures/plot.pdf", replace
esttab using "$tables/results.tex", replace
```

**LaTeX integration:**
```latex
\graphicspath{{../output/figures/}}
\input{../output/tables/table.tex}
```

---

## Pipeline Tree

```
PROJECT PIPELINE
================

[RAW DATA SOURCES] (data/raw/ -- READ-ONLY)
├── [Source 1 description]
├── [Source 2 description]
└── [Source 3 description]

                    |
                    v
+------------------------------------------------------------------+
|  PHASE 1: DATA PREPARATION                                       |
+------------------------------------------------------------------+
    |
    |-->  Step 01: [Import & Clean Source 1]
    |     INPUT:  data/raw/[source_file]
    |     OUTPUT: data/processed/[clean_data].dta
    |
    +-->  Step 05: [Merge & Construct Analysis Sample]
          INPUT:  data/processed/[file1].dta, data/processed/[file2].dta
          OUTPUT: data/processed/analysis_sample.dta

+------------------------------------------------------------------+
|  PHASE 2: DESCRIPTIVE ANALYSIS                                    |
+------------------------------------------------------------------+
    |
    |-->  Step 10: [Summary Statistics]
    |     INPUT:  data/processed/analysis_sample.dta
    |     OUTPUT: output/tables/summary_stats.tex
    |
    +-->  Step 15: [Descriptive Figures]
          INPUT:  data/processed/analysis_sample.dta
          OUTPUT: output/figures/[descriptive_plot].pdf

+------------------------------------------------------------------+
|  PHASE 3: ESTIMATION                                              |
+------------------------------------------------------------------+
    |
    |-->  Step 20: [Main Estimation]
    |     INPUT:  data/processed/analysis_sample.dta
    |     OUTPUT: output/tables/main_results.tex
    |             output/figures/[event_study].pdf
    |             output/results/[estimates].ster
    |
    +-->  Step 25: [Robustness Checks]
          INPUT:  data/processed/analysis_sample.dta
          OUTPUT: output/tables/robustness.tex

================================================================================
                            OUTPUT PRODUCTS
================================================================================

FIGURES (for manuscript)
└── output/figures/
    └── [list your figures here]

TABLES (for manuscript)
└── output/tables/
    └── [list your tables here]

LOGS
└── output/logs/
    └── [All execution logs from run_all.sh]
```

---

## Script Status

| Step | Script | Language | Status | Notes |
|------|--------|----------|--------|-------|
<!-- | 01 | code/stata/01_import.do | Stata | Pending | | -->
<!-- | 05 | code/stata/05_merge.do | Stata | Pending | | -->
<!-- | 10 | code/stata/10_summary_stats.do | Stata | Pending | | -->
<!-- | 15 | code/python/15_figures.py | Python | Pending | | -->
<!-- | 20 | code/stata/20_estimation.do | Stata | Pending | | -->
<!-- | 25 | code/stata/25_robustness.do | Stata | Pending | | -->

---

## Data Files

| File | Size | Purpose | Created by | Used by |
|------|------|---------|------------|---------|
<!-- | data/processed/clean_data.dta | TBD | Cleaned import | Step 01 | Step 05 | -->
<!-- | data/processed/analysis_sample.dta | TBD | Analysis-ready | Step 05 | Steps 10-25 | -->

---

## Manuscript Figure Manifest

| Manuscript ref | Filename | Source script | Step | Input data |
|---------------|----------|---------------|------|------------|
<!-- | Figure 1 | descriptive_plot.pdf | 15_figures.py | 15 | analysis_sample.dta | -->
<!-- | Table 1 | summary_stats.tex | 10_summary_stats.do | 10 | analysis_sample.dta | -->
<!-- | Table 2 | main_results.tex | 20_estimation.do | 20 | analysis_sample.dta | -->

---

## Notes

- All outputs go to `output/` -- figures in `output/figures/`, tables in `output/tables/`
- Step numbers use gaps (01, 05, 10, 15, 20, 25) for easy insertion
- Use `/check` to verify consistency between pipeline.md and actual files
- Use `/add-step` to scaffold new pipeline steps
