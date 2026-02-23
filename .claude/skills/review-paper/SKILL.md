---
name: review-paper
description: Comprehensive manuscript review covering argument structure, econometric specification, citation completeness, and potential referee objections
disable-model-invocation: true
argument-hint: "[paper filename in master_supporting_docs/ or path to .tex/.pdf]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Task"]
---

# Manuscript Review

Produce a thorough, constructive review of an academic manuscript -- the kind of report a top-journal referee would write.

**Input:** `$ARGUMENTS` -- path to a paper (.tex, .pdf), or a filename in `master_supporting_docs/`.

## Steps

1. **Locate and read the manuscript.**
2. **Read the full paper** end-to-end. For long PDFs, read in chunks.
3. **Evaluate across 6 dimensions:** Argument Structure, Identification Strategy, Econometric Specification, Literature Positioning, Writing Quality, Presentation.
4. **Generate 3-5 "referee objections"** -- the tough questions a top referee would ask.
5. **Produce the review report.**
6. **Save to** `quality_reports/paper_review_[sanitized_name].md`

## Principles

- **Be constructive.** Every criticism should come with a suggestion.
- **Be specific.** Reference exact sections, equations, tables.
- **Think like a referee at a top-5 journal.**
- **Distinguish fatal flaws from minor issues.**
- **Acknowledge what's done well.**
- **Do NOT fabricate details.**
