# Orchestrator Protocol: Contractor Mode

**After a plan is approved, the orchestrator takes over autonomously.**

## The Loop

```
Plan approved → orchestrator activates
  │
  Step 1: IMPLEMENT — Execute plan steps
  │
  Step 2: VERIFY — Run scripts, check logs, check outputs
  │         If verification fails → fix → re-verify
  │
  Step 3: REVIEW — Run review agents (by file type)
  │
  Step 4: FIX — Apply fixes (critical → major → minor)
  │
  Step 5: RE-VERIFY — Confirm fixes are clean
  │
  Step 6: SCORE — Apply quality-gates rubric
  │
  └── Score >= threshold?
        YES → Present summary to user
        NO  → Loop back to Step 3 (max 5 rounds)
              After max rounds → present with remaining issues
```

## Adversarial Sub-Loop (Steps 3-4)

When the orchestrator reaches REVIEW + FIX, it runs adversarial critic-fixer pairs by file type instead of manual fix cycles.

### File-Type Routing

| Modified file type | Critic agent | Fixer agent |
|--------------------|-------------|-------------|
| `.do`, `.py` | `code-reviewer` | `code-fixer` |
| `.tex` (manuscript) | `proofreader` | `manuscript-fixer` |
| `output/tables/*.tex`, `output/figures/*.pdf` | `output-critic` | `output-fixer` |
| Any (substance) | `domain-reviewer` | *NONE — human review* |

### Sub-Loop Protocol

```
ROUND = 1
while ROUND <= 5:
  1. Run CRITIC on file → report + verdict (APPROVED / NEEDS_REVISION)
  2. If APPROVED: break
  3. Run FIXER with critic report
     - Classify each issue: MECHANICAL (auto-fix) or SUBSTANTIVE (human)
     - Apply MECHANICAL fixes only
     - Log all changes to quality_reports/
  4. ROUND += 1
After exit: collect remaining + all SUBSTANTIVE issues for user
```

### Verdict Thresholds

- **Code:** APPROVED when quality score >= 80 (quality-gates.md rubric)
- **Manuscript:** APPROVED when zero High-severity proofreading issues
- **Output:** APPROVED when zero Critical/Major AEA style violations
- **Domain:** Always goes to human (domain-reviewer is REPORT-ONLY, no fixer)

### Fixer Constraints

All fixers are CONSERVATIVE:
1. Fix ONLY what the critic found — no independent "improvements"
2. If uncertain whether fix is mechanical → classify as SUBSTANTIVE
3. NEVER change empirical results, specifications, or research claims
4. Log every change with before/after text

### Human Review Collection

After all sub-loops complete, present to user:
1. Fixes applied (count by category)
2. Substantive issues requiring human judgment (priority order)
3. Issues that persisted after 5 rounds (if any)
4. Final scores per file

## Limits

- **Main loop:** max 5 review-fix rounds
- **Critic-fixer sub-loop:** max 5 rounds per file per pair
- **Total sub-loop budget:** max 15 rounds per main loop iteration
- **Verification retries:** max 2 attempts
- Never loop indefinitely

## "Just Do It" Mode

When user says "just do it" / "handle it":
- Skip final approval pause
- Auto-commit if score >= 80
- Still run the full verify-review-fix loop
- Still present the summary
