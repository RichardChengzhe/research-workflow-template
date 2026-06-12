---
name: verify-claims
description: Run Chain-of-Verification (CoVe) on a draft or a block of text with factual claims. Spawns the `claim-verifier` agent in a forked (fresh) context so it never sees the draft — then reports which claims are supported, contradicted, or unverifiable. Use when user says "verify these citations", "check the claims in X", "did I hallucinate anything", "fact-check this draft", "run CoVe on this", or after any text generation that asserts facts about papers, datasets, or numerical results. NOT for style/grammar review (use `/proofread`) or substance review (use `/review-paper`).
argument-hint: "[file-or-text-path] [--source <path-or-url>] [--no-fail-closed]"
allowed-tools: ["Read", "Grep", "Glob", "Task", "Write"]
---

# /verify-claims — Chain-of-Verification on a Draft

Fact-check a draft using the **Post-Flight Verification protocol** ([`.claude/rules/post-flight-verification.md`](../../rules/post-flight-verification.md)).

**Input:** `$ARGUMENTS` — path to a file containing the draft (`.tex`, `.md`, `.txt`) or a shorthand pointer. Optional flags:

- `--source <path-or-url>` — one or more source-material pointers (repeat for multiple). Sources are the artifacts a claim must trace back to: a paper PDF in `master_supporting_docs/supporting_papers/`, a regression `.log` in `output/logs/`, a reported table in `output/tables/`, a `.ster` estimate, the `.dta`/`.csv` a number was computed from, or a canonical URL (DOI / journal page). If omitted, the skill infers from context (e.g., papers referenced, cited DOIs).
- `--no-fail-closed` — downgrade FAIL outcomes to warnings without regeneration. Use sparingly.

## When to pick this skill

- **`/verify-claims`** (this skill) — ad-hoc fact-checking on any draft or text block the user hands you. One-shot, user-invoked. Equally for **citations** (does the cited paper say what the draft attributes to it?) and **empirical numbers** (does the reported t-stat / coefficient / N match the estimation artifact that produced it?).
- **Other skills that auto-run Post-Flight internally** (`/lit-review`, `/research-ideation`, `/respond-to-referees`, `/review-paper --peer`) — no need to call this separately; they already run it.
- **`/proofread`** — grammar, typos, overflow. Different lens.
- **`/review-paper`** (default mode) — full manuscript review, not just claim verification.
- **`/validate-bib`** — checks citations *exist* and are well-formed (structural + DOI). This skill checks they *hold* (the cited paper supports the attributed claim) and that *reported numbers reconcile to their source*. Complementary — run both before submission.

## How it works

