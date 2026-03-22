---
name: status
description: Quick project overview showing pipeline status, recent logs, and current state. Run silently at session start.
allowed-tools: ["Read", "Glob", "Bash"]
---

# Project Status Overview

Quick project overview for session orientation.

## Steps

1. **Pipeline status:**
   - Read `pipeline.md` Script Status table
   - Check which scripts exist in `code/stata/` and `code/python/`

2. **Recent logs:**
   - List most recent log per script in `output/logs/`
   - Show dates and whether they ended clean or with errors

3. **Recent git activity:**
   - `git log --oneline -5` (if git is initialized)
   - `git status` for uncommitted changes

4. **Data status:**
   - Check which raw data files exist
   - Check which processed data files exist

5. **Active work:**
   - Check `scratch/` for active work
   - Check `explorations/` for active projects
   - Check `quality_reports/plans/` for active plans

## Output Format

```
Project: [YOUR PROJECT NAME]

Pipeline Status:
| Step | Script | Last Run | Status |
|------|--------|----------|--------|
| ... | ... | ... | ... |

Recent Activity:
- [git log summary]
- [uncommitted changes if any]

Data:
- Raw: [N files in data/raw/]
- Processed: [N files in data/processed/]

Active Work:
- Plan: [active plan or "none"]
- Explorations: [active explorations or "none"]
```

## Notes

- This skill is called silently at session start (per CLAUDE.md)
- Only report to user if something needs attention
- Keep output concise
