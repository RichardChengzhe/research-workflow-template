---
name: review-paper
description: Comprehensive manuscript review for empirical finance/accounting papers. Three modes - single-pass (default, the original 6-dimension referee report), --adversarial (critic-fixer loop-until-dry), and --peer [journal] (simulated editorial pipeline - editor + 2 dispositioned referees + decision, calibrated to a target journal). R&R continuation via --peer --r2/--r3; hostile-editor stress test via --peer --stress; reviewer-disposition variance via --peer --variance N.
disable-model-invocation: true
argument-hint: "[paper path / filename in master_supporting_docs/] [--adversarial | --peer <journal> [--r2 | --r3 | --stress | --variance N] [--no-novelty-check]] [--no-cross-artifact]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Edit", "Bash", "Task"]
---

# Manuscript Review

Produce a thorough, constructive review of an academic manuscript -- the kind of report a top-journal referee would write.

> **Which review skill do I want?**
>
> - **`/review-paper`** (this skill) -- single comprehensive report (default), optional `--adversarial` critic-fixer loop, or `--peer <journal>` simulated peer-review pipeline. Best for **most drafts**.
> - **`/seven-pass-review`** -- seven independent lenses in parallel (abstract, intro, methods, results, robustness, prose, citations) then synthesized. Heavier (~7x token cost). Best for **submission-ready drafts** or **R&R stage**.
> - **`/respond-to-referees`** -- if you already have referee comments and need a response document, not another review.

**Input:** `$ARGUMENTS` -- path to a paper (`.tex`, `.pdf`), or a filename in `master_supporting_docs/`. Optional flags:

- `--adversarial` -- critic-fixer loop-until-dry (fallback cap 5 rounds).
- `--peer <JOURNAL>` -- simulated peer-review pipeline calibrated to `<JOURNAL>` (short names in `.claude/references/journal-profiles.md`).
- `--r2` / `--r3` -- R&R continuation mode (requires `--peer`). Reloads prior round, classifies concerns Resolved / Partial / Not addressed. Hard cap at `--r3`.
- `--stress` -- hostile-editor stress test (requires `--peer`). Forces SKEPTIC dispositions, doubles critical peeves.
- `--variance N` -- reviewer-disposition variance mode (requires `--peer`; N in {3,4,5}, default 3). Runs N referees with independently sampled dispositions; the editor aggregates into a **decision distribution**, not a point estimate. Mutually exclusive with `--stress` and `--r2`/`--r3`.
- `--no-novelty-check` -- skip the editor's WebSearch novelty probe (default ON).
- `--no-cross-artifact` -- skip auto-invocation of `/audit-reproducibility` on referenced scripts.

---

## Modes

### Default mode (single-pass)

One comprehensive review report across the 6 dimensions below. Fast, low token cost, suitable for early drafts where the author wants feedback and will iterate manually. **This is the original behavior of the skill and is unchanged.**

### Adversarial mode (`--adversarial`)

Iterative critic-fixer loop: the critic produces the same 6-dimension review, the fixer proposes and applies edits (with user approval), and a fresh-context critic re-audits. Loops until APPROVED or the fallback cap. Use when preparing a pre-submission draft or after your own major rewrite. Costs more tokens but produces a manuscript the critic has signed off on.

### Peer-review mode (`--peer <JOURNAL>`)

Simulated editorial pipeline: **editor desk review -> referee selection -> 2 blind referees with different dispositions -> editorial synthesis**, calibrated to a target journal. Use as a pre-submission dress rehearsal, to choose between target journals, or to plan an R&R. Materially different from `--adversarial`: that runs the *same* critic with fresh context; `--peer` runs **different personas** (editor + 2 referees drawn from the 6-way disposition taxonomy STRUCTURAL / CREDIBILITY / MEASUREMENT / POLICY / THEORY / SKEPTIC) whose priors are deliberately different and who are blind to each other.

