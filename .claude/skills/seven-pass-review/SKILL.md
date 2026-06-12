---
name: seven-pass-review
description: The seven-pass adversarial review protocol for an empirical finance/accounting manuscript. Spawns 7 forked subagents in parallel (abstract, intro, methods/identification, results, robustness, prose, citations), loops until two consecutive dry rounds, then synthesizes a prioritized revision checklist. Use for submission-ready or R&R-stage papers where single-pass review isn't enough.
argument-hint: "[manuscript path]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Task"]
effort: high
---

# Seven-Pass Adversarial Review

Runs seven independent reviewers, each focused on a single lens, then synthesizes their findings into one prioritized revision plan. Loops until the review is dry (two consecutive rounds with no new CRITICAL/MAJOR).

**Why seven passes?** A single-agent review blends lenses and softens each one. Seven forked agents each approach the paper with full context budget for their own lens, then a synthesizer resolves conflicts and de-duplicates.

> **When to pick this over `/review-paper`:** This skill costs roughly 7x more tokens than `/review-paper` (default) and ~2x more than `/review-paper --adversarial`. Use it when the paper is submission-ready or at R&R stage and you need maximum lens coverage. For early drafts or iterative work, `/review-paper` is the right tool. For a journal-simulation pressure test (editor + two dispositioned referees), use `/review-paper --peer <journal>` instead.

## Inputs

- `$0` — manuscript path (`.tex`, `.md`, or `.pdf`). Required. Authoritative source is normally `manuscript/main.tex`.

## The Seven Lenses

Each lens runs as a **forked subagent** (context: fork) so the main conversation stays clean.

| # | Lens | Focus | Agent type |
|---|---|---|---|
| 1 | Abstract audit | Does the abstract state the question, method, result, and contribution? Does it match the paper? | general-purpose |
| 2 | Intro structure | Does the intro follow the Cochrane (2005) "Writing Tips" arc? Literature placement? Contribution clarity? | general-purpose |
| 3 | Methods / identification | Are assumptions stated? Is identification credible? Are alternatives addressed? | domain-reviewer |
| 4 | Results + tables + figures | Do tables read standalone? Is magnitude + significance discussed? Are figures legible at print size? | general-purpose |
| 5 | Robustness | Are obvious threats pre-empted? Is the robustness section convincing or theatrical? | general-purpose |
| 6 | Prose quality | Sentence-level clarity, hedging, passive voice, paragraph cohesion | proofreader |
| 7 | Citation audit | Invokes `/validate-bib` (structural existence); checks cite-claim direction for top-10 works | general-purpose |

## Workflow

### Phase 0: Pre-flight

1. Resolve manuscript path.
2. Decide if `.pdf` → extract text first (`pdftotext -layout "$0" out.txt`). For a multi-file `.tex` project, resolve `\input{}` / `\include{}` so each lens sees the whole paper.
3. Create output dir: `quality_reports/seven_pass_[stem]/`.

### Phase 1: Spawn 7 reviewers in parallel

In a single message, spawn 7 Task tool calls (one per lens). Each subagent gets:

- The manuscript path (to re-read with its own context).
- The lens-specific prompt (below).
- Instructions to write to `quality_reports/seven_pass_[stem]/lens_[N]_[lens-name].md`.
- A closing `findings:` + `scorecard:` block in the shared schema ([`orchestration-schemas.md`](../../references/orchestration-schemas.md)): `severity: CRITICAL | MAJOR | MINOR`, with `evidence` and `change_my_mind` on every CRITICAL/MAJOR. Phase 2 reduces over these typed findings — it does not re-read the prose.

