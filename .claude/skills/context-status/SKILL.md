---
name: context-status
description: |
  Show current context status and session health.
  Use to check how much context has been used, whether auto-compact is
  approaching, and what state will be preserved.
author: Claude Code Academic Workflow
version: 1.0.0
---

# /context-status -- Check Session Health

Show the current session status including context usage estimate, active plan,
and preservation state.

## What This Skill Shows

1. **Context usage estimate** -- Approximate % of context window used
2. **Active plan** -- Current plan file and status
3. **Session log** -- Most recent session log
4. **Preservation state** -- What will survive compaction

## Workflow

### Step 1: Check Context Monitor Cache

```bash
cat ~/.claude/sessions/*/context-monitor-cache.json 2>/dev/null | head -20
```

### Step 2: Find Active Plan

```bash
ls -lt quality_reports/plans/*.md 2>/dev/null | head -3
```

### Step 3: Find Session Log

```bash
ls -lt quality_reports/session_logs/*.md session_logs/*.md 2>/dev/null | head -3
```

### Step 4: Report Status

Format a clean status summary showing context usage, active plan, session log, and preservation state.
