# Model Tiers (roles, not product versions)

This file deliberately names **no current model point-version, ID, or price.** Those drift fast and go stale between releases; pinning them here creates a second source of truth that rots. Instead, the template refers to models by **role tier** — *high-judgment*, *review*, *mechanical* — and this file maps each role to what it's for. The companion routing rule, [`model-routing.md`](../rules/model-routing.md), assigns those tiers to specific agents and skills.

> **Verify before you pin.** Model IDs, prices, context-window sizes, fast-mode multipliers, and effort-level names/defaults change with every Anthropic release. **Check the live Claude Code / Anthropic documentation for the current model IDs, prices, and effort levels before writing any concrete model name into an agent's `model:` frontmatter or a script.** Treat the tier table below as stable; treat any specific product name as a thing to look up.
>
> **Last reviewed:** 2026-06-11. (This date tracks when the *tier mapping* was last sanity-checked, not a model-currency claim.)

## The three tiers

| Tier (role) | Use for | Routed to (examples) |
|---|---|---|
| **High-judgment** | Research-design decisions; multi-file refactors with judgment calls; report / LaTeX / table builders; data-pipeline changes (merges, winsorization, FE specs); non-trivial `.do` / `.py` / `.sas` writing; domain (finance/accounting) reasoning; **and every audit / verifier / referee / editor pass.** | `verifier`, `claim-verifier`, `domain-reviewer`, `editor`, `domain-referee`, `methods-referee`; any non-trivial implementer. |
| **Review / critique** | Bounded review passes — proofreading inspection, table/figure style audit, AI-voice audit, a critic that hands a diff to a mechanical fixer. | `code-reviewer`, `output-critic`, `proofreader`, `humanize-auditor`, `slide-auditor`. |
| **Mechanical** | File renames; search-and-replace; citation/bib formatting; applying a critic's verbatim "replace X with Y" fix; simple file lookups. | `code-fixer`, `manuscript-fixer`, `output-fixer`, `promote-memory-council`. |

The mapping to the current Anthropic product line is the obvious one — the most capable model for the high-judgment tier, the workhorse model for review, the fast/cheap model for mechanical work — but **which named model fills each slot is a live-docs lookup, not a constant in this file.**

## Two cost levers, in order

1. **Effort first.** Most models expose an effort level (low / medium / high / …). Lowering effort on a bounded task is usually cheaper than dropping a tier. Mechanical work → low/medium; review and judgment → high; the hardest gates → the highest effort the model offers. (Effort-level names change between releases — verify in live docs.)
2. **Tier second.** Drop to a cheaper tier only when effort alone won't do it — and **never below the audit lens.** Demoting `claim-verifier`, `domain-reviewer`, the referee/editor agents, or a non-trivial `verifier` to save cost is the one move the routing rule forbids: a too-cheap judge is as bad as no judge.

## Mentioning specific versions

It is fine to name a specific model in a **historical** context (a CHANGELOG entry, a "this was built on model X" note) or in an explicit **comparison** ("X's high effort does what Y's xhigh did"). It must **not** be presented as *the current / newest / default* model anywhere in user-facing surfaces — that claim goes stale the next release and there is no checker here validating it. When you need "the current Opus", say exactly that (a tier-relative phrase that stays true), not a point version.

## Cross-references

- [`model-routing.md`](../rules/model-routing.md) — the rule that assigns these tiers to agents/skills and forbids demoting the judgment tier.
- [`agent-fleet.md`](agent-fleet.md) — the per-agent manifest with each agent's tier.