**Agents used:**

- `.claude/agents/editor.md` -- editor (desk review, referee selection, synthesis, hallucination gate).
- `.claude/agents/domain-referee.md` -- substance referee.
- `.claude/agents/methods-referee.md` -- methodology referee (paper-type-aware).

---

## Steps (all modes)

1. **Locate and read the manuscript.** First strip flags from `$ARGUMENTS` to get the bare manuscript path. Check, in order:
   - Direct path (the bare path).
   - `master_supporting_docs/supporting_papers/$ARGUMENTS`.
   - Glob for partial matches.
   The project's authoritative source is normally `manuscript/main.tex`; resolve `\input{}` / `\include{}` so the reviewer sees the whole paper.
2. **Read the full paper** end-to-end with the Read tool. For long PDFs, page through with the `pages` parameter (up to 20 pages per request).
3. **Evaluate across the 6 dimensions** (below).
4. **Generate 3-5 "referee objections"** -- the tough questions a top referee would ask.
5. **Produce the review report.**
6. **Save to** `quality_reports/paper_review_[sanitized_name]_round[N].md` (N=1 in default mode; N increments in adversarial mode).
6b. **Cross-artifact integration.** Unless `$ARGUMENTS` contains `--no-cross-artifact`, and if the manuscript's reported numbers come from analysis scripts (the `code/` pipeline that writes `output/tables/` and `output/logs/`), auto-invoke `/audit-reproducibility` on the manuscript + `output/` so that any reproducibility FAIL (a reported number that does not trace to its estimation artifact) surfaces in the review. Merge critical cross-artifact findings into a "Cross-Artifact Findings" section at the top of the report. See [`.claude/rules/cross-artifact-review.md`](../../rules/cross-artifact-review.md).
7. **If `--adversarial` is in `$ARGUMENTS`:** invoke the critic-fixer loop (below). **If `--peer` is in `$ARGUMENTS`:** invoke the peer-review pipeline (below). Otherwise stop here.

---

## Review Dimensions

### 1. Argument Structure
- Is the research question clearly stated?
- Does the introduction motivate the question effectively?
- Is the logical flow sound (question -> method -> results -> conclusion)?
- Are the conclusions supported by the evidence?
- Are limitations acknowledged?

### 2. Identification Strategy
- Is the causal claim credible?
- What are the key identifying assumptions? Are they stated explicitly (ideally in one testable sentence)?
- Are there threats to identification (omitted variables, reverse causality, measurement error, look-ahead bias)?
- Are robustness checks adequate?
- Is the estimator appropriate for the research design?

### 3. Econometric Specification
- Correct standard errors (clustered at the right level -- firm and/or time? robust? bootstrap?)?
- Appropriate functional form?
- Sample selection / survivorship / delisting issues?
- Multiple-testing concerns when many specifications or sorts are run?
- Are point estimates economically meaningful (bps of return, pp of an outcome, $ of value -- not just statistically significant)?

### 4. Literature Positioning
- Are the key papers cited (including the closest competing / contemporaneous work)?
- Is prior work characterized accurately?
- Is the contribution clearly differentiated from existing work?
- Any missing citations a referee would flag?

