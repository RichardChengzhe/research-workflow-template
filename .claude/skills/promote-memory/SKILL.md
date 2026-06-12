---
name: promote-memory
description: Review candidate `[LEARN]` entries in `personal-memory.md` (root, gitignored) and run them through a five-critic council in parallel: generality, staleness, redundancy, evidence, format. Majority vote (3+ of 5) proposes promotion to MEMORY.md (committed). Use when the user says "promote memory", "review my learnings", "what should graduate to MEMORY.md", "five-critic council", or as monthly memory maintenance. Pairs with the `promote-memory-council` agent.
author: Claude Code Academic Workflow
version: 1.0.0
argument-hint: "[entry-substring or 'all']"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Glob", "Grep", "Task", "Bash"]
---

<!-- Pattern adapted with attribution from Chris Blattman's "five-critic council"
     (claudeblattman.com continuous-improvement loop). Blattman uses it to decide
     what enters his MEMORY layer; we adapt it to the personal-memory -> MEMORY.md
     promotion question codified in .claude/rules/meta-governance.md. -->

# `/promote-memory` -- five-critic council for memory promotion

The template's [`meta-governance.md`](../../rules/meta-governance.md) rule splits memory into two tiers:

- **`MEMORY.md`** (root, committed, index kept under ~200 lines / ~24 KB) -- generic learnings that help all forkers.
- **`personal-memory.md`** (root, gitignored, no size cap) -- machine-specific and user-specific learnings.

The rule says generic patterns should sync via git; personal patterns stay local. **What it doesn't say** is *who decides which is which*. `/promote-memory` operationalizes the call: spawn five critics in parallel, each reviewing the candidate `[LEARN]` entries on a single dimension, and propose promotion on majority vote (3+ of 5). The user is always the final gate.

> **Why the bar is high here:** the committed index loads into every future session and has a real size budget -- over-long entries get truncated at load time. A YES vote means the entry earns a permanent line of committed-index space. When in doubt: "would this still be worth its line six months and one new paper from now?"

## When to use

- **Monthly memory maintenance.** `personal-memory.md` accumulates faster than `MEMORY.md`; the council periodically harvests the genuinely generic learnings (a Stata batch-mode flag, a WRDS/SAS gotcha, a cross-build merge-key rule).
- **Before sharing a fork.** Someone is about to clone your template -- what should they inherit?
- **After a large project ships.** Lessons from a paper deserve curation before the next project starts adding noise.
- **As a recurring task.** Wire a monthly schedule (`/loop`, `/schedule`, or cron) to `/promote-memory all` if you want automated *proposal* cadence (still requires user approval for each promotion).

## When NOT to use

- **For a single fresh `[LEARN]` after one correction.** Just add it to `personal-memory.md`; let it sit until the next council runs.
- **For deleting stale entries.** `/promote-memory` only promotes; it does not demote. Demotion is a manual edit + commit.
- **For project-specific context** (a dataset's md5, a named treatment dummy, a particular paper's t-stat). That belongs in CLAUDE.md or a session log, not in either memory tier.

## The five critics

Each critic runs in a forked context (`Task` with the `promote-memory-council` agent) -- they don't see each other's verdicts or the user's draft. Each casts one **YES/NO** vote per candidate entry with a one-sentence rationale. The full per-dimension rubric lives in [`.claude/agents/promote-memory-council.md`](../../agents/promote-memory-council.md); the short form:

1. **Generality** -- would a *different* empirical-research project (a different finance/accounting paper, or a forker in labor, health, marketing) benefit, or is the lesson welded to one machine path / one dataset / one paper's facts? Welded -> NO.
2. **Staleness** -- does the entry contradict the current codebase? `Grep`/`Read` every file path, script name, `params.do` global, or setting it references. Renamed / removed / now-automated -> NO.
3. **Redundancy** -- is this already in MEMORY.md, CLAUDE.md, or a `.claude/rules/*.md` file (even paraphrased)? Duplicate or strict sub-case -> NO.
4. **Evidence** -- does the entry cite the incident, commit, or file that motivated it (a `**Why:**` / `**How to apply:**` anchor)? Bare "always do X" with no rationale -> NO.
5. **Format** -- does it follow the `[LEARN:category] wrong -> right` schema in [`meta-governance.md`](../../rules/meta-governance.md), with a category consistent with its neighbours, and an index line short enough to fit the budget? Free-form / mis-tagged / over-long -> NO.

### Council verdict

The promotion threshold is **majority (3+ YES)**:

