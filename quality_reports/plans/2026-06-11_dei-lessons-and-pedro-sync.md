# Plan: DEI-Lessons + Pedro v2.1 Sync into the Research Workflow Template

**Status:** APPROVED (scope + phasing confirmed 2026-06-11) — awaiting final go-ahead to execute
**Date:** 2026-06-11
**Branch:** `feat/dei-lessons-pedro-sync-2026-06` (template repo, off `master`)
**Driven by:** Chengzhe Li. Source projects read this session: DEI Sentiment project (`E:`), Claude memory files (`C:\...\memory`), Pedro `pedrohcgs/claude-code-my-workflow` (GitHub API).

## Hard constraints

- **WRITE ONLY to the template repo** (`F:\Personal Dropbox\Dropbox (Personal)\ResearchWorkFlowTemplate`). The DEI project folder (`E:\...\DEI Sentiment`) is **READ-ONLY** — extract lessons by reading; never create/edit/delete anything there.
- Template repo is its own GitHub repo (`RichardChengzhe/research-workflow-template`); default branch `master`.
- Generic template: strip all project-specific facts (washer/husher, v11/v12, t-stats, panel md5s, DEI specifics). Keep only generalizable workflow/tooling/methodology lessons.
- Every subagent implementer = Opus; audit each with a separate Opus reading literal file bytes.

## Provenance of "what each Pedro feature does"

VERIFIED this session from Pedro's own `CHANGELOG.md` + `.claude/WORKFLOW_QUICK_REF.md` (fetched via GitHub API) and his file tree. Not from memory.

---

## Scope decisions (locked)

**Comprehensive sync, all four workstreams, ONE pass on one branch, combined review + commit.**

### Pedro adoption — INCLUDE (adapt R/Quarto-isms to Stata/Python/SAS)
- **Reproducibility producer:** `/replication-package`, `/capture-environment`, `/audit-reproducibility`, `/data-management-plan`, `passport-template.yaml`
- **DiD / causal:** `/did-event-study` (Stata-first: csdid/eventstudyinteract/honestdid), `did-conventions`, `inference-robustness`, `/power-analysis`
- **Claim verification:** `/verify-claims` + `claim-verifier` agent + `claim-reconcile.py` hook; `content-invariants`, `cross-artifact-review`, `summary-parity` rules
- **Referee / revision:** `/respond-to-referees` + template, `/review-paper --variance`, `/seven-pass-review`, `/deep-audit`, `domain-referee` + `methods-referee` + `editor` agents, `journal-profiles` ref + template
- **Submission / ethics:** `/submission-disclosures`, `/disclosure-check`, `confidential-data` rule
- **Context / memory / autonomy:** `/promote-memory` + `promote-memory-council` agent, `/compress-session`, `/checkpoint`, `/diagnose`
- **Orchestration + git safety:** orchestrator-protocol runtime upgrade, `agent-fleet` + `orchestration-schemas` refs, `install-hooks.sh` + `.githooks/pre-commit`, `git-guardrails.py`, `post-flight-verification` rule
- **Model routing:** `model-routing` rule + **slimmed** `model-versions` (no Fable-5-verbatim; keep Opus/Sonnet/Haiku tiers + the drift-gate idea)
- **Authoring:** `/humanize` + `humanize-auditor`, output-styles `academic-writing` + `referee`, `prompt-shaping` rule, `prompt-formatting-core` ref
- **Misc:** `/coauthor-brief`, `/new-skill`, `/visual-audit`, `/preregister` + template, `decision-record` template, `/permission-check`
- **Slides/Beamer (KEPT per user):** `/slide-excellence`, `slide-auditor` agent, `beamer-translator` agent, `no-pause-beamer` rule
- **Grant (KEPT per user):** `/grant-proposal`, `/data-management-plan`
- **Meta:** `meta-governance` + `knowledge-base-template` rules; `CHANGELOG.md` (keep-a-changelog for the template)

