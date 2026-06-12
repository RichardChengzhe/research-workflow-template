---
name: slide-excellence
description: Multi-agent comprehensive review of a Beamer seminar/conference deck (visual layout + proofreading + substance, plus methodology and voice conditionally). Use when the user says "full review", "excellence pass", "comprehensive check", "review the deck", "pre-seminar review", "slide excellence", or before presenting / shipping a research talk. Fan-out wrapper -- for a single lens, use `/visual-audit` (figures), `slide-auditor` (deck layout), or `/proofread` directly.
argument-hint: "[TEX deck filename] [--fast] [--skip-substance] [--with-methods] [--with-voice]"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Task"]
context: fork
---

# Slide Excellence Review (Beamer seminar deck)

Run a comprehensive multi-dimensional review of an academic Beamer deck -- a seminar or conference research talk, not a teaching lecture. Multiple agents analyze the file independently, then results are synthesized via fan-out -> reduce.

> **Which slide-review tool do I want?**
>
> - **`/slide-excellence`** (this skill) -- multi-agent fan-out (visual + proofread + substance, plus methodology / voice conditionally). Best for a **pre-seminar** or **pre-submission** deck check.
> - **`slide-auditor`** (agent) -- single lens, deck layout/overflow/font/spacing/box-fatigue only. Fast.
> - **`/visual-audit`** -- single lens, *publication-figure* legibility (the `.pdf`/`.png` plots a deck `\includegraphics`-es), not the deck itself.
> - **`/proofread`** -- single lens, grammar/typos/overflow/terminology.
> - **`/devils-advocate`** -- 5-7 pointed challenges to the argument, not a full review.

**Important:** this orchestrator does **conditional** dispatch -- it only spawns the subagents that can produce useful output for the given deck. Methodology and voice lenses are opt-in; substance is gated on the deck being a `.tex` file.

> **Overlay policy (hard rule):** this project forbids `\pause`, `\onslide`, `\only`, `\uncover`, and all Beamer overlay commands -- progressive builds are done by *splitting frames* (see [`no-pause-beamer.md`](../../rules/no-pause-beamer.md)). Pre-flight checks for them; the `slide-auditor` lens flags any that slip through and never recommends adding one.

## Step 1: Identify the deck

