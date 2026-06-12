---
name: new-skill
description: Scaffold a new skill that follows this repo's conventions -- interviews for purpose, trigger phrases, and tool needs, then writes `.claude/skills/<name>/SKILL.md` from the skill template with frontmatter and body that pass the integrity gates on first try. Use when the user says "write a skill", "scaffold a skill", "create a new skill", "I keep doing X, make it a skill", "new slash command", or "turn this workflow into a skill". NOT for capturing a one-off session discovery -- that is `/learn`.
author: Claude Code Academic Workflow
version: 1.0.0
argument-hint: "[skill-name (kebab-case)] [--from-learn] [--dry-run]"
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash"]
disable-model-invocation: true
effort: medium
---

# /new-skill -- author a convention-compliant skill

Scaffold a new skill the way this template's gold-standard skills are written: a **deep module behind a simple interface** (Ousterhout, *A Philosophy of Software Design* -- "deep modules": a small surface that hides substantial implementation). The user supplies a fuzzy intent; this skill interviews it into a tight spec, then writes `.claude/skills/<name>/SKILL.md` with frontmatter and body that are mutually consistent -- so the skill-integrity and surface-sync gates pass without a second pass.

Adapted from the *write-a-skill* pattern in [mattpocock/skills](https://github.com/mattpocock/skills), reshaped to this repo's frontmatter, section, and gate conventions.

## Relation to `/learn`

Both are kept, and they are complementary:

- **`/learn`** *extracts* a non-obvious discovery from the **current session** into a quick persistent skill (the lighter, reactive path -- see [`/learn`](../learn/SKILL.md)).
- **`/new-skill`** *designs* a skill **from scratch**: it interviews for an interface, enforces flag/tool parity, and emits a full gold-standard SKILL.md.

Use `/learn` when the trigger is "I just figured something out". Use `/new-skill` when the trigger is "I keep doing this multi-step thing; make it a proper command." With `--from-learn`, this skill upgrades a `/learn`-shaped stub into a full convention-compliant skill.

## When to use

- You keep re-explaining the same 3+ step workflow to Claude and want it captured as a reusable slash command.
- You need a domain-specific check or output format (a citation style, a replication gate, a new review lens, a WRDS/Stata pattern).
- You want a new skill consistent with the dozens of siblings in `.claude/skills/` -- same sections, same cross-reference style, same gate-passing frontmatter.

## Phases

### Phase 0 -- Resolve the name and check for collisions

1. Take the kebab-case name from `$0` (or ask). Reject non-kebab-case, names that collide with an existing `.claude/skills/<name>/`, or names that shadow a built-in (`commit`, `learn`, ...) -- `ls .claude/skills/` and stop if taken.
2. Read [`templates/skill-template.md`](../../../templates/skill-template.md) for the canonical structure and the frontmatter-field reference.
3. Skim 2-3 sibling skills near the intended domain (`Glob .claude/skills/*/SKILL.md`, then `Read` the closest matches) so the new skill borrows real conventions, not invented ones.

### Phase 1 -- Interview (collect everything *before* writing)

A skill cannot stop to ask mid-write, so gather all interactivity up front (the [orchestrator-protocol.md](../../rules/orchestrator-protocol.md) "collect interactivity first" discipline). Ask, in one batch:

1. **Purpose** -- one sentence: what does it accomplish and why does it exist?
2. **Trigger phrases** -- the 4-7 quoted phrases a user would actually say. These become the `description`'s "Use when..." clause and are what makes the skill auto-discoverable.
3. **Inputs / arguments** -- positional args and any **flags** (each must become a documented `--token`).
4. **Tools** -- does the body Read? Write? Grep/Glob? run `Bash`? fan out to a subagent (the `Task` tool)? hit the web via `WebSearch`/`WebFetch`? Only declare what it actually uses.
5. **Output** -- a written file (where?), a chat report, or an in-place edit? Should it be read-only?
6. **Scope boundary** -- the one or two things it explicitly does NOT do (and which sibling owns those).

Echo a one-paragraph **design brief** back for confirmation before writing.

### Phase 2 -- Write the SKILL.md (deep module, simple interface)

Write `.claude/skills/<name>/SKILL.md` from the template, with these gold-standard sections:

- Frontmatter: `name`, `description` (third person, with the quoted trigger phrases), `argument-hint`, `allowed-tools`, `effort`. Add `disable-model-invocation: true` if it writes a persistent, load-bearing file (the template's "when to disable" rule).
- Body sections: **When to use**, numbered **Phases** (or Steps), an **Output / report format**, **Exit behavior**, **Cross-references** (to real sibling files), **What this skill does NOT do**, and a **## Flags** section if any flags are advertised.
- Keep the *interface* small (a few args) and the *implementation* deep (the phases carry the weight) -- resist exposing a knob for every internal choice.

### Phase 3 -- Enforce parity so the gates pass first try

This repo's pre-commit hook ([`.githooks/pre-commit`](../../../.githooks/pre-commit), installed via `./scripts/install-hooks.sh`) runs two deterministic surface gates on commit. Their check scripts -- `scripts/check-skill-integrity.py` and `scripts/check-surface-sync.sh` -- are provided as a sibling unit of this template; when a script is absent the hook **warns-and-skips** rather than hard-failing, but you should still write the skill to satisfy them so it passes the moment they are present. The two parities to satisfy:

- **Flag parity (both directions).** Every flag in `argument-hint` MUST appear in the body as a bare-backticked token, and every flag documented in the body MUST appear in `argument-hint`. So `--from-learn` and `--dry-run` are listed in the hint *and* described under `## Flags`. A stale hint flag fails the gate as surely as a missing one.
- **allowed-tools parity.** The body may only invoke tools listed in `allowed-tools`. If a phase fans out to a subagent (the `Task` tool), that tool must be in the list; if it never does, do not list it. This skill lists exactly `Read, Write, Glob, Grep, Bash` -- the tools its phases use, and no subagent fan-out.
- **Anchor resolution.** Internal `[text](path#anchor)` links must resolve -- only link to headings that exist.

If `scripts/check-skill-integrity.py` is present, run it (`python scripts/check-skill-integrity.py --verbose`, falling back to `python3`) and fix any reported issue before declaring done. If it is not yet present, self-check the three parities above by hand.

### Phase 4 -- Remind: register the surface (table-row gate)

The skill is NOT discoverable to a reader until it is listed in the two surface tables. `scripts/check-surface-sync.sh` (when present) enforces a **table-row gate**: each skill on disk needs exactly one data row in both surface tables. Adding a skill without rows fails the gate.

REMIND the user to add a row to BOTH tables (both use the `| Command | What It Does |` two-column form):

1. **CLAUDE.md** "Skills Quick Reference" table.
2. **README.md** "Skills (Slash Commands)" table.

Print the two ready-to-paste rows so the user can drop them in, e.g.:

```markdown
| `/<name> [args]` | <one-line what-it-does> |
```

Then have the user run the gates: `./scripts/check-surface-sync.sh` and `python scripts/check-skill-integrity.py` (when present) -- both must exit 0 -- or simply attempt a commit, which runs both via the pre-commit hook.

## Output / report format

- A new file at `.claude/skills/<name>/SKILL.md`.
- A chat summary: the resolved name, the design brief, the parity self-check (or gate) results, and the two paste-ready table rows with the explicit "now add those rows" reminder.
- With `--dry-run`: emit the proposed SKILL.md to chat only and write nothing.

## Exit behavior

- **Skill written, parities satisfied:** exit with the path, the two table rows, and the explicit "now add those rows + run the gates (or commit)" reminder.
- **Name collision or non-kebab-case:** stop in Phase 0 with the conflict named; write nothing.
- **`check-skill-integrity.py` present and reports an issue:** fix in-place and re-run before returning; never hand back a skill that fails its own gate.
- **`--dry-run`:** print the draft, write nothing, exit.

## Flags

- `--from-learn` -- Seed the interview from an existing `/learn`-style stub (or the current session's discovery) and upgrade it into a full convention-compliant skill rather than starting blank.
- `--dry-run` -- Produce the SKILL.md content in chat for review without writing it to disk or touching any surface table.

## Cross-references

- [`templates/skill-template.md`](../../../templates/skill-template.md) -- the canonical structure, frontmatter-field reference, and the "when to set `disable-model-invocation`" rule this skill follows.
- [`.claude/skills/learn/SKILL.md`](../learn/SKILL.md) -- capture a session discovery (the lighter sibling); `--from-learn` upgrades its output.
- [`.claude/skills/coauthor-brief/SKILL.md`](../coauthor-brief/SKILL.md) -- a gold-standard skill to imitate (interview -> write -> flags -> exit-behavior shape).
- [`.claude/rules/orchestrator-protocol.md`](../../rules/orchestrator-protocol.md) -- why the interview collects all interactivity *before* writing.
- [`.githooks/pre-commit`](../../../.githooks/pre-commit) and `scripts/check-skill-integrity.py` / `scripts/check-surface-sync.sh` -- the gates this skill is built to pass (provided as a sibling unit; warn-and-skip when absent).

## What this skill does NOT do

- **Capture a session discovery** -- that is [`/learn`](../learn/SKILL.md). This skill designs an interface; `/learn` records a finding.
- **Edit the README / CLAUDE.md surface tables for you.** It *prints* the two rows and reminds you; registering them (and re-running the gates) is a deliberate human step so the surface gate is never silently satisfied.
- **Write agents, rules, or hooks.** It scaffolds a skill only; an agent goes in `.claude/agents/`, a rule in `.claude/rules/`.
- **Commit anything.** Branch / PR / merge is [`/commit`](../commit/SKILL.md)'s job.
