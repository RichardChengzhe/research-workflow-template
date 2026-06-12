# Changelog

All notable changes to this research-workflow template are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project aims to follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — empirical-project lessons + Pedro v2.1 sync (2026-06-11)

Comprehensive sync that (a) folds generalizable lessons harvested from a live
empirical-finance project back into the template, and (b) ports the curated,
discipline-appropriate parts of the upstream `pedrohcgs/claude-code-my-workflow`
(v2.1) workflow — adapted from its R/Quarto/TikZ origins to this template's
Stata / Python / SAS empirical-finance stack. Teaching, R-package, Quarto,
TikZ, and R-simulation families were intentionally excluded.

### Added

- **Reproducibility machinery** — skills for building and auditing a
  replication package, capturing the compute environment, drafting a
  data-management plan, and an exhibit-level provenance "passport"
  (`templates/passport-template.yaml`) that maps each Table/Figure to its
  generator script, line/command, output file, and verification status
  (PASS / FAIL / EXPLAINED / STALE).
- **Causal-inference support** — a DiD / event-study skill (Stata-first:
  `csdid` / `eventstudyinteract` / `honestdid`), DiD conventions, an
  inference-robustness rule, and a power-analysis skill.
- **Claim verification** — a `claim-verifier` agent, a `/verify-claims`
  skill, a claim-reconcile hook, and the supporting content-invariants /
  cross-artifact-review / summary-parity rules.
- **Referee & revision** — a response-to-referees template and skill, a
  journal-profile template + a finance/accounting/econ `journal-profiles`
  reference, and `domain-referee` / `methods-referee` / `editor` agents that
  drive a simulated peer-review pass.
- **Submission & ethics** — submission-disclosure and disclosure-check
  skills and a confidential-data rule for restricted sources (CRSP /
  Compustat / IBES / TAQ).
- **Context, memory & autonomy** — promote-memory (with a council agent),
  compress-session, checkpoint, and diagnose skills.
- **Authoring** — a humanize skill + auditor, academic-writing / referee
  output styles, and prompt-shaping / prompt-formatting references.
- **Report library** — a reusable HTML report module + `build-report` skill +
  builder template, with clickable heatmap→table anchors and a build-time
  bidirectional link verifier; report-conventions rule.
- **Manuscript / Overleaf** — an Overleaf-as-git-repo protocol, a generic
  booktabs/threeparttable regression-table template, and a brace-matched red
  change-mark stripper.
- **Reference library** — a new `.claude/references/` directory (agent-fleet,
  orchestration-schemas, journal-profiles, audit-pet-peeves, discipline-cards,
  prompt-formatting-core, a slimmed model-versions).
- **Templates** — journal-profile, decision-record (ADR), response-to-referees,
  passport (exhibit/claims provenance), and preregistration (OSF / AsPredicted /
  AEA RCT, with MDE) templates.
- **Tooling scripts** — `check-skill-integrity.py` (per-SKILL.md frontmatter,
  tool/flag/anchor/rule parity), `check-surface-sync.py` + `.sh` (count and
  enumerative-table consistency across CLAUDE.md / README.md /
  WORKFLOW_QUICK_REF), `install-hooks.sh`, and a stack-adapted
  `validate-setup.sh`.
- **Git safety** — a version-controlled `.githooks/pre-commit` gate
  (surface-sync + skill-integrity + quality score on staged files) and a
  git-guardrails hook.
- **Empirical-project lessons (generalized)** — worktree-parallel-exploration and
  remote-jobs rules; a project-level Cypress HPC skill and a worktree-probe
  scaffold; new `[LEARN]` entries (cross-build string-id merges, post-merge
  measure construction, retrieval-ladder-before-dead, Stata/SAS Windows
  pitfalls) added to MEMORY.md.

### Changed

- **`scripts/quality_score.py`** — merged in a **could-not-verify** state: a
  missing or timed-out external tool is now a distinct "skipped" note (it no
  longer zeroes the score), while a tool that runs and reports a real failure
  still fails. Added an optional `latexmk` compile check for `.tex` and an
  optional interpreter syntax double-check for `.py` (both governed by tunable
  timeout env knobs), plus a static `.sas` rubric. The single-file CLI and
  exit-code behavior (<80 blocks) are preserved.
- **Orchestration** — the orchestrator-protocol gains a runtime loop
  (fan-out → reduce → judge → hallucination-gate → loop-until-dry) while
  keeping the template's file-type critic-fixer routing.
- **Verification / replication / quality-gates rules** — adopted the
  `EXPLAINED` disposition and a post-flight verification stage; kept the
  Stata/SAS-specific rubric content.
- **Hooks** — context-monitor / log-reminder / pre-compact / post-compact
  hooks updated to the upstream JSON hook contract and a token-based context
  estimate.
- **Style guide** — `manuscript/aea_style_guide.md` corrected to t-statistics
  (not standard errors) in parentheses, with real table conventions added.
- **Existing agents** (proofreader, domain-reviewer, verifier) — merged in
  upstream improvements without dropping template-specific behavior.
- **`.gitignore`** — ignore generated report artifacts (`output/*.html`,
  `output/**/*Report*.html`, `*_report_lib_smoke.html`).

### Notes

- Upstream features ported from `pedrohcgs/claude-code-my-workflow` (v2.1)
  were **adapted** to Stata / Python / SAS empirical finance; the disposition
  vocabulary, schemas, and surface-sync tooling are reused, but examples,
  paths, and tool invocations were rewritten for this stack. Excluded
  families: teaching, R-package development, Quarto, TikZ, R-simulation, CI
  workflows, and scheduled-autonomy infrastructure.
- The surface-sync and skill-integrity gates **dynamically count what is on
  disk**. Until the count/index surfaces (CLAUDE.md, README.md,
  WORKFLOW_QUICK_REF) are reconciled to match, `check-surface-sync.py` will
  legitimately report drift — that is the intended signal, not a regression.
- **Final on-disk inventory at sync close:** 52 skills, 16 agents, 31 rules,
  9 hooks, 7 references, 2 output-styles, 14 templates, 7 scripts. (The
  `check-surface-sync.py` ground truth — skills/agents/rules/hooks — and
  `check-skill-integrity.py` both pass against these counts.)
