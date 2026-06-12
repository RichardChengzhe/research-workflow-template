# Meta-Governance: This Repository's Dual Nature

**This repository is BOTH a working project AND a template for others.**

Understanding this distinction is critical for deciding what to commit, what to document, and where to save learnings.

---

## The two identities

### Identity 1: Working project
- We actively develop the manuscript, analysis code, slides, and documentation
- We accumulate learnings specific to our setup and workflow (HPC, WRDS, machine paths)
- We test new features and iterate on infrastructure
- We have institutional context (a specific university, dataset licenses, a particular paper)

### Identity 2: Public template
- Others fork this repo to bootstrap their own empirical-research workflows
- They use different fields (finance, accounting, labor, health, marketing)
- They use different tool mixes (pure Stata, Python + Jupyter, SAS-on-WRDS, R)
- They need generic patterns, not our specific decisions

---

## Decision framework

When creating or modifying content, ask:

### "Is this GENERIC or SPECIFIC?"

**GENERIC (commit to repo, helps all users):**
- Workflow patterns (spec-then-plan, quality gates, orchestrator, plan-first)
- Design principles (replication-first, t-stats-not-SE, single-source-of-truth for parameters)
- Templates (requirements spec, regression-table template, skill template)
- Documentation standards (update README + guide together)
- Rules that adapt to user context (path-scoped rules)