### Pedro adoption — EXCLUDE / DEFER
- **Teaching:** `/syllabus`, `/teach-from-paper`, `/scaffold-exercises`, `/respond-to-eval`, `/create-lecture`, `/pedagogy-review`, `pedagogy-reviewer`
- **R-package dev:** `/r-package-check`, `/review-r`, `r-reviewer`, `r-package-reviewer`, `r-code-conventions`, `r-package-conventions`, `scripts/R/*`
- **Quarto:** `/qa-quarto`, `/translate-to-quarto`, `quarto-critic`, `quarto-fixer`, `beamer-quarto-sync`, `Quarto/`, `guide/*.qmd`
- **TikZ:** `/extract-tikz`, `/new-diagram`, `tikz-reviewer`, `tikz-*` rules, `tikz-snippets/`, `check-tikz`/`check-palette`
- **Simulation (R):** `/simulation-study`, `simulation-conventions`, `sim-reviewer` (keep one MCSE line in `inference-robustness` only)
- **Autonomy infra:** `scheduled-routines`, `nightly-repro-check.sh`, `/triage-inbox`
- **CI:** `gates.yml`, `deploy.yml` (adapt-later; local pre-commit hook covers the gate)

---

## WS1 — DEI project's generalizable lessons (~5 weeks since last sync)

Source: `C:\...\memory\feedback_*.md` + `reference_*.md` (full text saved to a tool-results file this session) + recent session logs. Generic phrasing only.

**MODIFY `MEMORY.md`** — add categorized `[LEARN]` entries:
- `[LEARN:worktree]` location `E:/worktrees/<tail>`; write INTO the worktree (absolute main-project paths land on the wrong branch); copy gitignored creds; junction + hard-link to wire gitignored data; ceteris-paribus probe → cherry-pick winners.
- `[LEARN:data]` numeric `egen group` id is build-specific → key cross-build merges on STRING id × date, never the numeric id; construct rank/treatment/"washer"-type measures AFTER all merges + control filters (pre-merge construction inflates rates via sample-selection bias).
- `[LEARN:wrds]` CRSP-v2/CIZ reaches 2025 vs legacy 2024 cutoff; `qhold` to promote a critical-path job; `stocknames` refresh-lag → bail-out guards on empty sets; plink/pscp + Duo-per-day; `/scratch` default for intermediates.
- `[LEARN:stata]` Git-Bash needs `MSYS_NO_PATHCONV=1` + `cygpath -w`; use `-e` not `-b`; end `.do` with `exit, clear STATA` to kill the completion modal.
- `[LEARN:execution]` poll >10-min WRDS/Cypress/batch jobs via `/loop` or cron; download outputs before remote cleanup.
- `[LEARN:research]` verify new DV/IV/measure against published lit + source docs BEFORE coding; retrieval ladder before declaring a cited resource dead (WebFetch → Wayback → Playwright → mirrors → author); audit subagent work with a separate Opus reading literal bytes.
- `[LEARN:cypress]` Stata-MP needs reghdfe+ftools+estout+moremata+**require**; 8-core cap → speed via MORE array tasks; SLURM array + SAMPLE env split.

**CREATE `.claude/rules/worktree-parallel-exploration.md`** — the probe methodology (worktree location, data junction/hard-link wiring, write-into-worktree discipline, branch + cherry-pick).
**CREATE `.claude/rules/remote-jobs.md`** — poll/monitor long remote jobs; download before cleanup; cron/loop patterns.
**MODIFY `.claude/skills/sas/SKILL.md`** — CIZ-2025 vs legacy cutoff, `qhold`, `stocknames` lag guards, `/scratch` default.
**MODIFY `.claude/skills/stata-execution/SKILL.md`** — `-e` flag, MSYS/cygpath, `exit, clear STATA`.
**CREATE `.claude/skills/cypress/SKILL.md`** — project-level Cypress HPC (SLURM array decomposition, Stata-MP setup).
**CREATE `.claude/skills/worktree-probe/SKILL.md`** — scaffold a ceteris-paribus probe (worktree + data symlink + branch).
**MODIFY `CLAUDE.md`** — new anti-patterns (numeric-gvkey cross-build merge; pre-merge measure construction; trusting WebFetch-dead; trusting a SAS .log when results are in `.lst`).

