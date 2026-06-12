---
name: deep-audit
description: |
  Exhaustive adversarial audit of the manuscript and its supporting repository.
  Launches parallel specialist agents (referee/editor + claim-verifier + code-reviewer)
  to find unsupported claims, code bugs, table/figure-vs-text mismatches, and
  cross-document count inconsistencies. Triages, fixes mechanical issues, and
  loops until two consecutive dry rounds.
  Use when: after broad changes to the paper or pipeline, before submission, or
  when the user says "audit", "find inconsistencies", "check everything".
author: Claude Code Academic Workflow
version: 1.0.0
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "Task"]
disable-model-invocation: true
---

# /deep-audit — Manuscript + Repository Adversarial Audit

Run a comprehensive consistency audit across the manuscript and the repository artifacts that back it (estimation logs, tables, figures, scripts, skills/rules/agents, and the top-level index docs), fix what is mechanically fixable, and loop until clean.

This is the heaviest review tool in the kit. For a single-paper referee simulation use `/review-paper --peer <journal>`; for lens coverage use `/seven-pass-review`. Use `/deep-audit` when you also want the *infrastructure around the paper* checked — does the code that produced Table 3 still run, do the counts in `README.md` match disk, does every reported number trace to an artifact.

## When to Use

- After broad changes (new analyses, refactored pipeline, new skills/rules/agents).
- Before submission or a major commit.
- When the user asks to "find inconsistencies", "audit", or "check everything".

## Workflow

### PHASE 0: Mechanical checks (run FIRST, cheap, deterministic)

Before spawning agents, run the mechanical parity checks. These are cheaper and more precise than agent prompts for the classes of bug they cover.

```bash
# Skill/rule/agent surface integrity (if present — planned sibling tool)
python3 scripts/check-skill-integrity.py --verbose 2>/dev/null || echo "check-skill-integrity.py not present; skipping mechanical surface check"

# Bibliography integrity (every cited key resolves; no orphan entries)
# (run /validate-bib — structural citation check)
```

`check-skill-integrity.py` (when present) catches classes of bug that agent-based audits historically miss:

1. Frontmatter `allowed-tools` ↔ body tool-invocation parity (e.g. body spawns `Task` but `Task` is not in `allowed-tools`).
2. `argument-hint` ↔ body flag parity (flags documented but not advertised, or vice versa).
3. Internal markdown anchors resolve (no broken `[text](path#anchor)` links).
4. Rule `paths:` ↔ skill implementation parity (a rule claims a skill follows a protocol but the skill body has none of the protocol keywords).

If Phase 0 reports findings, fix them (or tune the regex if they are false positives) **before** launching the agents.

### PHASE 1: Launch parallel audit agents

Launch these agents simultaneously using `Task`. Each agent's prompt **must** tell it to read [`.claude/references/audit-pet-peeves.md`](../../references/audit-pet-peeves.md) (a living catalogue of drift patterns) and explicitly check each class before reporting clean.