This is the **fan-out** primitive from [`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md); `Task` subagents are the portable mechanism (the agents that fill lenses 3/6 are catalogued in [`agent-fleet.md`](../../references/agent-fleet.md)).

Lens prompt rubrics are embedded inline below — one summary paragraph per lens. Each forked subagent receives its lens's rubric plus the manuscript path.

**Lens prompt summaries:**

- **Lens 1 (Abstract):** Does the first sentence state the question? Does it name the method (panel FE / event study / Fama-MacBeth / structural)? Quantify the headline result in economically meaningful units (bps of return, pp of an outcome, $ of value)? State a one-sentence contribution? Cross-check: do these four things match the body?
- **Lens 2 (Intro):** Does the intro open with the question? Hook → institutional/economic context → contribution → roadmap (Cochrane 2005)? Literature placed correctly (after the hook, not before)? Contribution-counted (1, 2, 3…)? Preview of findings with magnitudes, not just signs?
- **Lens 3 (Methods):** Is every identifying assumption stated in one testable sentence? Are they strong or weak? Are known threats (selection, measurement error, look-ahead bias, reverse causality, omitted risk factor) addressed? For DiD/event study: are pre-trends / pre-event CARs shown? For IV: is the exclusion restriction argued narratively, not just an F-stat? Is the standard-error clustering matched to the dependence structure (firm, and/or time)?
- **Lens 4 (Results, tables, figures):** Does each table read standalone (caption, column labels, what's in parentheses — t-stats vs SE — N, adj-R², FE rows)? Is magnitude interpreted, not just significance? Are units consistent across tables? Are figures legible when printed at journal width: axis labels and tick labels readable at ~8pt, no reliance on color alone (grayscale-safe), 300 DPI? (Defer the deep figure-rendering check to `/visual-audit`.)
- **Lens 5 (Robustness):** Does the paper ANTICIPATE a sharp referee's objections? Are robustness checks motivated by a specific threat, or just listed (robustness theater)? Alternative FE / alternative factor model / alternative sample / alternative clustering present where it matters? Placebo / falsification tests? Heterogeneity explored where promised and pre-specified (not p-hacked)?
- **Lens 6 (Prose):** Sentences under ~30 words? Active voice dominant? Hedging proportionate (neither overclaiming causality nor endless "may suggest")? Paragraph topic sentences? Notation consistent (a symbol defined in §2 still means that in §5)?
- **Lens 7 (Citations):** Invoke `/validate-bib` to confirm every in-text citation key resolves to a bib entry and no entries are orphaned. Then, for the top-10 cited works, check the in-text claim matches the cited paper's actual finding direction (a mis-attribution is a CRITICAL). Are the closest competing / contemporaneous papers cited? For deeper citation-holds-the-claim verification, recommend `/verify-claims`.

### Phase 2: Synthesize (reduce → judge, with the hallucination gate)

Wait for all 7 lens reports. **Reduce, don't re-review:** stack the seven `scorecard`s and apply the gate predicate from [`orchestration-schemas.md` §3](../../references/orchestration-schemas.md) — the Executive verdict is a function of the typed findings, not a fresh eighth opinion. Then **run the post-judge hallucination gate** ([§4](../../references/orchestration-schemas.md)): any CRITICAL the synthesis introduces that **no lens raised** must be re-verified in a fresh `claim-verifier` fork, or dropped to `[JUDGE-HALLUCINATED]` and the verdict recomputed. A synthesis may freely downgrade or de-duplicate lens findings; it may not invent a new blocker. (This is the same hallucination-gate discipline the `editor` agent enforces in `/review-paper --peer`.)

Then produce:

`quality_reports/seven_pass_[stem]/_SYNTHESIS.md`

```markdown
# Seven-Pass Review: [Manuscript]

**Date:** YYYY-MM-DD
**Path:** [manuscript]
**Rounds run:** [N] (dry after [M] consecutive clean rounds)

## Executive verdict

**Overall state:** [SUBMIT / REVISE-MINOR / REVISE-MAJOR / REJECT-AND-RESTART]

## Cross-lens CRITICAL issues
| # | Lens(es) | Issue | Recommendation |
|---|---|---|---|

## MAJOR issues (second-round)
| # | Lens(es) | Issue |
|---|---|---|

## MINOR polish
[bulleted]

## Per-lens scorecard
| Lens | Critical | Major | Minor | Score/10 |
|---|---|---|---|---|
| 1. Abstract | | | | |
| 2. Intro | | | | |
| 3. Methods | | | | |
| 4. Results | | | | |
| 5. Robustness | | | | |
| 6. Prose | | | | |
| 7. Citations | | | | |
| **Overall** | | | | |

## Revision plan (in recommended order)
1. [Highest-leverage fix — usually a lens with 2+ CRITICALs]
2. …
7. [Lowest-leverage polish]

## Contradictions between lenses
[If two lenses disagree, surface here. E.g., Lens 2 says "expand contribution" but Lens 6 says "trim intro".]
```

### Phase 3: Loop-until-dry (two consecutive dry rounds)

After synthesizing round N, decide whether to loop. This is the **loop-until-dry** primitive ([`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md)), with a two-dry-round stopping rule so a single quiet pass doesn't prematurely declare victory:

- A round is **dry** when it surfaces **0 new** CRITICAL or MAJOR findings (deduped on lens+issue against all prior rounds). MINOR-only deltas still count as dry.
- **Converge** after **two consecutive dry rounds**. Re-running the seven lenses on an unchanged manuscript should reproduce the same findings; the second dry round confirms the first wasn't a sampling fluke.
- If a round surfaces a new CRITICAL/MAJOR, it is not dry → record it, then re-spawn the affected lenses (or all seven) for another round.
- **Fallback cap: 5 rounds** bounds a non-converging review. A finding that keeps reappearing across rounds is escalated to the user as an open item rather than re-litigated ([`summary-parity.md`](../../rules/summary-parity.md)).
- Record `Rounds run` and the dry-round count in `_SYNTHESIS.md`.

> Note: this skill **does not auto-apply fixes** — it reviews and re-reviews. If you want the loop to *fix* between rounds, run `/review-paper --adversarial` (critic-fixer), then come back here for the final clean-room pass.

### Phase 4: Token-budget report

After convergence, print:

```
Seven-pass review complete.
Subagents: 7 (parallel) per round x [N] rounds + 1 synthesizer per round.
Approx token usage: ~80-120k per round (vs ~15k for single-pass /review-paper).
Runtime: ~3-5 min wall-clock per round.
For cheaper alternatives:
  - Single-pass: /review-paper
  - Iterative fix loop: /review-paper --adversarial
  - Journal simulation: /review-paper --peer <journal>
```

## When to use this skill

- **Before first submission** to a top finance/accounting journal.
- **After a major revision** when you want to catch drift.
- **R&R when referees disagree** — surfaces contradictions your revision must navigate.

## When NOT to use

- Early drafts (use `/review-paper` single-pass first).
- Short notes, comments, or replies (overkill).
- When you've already run this recently and nothing substantive changed (check the git diff against the `Date` in `_SYNTHESIS.md`).

## Cross-references

- `.claude/skills/review-paper/SKILL.md` — the single-pass, `--adversarial`, and `--peer` modes (cheaper/faster, or journal-simulation).
- `.claude/skills/validate-bib/SKILL.md` — invoked by Lens 7 (structural citation check).
- `.claude/skills/verify-claims/SKILL.md` — deeper citation-holds-the-claim and numeric-claim verification.
- `.claude/skills/visual-audit/SKILL.md` — the deep figure/exhibit audit Lens 4 defers to.
- `.claude/skills/audit-reproducibility/SKILL.md` — complementary; the numeric-claims side of the audit.

## Exit behavior

- Exits 0 always (review is informational). The synthesis report's "Executive verdict" is the gate.
- Any `CRITICAL` at the top of the synthesis should block submission until resolved.

## What this skill does NOT do

- Re-run seven lenses on a manuscript that hasn't changed beyond the loop — the two-dry-round rule stops it; a fresh invocation should check the git diff against the last run date.
- Auto-apply fixes — that's `/review-paper --adversarial`'s job.
- Replace human judgment. A reviewer who knows your subfield still beats seven LLMs.