### 5. Writing Quality
- Clarity and concision; academic tone.
- Consistent notation throughout (a symbol defined in §2 still means that in §5).
- Abstract effectively summarizes the paper.
- Tables and figures are self-contained (clear labels, notes, sources, what's in parentheses).

### 6. Presentation
- Are tables and figures well-designed and legible at print size?
- Is notation consistent throughout?
- Any typos, grammatical errors, or formatting issues?
- Is the paper the right length for the contribution?

---

## Output Format

```markdown
# Manuscript Review: [Paper Title]

**Date:** [YYYY-MM-DD]
**Reviewer:** review-paper skill
**File:** [path to manuscript]

## Summary Assessment

**Overall recommendation:** [Strong Accept / Accept / Revise & Resubmit / Reject]

[2-3 paragraph summary: main contribution, strengths, and key concerns]

## Strengths

1. [Strength 1]
2. [Strength 2]
3. [Strength 3]

## Major Concerns

### MC1: [Title]
- **Dimension:** [Identification / Econometrics / Argument / Literature / Writing / Presentation]
- **Issue:** [Specific description]
- **Suggestion:** [How to address it]
- **Location:** [Section/page/table if applicable]

[Repeat for each major concern]

## Minor Concerns

### mc1: [Title]
- **Issue:** [Description]
- **Suggestion:** [Fix]

[Repeat]

## Referee Objections

These are the tough questions a top referee would likely raise:

### RO1: [Question]
**Why it matters:** [Why this could be fatal]
**How to address it:** [Suggested response or additional analysis]

[Repeat for 3-5 objections]

## Specific Comments

[Line-by-line or section-by-section comments, if any]

## Summary Statistics

| Dimension | Rating (1-5) |
|-----------|-------------|
| Argument Structure | [N] |
| Identification | [N] |
| Econometrics | [N] |
| Literature | [N] |
| Writing | [N] |
| Presentation | [N] |
| **Overall** | **[N]** |
```

---

## Principles

- **Be constructive.** Every criticism should come with a suggestion.
- **Be specific.** Reference exact sections, equations, tables.
- **Think like a referee at a top-5 journal.** What would make them reject?
- **Distinguish fatal flaws from minor issues.** Not everything is equally important.
- **Acknowledge what's done well.** Good research deserves recognition.
- **Do NOT fabricate details.** If you can't read a section clearly, say so.

---

## Adversarial Mode -- Critic-Fixer Loop

**Only runs if `--adversarial` is in `$ARGUMENTS`.** Added because the single-pass review otherwise leaves authors doing manual fix-and-resubmit cycles.

### Flow

```
Phase 0: Pre-flight
  ├─ Verify the manuscript compiles (latexmk -pdf manuscript/main.tex) if it is a compile target
  ├─ Snapshot the pre-review version: git stash OR copy to .review-backup/
  │
Phase 1: Critic audit (round N=1,2,3,...)
  ├─ Run the default 6-dimension review, producing a round-N report
  ├─ If the report has ZERO Major Concerns and ZERO Referee Objections rated "fatal":
  │     → VERDICT = APPROVED. Stop the loop. Write final summary.
  │  Else: continue.
  │
Phase 2: Fixer
  ├─ For each Major Concern, produce a concrete proposed edit (diff or new text block).
  ├─ Present proposed edits to the user grouped by severity (Critical → Major → Minor).
  │  Ask: "apply all", "apply critical+major only", "review each", or "abort".
  ├─ Apply approved edits with the Edit tool.
  ├─ If the manuscript is a compile target, re-compile and verify it still builds.
  │  CONSERVATIVE FIXER RULE: never change an empirical result, a specification, or a
  │  research claim. Those are SUBSTANTIVE — surface to the user, do not auto-edit.
  │
Phase 3: Re-audit
  └─ Spawn a FRESH-CONTEXT subagent (Task, subagent_type=general-purpose) to re-read the
     paper and produce a round-(N+1) report. Fresh context prevents anchoring bias —
     the new reviewer sees the edited paper, not the diff. → Jump back to Phase 1.
```

### Iteration limits -- loop-until-dry

Same **loop-until-dry** primitive as the rest of the kit ([`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md)): the critic returns `FINDING`s in the shared schema ([`orchestration-schemas.md`](../../references/orchestration-schemas.md)) and the loop **converges when a round adds 0 new CRITICAL/MAJOR concerns** (deduped on `location`+`finding`), not at a fixed count.

- **Convergence:** APPROVED when a round produces zero Major Concerns and zero fatal Referee Objections.
- **Fallback cap:** 5 rounds bounds a non-converging loop; after round 5, halt and list remaining concerns.
- **Two-strikes:** if the same Concern label appears in rounds N and N+2, flag as "author disagreement" and let the user decide ([`summary-parity.md`](../../rules/summary-parity.md)).
- **Budget escape:** if cumulative token cost exceeds the spend cap (default ~500k -- a spend ceiling, since each re-audit runs in fresh context), warn and let the user cap further rounds.

### Stopping criteria

| Condition | Action |
|---|---|
| Zero Major Concerns, zero fatal Referee Objections | APPROVED -- final summary |
| Max 5 rounds reached | HALTED -- list remaining concerns, user decides |
| User approves zero fixes in a round | HALTED -- user signals "I disagree with this review" |
| Compile fails after applied fixes | ROLLED BACK to pre-round-N snapshot, report compile error, user decides |

### Final report

After the loop ends, write `quality_reports/paper_review_[sanitized_name]_FINAL.md`:

```markdown
# Final Review: [Paper Title]

**Rounds:** N
**Verdict:** APPROVED | HALTED (max rounds) | HALTED (user override) | ROLLED BACK
**Token cost estimate:** ~XXk

## Round Summary
| Round | Major Concerns | Fatal Objections | Status |
|---|---|---|---|
| 1 | 7 | 2 | Fixed 5, deferred 2 |
| ... | ... | ... | ... |
| N | 0 | 0 | APPROVED |

## Changes Applied
[link to git diff between the pre-round-1 snapshot and HEAD]

## Remaining Concerns (if HALTED)
[list with severity + rationale]

## Next Steps
[recommended action: submit / one more pass / substantial revision]
```

### When NOT to use adversarial mode

- Early exploratory drafts (the loop forces premature polish on ideas still being shaped).
- Papers you don't yet have compilable source for (can't verify edits).
- When you'd rather get ONE opinion and decide for yourself.

---

## `--peer [journal]` workflow detail

### Phase 0: Cross-artifact pre-flight (runs BEFORE desk review in --peer mode)

Unless `--no-cross-artifact` is set, auto-invoke `/audit-reproducibility` on the manuscript + `output/` *first*. Any reproducibility FAIL becomes desk-reject-worthy evidence the editor can cite. See [`.claude/rules/cross-artifact-review.md`](../../rules/cross-artifact-review.md). Report: `quality_reports/cross_artifact_[paper]/reproducibility.md`.

**Novelty-probe Post-Flight.** The editor's novelty probe uses `WebSearch`, whose results can be hallucinated (fabricated prior work, misattributed findings, wrong years). Before the editor incorporates novelty-probe claims into its decision, those claims must pass Post-Flight Verification per [`.claude/rules/post-flight-verification.md`](../../rules/post-flight-verification.md):

1. The editor collects novelty-probe claims (e.g., "Smith 2022 already showed this exact result").
2. Spawn `claim-verifier` via `Task` with `subagent_type=claim-verifier` and `context=fork`, passing the claims + verification questions + candidate source URLs. Forked fresh context is the CoVe independence trick.
3. Only verified claims enter the desk-review narrative. Unverified claims are surfaced separately as "editor could not verify -- manual check recommended," never presented as established prior work.

Opt-out: `--no-novelty-check` skips the probe entirely. If the probe runs, Post-Flight is mandatory.

**Pre-Flight Report (required before Phase 1).** This is the `RUN_CONFIG` echo from [`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md) -- every interactive choice (journal, dispositions, peeve budget, N referees, cross-artifact/novelty toggles, round) is resolved **before** the forked editor/referees spawn, because a forked subagent cannot stop to ask. Halt here on any unresolved required field:

```markdown
## Pre-Flight Report -- /review-paper --peer

**Manuscript:** [path] -- [page count, last modified]
**Target journal:** [JOURNAL_SHORT] → [full name from `.claude/references/journal-profiles.md`]
**Journal profile loaded:** [yes/no; key adjustments, e.g. "Identification 35 → 40"]
**Cross-artifact:** [reproducibility PASS / FAIL — N of M reported numbers within tolerance]
**Mode:** [fresh / r2 / r3 / stress / variance N]
```

If the manuscript path doesn't exist, the target journal isn't in `journal-profiles.md`, or a referenced artifact is missing, stop and surface the issue before proceeding.

### Phase 1: Editor desk review

Spawn forked subagent `editor` with the manuscript path and `--peer <JOURNAL>` context. The editor reads the journal profile, reads abstract + intro + methods overview + headline results, runs novelty probes (unless opted out), and either **DESK REJECTs** (pipeline terminates with a rejection letter) or **SENDs OUT**. Report: `quality_reports/peer_review_[paper]/desk_review.md`.

### Phase 1b: Referee selection (inside editor)

Editor draws 2 DIFFERENT dispositions from the journal's referee-pool weights and assigns each referee 1 critical + 1 constructive peeve (stress mode: 2 critical + 1 constructive; variance mode: see below). Appended to `desk_review.md`.

### Phase 2: Two parallel referees, blind to each other

Spawn in parallel:
- Forked `domain-referee` with disposition D1, peeves P1 → `referee_domain.md`.
- Forked `methods-referee` with disposition D2, peeves P2 → `referee_methods.md`.

Each referee must include "What would change my mind: [specific ask]" on every MAJOR concern.

### Phase 3: Editor synthesis (reduce -> judge, with the hallucination gate)

Read both referee reports. **Reduce** their findings, classify each MAJOR concern as FATAL / ADDRESSABLE / TASTE, and produce the editorial decision via the decision-rule table in `editor.md`.

**Post-judge hallucination gate** ([`orchestration-schemas.md` §4](../../references/orchestration-schemas.md)): the editor reduces the referees -- it must not desk-reject or escalate on a CRITICAL reason **neither referee raised**. Any editor-introduced blocker not traceable to a referee finding is re-verified in a fresh `claim-verifier` fork or dropped to `[JUDGE-HALLUCINATED]` and the decision recomputed. (The editor may always downgrade or de-duplicate.) Report: `quality_reports/peer_review_[paper]/editorial_decision.md`.

### Phase 4: Summary

Tell the user: final decision (Accept / Minor / Major / Reject / Desk Reject); token usage + wall-clock; paths to all reports.

---

### Variance mode (`--peer --variance N`)

**Why this mode exists.** Default `--peer` runs an editor + 2 referees with dispositions sampled once -- a *point estimate* of how the paper would fare. The AgentReview ACL 2024 study ([arXiv:2406.12708](https://arxiv.org/abs/2406.12708)) found that ~37% of paper decisions vary purely from reviewer-disposition sampling. A point estimate hides this. Variance mode runs N independent referees with disposition sampling and reports a **decision distribution**.

**How it works:**

1. The editor performs the desk review once (shared across the N referees).
2. The editor samples N dispositions from the 6-way taxonomy **with replacement** (repeats allowed -- two STRUCTURAL referees who disagree is itself a signal). **Stratification rule (N >= 3):** if no SKEPTIC was drawn, replace one randomly chosen referee with a SKEPTIC (avoids a misleadingly friendly draw that understates publication risk).
3. Each of the N referees runs in an isolated forked context (`Task`, `context: fork`) -- same manuscript, same paper-type rubric, different disposition. Referees are blind to each other. Use `domain-referee` / `methods-referee` as the referee personas across the N draws.
4. The editor receives N reports and produces (instead of a single `editorial_decision.md`):
   - **`decision_distribution.md`** -- a decision-distribution table (e.g., `2/3 Major Rev, 1/3 Reject`, modal verdict highlighted) and a **concern-frequency table** (a concern in K-of-N reports; high K = robust criticism, low K = disposition-dependent pet issue).
   - **`editor_synthesis.md`** -- a short editorial letter that explicitly references the variance and does **not** collapse the distribution to a single point verdict ("modal verdict Major Rev, with one SKEPTIC dissent on identification -- address the identification concern even though it's not the majority position").

**Per-referee reports:** `quality_reports/peer_review_<paper>/referee_1.md` … `referee_N.md`.

**Cost discipline.** Variance multiplies referee-tier cost by N. Keep referees mid-tier (Sonnet) for variance runs and reserve Opus for the editor synthesis; hard cap N=5 (for more, run `--variance 5` twice and combine offline).

**Mutual exclusivity.** `--variance` cannot combine with `--stress` (which forces SKEPTIC x 2, defeating sampling) or `--r2`/`--r3` (which reuses prior-round dispositions). The skill halts with an error if mutually-exclusive flags are combined.

**When to reach for it:** a pre-submission dress rehearsal where you want to know not just "will this survive review" but "*how confidently*"; deciding between target journals (run `--variance 3` against two journal profiles, compare distributions); or stress-testing after a rejection where the referee panel felt unrepresentative.

### Stress mode (`--peer --stress`)

Forces BOTH referees to SKEPTIC disposition, doubles critical peeves, and shifts the editor persona to "looking for reasons to reject -- hostile but fair." Output is a concern-list gauntlet the author must prepare to defend, not a decision letter.

### R&R continuation (`--peer --r2` / `--r3`)

Skips the fresh desk review; reloads the prior round's reports; reuses the SAME referees + dispositions + peeves; each prior concern is classified Resolved / Partial / Not addressed. Decision options narrow each round (`--r3` has no fourth round). Output filenames carry an `_r2` / `_r3` suffix.

---

## Output layout for `--peer` mode

```
quality_reports/
  peer_review_[sanitized_paper_name]/
    desk_review.md                       # Phase 1 + Phase 1b
    referee_domain.md                    # Phase 2 (parallel)        [default/stress/r2/r3]
    referee_methods.md                   # Phase 2 (parallel)        [default/stress/r2/r3]
    referee_1.md ... referee_N.md        # Phase 2                   [variance only]
    editorial_decision.md                # Phase 3                   [default/stress/r2/r3]
    decision_distribution.md             # Phase 3                   [variance only]
    editor_synthesis.md                  # Phase 3                   [variance only]
    (R&R rounds: desk_review_r2.md, referee_domain_r2.md, ...)
  cross_artifact_[sanitized_paper_name]/
    reproducibility.md                   # Phase 0
```

---

## Field calibration

The peer pipeline is field-agnostic; only the calibration data changes. `journal-profiles.md` should carry the target finance/accounting venues (*JF*, *RFS*, *JFE*, *JAR*, *TAR*, *JAE*); copy `templates/journal-profile-template.md` into a new section to add one. `methods-referee.md` already branches by paper type (reduced-form / structural / theory+empirics / descriptive / asset-pricing-test) -- extend the list there if a new design appears.

## Cross-references

- [`.claude/agents/{editor,domain-referee,methods-referee}.md`](../../agents/) -- the `--peer` pipeline personas.
- [`.claude/agents/claim-verifier.md`](../../agents/claim-verifier.md) -- forked CoVe verifier for the novelty-probe gate.
- [`.claude/skills/audit-reproducibility/SKILL.md`](../audit-reproducibility/SKILL.md) -- numeric-claim verification (auto-invoked unless `--no-cross-artifact`).
- [`.claude/skills/seven-pass-review/SKILL.md`](../seven-pass-review/SKILL.md) -- heavier 7-lens pass for submission-ready drafts.
- [`.claude/skills/respond-to-referees/SKILL.md`](../respond-to-referees/SKILL.md) -- if you already have referee comments.
- [`.claude/references/journal-profiles.md`](../../references/journal-profiles.md) -- journal calibration data.