## WS2 — Manuscript & Overleaf machinery

**MODIFY `manuscript/aea_style_guide.md`** — fix **SE → t-statistics in parentheses**; add real conventions: `threeparttable` notes, full-width `tabular*{\textwidth}{@{\extracolsep{\fill}}...}`, `1{,}234` number format, `\textit{Notes:}` block, Δ/× notation, FE + N + adj-R² rows, variable-definitions appendix, `\fontsize{10}{12}` table body.
**CREATE `manuscript/CLAUDE.md`** — generalized **Overleaf-as-git-repo protocol**: pull-first before any `.tex` edit; never auto-push; never `git add -A` / stage unedited files; red `\textcolor{red}{}` + `\sout{}` change-marking; table ↔ reference-output sync via a `RESULTS_PROVENANCE.md`; don't compile locally; review-by-severity protocol; never modify `.sty`.
**CREATE `templates/manuscript-table-template.tex`** — generic booktabs/threeparttable regression table (focal terms → Controls block → N/adj-R², t-stats in parens, notes).
**CREATE `scripts/strip_redmarks.py`** — brace-matched (depth-count) `\textcolor{red}{...}` stripper + `\sout{}` remover; NOT regex (handles nested `$^{**}$`/`\citet{}`); occurrence-count verify.
**CREATE `.claude/rules/manuscript-overleaf-sync.md`** — the manuscript git/change-marking/reference-output-sync rule (reconcile with Pedro `content-invariants` + `cross-artifact-review` + `summary-parity` + passport).

## WS3 — Canonical HTML report (module + skill + template)

**CREATE `code/python/report_lib.py`** — reusable helpers with embedded CSS mirroring the manuscript look:
- `heat_grid()`, `hcell()` (sign×significance color: pos1/2/3, neg1/2/3, ns, fail), `aea_table()`/`make_table()` (coef + (t) two-line cells, focal-shaded `hi=True`, Controls block, N + adj-R² sep rows), `finding_box()`, `model_box()`.
- Clickable heatmap → full-table anchors (`_anchor_id()`), `:target` highlight, and a **bidirectional link verifier** (zero broken / zero orphan) run at build.
- CSS: serif body, booktabs-style horizontal rules, `.aea`/`.heat`/`.heat-grid`/`.aea-grid` (CSS grid auto-fit), dual-cluster `(t)`/`[t]` cells, `&Delta;`/`&times;`/`&minus;` entities, provenance footer.
**CREATE `.claude/skills/build-report/SKILL.md`** — structure (exec summary → TOC → variable defs → heatmaps → model → full AEA tables → reading guide → caveats/provenance), versioned `vN`, fail-cell audit (`grep class="fail"`), clickable-heatmap requirement.
**CREATE `templates/report-builder-template.py`** — minimal reference builder importing `report_lib`.
**CREATE `.claude/rules/report-conventions.md`** — one manuscript-spec main column + Controls + consolidated robustness; full tables for ALL tests; t-stats (not SE); Δ-labels; each major revision = new `vN`; clickable heatmaps when both heatmaps + full tables present.

## WS4 — Pedro v2.1 port (curated above, adapted)