- **5 YES** -- propose promotion without modification.
- **4 YES** -- propose promotion with a one-line note about the dissenting concern.
- **3 YES** -- propose promotion but address the dissenting critics' concerns first (typically: trim to one line, add evidence, fix the tag).
- **2 or fewer YES** -- do not propose. Either fix the entry per the dissenting critics' feedback and re-submit, or leave it in `personal-memory.md`.

## Steps

### Step 1: Read candidate entries

If `$ARGUMENTS` is `all`, read every `[LEARN:*]` entry in `personal-memory.md` (root). Otherwise treat `$ARGUMENTS` as a substring filter (e.g., `stata` matches all `[LEARN:stata]` entries).

### Step 2: Spawn the council

Five `Task` invocations in parallel, one per critic, each dispatching the `promote-memory-council` agent with the critic role named in the prompt:

- **Generality** -- context: the candidate entry + a one-paragraph note that the template's audience is empirical researchers across quantitative fields.
- **Staleness** -- context: the candidate entry + `Read`/`Grep` access. Must explicitly check every file path / script / global / setting the entry references.
- **Redundancy** -- context: the candidate entry + current `MEMORY.md` + `CLAUDE.md` + relevant rule files.
- **Evidence** -- context: the candidate entry only. Vote on whether it self-describes its motivation.
- **Format** -- context: the candidate entry + [`meta-governance.md`](../../rules/meta-governance.md) for the schema.

The agent already pins the **Haiku tier** (per [`.claude/rules/model-routing.md`](../../rules/model-routing.md): bounded mechanical-ish review). Override via the agent's `model:` field only if a harder call needs Sonnet.

### Step 3: Aggregate votes

Collect verdicts. For each candidate entry, compute the vote count + per-critic verdicts.

### Step 4: Present the verdicts

For each entry:

```markdown
## `[LEARN:stata] <summary>`

**Vote:** 4-of-5 YES (propose with note)

| Critic | Vote | Rationale |
|---|:---:|---|
| Generality | YES | Stata batch-mode flag recurs across any Windows Stata project. |
| Staleness  | YES | `00_run.do` and the flag still resolve. |
| Redundancy | YES | Not in MEMORY.md or any rule file. |
| Evidence   | NO  | Doesn't cite the originating r(601) failure. Add a one-line "Incident:" pointer before promoting. |
| Format     | YES | Tag consistent with neighbours; index line fits the budget. |

**Recommendation:** Address Evidence critic (add incident pointer), then promote.

**Proposed MEMORY.md addition (one line):**
[LEARN:stata] <full proposed text, single line, under the index budget>
```

### Step 5: User approves the promotions

The user reviews the report and explicitly approves which entries to promote. The skill then:
- appends approved entries to MEMORY.md at the appropriate `[LEARN:category]` section, **one line each**, re-checking the index size budget after the append;
- removes the same entries from `personal-memory.md` (or marks them `# promoted YYYY-MM-DD` for audit);
- surfaces a summary.

Do **not** auto-promote -- even on 5-of-5 YES. The user's domain judgment is the final gate.

## Output

- Per-entry council report (verdicts, rationales, recommendations) -- to the conversation.
- On approval: MEMORY.md updated (append at the right `[LEARN:category]` section, one line each); `personal-memory.md` updated (entry marked promoted).
- A `quality_reports/memory_promotion_<date>.md` audit file recording the full council session for forensics.

## Anti-patterns

- **Auto-promoting on 5-of-5 YES.** Even unanimous agreement can be wrong; the user's domain judgment is the final gate.
- **Promoting a multi-line entry.** The index has a hard budget -- if the lesson needs more than one line, move detail to a topic file and promote a one-line pointer.
- **Re-running the council on the same entry** hoping for a different result. If 4 critics consistently say NO, file it in `personal-memory.md` and stop.
- **Skipping the Evidence critic** because the entry "looks obvious." Evidence is what makes the entry portable across forkers; obvious-to-you is not obvious-to-them.
- **Demoting via this skill.** It only promotes. Demotion is a manual edit + commit.

## Cross-references

- [`.claude/rules/meta-governance.md`](../../rules/meta-governance.md) -- the two-tier memory contract this skill operationalizes (and the index size budget).
- [`.claude/agents/promote-memory-council.md`](../../agents/promote-memory-council.md) -- the five-critic implementation (one agent file, five role specs, dispatched in parallel via `Task`).
- [`.claude/rules/model-routing.md`](../../rules/model-routing.md) -- why critics default to the Haiku tier.
- `/learn` (existing skill) -- captures new `[LEARN]` entries; pairs with `/promote-memory` (which decides what graduates).
- `/compress-session`, `/checkpoint` -- both surface candidate `[LEARN]` entries mid-session; `/promote-memory` is where those candidates are adjudicated for the committed index.
