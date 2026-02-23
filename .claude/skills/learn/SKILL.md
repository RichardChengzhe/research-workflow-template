---
name: learn
description: |
  Extract reusable knowledge from the current session into a persistent skill.
  Use when you discover something non-obvious, create a workaround, or develop
  a multi-step workflow that future sessions would benefit from.
author: Claude Code Academic Workflow
version: 1.0.0
argument-hint: "[skill-name (kebab-case)]"
---

# /learn -- Skill Extraction Workflow

Extract non-obvious discoveries into reusable skills that persist across sessions.

## When to Use This Skill

Invoke `/learn` when you encounter:

- **Non-obvious debugging** -- Investigation that took significant effort
- **Misleading errors** -- Error message was wrong, found the real cause
- **Workarounds** -- Found a limitation with a creative solution
- **Tool integration** -- Undocumented API usage or configuration
- **Repeatable workflows** -- Multi-step task you'd do again

## Workflow Phases

### PHASE 1: Evaluate (Self-Assessment)

1. "What did I just learn that wasn't obvious before starting?"
2. "Would future-me benefit from this being documented?"
3. "Was the solution non-obvious from documentation alone?"
4. "Is this a multi-step workflow I'd repeat?"

**Continue only if YES to at least one question.**

### PHASE 2: Check Existing Skills

```bash
ls .claude/skills/ 2>/dev/null
```

### PHASE 3: Create Skill

Create the skill file at `.claude/skills/[skill-name]/SKILL.md` using the template from `templates/skill-template.md`.

### PHASE 4: Quality Gates

- [ ] Description has specific trigger conditions
- [ ] Solution was verified to work
- [ ] Content is specific enough to be actionable
- [ ] Content is general enough to be reusable
- [ ] No sensitive information
