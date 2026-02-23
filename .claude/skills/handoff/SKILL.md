---
name: handoff
description: End-of-session summary documenting what changed, open questions, and next steps. Writes to session_logs/.
allowed-tools: ["Read", "Glob", "Bash", "Write"]
---

# Session Handoff

Prepare an end-of-session or co-author summary.

## Steps

1. **Review recent activity:**
   - `git log --oneline` since the last handoff (or last 7 days)
   - `git diff --stat` for any uncommitted changes
   - Run `/status` internally

2. **Check for open work:**
   - Active plans in `quality_reports/plans/`
   - Active explorations in `explorations/`
   - Uncommitted changes

3. **Produce summary** covering:
   - What changed (scripts created/modified, data processed, results generated)
   - What outputs were regenerated
   - What to review
   - Open questions or decisions needed
   - Suggested next steps

4. **Write to session log:**

File: `session_logs/YYYY-MM-DD_handoff.md`

```markdown
# Session Handoff: [Date]

## Summary
[2-3 sentence overview of what was accomplished]

## Tasks Completed
- [Task 1]
- [Task 2]

## Files Created/Modified
- [file1] -- [what changed]
- [file2] -- [what changed]

## Commands Run
- [key commands executed]

## Results
- [key findings or output generated]

## Open Questions
- [question 1]
- [question 2]

## Next Steps
1. [Priority 1]
2. [Priority 2]

## Errors/Blockers
- [any unresolved issues]
```

Create `session_logs/` directory if it doesn't exist.

## Notes

- One log per day -- append if a log already exists for today
- Be specific about file paths and results
- Include enough context for a co-author to pick up where you left off
