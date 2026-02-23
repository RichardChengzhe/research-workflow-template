---
name: check
description: Run a full project integrity check. Verifies pipeline files exist, params match, manuscript references resolve, and finds orphan files. Use periodically to catch inconsistencies.
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# Pipeline Integrity Check

Run a full project integrity check in two phases.

## Phase 1: Pipeline Integrity

1. **Script existence:** Every script listed in `pipeline.md` exists in `code/`
2. **Input data:** Every input data file listed in pipeline exists
3. **Output directories:** `output/logs/`, `output/figures/`, `output/tables/`, `output/results/` exist
4. **params.do values:** Check that `code/stata/params.do` has uncommented values for key parameters
5. **File location:** No scripts or data files sitting in wrong directories
6. **00_run.do consistency:** Scripts in `00_run.do` match those in `pipeline.md`
7. **run_all.sh consistency:** Scripts in `run_all.sh` match those in `pipeline.md`

## Phase 2: Manuscript Audit

1. **Table/figure map:** Every entry in pipeline.md Manuscript Figure Manifest has an existing output file and source script
2. **LaTeX references:** Every `\input{}` and `\includegraphics{}` in `manuscript/main.tex` resolves to an existing file
3. **Orphan outputs:** Find any output files NOT referenced in the manuscript
4. **Undocumented references:** Find any manuscript references NOT in the figure manifest
5. **Bibliography:** Every `\cite` key in manuscript has an entry in `references.bib`

## Report

```markdown
# Integrity Check: [Date]

## Pipeline
- Scripts found: N/M
- Missing scripts: [list]
- Missing data files: [list]
- Parameter issues: [list]

## Manuscript
- References resolved: N/M
- Missing files: [list]
- Orphan outputs: [list]
- Missing bib entries: [list]

## Status: [PASS / WARNINGS / FAIL]
```

**Report all findings. Do not fix anything without user approval.**
