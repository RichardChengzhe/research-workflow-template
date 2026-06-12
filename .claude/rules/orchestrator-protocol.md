# Orchestrator Protocol: the review runtime (Contractor Mode)

**After a plan is approved and a fix/review skill is invoked, the orchestrator takes over the review-fix loop as a real runtime contract** — expressed with the primitive every Claude Code session has: the `Task` subagent. The skill fans out to forked reviewers, reduces their *structured* findings through a deterministic gate, judges with a hallucination guard, and loops until dry. What is *not* automatic is the **trigger**: nothing launches this loop on its own — the user (or a skill invocation) starts it. That boundary is deliberate (see "What is NOT automatic").

## The loop (the contract)

```
Plan approved → fix/review skill invoked (with a RUN_CONFIG)
  │
  Step 1: IMPLEMENT / DRAFT — execute plan steps
  │
  Step 2: VERIFY — run scripts, read logs, check outputs        (retry ≤ 2)
  │        If verification fails → fix → re-verify
  │
  Step 3: FAN-OUT REVIEW — parallel forked critics by file type, each returns FINDINGs
  │
  Step 4: REDUCE + JUDGE — stack scorecards; gate predicate → verdict;
  │        run the post-judge hallucination gate on judge-introduced CRITICALs
  │
  Step 5: FIX — fixer agents apply critical → major → minor (MECHANICAL only)
  │
  Step 6: SCORE — quality_score.py / quality-gates.md roll-up
  │
  └── converged?  (a round adds 0 new CRITICAL/MAJOR — see loop-until-dry)
        YES → present summary to user
        NO  → back to Step 3, in FRESH context
              (hard fallback cap reached → present with remaining issues)
```

## The runtime primitives

These four primitives are the runtime. The file-type critic→fixer machinery below is a *composition* of them: each critic is a fan-out lens, the verdict is the reduce step, and the round counter is replaced by loop-until-dry.

### 1. Fan-out

Spawn the critics **in parallel in a single message** — N `Task` calls, each `context: fork` so the main thread stays clean and each reviewer gets full budget for its lens. `Task` subagents are the **portable primitive**: they exist in every Claude Code install, so the protocol depends on them, not on any session-gated workflow tool. Which agent fills which lens, and at which model tier, is in [`agent-fleet.md`](../references/agent-fleet.md) when present; the file-type routing table below is the default mapping for this template.

### 2. Reduce (typed, not eyeballed)

Each critic returns `FINDING`s and a `SCORECARD` in the shared schema ([`orchestration-schemas.md`](../references/orchestration-schemas.md) when present). The synthesizer **stacks typed objects** and applies the **gate predicate** — `CRITICAL>0 → BLOCK`, `MAJOR>0 → REVISE`, else `PASS`. The verdict is a deterministic function of the findings, not a re-judgment of the artifact.

### 3. Judge + hallucination gate

A synthesizer/editor may freely *downgrade* or *de-duplicate* lens findings, but any **CRITICAL it introduces that no lens raised** must survive the post-judge hallucination gate: re-verify it in a fresh `verifier`/`claim-verifier` fork (see [`post-flight-verification.md`](post-flight-verification.md)); if it can't be grounded, drop it to `[JUDGE-HALLUCINATED]` and recompute. This is what makes an autonomous review trustworthy next to a credibility-sensitive artifact (a manuscript, a results table, a co-author's draft).

### 4. Loop-until-dry

Replace bespoke "max 5 rounds" stopping logic with **convergence**: stop after **2 consecutive dry rounds** (a round that adds 0 new CRITICAL/MAJOR findings, deduped on `location`+`finding`). Guards:

- **Fallback cap** — `RUN_CONFIG.max_rounds` (default 5) bounds a non-converging loop. The old hard "max 5" is now a fallback, not the primary stop.
- **Two-strikes** — the *same* finding surviving rounds N and N+2 is escalated to the user, not patched a third time (see [`summary-parity.md`](summary-parity.md) when present).
- **Spend cap** — `RUN_CONFIG.spend_cap_tokens` warns-and-asks; it is a spend ceiling, not a context limit (each re-audit is fresh).
- **Runaway backstop** — never exceed the harness's hard subagent cap; cost-pilot any large fan-out before a full sweep.

### RUN_CONFIG: collect interactivity *before* launch

A forked subagent cannot stop to ask the user a question. So every interactive choice a fan-out needs is gathered **before** the critics spawn, echoed back as a **Pre-Flight Report**, and only then launched. An unresolved required field halts *before* launch, never mid-run.

## Adversarial Sub-Loop: file-type critic→fixer routing

When the orchestrator reaches Steps 3–5, it instantiates the runtime with adversarial critic-fixer pairs **by file type** rather than manual fix cycles. This is the template's concrete fan-out fleet.

### File-Type Routing

| Modified file type | Critic agent (fan-out lens) | Fixer agent |
|--------------------|-----------------------------|-------------|
| `.do`, `.py`, `.sas` | `code-reviewer` | `code-fixer` |
| `.tex` (manuscript) | `proofreader` | `manuscript-fixer` |
| `output/tables/*.tex`, `output/figures/*.pdf` | `output-critic` | `output-fixer` |
| Any (substance) | `domain-reviewer` | *NONE — human review* |

When several file types change in one task, fan the matching critics out **in parallel in a single message** (primitive 1), then reduce their findings together (primitive 2).

### Sub-Loop Protocol (expressed as loop-until-dry)