For each INCLUDED Pedro file: fetch via GitHub API, adapt R/Quarto/TikZ-isms to Stata/Python/SAS, place at the mirrored path. For SHARED files already in the template, **MERGE** (preserve template's Stata/Python/SAS specifics + adopt Pedro's improvements) — do not blind-overwrite:
- `.claude/rules/orchestrator-protocol.md` — upgrade pattern → runtime (fan-out→reduce→judge→hallucination-gate→loop-until-dry); keep template's file-type critic-fixer routing.
- `.claude/rules/{replication,verification,quality-gates}.md` — adopt Pedro's `EXPLAINED` disposition + post-flight verification; keep SAS/Stata rubric bits.
- `.claude/hooks/{context-monitor,log-reminder,pre-compact,post-compact-restore}.py` — adopt Pedro's v1.10 fixes (JSON hook contract not raw ANSI; token-based context estimate; auto-writing log).
- `scripts/quality_score.py` — adopt Pedro's could-not-verify state; keep template's checks.
- Agents already present (proofreader, domain-reviewer, verifier) — merge Pedro improvements.
- NEW agents: claim-verifier, domain-referee, methods-referee, editor, humanize-auditor, promote-memory-council, slide-auditor, beamer-translator.
- NEW rules: did-conventions, inference-robustness, confidential-data, content-invariants, cross-artifact-review, summary-parity, model-routing, post-flight-verification, prompt-shaping, meta-governance, knowledge-base-template, orchestrator-research, no-pause-beamer.
- NEW skills: replication-package, capture-environment, audit-reproducibility, data-management-plan, did-event-study, power-analysis, verify-claims, respond-to-referees, seven-pass-review, deep-audit, submission-disclosures, disclosure-check, promote-memory, compress-session, checkpoint, diagnose, coauthor-brief, new-skill, visual-audit, preregister, humanize, slide-excellence, grant-proposal, permission-check. (Upgrade existing review-paper with `--variance`.)
- NEW references dir `.claude/references/`: agent-fleet, orchestration-schemas, journal-profiles, audit-pet-peeves, discipline-cards, prompt-formatting-core, model-versions (slim).
- NEW output-styles `.claude/output-styles/`: academic-writing, referee.
- NEW hooks: git-guardrails.py, claim-reconcile.py; `.githooks/pre-commit` + `scripts/install-hooks.sh`.
- NEW templates: journal-profile-template, decision-record, response-to-referees, passport-template.yaml, preregistration-template.
- NEW scripts: check-skill-integrity.py, check-surface-sync.py/.sh, install-hooks.sh, validate-setup.sh.
- NEW top-level: CHANGELOG.md (template's own), TROUBLESHOOTING.md (optional), CITATION.cff (optional), `.github/` community files (optional).

## Surface reconciliation (do last)

Update count/index surfaces so they match disk:
- `CLAUDE.md` skills table + anti-patterns + folder structure
- `README.md` agent/skill/rule counts + new sections
- `.claude/WORKFLOW_QUICK_REF.md`
- `MEMORY.md` (new categories)
- `CHANGELOG.md` entry for this sync

## Execution approach (one pass)

1. Operate on `feat/dei-lessons-pedro-sync-2026-06` in the template repo only.
2. Dispatch parallel Opus subagents by independent work unit (WS1-lessons, WS2-manuscript, WS3-report, WS4a-rules+orchestration, WS4b-skills, WS4c-agents+hooks, WS4d-references+templates+scripts). Each subagent fetches needed Pedro files via GitHub API and writes to mirrored template paths.
3. Audit each unit with a separate Opus reading literal file bytes (per standing rule): generic-phrasing check, no excluded-family leakage, R/Quarto/TikZ-ism adaptation, merge-not-overwrite on shared files.
4. Reconcile surfaces + run `check-surface-sync` / `check-skill-integrity` / `validate-setup`.
5. Final combined review (code-reviewer on new .py/.sh; output/manuscript critics where relevant), fix mechanical issues.
6. Commit to the branch with a descriptive message + a session log in the template's `quality_reports/session_logs/`. Leave the push to the user.

## Verification checklist

- [ ] No writes outside the template repo (`F:`); DEI folder untouched.
- [ ] No excluded family (teaching/R-package/Quarto/TikZ/simulation/triage/CI) present on disk.
- [ ] Slides (kept) + grant (kept) present.
- [ ] Shared files merged, not blind-overwritten (template's SAS/Stata specifics preserved).
- [ ] `report_lib.py` imports + a smoke build produces an HTML with zero broken/orphan anchors.
- [ ] `strip_redmarks.py` round-trips a nested-brace sample.
- [ ] Surface counts in CLAUDE.md/README/QUICK_REF match disk.
- [ ] All new SKILL.md pass skill-integrity.
- [ ] Generic phrasing — no DEI/washer/v12 leakage.
