# Agent Fleet (which agent fills which lens, at which model tier)

The subagent roster the orchestration skills fan out to. This manifest is built **from the actual files in `.claude/agents/`** — each row names one agent, its one-line role, and its model/effort tier. The tier column is consistent with [`.claude/rules/model-routing.md`](../rules/model-routing.md): high-judgment work (referees, verifiers, the claim verifier, domain review, the editor) stays on the **Opus** tier and is never demoted to save cost; bounded review/critique passes run on the **Sonnet** tier; mechanical fix-application runs on the **Haiku** tier.

> **Tier vs. literal frontmatter.** The "Tier" column is the *role* the routing rule assigns (high-judgment / review / mechanical). The "`model:` frontmatter" column is what the file literally declares. Several fixer/critic agents declare `model: inherit` — they inherit the caller's model unless pinned. The routing rule's intent for each is given in the Tier column; pin the `model:` field to that tier when you profile the agent. Verify the current model IDs / effort defaults against the live Claude Code / Anthropic docs before pinning (see [`model-versions.md`](model-versions.md)).

## How this file is used

- [`orchestration-schemas.md`](orchestration-schemas.md) defines the `FINDING` / `SCORECARD` / `RUN_CONFIG` contracts every reviewer subagent below emits; this file says *which* agent fills *which* lens.
- [`.claude/rules/orchestrator-protocol.md`](../rules/orchestrator-protocol.md) routes the critic→fixer pairs by file type; the pairs are drawn from the agents below.
- The simulated-peer-review fleet (`editor` + `domain-referee` + `methods-referee`) is calibrated by [`journal-profiles.md`](journal-profiles.md) and [`discipline-cards.md`](discipline-cards.md).

---

## The eight original agents (critic / fixer / verifier core)

| Agent | Role (one line) | Tier (routing intent) | `model:` frontmatter |
|---|---|---|---|
| `code-reviewer` | Reviews `.do` / `.py` / `.sas` analysis scripts through 8 lenses (structure, reproducibility, data handling, domain correctness, output, docs, error handling, polish). Report only — no edits. | Review (Sonnet) | `inherit` |
| `code-fixer` | Applies ONLY the mechanical fixes a `code-reviewer` report identified (headers, paths, labels, seeds, formatting) to `.do` / `.py` / `.sas`; flags substantive issues for a human. | Mechanical (Haiku) | `inherit` |
| `proofreader` | Grammar / typo / overflow / consistency proofread of manuscript `.tex`. Report only — no edits. | Review (Sonnet) | `sonnet`, effort `high` |
| `manuscript-fixer` | Applies ONLY the approved language/formatting fixes a `proofreader` report identified to `.tex`; never touches substantive content. | Mechanical (Haiku) | `inherit` |
| `output-critic` | Checks tables/figures against the AEA style guide (`manuscript/aea_style_guide.md`): stars, notes, labels, `\input{}` path resolution. Report only. | Review (Sonnet) | `inherit` |
| `output-fixer` | Applies ONLY the formatting fixes an `output-critic` report identified to output `.tex` and the source `esttab` commands. | Mechanical (Haiku) | `inherit` |
| `domain-reviewer` | General substantive-correctness review of analysis/manuscript sections (identification assumptions, derivation correctness, citation fidelity, code↔theory alignment). NOT disposition-primed. Report only. | High-judgment (Opus) | `opus`, effort `high` |
| `verifier` | End-to-end reproducibility gate: runs scripts, reads logs for errors, confirms the manuscript compiles and outputs resolve. Runs actual commands — a reported PASS is not a PASS until re-run. | High-judgment (Opus) | `opus`, effort `high` |

## The eight newer agents (peer-review fleet, verification, humanizing, slides, memory)

