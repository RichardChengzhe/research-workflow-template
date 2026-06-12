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

**NEVER:** Skip reading the log. Assume a script succeeded without checking. Leave logs in `code/` or at the project root.

**SAS exit codes are unreliable.** A SAS run may return 0 while the log contains `ERROR:` lines. Always grep the log for `^ERROR` and `^WARNING` after every SAS run. See `.claude/skills/sas/SKILL.md`.

## Common Anti-Patterns (Learned the Hard Way)

- **Running Stata/Python/SAS directly instead of via `run_all.sh`** -- logs scatter to the project root with no timestamps and silently overwrite each other. Symptom: dozens of `*.log` files at root level. Cure: route all execution through `run_all.sh` or the MCP Stata tool.
- **Hardcoding paths inside individual scripts** -- breaks when a coauthor runs the pipeline. Use `$root` / `$data` / `$tables` globals defined once in `code/stata/00_run.do` (Stata) or `pathlib.Path(__file__).resolve().parent.parent` (Python).
- **Trusting a SAS exit code of 0 as success** -- SAS does not propagate runtime errors to the OS exit. A clean exit with `ERROR:` in the log = failed run with possibly wrong results.
- **Running heavy WRDS jobs through PC-SAS `rsubmit`** -- bodies above ~100 lines deadlock during autoexec streaming (TBUFSIZE buffer exhaustion). Use SSH + `qsas` instead. See SAS skill section 2.0.
- **Committing `autoexec.sas` with real WRDS credentials** -- the file is in `.gitignore` for a reason. If you ever see it staged, abort the commit.
- **Editing a script without tracing its consumers** -- if `pipeline.md` says other scripts read this file's outputs, you must verify they still work after your change. Use `/check`.
- **Merging two builds on the numeric `egen group` id** -- the same id denotes different entities across builds; cross-build merges must key on the STRING identifier x date.
- **Constructing rank/treatment measures before all merges and filters** -- inflates group rates via sample-selection bias. Build them on the FINAL estimation sample.
- **Declaring a cited URL/resource "dead" on a single failed fetch** -- escalate the retrieval ladder (Wayback -> headless browser -> mirrors -> author) before giving up.
- **Reading the SAS `.log` when results are in `.lst`** -- some WRDS queries write results to `.lst`; a clean `.log` is not proof of success.

## Folder Structure

```
project-root/
├── CLAUDE.md, MEMORY.md, pipeline.md, run_all.sh
├── .claude/             <- Claude Code infrastructure (skills, agents, rules, hooks)
│   ├── references/      <- Shared reference docs
│   └── output-styles/   <- Output styles
├── code/stata/          <- Stata .do files (numbered pipeline steps)
├── code/python/         <- Python scripts
├── code/sas/            <- SAS .sas programs (WRDS queries, data prep)
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
| `/new-skill [name]` | Scaffold a new skill following repo conventions (interview -> SKILL.md) |
| `/build-report` | Build an HTML results report (heatmaps + AEA tables, clickable links) |
| `/cypress [job]` | Run Python/Stata jobs on a SLURM HPC cluster (SSH, array tasks, transfer) |
| `/worktree-probe` | Scaffold a ceteris-paribus exploration in an isolated git worktree |
| `/data-management-plan` | Draft a funder-compliant DMP (NSF/NIH/ERC/Horizon Europe) |
| `/capture-environment` | Snapshot the compute environment for a replication package |
| `/replication-package` | Assemble a submission-ready replication package (AEA DCAS / openICPSR) |
| `/audit-reproducibility` | Cross-check manuscript numbers against actual Stata/Python/SAS outputs |
| `/disclosure-check` | Pre-screen outputs on restricted data for disclosure-limitation issues |
| `/submission-disclosures` | Generate the journal AI-use / CRediT / disclosure block |
| `/did-event-study` | Staggered DiD / event study to the Callaway-Sant'Anna standard |
| `/power-analysis` | Compute power / sample size / MDE and write a registry-ready section |
| `/preregister` | Draft a preregistration (OSF / AsPredicted / AEA RCT) from a spec |
| `/grant-proposal` | Scaffold a grant proposal (NSF/NIH/ERC/foundation) from primitives |
| `/coauthor-brief` | Cross-machine, cross-person collaborator handoff brief |
| `/respond-to-referees` | Map each referee comment to its revision in a response document |
| `/seven-pass-review` | Seven forked adversarial review passes over a manuscript |
| `/deep-audit` | Exhaustive adversarial audit of manuscript + repo, loops until dry |
| `/verify-claims` | Chain-of-Verification on a draft via a forked claim-verifier agent |
| `/humanize` | Read-only audit of .tex/.md for AI-voice tells |
| `/slide-excellence` | Multi-agent review of a Beamer deck (layout + proofing + substance) |
| `/visual-audit` | Adversarial legibility audit of matplotlib / Stata figures |
| `/diagnose` | Root-cause a failing/wrong result (reproduce -> minimise -> fix loop) |
| `/checkpoint` | Save a structured state snapshot before stopping or handing off |
| `/compress-session` | Distill the conversation into a structured note for `quality_reports/` |
| `/promote-memory` | Run `[LEARN]` candidates through a five-critic council before promotion |
| `/permission-check` | Diagnose why Claude Code is (or isn't) prompting for permission |

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
