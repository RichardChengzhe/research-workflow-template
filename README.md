# Research Workflow Template

A combined research project workflow for empirical economics/finance using **Python + Stata + SAS**, with AI-assisted development via Claude Code.

Combines infrastructure from:
- **[pedrohcgs template](https://github.com/pedrohcgs/claude-code-my-workflow)**: Plan-first workflow, quality gates, orchestrator mode, context survival hooks, review agents, [LEARN] memory system
- **[Research-Project-Flow](https://github.com/Black-JL/Research-Project-Flow)**: Pipeline management, `run_all.sh`, `params.do`, break-the-glass guardrails, session commands

## Quick Start

1. **Create a new project from this template:**
   ```bash
   gh repo create my-new-project --template RichardChengzhe/research-workflow-template --private --clone
   cd my-new-project
   ```

2. **Fill in placeholders:**
   - `CLAUDE.md` — Replace `[YOUR PROJECT NAME]`, `[YOUR NAME]`, and the Research Design section
   - `code/stata/00_run.do` — Set your `$root` path for each collaborator
   - `code/stata/params.do` — Define your research parameters
   - `run_all.sh` — Set `STATA_PATH` to your Stata installation
   - `manuscript/main.tex` — Fill in title, authors, abstract

3. **Start working:**
   ```bash
   claude  # Launch Claude Code in the project
   ```

## What's Included

### Directory Structure

```
project-root/
├── CLAUDE.md                    # AI agent instructions (edit for your project)
├── MEMORY.md                    # Persistent learnings ([LEARN] tags)
├── pipeline.md                  # Master pipeline: steps, dependencies, figure manifest
├── run_all.sh                   # Shell executor for pipeline steps
├── .gitignore                   # Python/Stata/LaTeX/data exclusions
│
├── .claude/                     # Claude Code infrastructure
│   ├── settings.json            # Permissions and hooks
│   ├── WORKFLOW_QUICK_REF.md    # Contractor model quick reference
│   ├── rules/        (14)       # Path-scoped behavioral rules
│   ├── agents/       (8)        # Specialized review + fixer agents
│   ├── skills/       (25)       # Slash commands (/run, /check, /fix-code, /sas, etc.)
│   └── hooks/        (7)        # Automation hooks
│
├── code/
│   ├── stata/                   # Stata .do files (numbered pipeline steps)
│   │   ├── 00_run.do            # Master do-file with globals
│   │   └── params.do            # Centralized research parameters
│   ├── python/                  # Python scripts
│   ├── sas/                     # SAS .sas programs (WRDS queries, data prep)
│   └── programs/                # Shared utilities
│
├── data/
│   ├── raw/                     # READ-ONLY source data
│   │   └── README.md            # Document your data sources here
│   └── processed/               # Derived datasets (created by scripts)
│
├── output/
│   ├── logs/                    # Execution logs (from run_all.sh)
│   ├── figures/                 # Publication-ready figures
│   ├── tables/                  # LaTeX tables
│   └── results/                 # Intermediate results (.ster, .pkl)
│
├── manuscript/                  # LaTeX paper
│   ├── main.tex                 # Paper stub
│   ├── references.bib           # Bibliography
│   └── aea_style_guide.md       # AEA formatting reference
│
├── quality_reports/             # Plans, session logs, specs, merge reports
├── explorations/                # Research sandbox (60/100 threshold)
├── scripts/                     # Utility scripts (quality_score.py)
├── templates/                   # Session log, quality report, archive, governance templates
├── session_logs/                # Session handoff logs
├── master_supporting_docs/      # Papers and reference materials
└── scratch/                     # Temporary work (gitignored)
```

### Core Workflow

```
Your instruction
    │
    ▼
[PLAN] — Enter plan mode for non-trivial tasks
    │       Save plan to quality_reports/plans/
    ▼
[APPROVE] — User reviews and approves
    │
    ▼
[EXECUTE] — Orchestrator implements autonomously
    │         Run scripts via run_all.sh
    │         Read logs, verify output
    ▼
[REVIEW] — Quality agents check work
    │         Score against rubrics (80/90/95)
    ▼
[REPORT] — Summary + what's ready
```

### Key Principles

| Principle | What It Means |
|-----------|--------------|
| **Plan first** | Enter plan mode before multi-file or complex tasks |
| **Verify after** | Run scripts, check logs, confirm output every time |
| **Data integrity** | `data/raw/` is READ-ONLY, enforced by hooks |
| **Quality gates** | 80 = commit, 90 = PR ready, 95 = excellence |
| **Break the glass** | STOP and warn before changing pipeline structure or params |
| **Pipeline tracing** | Check upstream/downstream before modifying any script |
| **Adversarial QA** | Critic-fixer loops auto-fix mechanical issues; substantive -> human |
| **[LEARN] tags** | Capture reusable knowledge in MEMORY.md |

### Skills (Slash Commands)

| Command | What It Does |
|---------|-------------|
| `/run [script]` | Execute pipeline step, read log, summarize |
| `/add-step` | Scaffold new pipeline step (script + pipeline.md + 00_run.do) |
| `/check` | Pipeline integrity check (files exist, params match, refs resolve) |
| `/status` | Quick project overview (pipeline, logs, git, data) |
| `/handoff` | End-of-session summary to session_logs/ |
| `/compile-latex` | Compile manuscript with latexmk |
| `/proofread [file]` | Grammar/typo review (report only, no edits) |
| `/review-code [file]` | 8-lens code quality review |
| `/format-table` | Format regression output as publication-ready LaTeX |
| `/validate-bib` | Cross-reference citations vs bibliography |
| `/devils-advocate` | Challenge research design with critical questions |
| `/commit [msg]` | Stage, commit, PR, merge |
| `/data-analysis [goal]` | End-to-end Python/Stata analysis |
| `/lit-review [topic]` | Literature search + synthesis |
| `/research-ideation` | Generate research questions + strategies |
| `/interview-me` | Interactive research interview |
| `/review-paper [file]` | Comprehensive manuscript review |
| `/context-status` | Session health check |
| `/learn [name]` | Extract reusable skill |
| `/sas [script]` | SAS execution: local batch, WRDS remote, debugging |
| `/fix-code [script]` | Adversarial code quality loop (critic -> fixer) |
| `/fix-manuscript [file]` | Adversarial proofreading loop |
| `/fix-output` | AEA table/figure formatting loop |

### Review Agents

| Agent | Purpose |
|-------|---------|
| **domain-reviewer** | Top-journal referee: identification, derivations, citations, code-theory alignment |
| **code-reviewer** | 8-lens code quality: structure, reproducibility, data management, correctness |
| **proofreader** | Grammar, typos, overflow, consistency, academic quality |
| **verifier** | End-to-end verification: scripts run, logs clean, manuscript compiles |
| **code-fixer** | Implements mechanical fixes from code-reviewer reports |
| **manuscript-fixer** | Applies approved proofreader fixes to .tex files |
| **output-critic** | AEA style compliance for tables and figures |
| **output-fixer** | Fixes table formatting and figure references |

### Hooks (Automatic)

| Hook | When | What |
|------|------|------|
| protect-files | Before Edit/Write | Blocks edits to `data/raw/` and protected files |
| verify-reminder | After Edit/Write | Reminds to compile/run after editing .tex/.do/.py |
| context-monitor | After Bash/Task | Tracks context usage, suggests /learn at 40/55/65% |
| pre-compact | Before compression | Saves state (plan, decisions) for restoration |
| post-compact-restore | After compression | Restores context from saved state |
| log-reminder | At session stop | Reminds to update session log |

## Customization Guide

### For a New Project

1. **CLAUDE.md**: Fill in project name, research design summary, current state table
2. **params.do**: Define treatment dates, sample restrictions, outcome variables
3. **pipeline.md**: Replace example pipeline with your project's phases and steps
4. **00_run.do**: Set root paths for each collaborator
5. **run_all.sh**: Set STATA_PATH for your system
6. **manuscript/main.tex**: Fill in title, abstract, JEL codes
7. **data/raw/README.md**: Document your data sources

### For a Different Language Stack

- **R instead of Stata**: Replace `.do` references in rules with `.R`, adapt 00_run.do to 00_run.R, update run_all.sh
- **Julia/MATLAB**: Add new file type to quality-gates.md rubrics, update run_all.sh
- **No Stata at all**: Remove Stata references, keep Python pipeline

### For Slides Instead of Papers

- Change `single-source-of-truth.md` to make slides authoritative
- Add Beamer/Quarto rules from the pedrohcgs template
- Update verification-protocol.md for slide compilation

## Quality Scoring

```bash
python scripts/quality_score.py code/stata/01_import.do    # Score a Stata file
python scripts/quality_score.py code/python/15_figures.py   # Score a Python file
python scripts/quality_score.py manuscript/main.tex         # Score the manuscript
```

## Pipeline Management

```bash
./run_all.sh "01_import.do"          # Run single Stata step
./run_all.sh "0_CompControls.sas"    # Run single SAS step
./run_all.sh --all                   # Run full pipeline
```

## Recommended Plugins

For comprehensive Stata language support, install the [dylantmoore/stata-skill](https://github.com/dylantmoore/stata-skill) plugin. It provides 37 reference files covering syntax, econometrics, causal inference, and 20+ community packages (reghdfe, csdid, did_multiplegt, rdrobust, synth, etc.) with progressive disclosure to keep context lean.

```bash
/plugin marketplace add dylantmoore/stata-skill
/plugin install stata@dylantmoore-stata-skill
```

This complements the two Stata skills bundled with the template:
- **stata-execution** — Windows batch execution, MCP tool usage, syntax pitfalls, debugging
- **stata-workflow** — Panel data patterns, reghdfe specs, esttab formatting, merge workflows

## Requirements

- **Stata** (StataMP/SE) — update path in `run_all.sh`
- **SAS 9.4+** (optional) — for WRDS queries and data preparation; update path in `run_all.sh`
- **Python 3.8+** — for scripts and quality scoring
- **LaTeX** (TeX Live or MiKTeX) — for manuscript compilation
- **Git + GitHub CLI** (`gh`) — for version control
- **Claude Code** — AI development assistant
- **pdftotext** (poppler) — for token-efficient PDF doc searches (included with Git for Windows/mingw64)

## License

MIT — use freely for your own research projects.

## Credits

Built by combining:
- [pedrohcgs/claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow) — Academic workflow template with quality gates and review agents
- [Black-JL/Research-Project-Flow](https://github.com/Black-JL/Research-Project-Flow) — Research project structure with pipeline management