| Agent | Role (one line) | Tier (routing intent) | `model:` frontmatter |
|---|---|---|---|
| `claim-verifier` | Fresh-context (forked) verifier of factual claims — citations, t-stats, coefficients, N, named entities — checked WITHOUT seeing the draft that produced them (Chain-of-Verification independence). The hallucination guard. | High-judgment (Opus) | `opus`, effort `high` |
| `editor` | Journal editor: desk-reviews a manuscript, selects two referees with deliberately opposed dispositions, calibrates to a target journal from `journal-profiles.md`, and synthesizes a decision. Enforces the post-judge hallucination gate (never rejects on a reason no referee raised). Drives `/review-paper --peer`. | High-judgment (Opus) | `opus`, effort `high` |
| `domain-referee` | Disposition-primed substantive referee (whole-paper contribution, lit positioning, external validity, journal fit), calibrated to a target journal + pet peeves by `editor`. Used by `/review-paper --peer`. | High-judgment (Opus) | `opus`, effort `high` |
| `methods-referee` | Disposition-primed methodology referee, paper-type-aware (reduced-form / structural / theory+empirics / descriptive / asset-pricing-test), each with its own dimension weights + mandatory sanity checks. Used by `/review-paper --peer`. | High-judgment (Opus) | `opus`, effort `high` |
| `humanize-auditor` | Read-only auditor for AI-voice tells in `.tex` / `.md` prose (boilerplate transitions, AI-cliché lexicon, em-dash overuse, symmetric shapes, tricolon abuse, hedging stacks, "not only X but also Y", formulaic openers, sycophancy). Report only. Drives `/humanize`. | Review (Sonnet) | `sonnet`, effort `high` |
| `slide-auditor` | Visual-layout auditor for Beamer slides under `slides/`: overflow, font consistency, box fatigue, spacing. Report only. | Review (Sonnet) | `sonnet`, effort `high` |
| `beamer-translator` | Translates source material (a manuscript section, notes, or a deck in another format) INTO project-standard Beamer LaTeX — environment mapping, citation conversion, math, figures, tables. The slide-construction worker. | Review/build (Sonnet) | `sonnet`, effort `medium` |
| `promote-memory-council` | One of a five-critic council that votes YES/NO on promoting a candidate `[LEARN]` entry from `personal-memory.md` (gitignored) to MEMORY.md (committed) — each critic judges one dimension (generality / staleness / redundancy / evidence / format) in a forked context. Drives `/promote-memory`. | Mechanical (Haiku) | `haiku` |

---

## Routing notes (consistency with `model-routing.md`)

- **Critic→fixer pairs by file type** (from `orchestrator-protocol.md`): `.do`/`.py`/`.sas` → `code-reviewer` (Sonnet) hands a diff to `code-fixer` (Haiku); manuscript `.tex` → `proofreader` (Sonnet) → `manuscript-fixer` (Haiku); output `output/tables/*.tex` + figures → `output-critic` (Sonnet) → `output-fixer` (Haiku). The critic judges; the fixer applies a verbatim "replace X with Y" — that asymmetry is why the critic sits a tier above the fixer.
- **Never demote the judgment tier.** `claim-verifier`, `domain-reviewer`, `editor`, `domain-referee`, `methods-referee`, and a non-trivial `verifier` stay on Opus. These are the agents that protect the paper from hallucinated citations, weak identification, and desk-reject mistakes; a too-cheap judge is as bad as no judge (`model-routing.md`, "Anti-pattern: pushing the high-judgment tier down").
- **Diversity over self-pairing.** Run a *different* tier (or at minimum a freshly-forked context) on an auditor than on the implementer it audits — same-model self-pairings launder correlated errors as independent confirmation.
- **Effort is the first cost lever.** Mechanical agents → low/medium effort; review and judgment → high effort. Drop effort before dropping a tier, and never below the audit lens.

## Cross-references

- [`.claude/rules/model-routing.md`](../rules/model-routing.md) — the tier-assignment rule this manifest is consistent with.
- [`orchestration-schemas.md`](orchestration-schemas.md) — the `FINDING` / `SCORECARD` / `RUN_CONFIG` contracts these agents emit and consume.
- [`.claude/rules/orchestrator-protocol.md`](../rules/orchestrator-protocol.md) — the critic→fixer fan-out routing.
- [`journal-profiles.md`](journal-profiles.md) / [`discipline-cards.md`](discipline-cards.md) — calibration for the `editor` / referee fleet.
- [`model-versions.md`](model-versions.md) — verify current model IDs / prices / effort before pinning a `model:` field.
