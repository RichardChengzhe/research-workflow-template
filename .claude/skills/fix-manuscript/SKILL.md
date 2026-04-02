---
name: fix-manuscript
description: Run the adversarial proofreading loop on a manuscript file. Proofreader finds issues, manuscript-fixer applies approved fixes, re-reviews until APPROVED or max 5 rounds.
argument-hint: "[file path, e.g., manuscript/main.tex]"
allowed-tools: ["Read", "Grep", "Glob", "Edit", "Write", "Bash", "Task"]
---

# Adversarial Proofreading Loop

Run the proofreader (critic) and manuscript-fixer pair in an adversarial loop on a `.tex` file.

**Input:** `$ARGUMENTS` — path to a `.tex` file, or "all" for all manuscript files.

## Steps

1. **Identify target file(s):**
   - If `$ARGUMENTS` is a specific file: use it
   - If `$ARGUMENTS` is "all": process each `.tex` file in `manuscript/`
   - If not specified: default to `manuscript/main.tex`

2. **Run the adversarial loop (per file):**

   ```
   ROUND = 1
   while ROUND <= 5:
   ```

   **a. Launch the `proofreader` agent** on the target file.
   - Agent produces a report at `quality_reports/[FILENAME]_report.md`
   - Report lists issues by category (Grammar, Typo, Overflow, Consistency, Academic Quality) and severity (High, Medium, Low)

   **b. Check verdict:**
   - If zero High-severity issues: **APPROVED** — break the loop
   - Otherwise: **NEEDS_REVISION** — continue

   **c. Present fixes to user for approval** (interactive mode):
   - Group proposed fixes by category
   - Highlight High-severity items that need human judgment
   - Wait for user to approve all, approve selectively, or reject

   **d. Launch the `manuscript-fixer` agent** with:
   - The proofreader report path
   - The target file path
   - Mode: `interactive`
   - Agent applies only approved fixes
   - Agent logs to `quality_reports/[FILENAME]_manuscript_fixes_roundN.md`

   **e. Increment ROUND**

3. **Compile the manuscript** to verify no new errors:
   ```bash
   cd manuscript && latexmk -pdf main.tex
   ```

4. **Present summary:**
   - Number of rounds taken
   - Fixes applied (count by category)
   - Issues deferred to user
   - Compilation result (PASS/FAIL)
   - If max rounds reached: remaining issues

## Important

- The proofreader agent does NOT edit files — it only produces a report
- The manuscript-fixer respects the 3-phase proofreading protocol
- In interactive mode: user approves before each fix round
- The fixer NEVER changes sentence meaning, research claims, or equation content
- Maximum 5 rounds per file