#### Agent 1: Manuscript factual + claim accuracy  — `subagent_type=claim-verifier` (forked) + `domain-referee`
Focus: `manuscript/main.tex` (resolve `\input{}`/`\include{}`), `output/tables/*.tex`, the abstract and intro.
- Every numeric claim in the prose traces to a source artifact (a regression `.log` in `output/logs/`, a `.tex` in `output/tables/`, a `.ster`, or the `.dta`/`.csv` it was computed from). A reported coefficient / t-stat / N that does not match the artifact is a finding. Run this via a forked `claim-verifier` (CoVe — it never sees the draft's framing).
- Every citation holds the claim attributed to it (not just exists). Mis-attribution is CRITICAL.
- Table/figure numbers referenced in text exist and say what the text claims (`Table 3 shows X` — does it?).
- The contribution stated in the abstract matches what the results deliver — route the contribution-level read to `domain-referee` (substantive lens).
- Notation consistency: a symbol defined in §2 still means that in §5.

#### Agent 2: Executable code quality — `subagent_type=code-reviewer`
Focus: **all** executable analysis code — `code/**/*.do`, `code/**/*.py`, `code/**/*.sas`, `scripts/*.py`, `scripts/*.sh`, `.claude/hooks/*.py`, `.claude/hooks/*.sh`.
Analysis-code checks (Stata/Python/SAS):
- No hardcoded absolute paths (Stata via `$root`/`00_run.do` globals; Python via `pathlib.Path` relative to project root; SAS via libname/`%let`).
- `params.do` is the single source of research parameters — no magic numbers redefined downstream.
- Look-ahead / point-in-time discipline in the data construction (no fiscal-year-end data leaking into earlier-month returns).
- Merge keys are correct and stable (e.g. cross-build merges keyed on a STRING id × date, never a build-specific numeric `egen group` id).
- Winsorization / sample-filter order is correct (treatment/rank measures constructed AFTER merges and control filters, not before — pre-merge construction inflates rates via sample selection).
- Every script writes a log; the log is checked, not assumed (a SAS job's results may be in `.lst` while the `.log` looks clean).
Hook-specific checks (`.claude/hooks/` only): fail-open pattern where the docstring promises it (top-level `try/except` with `sys.exit(0)`; `read_text()` catches `UnicodeError`, not just `OSError`); JSON hook contract (stdin in; stdout/stderr out); correct exit codes (blocking hooks use exit 2 + stderr, or exit 0 + JSON `{"decision":"block","reason":...}`; PreCompact must exit 0); `from __future__ import annotations` for older-Python compatibility; correct hook-input field names (`source` not `type` for SessionStart).
- **Docstring-claim ↔ implementation parity** across all code: if a docstring promises "fail-open" / "bidirectional" / "exits 1 on X", the implementation must match.
- **Config-map entries point at live targets**: path maps, rule registries, and keyword dicts should not contain dead entries.

#### Agent 3: Skills / rules / agents consistency — `subagent_type=general-purpose`
Focus: `.claude/skills/*/SKILL.md`, `.claude/rules/*.md`, `.claude/agents/*.md`.
- Valid YAML frontmatter in all files; no stale `disable-model-invocation: true`; sensible `allowed-tools`.
- **`allowed-tools` covers every tool the body invokes.** For every `Task` spawn, `Bash` command, `Write`/`Edit` call mentioned in the body, verify the tool appears in `allowed-tools`. Common miss: body says "spawn agent-X via `Task`" but `Task` is absent.
- **Rule `paths:` scope matches skill implementation.** If rule X lists skill Y in `paths:`, verify Y actually implements the protocol X mandates.
- Rule `paths:` reference existing directories; no contradictions between rules.
- `CLAUDE.md` skills table matches the actual `.claude/skills/` directories 1:1; the agent/rule counts in `CLAUDE.md`/`README.md` match disk.
- All templates referenced in rules / skills exist in `templates/`.

#### Agent 4: Cross-document consistency + design soundness — `subagent_type=general-purpose` + `methods-referee`
Focus (index/landing docs): `README.md`, `CLAUDE.md`, `pipeline.md`, `MEMORY.md`, `CHANGELOG.md`.
- All feature counts (skills / agents / rules / hooks) agree across `README.md` and `CLAUDE.md`.
- The directory tree in `CLAUDE.md`/`README.md` matches the actual structure.
- `pipeline.md` step order + file dependencies match `code/00_run.do` / `run_all.sh` and the scripts on disk; the table/figure manifest matches `output/`.
- No stale counts from previous versions; license/citation sections match `LICENSE`/`CITATION.cff` if present.
- Route a design-soundness read of the manuscript's method section to `methods-referee` (paper-type-aware: is the identification / factor model / SE clustering defensible?). Its blockers feed the triage.

### PHASE 2: Triage Findings

Categorize each finding:
- **Genuine bug**: fix immediately (if mechanical) or escalate to the user (if substantive).
- **False alarm**: discard (document WHY it's false for future rounds).

Common false alarms to watch for:
- `allowed-tools` linter warning — known linter quirk; the field IS valid.
- Counts in old session logs (`quality_reports/session_logs/`) — historical records, not user-facing docs.
- Counts in `CHANGELOG.md` under past version headings — snapshots; do NOT update.
- A licensed-vendor number (CRSP/Compustat/IBES) the verifier flags `cannot-verify` — LOW-WARN, not a bug; the verifier just can't re-pull the licensed source.
- A numeric mismatch with a recorded `author_alternative` (different defensible specification/sample) — EXPLAINED, non-gating.

**Count drift specifically: search every phrasing variant.** A common failure mode is that `replace_all` on one phrasing (e.g., `"26 skills"`) misses sibling phrasings. When checking counts, grep for ALL of:
- `"N skills"`, `"N skill "` (with space)
- `"N slash commands"`, `"N specialized"` (as in "N specialized agents")
- Commas/conjunctions: `"skills,"` vs `"skills, and"` are different strings to `replace_all`
Verify zero matches for the OLD number across the whole tree before declaring clean.

### PHASE 3: Fix All Issues

Apply mechanical fixes in parallel where possible. For each fix:
1. Read the file first (required by Edit tool).
2. Apply the fix.
3. Verify the fix (grep for stale values, check syntax).

**Substantive findings** (an identification concern, a sign that disagrees with theory, a fragile result) are NOT auto-fixed — collect them for the user. This skill never edits empirical results, specifications, or research claims.

### PHASE 4: Re-verify reported numbers if the pipeline changed

If any script under `code/` was modified in the fix phase, the numbers it produces may have moved. Re-run the affected step via `./run_all.sh "<script>"`, read the log, and re-check the manuscript claims that depend on it before declaring clean. Do not declare a numeric audit clean off stale logs.

### PHASE 5: Loop-until-dry (two consecutive dry rounds)

After fixing, launch a fresh set of audit agents to verify. This is the **loop-until-dry** primitive ([`orchestrator-protocol.md`](../../rules/orchestrator-protocol.md)):
- A round is **dry** when it surfaces **0 new genuine issues** (deduped on file+issue).
- **Converge after two consecutive dry rounds** — a second clean pass confirms the first wasn't a fluke. Declare clean and report the summary.
- If new issues are found → fix (mechanical) or escalate (substantive) and loop again.
- **Fallback cap: 5 loops** bounds a non-converging audit; a finding that survives rounds N and N+2 is escalated to the user rather than re-patched ([`summary-parity.md`](../../rules/summary-parity.md)).

## Key Lessons (genericized; check these specifically)

| Bug Pattern | Where to Check | What Went Wrong |
|-------------|---------------|-----------------|
| Stale counts ("19 skills" → "21") | README, CLAUDE.md | Added skills but didn't update all mentions |
| Reported number ≠ artifact | manuscript vs `output/logs`, `output/tables` | Prose edited but the table/log wasn't re-pulled |
| Mis-attributed citation | manuscript vs the cited PDF | Cited the right author, wrong claim/direction |
| Build-specific numeric id in a cross-build merge | `code/**/*.do` | `egen group` id differs per build → wrong-firm merge |
| Pre-merge treatment construction | `code/**/*.do` | Rank/treatment built before control filters → inflated rate |
| SAS results in `.lst`, `.log` looks clean | `output/logs`, WRDS jobs | Trusted the `.log`; the real output/errors were in `.lst` |
| Hook exit codes | `.claude/hooks/*.py` | Exit 2 in PreCompact silently discards stdout |
| Hook field names | post-compact-restore.py | SessionStart uses `source`, not `type` |
| Missing fail-open | Python hooks `__main__` | Unhandled exception → exit 1 → confusing behavior |
| Missing directories | `quality_reports/specs/` | Referenced in rules but never created |
| Stale tool/skill references | rules, CLAUDE.md, CHANGELOG, settings.json | Removed item still mentioned somewhere |

## Output Format

After each round, report:

```
## Round N Audit Results

### Issues Found: X genuine (M mechanical / S substantive), Y false alarms

| # | Severity | File | Issue | Status |
|---|----------|------|-------|--------|
| 1 | Critical | code/stata/04_analysis.do:142 | Description | Fixed |
| 2 | Major | manuscript/main.tex:88 | Reported t-stat ≠ main_results.tex | Escalated |

### Verification
- [ ] No stale counts (grep confirms)
- [ ] Every reported number traces to an artifact
- [ ] All hooks have fail-open + future annotations
- [ ] Affected pipeline steps re-run; logs checked

### Result: [CLEAN (2 dry rounds) | N issues remaining | S substantive escalated to user]
```

## Cross-references

- `.claude/skills/review-paper/SKILL.md` — `--peer <journal>` referee/editor simulation (lighter, single-paper).
- `.claude/skills/seven-pass-review/SKILL.md` — seven-lens manuscript review (no infrastructure audit).
- `.claude/skills/verify-claims/SKILL.md` — the forked CoVe claim check Agent 1 uses.
- `.claude/agents/{claim-verifier,domain-referee,methods-referee,editor,code-reviewer}.md` — the specialists this skill orchestrates.
- `.claude/rules/{summary-parity,orchestrator-protocol,post-flight-verification}.md` — the loop + reduce + verify discipline.
