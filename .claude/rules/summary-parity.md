---
paths:
  - "CHANGELOG.md"
  - "README.md"
  - "manuscript/**/*.tex"
  - ".claude/skills/*/SKILL.md"
  - ".claude/rules/*.md"
  - ".claude/agents/*.md"
---

# Summary-Body Parity (anti-whack-a-mole)

**When editing any summary paragraph, do NOT apply surgical word-level fixes.** Summaries drift from their bodies when the body changes but the summary is not re-verified. Surgical edits to the flagged phrase almost always introduce a new drift elsewhere in the same paragraph.

## What counts as a "summary paragraph"

- CHANGELOG opening paragraph of a version entry (the lede before the first `###` subheading)
- README.md tagline and section ledes
- PR title and `## Summary` block
- Skill / rule / agent frontmatter `description:` field
- Manuscript abstract and section ledes (the abstract is the highest-stakes summary in the repo -- it must match the tables and the body claims)
- MEMORY.md `[LEARN:*]` entry headlines (the single-sentence summary before the prose)
- Any paragraph of the form "This release does X. It does not do Y. Counts are Z." -- the triple-claim shape is a drift magnet

## The protocol

When you edit a summary paragraph (or when a reviewer -- human, Copilot, or Codex -- flags one):

1. **Read the full body** the summary is summarizing. Not just the diff. The whole thing.
2. **Enumerate every substantive claim** in the current summary: every noun list ("skills, rules, hooks"), every count, every superlative ("no new"), every inclusion/exclusion ("except X"), every reported number (N, t-stat, coefficient).
3. **Check each claim against the body.** For each claim, find the body content (or the table) that supports or refutes it.
4. **Edit the whole paragraph, not just the flagged phrase.** Any specific claim that does not hold must be corrected in-place.
5. **Re-scan for orphan references.** A claim removed from the summary must not reappear in the body unreferenced, and vice versa.

## When to stop patching and rewrite

If a reviewer flags the same summary paragraph **twice in a row** (even on different words), stop patching -- rewrite structurally. Two hits on the same paragraph means the paragraph itself is the wrong shape, not the specific wording.

**Rewrite bias:** prefer abstraction over specificity in summaries. A summary that makes zero enumerative claims cannot drift.

| Drift-prone (specific) | Drift-proof (abstract) |
|------------------------|------------------------|
| "No new skills, no new rules, no new hooks" | "No new directories on disk" |
| "27 skills / 8 agents / 22 rules / 7 hooks" | "On-disk inventory unchanged -- see README for counts" |
| "Edits to `.claude/agents/X.md` and `.claude/skills/Y/SKILL.md`" | "Existing infrastructure revised" |
| "Main coefficient is -1.632 (t = -2.79)" | "Main coefficient is negative and significant (see Table 2)" |

The specific form is more informative when fresh but more likely to rot. The abstract form stays true across edits. (In a manuscript abstract a number is often *required* -- there, keep the number but treat it as a body-parity claim under rule step 3, not as prose to be reworded.)

## Lesson: review bots are drift detectors

Treat repeated review-bot findings (Copilot, Codex, a critic agent) on the same paragraph as a **structural signal**, not a list of bugs to patch one at a time. Each patch narrows the drift window but does not close it -- the next edit to the body reopens it elsewhere.

## The two-strikes pattern travels

The "flagged twice -> stop patching, escalate" rule is not specific to summaries. It applies wherever a disagreement can be quietly re-papered-over each round instead of resolved:

- `review-paper --adversarial` -- the same concern raised in rounds N and N+2 is flagged for the user rather than patched a third time.
- `verify-claims` / reproducibility audits -- a numeric claim downgraded to **EXPLAINED** in two consecutive audits without ever being corrected to PASS is surfaced prominently ("contested number EXPLAINED twice, never corrected") rather than left to hide behind its recorded note.

In each case, two strikes means the *artifact is the wrong shape*, not that the wording needs one more touch.

## Cross-references

- [`.claude/rules/content-invariants.md`](content-invariants.md) -- the numbered content rules a summary can violate.
- [`.claude/skills/commit/SKILL.md`](../skills/commit/SKILL.md) -- when writing the commit message for a doc-heavy PR, apply this rule to the `## Summary` section before pushing.
- [`.claude/skills/verify-claims/SKILL.md`](../skills/verify-claims/SKILL.md) -- "repeated EXPLAINED is a signal (two-strikes)" reuses this pattern for contested numeric claims.
