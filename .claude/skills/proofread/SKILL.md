---
name: proofread
description: Run the proofreading protocol on manuscript files. Checks grammar, typos, overflow, consistency, and academic writing quality. Produces a report without editing files.
argument-hint: "[filename or 'all']"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# Proofread Manuscript Files

Run the mandatory proofreading protocol on manuscript files. This produces a report of all issues found WITHOUT editing any source files.

## Steps

1. **Identify files to review:**
   - If `$ARGUMENTS` is a specific filename: review that file only
   - If `$ARGUMENTS` is "all": review all `.tex` files in `manuscript/`

2. **For each file, launch the proofreader agent** that checks for:

   **GRAMMAR:** Subject-verb agreement, articles (a/an/the), prepositions, tense consistency
   **TYPOS:** Misspellings, search-and-replace artifacts, duplicated words
   **OVERFLOW:** Overfull hbox, content exceeding margins
   **CONSISTENCY:** Citation format, notation, terminology
   **ACADEMIC QUALITY:** Informal language, missing words, awkward constructions, claims without citations

3. **Produce a detailed report** for each file listing every finding with:
   - Location (line number or section)
   - Current text (what's wrong)
   - Proposed fix (what it should be)
   - Category and severity

4. **Save each report** to `quality_reports/[FILENAME_WITHOUT_EXT]_report.md`

5. **IMPORTANT: Do NOT edit any source files.**

6. **Present summary** to the user:
   - Total issues found per file
   - Breakdown by category
   - Most critical issues highlighted
