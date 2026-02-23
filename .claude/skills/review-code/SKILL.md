---
name: review-code
description: Invoke the code-reviewer agent on a Python or Stata script. Produces a quality report with scores and recommendations.
argument-hint: "[script path, e.g., code/stata/01_import.do]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# Code Review

Run the code-reviewer agent on a specified script.

**Input:** `$ARGUMENTS` -- path to a `.do` or `.py` script.

## Steps

1. **Identify the target script:**
   - If `$ARGUMENTS` is provided, use it
   - If not, ask which script to review

2. **Launch the code-reviewer agent** on the target script.

3. The agent reviews through 8 lenses:
   - Script structure
   - Reproducibility
   - Data management
   - Domain correctness
   - Output quality
   - Documentation
   - Error handling
   - Professional polish

4. **Present the review report** to the user with:
   - Quality score (0-100)
   - Critical issues (must fix)
   - Major issues (should fix)
   - Minor issues (nice to fix)
   - Positive findings

5. **Save report** to `quality_reports/[script_name]_code_review.md`

## Important

- The agent does NOT edit files -- it only produces a report
- Address Critical issues before committing
- Use quality-gates.md rubrics for scoring