Parse `$ARGUMENTS` for the filename. Resolve the path in `slides/` (the overlay-rule-scoped deck directory) or `latex/` (the project's Beamer location per CLAUDE.md). This skill targets **Beamer `.tex` decks only** -- if handed a `.qmd`, `.md`, or a non-deck `.tex` (e.g. the manuscript), report the mismatch and stop rather than running deck lenses on the wrong file type.

## Step 2: Pre-flight -- detect conditions

Before spawning any agent, probe the deck:

```bash
FILE="$resolved_path"

# Overlay-policy violations (hard rule -- must be zero)
overlays=$(grep -cE '\\(pause|onslide|only|uncover)\b' "$FILE" 2>/dev/null); overlays=${overlays:-0}

# Frame count (sanity: matches the talk's time budget?)
frames=$(grep -cE '\\begin\{frame\}|\\frame\b' "$FILE" 2>/dev/null); frames=${frames:-0}

# Embedded figures (each should also pass /visual-audit at print size)
figs=$(grep -cE '\\includegraphics' "$FILE" 2>/dev/null); figs=${figs:-0}

# Speaker notes / prose blocks (gate the optional voice lens)
has_notes="false"
grep -qE '\\note\{|\\begin\{frame\}.*\}\{' "$FILE" 2>/dev/null && has_notes="true"
```

Report the detection:

```
File:           slides/seminar_2026.tex
Type:           Beamer (.tex)
Frames:         34
Overlay cmds:   0   (policy: must be 0)
\includegraphics: 6
Speaker notes:  none
```

If `overlays > 0`, surface it immediately as a **CRITICAL** pre-flight finding (with line numbers) -- the deck violates the no-pause rule before any agent runs.

## Step 3: Substance-lens readiness check (for `.tex`)

The substance lens uses [`domain-reviewer`](../../agents/domain-reviewer.md), which is a **template** until you tailor its lenses to your field. Running it unmodified yields generic "are assumptions stated?" feedback rather than real finance/accounting review. Before spawning it:

- If `domain-reviewer.md` still reads like the shipped template (its lenses untouched for your paper), warn the user and offer to (a) proceed with `--skip-substance`, or (b) run it anyway accepting generic feedback. Do **not** silently run a un-tailored substance reviewer.

(There is no template-marker token to grep here; judge by whether the five lenses have been adapted to the project's methods.)

## Step 4: Run review agents in parallel

Spawn only the agents whose conditions hold (fan-out per [`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md)):

**Always-on for a `.tex` deck:**

- **Agent A: Visual / layout audit** (`slide-auditor`) -- overflow, font consistency, box fatigue, spacing, image alignment, and overlay-policy enforcement. Save: `quality_reports/[FILE]_visual_audit.md`.
- **Agent B: Proofreading** (`proofreader`) -- grammar, typos, terminology consistency, citation sanity. Save: `quality_reports/[FILE]_proofread_report.md`.

**Conditional:**

- **Agent C: Substance review** (`domain-reviewer`) -- MANDATORY for `.tex` unless `--skip-substance`; GATED by Step 3. Domain correctness of the claims on the slides via the field lenses. Save: `quality_reports/[FILE]_substance_review.md`.
- **Agent D: Methodology referee** (`methods-referee`) -- only if `--with-methods`. A referee's-eye pass on the identification / specification / inference claims the deck makes -- useful before a conference where a discussant will probe the design. Save: `quality_reports/[FILE]_methods_review.md`.
- **Agent E: Voice audit** (`humanize-auditor`) -- only if `--with-voice` (or if speaker-notes/prose were detected). Flags AI-voice tells in any prose-heavy slides or speaker notes. Save: `quality_reports/[FILE]_voice_review.md`.

**De-duplication:** if the user already ran one of these lenses on this deck in the current session (e.g. ran `/proofread` first), ask whether to reuse the existing report or re-run. Default: reuse (saves tokens).

## Step 5: Synthesize the combined summary (reduce typed findings)

This is **fan-out -> reduce** ([`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md)): each agent returns its findings + a scorecard; this step **stacks the scorecards** rather than re-reading each report by eye. A skipped lens contributes no findings (not zeros to an average). Include only sections for agents that actually ran.

```markdown
# Slide Excellence Review: [Filename]

**File:** [path]
**Type:** Beamer (.tex)
**Detected:** frames=N | overlays=0 | figures=N | notes=[yes/no]
**Agents spawned:** [A, B, C] (skipped: D [no --with-methods], E [no prose])

## Overall Quality Score: [EXCELLENT / GOOD / NEEDS WORK / POOR]

| Dimension | Critical | Medium | Low |
|-----------|----------|--------|-----|
| Visual / Layout | | | |
| Proofreading | | | |
| Substance (if ran) | | | |
| Methodology (if ran) | | | |
| Voice (if ran) | | | |

### Critical Issues (immediate action required)
### Medium Issues (next revision)
### Recommended Next Steps
```

Any non-zero `overlays` count from Step 2 is reported as a standing **CRITICAL** under Visual / Layout, with the fix = split the frame (never add an overlay).

## Step 6: Report token/time budget

After completion, print an estimate:

```
Spawned N agents; approx token usage ~XXk. Sequential fallback
(one agent at a time) would cost ~XXk but take ~5x longer. For
cost-conscious reviews, run individual lenses directly
(slide-auditor, /proofread).
```

## Flags

- `--fast` -- Spawn a single synthesis agent that reads the deck directly, rather than parallel subagents. Cheaper but less thorough; use for a quick pre-read.
- `--skip-substance` -- Don't spawn the `domain-reviewer` (Agent C). Use when its lenses aren't yet tailored to your field, or you only want layout + proofreading.
- `--with-methods` -- Also spawn `methods-referee` (Agent D) for a referee's-eye pass on the design claims -- recommended before a conference talk.
- `--with-voice` -- Also spawn `humanize-auditor` (Agent E) on prose-heavy slides / speaker notes.

## Quality score rubric

| Score | Critical | Medium | Meaning |
|-------|----------|--------|---------|
| Excellent | 0-2 | 0-5 | Ready to present |
| Good | 3-5 | 6-15 | Minor refinements |
| Needs Work | 6-10 | 16-30 | Significant revision |
| Poor | 11+ | 31+ | Major restructuring |

(An overlay-policy violation is CRITICAL regardless of count -- a single `\pause` caps the deck at "Needs Work" until removed.)

## Why conditional dispatch matters

Spawning every lens regardless of the deck wastes tokens and erodes trust: a methodology referee on a five-slide intro deck, or a substance reviewer whose lenses were never tailored, produces feedback authors learn to ignore. Conditional dispatch runs only the lenses that can say something useful, and pushes the heavyweight methodology/voice passes behind explicit flags.

## Cross-references

- [`.claude/agents/slide-auditor.md`](../../agents/slide-auditor.md) -- the visual/layout lens (and overlay-policy enforcer) this orchestrator always runs on a deck.
- [`.claude/rules/no-pause-beamer.md`](../../rules/no-pause-beamer.md) -- the overlay ban; pre-flight enforces it, `slide-auditor` re-checks it.
- [`.claude/agents/proofreader.md`](../../agents/proofreader.md), [`.claude/agents/domain-reviewer.md`](../../agents/domain-reviewer.md), [`.claude/agents/methods-referee.md`](../../agents/methods-referee.md), [`.claude/agents/humanize-auditor.md`](../../agents/humanize-auditor.md) -- the conditional lenses.
- [`.claude/skills/visual-audit/SKILL.md`](../visual-audit/SKILL.md) -- audits the *publication figures* a deck embeds (a different lens from deck layout).
- [`.claude/agents/beamer-translator.md`](../../agents/beamer-translator.md) -- builds the deck in the first place; this skill reviews the result.
- [`.claude/rules/orchestrator-protocol.md`](../../rules/orchestrator-protocol.md) -- the fan-out -> reduce pattern Steps 4-5 implement.

## What this skill does NOT do

- **Review a `.qmd` / RevealJS / PowerPoint deck.** This template's slide stack is Beamer LaTeX only; there is no Quarto/RevealJS path.
- **Audit the embedded figures at print size** -- that is [`/visual-audit`](../visual-audit/SKILL.md). This skill reviews the deck; figure legibility is its own lens.
- **Edit the deck.** It produces reports; fixing is a separate step (and a layout fix is *split the frame*, never add an overlay).
- **Build slides from a manuscript** -- that is the [`beamer-translator`](../../agents/beamer-translator.md) agent's job.
