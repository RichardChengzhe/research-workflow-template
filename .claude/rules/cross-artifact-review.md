---
paths:
  - "manuscript/**/*.tex"
  - "master_supporting_docs/**/*.tex"
  - "slides/**/*.tex"
---

# Cross-Artifact Review Protocol

A paper is not an island. Its claims depend on the code that produced them. Reviewing the paper without reviewing the code is reviewing half the artifact. When [`/review-paper`](../skills/review-paper/SKILL.md) runs on a manuscript that references analysis scripts, it auto-invokes code review on the referenced scripts and a reproducibility check on the pair, then surfaces the cross-artifact findings alongside the paper review.

## The dependency graph

```
manuscript.tex --cites--> Table 2
Table 2        --from---> output/tables/table2.tex
table2.tex     --by-----> code/stata/03_analyze.do
03_analyze.do  --uses---> data/processed/clean.dta
clean.dta      --by-----> code/stata/02_clean.do
02_clean.do    --reads--> data/raw/raw.csv
```

A bug in `02_clean.do` invalidates Table 2. Reviewing `manuscript.tex` without touching the code misses this class of error entirely.

## When to apply

Applies when `/review-paper` runs on a manuscript that references analysis scripts. Detection is **pattern-based** -- if the manuscript has none of the signals below, no cross-artifact work happens (and `--no-cross-artifact` is a no-op). To force invocation, point `/review-paper` at a manuscript that `\input{}`s the table outputs, or invoke `/review-code` and the reproducibility audit directly alongside `/review-paper`.

Detection signals:

- `\input{../output/tables/...}` or `\input{tables/...}`
- `%% source: code/stata/03_analyze.do` comments
- Numeric claims in text (coefficients, N, t-stats, p-values) **combined with** a sibling `code/stata/` / `code/python/` / `code/sas/` directory
- Table labels in the paper that match output filenames under `output/tables/` or `output/results/`

Detection is intentionally conservative -- a theory paper with no code should not trigger the protocol, even if it lives in a repo that has scripts for other work.

## The protocol

When `/review-paper` detects any of the above:

### 1. Identify referenced scripts

Scan the manuscript for:

- `\input{path}` commands (tables, figures pulled from files)
- Line comments `%% from: code/...`
- Table labels that match output filenames (e.g., `tab:main` <-> `output/tables/main.tex` <-> `code/stata/03_analyze.do`)

Build a list of scripts that produced content in this paper.

### 2. Auto-invoke code review

For each identified `.do` / `.py` / `.sas` script, launch the code reviewer ([`/review-code`](../skills/review-code/SKILL.md), the `code-reviewer` agent) in a forked subagent (`context: fork`). Save reports to `quality_reports/cross_artifact_[paper]/review_[script].md`.

### 3. Auto-invoke the reproducibility check

Run the reproducibility audit ([`/verify-claims`](../skills/verify-claims/SKILL.md) against the table outputs) once. Save to `quality_reports/cross_artifact_[paper]/reproducibility.md`. This reads existing outputs and checks the paper's numeric claims against them under the tolerance contract in [`replication-protocol.md`](replication-protocol.md).

### 4. Surface cross-artifact findings

In the paper review report, add a new section:

```markdown
## Cross-Artifact Findings

**Scripts reviewed:** N (see quality_reports/cross_artifact_[paper]/)
**Reproducibility:** PASS / FAIL -- k of m claims within tolerance
**Code quality (merged from review reports):** C critical, M major, L minor

### Critical cross-artifact issues (paper + code together)
| Paper claim | Code location | Issue |
|---|---|---|

### Code-only issues (won't block paper, but file a follow-up)
...

### Paper-only issues (code is clean)
[Rest of the paper review goes here]
```

### 5. Exit behavior

- Any CRITICAL from the reproducibility audit (FAIL on tolerance) -> escalate to CRITICAL in paper review.
- Code CRITICAL bugs that affect paper claims -> escalate in paper review.
- Code CRITICAL bugs unrelated to paper claims -> file as separate action item.

## Opt-out

- `/review-paper --no-cross-artifact` skips the dependency graph. Useful for theory papers, comments, or preprints without code.

## Cross-references

- [`.claude/skills/review-paper/SKILL.md`](../skills/review-paper/SKILL.md) -- the orchestrator.
- [`.claude/skills/review-code/SKILL.md`](../skills/review-code/SKILL.md) -- code reviewer.
- [`.claude/skills/verify-claims/SKILL.md`](../skills/verify-claims/SKILL.md) -- numeric-claims verifier.
- [`replication-protocol.md`](replication-protocol.md) -- tolerance contract.

## What this rule does NOT require

- Running Stata / Python / SAS (that is the reproducibility audit's job, and it reads existing outputs).
- Git-blame archaeology -- we review current state.
- Judging whether a paper's authors wrote good code vs. whether their *results* are defensible. We care about the latter first.

## `--peer` mode ordering

In `/review-paper --peer [journal]` mode, cross-artifact review runs **before** the editor's desk review (as Phase 0). This gives the editor reproducibility evidence -- any FAIL on load-bearing claims is desk-reject-worthy. The editor's desk review will cite specific reproducibility findings when relevant.

In default and `--adversarial` modes, cross-artifact still runs after the paper review. Both orderings are valid; the `--peer` pre-flight ordering exists because editors make desk-reject decisions based on evidence of data errors.
