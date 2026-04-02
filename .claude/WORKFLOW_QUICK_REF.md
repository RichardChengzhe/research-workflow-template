# Workflow Quick Reference

**Model:** Contractor (you direct, Claude orchestrates)

---

## The Loop

```
Your instruction
    |
[PLAN] (if multi-file or unclear) -> Show plan -> Your approval
    |
[EXECUTE] Implement, verify, done
    |
[REPORT] Summary + what's ready
    |
Repeat
```

---

## I Ask You When

- **Design forks:** "Option A (fast) vs. Option B (robust). Which?"
- **Pipeline changes:** "This modifies the I/O graph. Breaking the glass -- here's what changes."
- **Parameter changes:** "This affects params.do. Confirm?"
- **Scope question:** "Also refactor Y while here, or focus on X?"

---

## I Just Execute When

- Code fix is obvious (bug, pattern application)
- Verification (log checks, compilation, output validation)
- Documentation (session logs, commits)
- Plotting (per established standards)

---

## Quality Gates (No Exceptions)

| Score | Action |
|-------|--------|
| >= 80 | Ready to commit |
| < 80  | Fix blocking issues |

---

## Adversarial QA

Critic-fixer pairs auto-fix mechanical issues, flag substantive issues for you:

| Command | What It Fixes |
|---------|--------------|
| `/fix-code [script]` | Headers, paths, labels, formatting |
| `/fix-manuscript [file]` | Grammar, typos, consistency |
| `/fix-output` | AEA table/figure formatting |

Fixers NEVER change empirical results, specifications, or research claims.

---

## Non-Negotiables

- **Relative paths only** -- globals defined in `code/stata/00_run.do` for Stata
- **`data/raw/` is READ-ONLY** -- never modify, never delete
- **Every Stata .do file produces a .log** -- via `run_all.sh` to `output/logs/`
- **`set seed` for stochastic computation** -- always, with project seed from params.do
- **Publication-ready figures:** 300 DPI minimum, explicit dimensions, vector (PDF) preferred
- **Pipeline changes require "break the glass" confirmation** -- I/O graph, step order, params
- **Check params.do before hardcoding** -- all research parameters centralized there
- **Read log after every run** -- never assume success without checking

---

## Preferences

**Execution:** `run_all.sh` for pipeline steps; MCP Stata for interactive exploration
**Reporting:** Concise bullets with key findings; details on request
**Session logs:** Always (post-plan, incremental, end-of-session)
**Code style:** Stata conventions in `python-stata-conventions.md`; Python PEP 8

---

## Exploration Mode

For experimental work, use the **Fast-Track** workflow:
- Work in `explorations/` folder
- 60/100 quality threshold (vs. 80/100 for production)
- No plan needed -- just a research value check (2 min)
- See `.claude/rules/exploration-fast-track.md`

---

## Next Step

You provide task -> I plan (if needed) -> Your approval -> Execute -> Done.
