---
paths:
  - ".claude/agents/**/*.md"
  - ".claude/skills/**/SKILL.md"
---

# Per-Agent Model Routing (architect/editor split)

**Match model tier to the cognitive demand of the work, but never sacrifice the audit lens to save cost.** The Aider architect/editor split is the canonical community shape: a high-judgment model plans, a cheaper model executes mechanical edits, and -- critically -- a *separate* high-judgment model audits the result.

> **Currency note:** specific model names, IDs, prices, and effort defaults drift fast. This rule deliberately fixes none of them. Treat the tiers below as *roles* (high-judgment / review / mechanical), and **verify the current model IDs, prices, and effort levels against the live Claude Code / Anthropic docs** before pinning anything in frontmatter.

## The template's standing rule (non-negotiable)

**Default to the high-judgment tier (Opus) for implementer subagents.** Use a cheaper tier only for genuinely superficial, mechanical work (a single-file rename, a glob-and-copy, a verbatim-block paste, a trivial grep-and-report).

**ALWAYS audit implementer-subagent work with a SEPARATE high-judgment (Opus) auditor that reads the literal file bytes** -- not the implementer's summary. The auditor (a) reads the actual file state, (b) verifies the implementer's claims against the literal bytes, (c) cross-checks against the spec, and (d) runs user-level verification (does the headline t-stat replicate? does the script run clean?). A reported PASS is not a PASS until the auditor has re-run the check.

This standing rule overrides any cost argument. The cost of one false-positive PASS -- a hallucinated citation, a wrong N shipped to the manuscript, a silently broken merge -- is far higher than the cost of running the high-judgment tier on the audit.

## The three tiers (roles, not product names)

| Tier (role) | Use for |
|-------------|---------|
| **High-judgment** (Opus) | Research-design decisions, multi-file refactors with judgment calls, report/LaTeX/table builders, data-pipeline changes (merges, winsorization, FE specs), non-trivial `.do` writing, domain (finance/accounting) reasoning, AND every audit/verifier/referee/editor agent. |
| **Review / critique** (Sonnet) | Bounded review passes -- proofreading inspection, layout/style audit, a critic that hands a diff to a mechanical fixer. |
| **Mechanical** (Haiku) | File renames, search-and-replace, citation-format conversion, bib validation, applying a critic's verbatim "replace X with Y" fix, simple file lookups. |

Set per-agent via `model:` in the agent's YAML frontmatter; set per-skill via the same field in `SKILL.md`. Inheritance (`model: inherit`) is fine for a new agent you have not profiled yet, or one whose work genuinely spans tiers in a single invocation.

```yaml
---
name: output-fixer
model: sonnet      # was: inherit
---
```

## The effort axis (the first cost lever)

Model tier is the *second* cost lever; **effort is the first.** Most models expose an effort level (low / medium / high / ...), and lowering effort is usually cheaper than dropping a tier -- reach for it first.

- **Mechanical work** -> low / medium effort.
- **Review and judgment** -> high effort (typically the default).
- **The hardest gates** (deep refactors, the toughest `/review-paper --peer`) -> the highest effort the model offers.
- When cost-constrained, **drop effort first, then tier -- never the reverse**, and never below the audit lens.

Set per skill/agent with the `effort:` frontmatter field. Match effort to cognitive demand the same way you match tier. (Exact effort-level names and defaults change between model releases -- check live docs.)

## Why route at all

Routing mechanical work down a tier and dropping effort on bounded tasks cuts cost materially with no quality loss on that tier. Per-agent routing recovers cost on the cheap tiers *without* touching the high-judgment lens where it matters -- which is the whole point.

## Routing recipe by task type (template fleet)

### Mechanical (Haiku tier)
- File rename / search-and-replace operations.
- Citation / bib formatting (the mechanical fix path of `/validate-bib`).
- Applying a critic's verbatim diff -- e.g. `code-fixer`, `manuscript-fixer`, `output-fixer` when the fix is a literal "replace X with Y".
- Simple file lookups / grep-and-report.

### Review / critique (Sonnet tier)
- Proofread inspection (`proofreader`).
- Output / table-style audit against house style (`output-critic`).
- A critic that produces a diff for a mechanical fixer to apply.

### High-judgment (Opus tier) -- and never demote these
- **The auditor / verifier** (`verifier`, and any reproducibility/audit pass) when gating a non-trivial commit.
- **The claim verifier in fresh-context mode** (`claim-verifier`) -- protects against hallucinated citations.
- **Domain review** (`domain-reviewer`) and, where present, the **referee / editor** agents for `/review-paper --peer`.
- **Any implementer** doing a data-pipeline change, a multi-file refactor, or research-design work.

## Anti-pattern: pushing the high-judgment tier down to save cost

Do **not** demote `claim-verifier`, `domain-reviewer`, the referee/editor agents, or a non-trivial `verifier` to the review tier to save cost. These are the agents that protect the paper from hallucinated citations, weak identification, and desk-reject mistakes. A too-cheap judge is as bad as no judge.

## Anti-pattern: self-as-architect-and-editor (correlated errors)

Aider's base pattern can use one model as both planner and executor; we deliberately do not. Same-model self-pairings produce **correlated errors** -- the implementer and its auditor share blind spots. Run a **different tier** (or at minimum a different, freshly-forked context) on the auditor than on the implementer. This diversity is the entire reason the audit catches what the implementer missed.

### Corollary: challenger != auditor tier

If anyone adds an explicit *challenger -> auditor* step (one agent argues against a claim, a second adjudicates), the challenger **must** run on a different tier than the auditor -- two same-tier models launder correlated errors as independent confirmation. This is a guardrail on a hypothetical future step, not a license to build it; the current verification path uses the cheaper EXPLAINED-with-named-alternative mechanism (see [`replication-protocol.md`](replication-protocol.md) and [`verify-claims`](../skills/verify-claims/SKILL.md)), which adds no second agent.

## Cross-references

- [`cross-artifact-review.md`](cross-artifact-review.md) -- paper <-> code dependency graph (invoked at similar moments).
- [`post-flight-verification.md`](post-flight-verification.md) -- the forked `claim-verifier` (keep on the high-judgment tier per the anti-pattern above).
- [`orchestrator-protocol.md`](orchestrator-protocol.md) -- the critic-fixer routing this rule assigns tiers to.
