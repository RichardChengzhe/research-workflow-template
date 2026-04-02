---
name: fix-output
description: Run the adversarial output formatting loop. Output-critic checks tables/figures against AEA style, output-fixer applies formatting fixes, re-checks until APPROVED or max 5 rounds.
argument-hint: "[optional: specific table/figure path]"
allowed-tools: ["Read", "Grep", "Glob", "Edit", "Write", "Bash", "Task"]
---

# Adversarial Output Formatting Loop

Run the output-critic and output-fixer pair in an adversarial loop on tables and figures.

**Input:** `$ARGUMENTS` — optional path to a specific table or figure. If omitted, checks all output.

## Steps

1. **Identify target files:**
   - If `$ARGUMENTS` specifies a file: check that file only
   - Otherwise: check all `output/tables/*.tex` and `output/figures/*.pdf`

2. **Run the adversarial loop:**

   ```
   ROUND = 1
   while ROUND <= 5:
   ```

   **a. Launch the `output-critic` agent** on target files.
   - Agent performs two passes:
     - Pass 1: Check output `.tex` files against AEA style guide
     - Pass 2: Check source `esttab` commands in `.do` files
   - Agent produces report at `quality_reports/output_review_roundN.md`
   - Verdict: APPROVED or NEEDS_REVISION

   **b. Check verdict:**
   - If zero Critical AND zero Major issues: **APPROVED** — break
   - Otherwise: **NEEDS_REVISION** — continue

   **c. Launch the `output-fixer` agent** with:
   - The output review report path
   - Agent applies output-level fixes (edit `.tex` tables)
   - Agent applies source-level fixes (edit `esttab` in `.do` files)
   - Agent logs to `quality_reports/output_fixes_roundN.md`

   **d. Increment ROUND**

3. **After the loop exits, present summary:**
   - Number of rounds taken
   - Output-level fixes applied
   - Source-level fixes applied
   - **Scripts that need re-running** (because source-level esttab commands were changed)
   - Compilation check result
   - Remaining issues (if max rounds reached)

4. **If source-level fixes were applied:**
   - List each `.do` script that was modified
   - Tell the user: "Run `./run_all.sh '[script]'` to regenerate output with corrected formatting"

## Important

- The output-critic does NOT edit files — it only produces a report
- The output-fixer NEVER changes coefficient values, standard errors, or any numeric content
- Output-level fixes to `.tex` files are temporary — they get overwritten when the pipeline re-runs
- Source-level fixes to `.do` esttab commands persist across re-runs
- Maximum 5 rounds
- References `manuscript/aea_style_guide.md` for all formatting standards
