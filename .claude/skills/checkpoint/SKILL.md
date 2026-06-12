---
name: checkpoint
description: Save a structured state snapshot before stopping or handing off. Captures the active plan, recent decisions, file pointers (with line numbers), open questions, and the next 1-3 actions into a checkpoint file under `quality_reports/checkpoints/`. Optionally proposes `[LEARN]` entries. Use when the user says "checkpoint", "save state", "snapshot before I stop", "where am I", "wrap up the session for handoff", or before a long break / model switch / collaborator handoff. Companion to (NOT a replacement for) the narrative session-log workflow.
author: Claude Code Academic Workflow
version: 1.0.0
argument-hint: "[short-topic-slug] [--no-memory]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Bash"]
---

<!-- Pattern adapted from Hugo Sant'Anna's clo-author /checkpoint (project-level
     session handoff: state snapshot + memory updates), reimplemented in original
     prose against this template's narrative-session-log + plan-on-disk + two-tier
     memory architecture. Attribution credit: Hugo Sant'Anna. -->

# /checkpoint -- structured session handoff

Produce a state snapshot that the next session (yours, a collaborator's, or a fresh-context reboot) can resume from in under a minute. The narrative `quality_reports/session_logs/` continues to live separately -- `/checkpoint` writes the *structured* side: facts, file pointers, and next actions.

## When to use

- Before a long break, a model switch (Opus <-> Sonnet <-> Haiku), or the end of a working day.
- Before auto-compaction would otherwise discard mid-plan context (paired with the PreCompact hook).
- Before handing off to a collaborator on the same repo (or to yourself on the home PC over SSH, or on the HPC).
- After completing a chunk of a multi-session plan, when "where am I" is the first question the next session will ask.

## When NOT to use

- For the narrative *what happened* -- that lives in `quality_reports/session_logs/` (see [`session-logging.md`](../../rules/session-logging.md)).
- For commit messages -- those go through `/commit`, which writes its own structured commit body.
- For a forced pre-compaction distillation with explicit noise-discard -- use `/compress-session`.

The two snapshot artifacts are complementary: **session-log = narrative**, **checkpoint = state to resume from**, **compression note = distilled state + discarded noise**.

## Workflow

### PHASE 1 -- Gather state

Read, in this order:

1. **Most recent plan** -- `ls -t quality_reports/plans/*.md | head -1`. Extract: status (DRAFT / APPROVED / COMPLETED), title, the files-to-modify list, and any line beginning with "Open questions" / "Risks" / "Next".
2. **Most recent session log** -- `ls -t quality_reports/session_logs/*.md | head -1`. Extract: latest "Next steps" or "Blockers" lines.
3. **MEMORY.md** (root) -- read the `[LEARN]` entries already on disk so you don't propose duplicates.
4. **Git state** -- `git log --oneline -20`, `git status -s`, `git branch --show-current`. Capture: current branch, last ~5 subjects, uncommitted file count.
5. **Working files** -- `git diff --stat HEAD` to see which files changed this session (skip if the branch is freshly cut; just say "no in-session edits").
6. **Active TODOs** -- if a TodoWrite list is in flight, capture the in-progress + next-pending items.

If any read fails (file missing), record "(none on disk)" rather than fabricating content.

### PHASE 2 -- Write the checkpoint

Write to `quality_reports/checkpoints/YYYY-MM-DD_$ARGUMENTS.md` (slug from `$ARGUMENTS`; if none, derive from the active plan's title and warn the user). Template:

```markdown
---
date: YYYY-MM-DD
branch: [current-branch]
plan: [path to active plan, or "(none)"]
session-log: [path to most recent session log, or "(none)"]
status: in_progress | paused | ready-to-merge
---

# Checkpoint -- [short topic]

## Goal (one sentence)
[What this work is trying to accomplish]

## Where I am (one paragraph)
[Last completed step, current step, what's just-not-yet-done. Bullets OK.]

## File pointers
[Concrete `path:line` references to where the next session should resume. Aim for 3-8.]
- `code/stata/04_analysis.do:412` -- Table 3 interaction block, FE spec just changed, needs re-run
- `quality_reports/plans/[slug].md:135` -- verification section to refresh after impl
- `output/logs/04_analysis.log` -- last run; check the `reghdfe` absorb line before re-running

## Recent decisions
[2-5 bullets of *why* we did what we did this session. Things not obvious from the diff. Skip if none -- do not pad.]

## Open questions
[Specific things you'd ask if someone else picked this up. Mark each Q1, Q2 ...]

## Next 1-3 actions
[Imperative, concrete. The next session opens this file and starts here.]
1. [...]
2. [...]
3. [...]

## Resume prompt
> Resuming from checkpoint `quality_reports/checkpoints/[filename]`. Read it, then continue with action 1.
```

Keep the file under ~80 lines. If state is too large for that, the plan file (not the checkpoint) is the right place; the checkpoint is a thin index pointing back at the plan.

### PHASE 3 -- Propose memory updates (skip if `--no-memory`)

Surface 0-3 candidate `[LEARN]` entries this session generated. **Don't write to MEMORY.md without user approval** -- propose-then-apply:

```
[LEARN:category] proposed: <one-line headline>
Why: <one sentence on what makes this non-obvious>
Apply where: <which future situations would benefit>
```

If the user says "yes" / "all" / "1 and 3", append to MEMORY.md (root, the committed one) in `[LEARN]` format -- **one line each**, respecting the index size budget in [`meta-governance.md`](../../rules/meta-governance.md). If a candidate is machine-specific (paths, tool versions, personal preference), recommend routing it to `personal-memory.md` (root, gitignored) instead. Full adjudication for the committed index is `/promote-memory`'s job.

Stay below 3 candidates. If you have more, the session was probably under-narrated -- flag it and recommend a session-log update instead.

### PHASE 4 -- Output summary

Print, to chat:

```
Checkpoint saved: quality_reports/checkpoints/YYYY-MM-DD_<slug>.md
  Branch: <branch>     Status: <in_progress|paused|ready-to-merge>
  Active plan: <path or none>     Open questions: <count>
  Resume: claude --continue   (or paste the file's "Resume prompt" into a fresh session)
```

If memory candidates were proposed, summarise which (if any) the user accepted.

## Cross-references

- [`.claude/rules/session-logging.md`](../../rules/session-logging.md) -- narrative companion. **Do not duplicate** -- the checkpoint references the latest session log by path; it does not re-tell the story.
- [`.claude/rules/plan-first-workflow.md`](../../rules/plan-first-workflow.md) -- the checkpoint reads the active plan; if none exists, recommend entering plan mode before invoking `/checkpoint`.
- [`.claude/rules/meta-governance.md`](../../rules/meta-governance.md) -- the two-tier memory model the PHASE 3 routing follows.
- [`.claude/hooks/pre-compact.py`](../../hooks/pre-compact.py) -- when `CLAUDE_PRECOMPACT_BLOCK_ON_DRAFT=1` is set, the PreCompact hook blocks compaction once per DRAFT plan. `/checkpoint` is the right thing to run when that block fires.
- `/compress-session` -- the forced-compression sibling (adds an explicit "discarded as noise" section).
- `/commit` -- for the commit body, not the state snapshot.

## Examples

### Example 1 -- End-of-day handoff
**User says:** "checkpoint table3-fe-rerun"
**Actions:**
1. Read `quality_reports/plans/2026-06-11_table3-fe-rerun.md` (active, APPROVED).
2. Read the latest session log.
3. Capture: branch `feat/table3-fe`, 3 commits ahead of main, 2 `.do` files modified.
4. Write `quality_reports/checkpoints/2026-06-11_table3-fe-rerun.md` with file pointers to the changed `reghdfe` absorb line in `04_analysis.do` and the un-refreshed verification block in the plan.
5. Propose 1 candidate `[LEARN:stata]` entry on the FE-spec change that fixed the coefficient.
**Result:** Next session: `claude --continue`, then "read the checkpoint and start at action 1".

### Example 2 -- Mid-plan model switch
**User says:** "switching to a cheaper model for the doc edits -- checkpoint first"
**Actions:**
1. Capture state.
2. Write checkpoint with `status: paused`.
3. Skip the memory proposal (small lift -- just resuming on a different model).
**Result:** State is on disk; the next session reads the checkpoint and continues without reloading the full plan.

## Troubleshooting

**No active plan found.** `/checkpoint` still writes a thin checkpoint with `plan: (none)`, but the right move is usually to enter plan mode first -- checkpoints without a plan reference are weak.

**Topic-slug missing.** If `$ARGUMENTS` is empty, derive from the active plan filename (strip the date prefix). If both are missing, prompt the user for one rather than fabricating.

**Output too long.** Trim "Recent decisions" and "Open questions" first. Plans go in plan files; the checkpoint should fit on a screen.