Implements the 4-step CoVe loop from Dhuliawala et al. 2023 ([arXiv:2309.11495](https://arxiv.org/abs/2309.11495)), with architectural enforcement of the fresh-context independence trick.

### Phase 0 — Pre-Flight

Confirm:
- Draft file exists and is readable
- At least one source pointer available (either `--source` or auto-detected from draft)
- `claim-verifier` agent file exists at `.claude/agents/claim-verifier.md`

If any fail → surface the failure, do NOT proceed.

### Phase 1 — Extract claims

Read the draft. Identify factual assertions of these types:

| Type | Example |
|------|---------|
| Citation | "Smith, Jones, and Lee (2021, *JFE*) show X" |
| Numerical fact | "N = 120{,}000", "the focal interaction is -0.0123 (t = -3.45)" |
| Negative literature | "No prior work prices this characteristic" |
| Named entity | researcher, paper title, venue, estimator name (e.g. `csdid`, Callaway-Sant'Anna), dataset (CRSP, Compustat, IBES) |
| Dataset claim | "CRSP-v2 / CIZ reaches 2025-12-31"; "Compustat `at` is total assets" |

Skip: opinions, forward-looking suggestions, definitions the draft introduces.

**For citation-type claims, extract the claim-citation PAIR — not just the citation.** Capture *what* the draft attributes to *which* work, so the verifier checks **appropriateness** (does SJL (2021) actually *show* X?), not merely existence. "Smith (2019) shows a positive abnormal-return effect" becomes `{cite: Smith2019, attributed: "positive abnormal-return effect"}`. This is the layer `/validate-bib` explicitly defers here: validate-bib confirms the citation *exists and is well-formed*; this skill confirms it *holds*. A mis-citation (the paper exists but says something else, or the opposite) is exactly a numeric/directional contradiction → HIGH-WARN unless a concrete `author_alternative` is recorded (then EXPLAINED).

**For numeric claims, record the source artifact, not just the number.** The source of truth for a t-stat is the regression that produced it, not memory or the manuscript prose. Pair each "ATT = 0.42 (t = 3.1)" with the `.log` / `.tex` / `.ster` it should reconcile to, so the verifier reads the literal estimation output rather than re-deriving.

Output a claims table:

```markdown
| ID | Claim | Source hint |
|----|-------|-------------|
| C1 | ... | ... |
```

### Phase 2 — Generate verification questions

One question per claim. Make it specific and answerable from the source alone.

### Phase 3 — Spawn `claim-verifier` (forked, fresh context)

```
Task: subagent_type=claim-verifier, context=fork
Prompt: hand over claims table + verification questions + source material pointers.
        Do NOT include the draft text.
```

The forked agent runs the CoVe independent-answer step. It has never seen the draft and cannot confirm-bias. It returns a structured verification report.

### Phase 4 — Reconcile

The verifier returns a per-claim verdict in one of these severity tiers:

- **HIGH-WARN** — fabricated reference (the cited paper doesn't exist at the named venue/year), draft claim directly contradicted by the source (including a reported coefficient / t-stat / N that does not match the estimation artifact), or `not_found` retrieval that the verifier interprets as a hallucinated citation. **Gate-refuse** — these block `/commit` for any file `/verify-claims` was just run against, unless the user explicitly overrides with `--no-fail-closed` or sets `verifyClaims.allowHighWarn: true` in `.claude/settings.json`.
- **MED-WARN** — transient infrastructure / retrieval failure (paywall the verifier can normally bypass via cached metadata; DOI resolver timeout; partial PDF read). Surface for the author; do not gate-refuse.
- **LOW-WARN** — source genuinely inaccessible: paywalled and not in cache, or a **licensed vendor dataset that cannot be redistributed** (CRSP, Compustat, IBES, TAQ), or a pre-print server transient. Surface with `cannot-verify` flag; do not gate-refuse — the number may well be correct; the verifier just cannot independently re-pull the licensed source.
- **EXPLAINED** — a numeric/directional contradiction the author has *pre-justified* with a concrete named alternative (a different but defensible specification — e.g. firm-FE vs industry-by-month FE, full sample vs common sample, winsorization cut, FE structure, or rounding convention), passed to the verifier via the claim's `author_alternative` field. Surfaced with the evidence and the recorded reason; **non-gating**. The hard floor holds: a *fabricated* citation is never EXPLAINED, and a blank/vague alternative stays HIGH-WARN. This mirrors `audit-reproducibility`'s EXPLAINED disposition for numeric claims — a mismatch is not always a failure when a defensible alternative is named.

Verdict aggregation by tier across all extracted claims (EXPLAINED counts as non-gating, like LOW):

| Tier counts | Outcome | `/commit` behaviour |
|---|---|---|
| 0 HIGH, 0 MED, >= 0 LOW/EXPLAINED | **PASS** (green block) | proceeds |
| 0 HIGH, >= 1 MED, any LOW/EXPLAINED | **PARTIAL** (yellow block) | proceeds with warning |
| >= 1 HIGH | **FAIL** (red block) | **halts** unless override |

`--no-fail-closed` opts out of the gate-refuse behaviour on HIGH-WARN. Use sparingly — it's there for offline / hallucination-sensitive contexts where the user accepts the risk in writing.

If the draft is writeable and the user asked for auto-correction, regenerate the affected sections using the verifier's evidence. Otherwise return the report and let the user decide.

## Example

```
/verify-claims quality_reports/lit-review_taste-based-pricing.md \
  --source master_supporting_docs/supporting_papers/smith_jones_lee_2021.pdf \
  --source master_supporting_docs/supporting_papers/callaway_santanna_2021.pdf \
  --source output/logs/04_analysis.log
```

Expected output (abridged):

```markdown
## Post-Flight Verification — lit-review_taste-based-pricing.md

**Claims extracted:** 14
**Verified independently:** 14 (forked claim-verifier)
**Outcome:** PARTIAL — 12 verified, 1 discrepancy, 1 unverifiable

### Discrepancies

- **C7** — draft claims "Callaway & Sant'Anna (2021) *propose* a synthetic-control estimator." Source Section 4 shows they propose a doubly-robust group-time ATT estimator, not synthetic control. Recommend correction.

### Unverifiable

- **C12** — draft cites a reported alpha that should trace to `output/logs/04_analysis.log`, but no matching estimation block was found in the provided log. Recommend user supply the correct log or table.

### Verified

| ID | Claim | Evidence |
|----|-------|----------|
| C1 | "SJL (2021) model a taste-driven equilibrium for a non-pecuniary characteristic" | p. 5, eq. (3) |
| C9 | "headline interaction = -0.0123 (t = -3.45)" | output/tables/main_results.tex, focal row |
| ... | ... | ... |
```

## Fail modes and recovery

**Verifier times out:** surface a warning block, return draft as provisional. Do not silently ship.

**Source material inaccessible** (paywall, 404, licensed WRDS data): report the specific claims that hinge on it, flag as `cannot-verify` (LOW-WARN), recommend user supply a local copy or an alternative source.

**Draft contains only opinions / forward-looking text:** report "no verifiable factual claims extracted — nothing to check" and return.

## Cross-references

- [`.claude/agents/claim-verifier.md`](../../agents/claim-verifier.md) — the forked verifier.
- [`.claude/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) — the protocol.
- [`.claude/rules/verification-protocol.md`](../../rules/verification-protocol.md) — the run-scripts / read-logs discipline (where empirical numbers come from).
- [`.claude/skills/validate-bib/SKILL.md`](../validate-bib/SKILL.md) — structural citation existence check (complementary).
- MEMORY.md `[LEARN:pattern]` on Chain-of-Verification vs critic-fixer vs cross-artifact review.