```
ROUND = 1
dry_streak = 0
while dry_streak < 2 and ROUND <= RUN_CONFIG.max_rounds (default 5):
  1. FAN-OUT the file-type CRITIC(s) on changed files → FINDINGs + verdict
  2. REDUCE + JUDGE: gate predicate → APPROVED / NEEDS_REVISION
     (run the hallucination gate on any judge-introduced CRITICAL)
  3. If APPROVED: break
  4. Run FIXER(s) with the critic report
     - Classify each issue: MECHANICAL (auto-fix) or SUBSTANTIVE (human)
     - Apply MECHANICAL fixes only
     - Log all changes to quality_reports/
  5. If this round added 0 new CRITICAL/MAJOR (deduped on location+finding):
         dry_streak += 1   else   dry_streak = 0
  6. ROUND += 1; re-audit in FRESH context
After exit: collect remaining + all SUBSTANTIVE issues for user
```

### Verdict Thresholds

- **Code:** APPROVED when quality score >= 80 ([`quality-gates.md`](quality-gates.md) rubric).
- **Manuscript:** APPROVED when zero High-severity proofreading issues.
- **Output:** APPROVED when zero Critical/Major AEA style violations.
- **Domain:** Always goes to human (domain-reviewer is REPORT-ONLY, no fixer). A *defensible, concretely-named* alternative the domain critic raises is surfaced as `EXPLAINED`, not auto-FAIL (see [`quality-gates.md`](quality-gates.md)); fabricated or unmatched claims stay fail-closed.

### Fixer Constraints

All fixers are CONSERVATIVE:
1. Fix ONLY what the critic found — no independent "improvements".
2. If uncertain whether a fix is mechanical → classify as SUBSTANTIVE (defer to human).
3. NEVER change empirical results, specifications, or research claims.
4. Log every change with before/after text.

### Human Review Collection

After all sub-loops complete, present to the user:
1. Fixes applied (count by category).
2. Substantive issues requiring human judgment (priority order).
3. Issues that persisted to the two-strikes escalation or the fallback cap.
4. Final scores per file.

## Where the runtime is implemented

| Skill | Primitives | Notes |
|-------|-----------|-------|
| `/commit` | verify (Step 2), score (Step 6) | Halts on failure; `.githooks/pre-commit` enforces the same gates on every commit |
| `/fix-code` | fan-out (`code-reviewer`) → fix (`code-fixer`), loop-until-dry | `.do` / `.py` / `.sas` |
| `/fix-manuscript` | fan-out (`proofreader`) → fix (`manuscript-fixer`), loop-until-dry | `.tex` |
| `/fix-output` | fan-out (`output-critic`) → fix (`output-fixer`), loop-until-dry | tables / figures |
| `/review-paper` | RUN_CONFIG → fan-out reviewers → reduce → judge **+ hallucination gate** | Manuscript review |
| `/deep-audit` | mechanical checks → fan-out → fix, loop-until-dry | Repo-wide consistency |

## What is NOT automatic

- **No post-plan-approval daemon.** Approving a plan and starting the contractor loop is a *user/skill-initiated* action; exiting plan mode does not silently launch a multi-agent fix loop, and there is no background service pointing the runtime at an artifact unattended. A fix loop with no human in it, run against a submission, shared data, or a co-author's draft, is exactly the failure mode we refuse. **This is a documented non-goal, not a missing feature.** (The template's contractor mode is autonomous *within* an invoked task; it is not a cron daemon.)
- **No repo-wide orchestrator chaining.** Skills compose the primitives within their own scope; they do not invoke each other without an explicit call.
- **Quality gate enforcement is checkpoint-based.** `quality_score.py` runs inside `/commit`, **and** — once `./scripts/install-hooks.sh` is run — the `.githooks/pre-commit` hook runs the surface-sync + quality gates on every commit, so a direct `git commit` no longer bypasses the review (bypass is explicit: `SKIP_QUALITY_GATE=1` / `--no-verify`).

## "Just Do It" mode

When the user says "just do it" / "handle it" (within an already-invoked task or skill):

- Skip the final approval pause for the current task; still run the full verify → fan-out → reduce → judge → loop-until-dry; still present the summary.
- Auto-commit only if score >= 80 **and** the request unambiguously authorized a commit. **Do NOT treat "just do it" alone as commit authorization** — commits require an explicit `/commit` or unambiguous request.

## Limits

- **Convergence stop:** 2 consecutive dry rounds (primary).
- **Fallback cap:** `RUN_CONFIG.max_rounds` (default 5) per critic-fixer pair.
- **Verification retries:** max 2 attempts.
- **Spend cap:** `RUN_CONFIG.spend_cap_tokens` warns-and-asks.
- Never loop indefinitely; never exceed the harness's hard subagent cap.

## Cross-references

- [`.claude/references/orchestration-schemas.md`](../references/orchestration-schemas.md) — FINDING / SCORECARD / RUN_CONFIG / hallucination-gate contracts (when present).
- [`.claude/references/agent-fleet.md`](../references/agent-fleet.md) — the reviewer fleet + model tiers (when present).
- [`.claude/rules/plan-first-workflow.md`](plan-first-workflow.md) — when to enter plan mode before invoking a skill.
- [`.claude/rules/quality-gates.md`](quality-gates.md) — threshold definitions, the `EXPLAINED` disposition, and the pre-commit hook.
- [`.claude/rules/post-flight-verification.md`](post-flight-verification.md) — the forked-verifier mechanism the hallucination gate reuses.
