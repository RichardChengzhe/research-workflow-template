# [YOUR PROJECT NAME]

**Researchers:** [YOUR NAME]
**Branch:** main
**Last Updated:** [DATE]

---

## Session Start

At the start of every session, run `/status` silently to orient yourself. Tell the user only if something needs attention.

## Core Principles

- **Plan first** -- enter plan mode before non-trivial tasks; save plans to `quality_reports/plans/`
- **Verify after** -- run scripts, check logs, and confirm output at the end of every task
- **Data integrity** -- `data/raw/` is READ-ONLY; all derived data goes to `data/processed/`
- **Quality gates** -- nothing ships below 80/100
- **[LEARN] tags** -- when corrected, save `[LEARN:category] wrong -> right` to MEMORY.md
- **Pipeline tracing** -- before modifying any script, trace upstream/downstream dependencies
- **Adversarial QA** -- critic-fixer loops auto-fix mechanical issues; substantive issues go to human

---

## Rules

- `data/raw/` is **READ-ONLY**. Never modify or delete raw data files.
- Read script headers before modifying any script (they document inputs/outputs/dependencies).
- Check `code/stata/params.do` before using hardcoded values. Values must match pipeline docs.
- **Break the glass.** STOP and warn the user before changing: the I/O graph (which scripts exist, what they read/write), the pipeline order in `00_run.do` or `run_all.sh`, research parameters in `params.do`, or `CLAUDE.md`. Say exactly what you plan to change and what it affects downstream. Do not proceed until the user confirms.
- Never present uncertain results with confidence. Flag uncertainty.
- See `templates/constitutional-governance.md` for formal project governance (optional).
- Pipeline tracing: before modifying a script, check upstream inputs and downstream consumers.

## Key Files

| File | Purpose |
|------|---------|
| `code/stata/00_run.do` | Master do-file with all path globals |
| `code/stata/params.do` | Research parameters |
| `run_all.sh` | Shell executor for pipeline steps |
| `pipeline.md` | Master pipeline: step order, file dependencies, figure manifest |
| `CLAUDE.md` | This file -- project instructions |
| `manuscript/main.tex` | Paper (authoritative source for all claims) |
| `manuscript/aea_style_guide.md` | AEA formatting rules |

## Execution Protocol

**Primary:** Use `./run_all.sh "<script_name>"` for all script execution. This runs the script, saves a timestamped log to `output/logs/`, and reports the exit code.

**Alternative:** Use the MCP Stata tool for interactive exploration or quick checks.

**ALWAYS:** Read the log after every run. Check for errors, warnings, unexpected output. Report what the log shows to the user.

**NEVER:** Skip reading the log. Assume a script succeeded without checking. Leave logs in `code/`.

## Folder Structure

```
project-root/
├── CLAUDE.md, MEMORY.md, pipeline.md, run_all.sh
├── code/stata/          <- Stata .do files (numbered pipeline steps)
├── code/python/         <- Python scripts
├── code/programs/       <- Shared utilities
├── data/raw/            <- READ-ONLY source data
├── data/processed/      <- Derived datasets
├── output/{logs,figures,tables,results}/
├── manuscript/          <- LaTeX paper
├── quality_reports/{plans,session_logs,specs,merges}/
├── explorations/        <- Research sandbox (60/100 threshold)
├── scripts/             <- Utility scripts (quality_score.py)
├── templates/           <- Session log, report templates
└── session_logs/        <- Session handoff logs
```

## Commands

```bash
./run_all.sh "01_import.do"           # Run single pipeline step
./run_all.sh --all                    # Run full pipeline
python code/python/script.py          # Run Python script
latexmk -pdf manuscript/main.tex      # Compile paper
python scripts/quality_score.py FILE  # Quality score
```

## Quality Thresholds

| Score | Gate | Meaning |
|-------|------|---------|
| 80 | Commit | Good enough to save |
| 90 | PR | Ready for review |
| 95 | Excellence | Publication-ready |

## Skills Quick Reference

| Command | What It Does |
|---------|-------------|
| `/run [script]` | Execute pipeline step, read log, summarize |
| `/add-step` | Scaffold new pipeline step |
| `/check` | Pipeline integrity check |
| `/status` | Quick project overview |
| `/handoff` | End-of-session summary |
| `/compile-latex` | Compile manuscript with latexmk |
| `/proofread [file]` | Grammar/typo review |
| `/review-code [file]` | Code quality review |
| `/format-table` | Format regression output as LaTeX |
| `/validate-bib` | Cross-reference citations |
| `/devils-advocate` | Challenge research design |
| `/commit [msg]` | Stage, commit, PR, merge |
| `/lit-review [topic]` | Literature search + synthesis |
| `/research-ideation` | Research questions + strategies |
| `/interview-me` | Interactive research interview |
| `/review-paper` | Manuscript review |
| `/data-analysis` | End-to-end Python/Stata analysis |
| `/context-status` | Session health check |
| `/learn [name]` | Extract reusable skill |
| `/stata-execution` | Stata execution on Windows: batch mode, MCP, pitfalls |
| `/stata-workflow` | Stata patterns: panel data, reghdfe, esttab, merges |
| `/sas [script]` | SAS execution: local batch, WRDS remote, log reading, debugging |
| `/fix-code [script]` | Adversarial code quality loop (critic -> fixer -> re-review) |
| `/fix-manuscript [file]` | Adversarial proofreading loop on .tex files |
| `/fix-output` | Adversarial AEA formatting loop on tables/figures |

## Research Design Summary

<!-- CUSTOMIZE: Replace with your project's research design -->

- **Question:** [YOUR RESEARCH QUESTION]
- **Identification:** [YOUR IDENTIFICATION STRATEGY]
- **Method:** [YOUR ESTIMATION METHOD]
- **Data:** [YOUR DATA SOURCES]
- **Key assumptions:** [YOUR KEY ASSUMPTIONS]

## Current Project State

<!-- CUSTOMIZE: Update as you progress -->

| Phase | Status | Notes |
|-------|--------|-------|
| Data preparation | Not started | |
| Descriptive analysis | Not started | |
| Main estimation | Not started | |
| Robustness | Not started | |
| Manuscript | Stub created | |
