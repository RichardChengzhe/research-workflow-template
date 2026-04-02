---
name: fix-code
description: Run the adversarial code quality loop on a script. Code-reviewer finds issues, code-fixer applies mechanical fixes, re-reviews until APPROVED or max 5 rounds.
argument-hint: "[script path, e.g., code/stata/01_import.do]"
allowed-tools: ["Read", "Grep", "Glob", "Edit", "Write", "Bash", "Task"]
---

# Adversarial Code Quality Loop

Run the code-reviewer (critic) and code-fixer pair in an adversarial loop on a single script.

**Input:** `$ARGUMENTS` — path to a `.do` or `.py` script.

## Steps

1. **Identify the target script:**
   - If `$ARGUMENTS` is provided, use it
   - If not, ask which script to review and fix

2. **Run the adversarial loop:**

   ```
   ROUND = 1
   while ROUND <= 5:
   ```

   **a. Launch the `code-reviewer` agent** on the target script.
   - Agent produces a report at `quality_reports/[SCRIPT]_code_review.md`
   - Agent assigns a quality score (0-100)

   **b. Check verdict:**
   - If score >= 80: **APPROVED** — break the loop
   - If score < 80: **NEEDS_REVISION** — continue

   **c. Launch the `code-fixer` agent** with:
   - The review report path
   - The target script path
   - Agent classifies each issue as MECHANICAL or SUBSTANTIVE
   - Agent applies MECHANICAL fixes, logs to `quality_reports/[SCRIPT]_code_fixes_roundN.md`

   **d. Increment ROUND**

3. **After the loop exits, present summary:**
   - Final quality score
   - Number of rounds taken
   - Fixes applied (count by category)
   - Substantive issues deferred to user (listed in priority order)
   - If max rounds reached: remaining issues that could not be auto-fixed

## Important

- The code-reviewer agent does NOT edit files — it only produces a report
- The code-fixer agent implements ONLY mechanical fixes from the report
- Substantive issues (wrong specs, wrong clustering, etc.) are ALWAYS deferred to the user
- Maximum 5 rounds — if still below 80 after 5 rounds, present remaining issues