**SPECIFIC (keep local or gitignore):**
- Machine-specific paths (`E:\Dropbox\...`, the SSH alias for your home PC, scratch dirs)
- Tool versions and credentials (`autoexec.sas`, WRDS username, API keys)
- Institutional requirements (a particular journal's house style, an IRB protocol number)
- Personal preferences (a 90/100 gate for this project, your preferred FE convention)
- Local workarounds (a Cypress module-load quirk, a one-off path junction)

---

## Memory management: two-tier system

### MEMORY.md (root directory, committed)

**Purpose:** Generic learnings that help ALL users

**What goes here:**
- Workflow improvements: `[LEARN:workflow] Spec-then-plan reduces rework`
- Design principles: `[LEARN:design] Construct rank/treatment measures AFTER all merges`
- Documentation patterns: `[LEARN:documentation] Update README + guide together`
- Quality standards: `[LEARN:quality] 80/90/95 thresholds work across fields`

**Review cadence:** After every significant session (plan approval, feature implementation)

**Size limit:** Keep the *index* under ~200 lines / ~24 KB (it loads into Claude's context). Move detail into per-topic files and keep one-line index entries.

---

### .claude/state/personal-memory.md (gitignored, local only)

**Purpose:** Machine-specific and user-specific learnings

**What goes here:**
- Machine setup: `[LEARN:stata] Git-Bash needs MSYS_NO_PATHCONV=1 + cygpath -w on this box`
- Tool quirks: `[LEARN:wrds] Duo caches per-day; one push per working day on this account`
- Local paths: `[LEARN:files] Raw extracts at E:\...\data\raw on the office desktop`
- Personal workflow: `[LEARN:workflow] I prefer 90/100 for ship-bound tables, 60/100 for explorations`

**Review cadence:** As needed (no pressure to formalize)

**Size limit:** None (does not load into context automatically)

---

## Cross-machine access

### Scenario: user works on multiple machines

**Machine A (office desktop):**
- Clone repo -> gets MEMORY.md with generic learnings
- Gets all infrastructure (skills, agents, rules, templates)
- Builds `.claude/state/personal-memory.md` specific to the desktop setup (WRDS creds, scratch paths)

**Machine B (laptop / HPC login node):**
- Clone same repo -> gets same MEMORY.md
- Gets same infrastructure
- Builds a DIFFERENT `.claude/state/personal-memory.md` for that environment

**Key insight:** Generic patterns sync via git; personal patterns stay local (or are manually copied if truly needed).

---

## Dogfooding: following our own guide

**We must follow the patterns we recommend to users.**

### Plan-first workflow
- Do: Enter plan mode for non-trivial tasks (>3 files, >1 hour, multi-step)
- Do: Save plans to `quality_reports/plans/YYYY-MM-DD_description.md`
- Don't: Skip planning for "quick fixes" that turn into multi-hour tasks

### Spec-then-plan
- Do: Create requirements specs for complex/ambiguous tasks (MUST/SHOULD/MAY)
- Don't: Jump straight to planning when requirements are fuzzy

### Quality gates
- Do: Run quality scoring before commits; nothing ships below 80/100
- Don't: Commit "WIP" code without quality verification

### Documentation standards
- Do: Update README and the relevant skill/rule together when adding a feature
- Don't: Let documentation drift from implementation (see [`summary-parity.md`](summary-parity.md))

### Context survival
- Do: Update MEMORY.md with `[LEARN]` entries after sessions; save active plans to disk before compression
- Don't: Rely solely on conversation history (it compresses)

---

## Template maintenance principles

### Keep it generic

**Bad (too specific):**
```markdown
# Stata Execution Rule
Always run with stata-mp -e and the autoexec at E:\Dropbox\proj for our WRDS account.
```

**Good (framework-oriented):**
```markdown
# Stata Execution Rule
Run via run_all.sh; configure the Stata binary and any autoexec path in CLAUDE.md for your setup.
```

### Provide examples from multiple fields

**Bad (single use case):** "Example: a single firm-month sentiment panel."

**Good (diverse use cases):**
```markdown
Examples:
- Finance: firm-month panel with firm + month fixed effects
- Labor: individual-year panel, staggered policy adoption (DiD)
- Health: hospital-quarter panel with restricted admin data
```

### Use templates, not prescriptions

**Bad (prescriptive):** "Your bibliography MUST be named refs.bib and live in root."

**Good (template with placeholders):** "Configure the bibliography location in CLAUDE.md: `[YOUR_BIB_FILE]` (e.g., `refs.bib`, `../library.bib`)."

---

## When to make exceptions

- **Templates can show specific examples.** It is fine for the README/guide to say "this workflow was developed for a firm-panel asset-pricing project" -- as long as it is clear that is ONE example, not THE requirement.
- **CLAUDE.md can have placeholders.** `[YOUR PROJECT NAME]`, `[YOUR INSTITUTION]` are correct; users fill them in.
- **Documentation can reference the original use case** to show what is *possible*, not what is *required*.

---

## Amendment process

**When to amend this file:**
- We discover a better way to distinguish generic vs specific
- Cross-machine workflows change (e.g., Claude Code adds cloud sync)
- The memory system evolves (e.g., automatic `[LEARN]` extraction)
- User feedback reveals confusion about template vs working project

**Amendment protocol:**
1. Propose the change in a session log or plan
2. Discuss implications (what breaks? what improves?)
3. Update this file
4. Document the change with a `[LEARN:meta-governance]` entry in MEMORY.md

---

## Quick reference table

| Content type | Commit to repo? | Where it goes | Syncs across machines? |
|--------------|----------------|---------------|----------------------|
| Workflow patterns (generic) | Yes | MEMORY.md | Yes (via git) |
| Machine-specific setup / credentials | No | .claude/state/personal-memory.md (+ gitignored autoexec) | No |
| Templates (generic) | Yes | templates/ | Yes |
| Skills (generic) | Yes | .claude/skills/ | Yes |
| Rules (path-scoped, generic) | Yes | .claude/rules/ | Yes |
| Agents (generic) | Yes | .claude/agents/ | Yes |
| Hooks (generic behavior) | Yes | .claude/hooks/ | Yes |
| Session logs | Yes | quality_reports/session_logs/ | Yes |
| Plans | Yes | quality_reports/plans/ | Yes |
| Local settings | No | .claude/settings.local.json | No |
| Session state | No | .claude/state/ | No |
| Build artifacts | No | .aux, .log, .synctex.gz, output/logs/ | No |
| Raw / restricted data | No | data/raw, data/restricted (gitignored) | No (see confidential-data.md) |

---

## Summary

**This repository serves two masters:** our working project (specific, contextual, evolving) and a template for others (generic, framework-oriented, stable).

**The solution:**
- Commit generic patterns that help all users (MEMORY.md, templates, infrastructure)
- Keep specific learnings local (.claude/state/personal-memory.md, gitignored)
- Dogfood our own workflow (plan-first, spec-then-plan, quality gates)
- Document with examples from multiple fields (not just our use case)
- Review periodically: promote generic patterns, refine specific ones

**When in doubt:** Ask "Would a health-economics PhD student forking this repo for a hospital panel benefit from this knowledge?" If yes -> MEMORY.md. If no -> personal-memory.md.

## Cross-references
- [`confidential-data.md`](confidential-data.md) -- the committed-vs-local model applied to restricted data and paths.
- [`summary-parity.md`](summary-parity.md) -- keeping committed summaries from drifting.
- [`plan-first-workflow.md`](plan-first-workflow.md) · [`quality-gates.md`](quality-gates.md) -- the dogfooded workflow.
