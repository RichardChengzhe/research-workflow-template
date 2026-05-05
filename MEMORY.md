# MEMORY.md -- Persistent Project Learnings

Save reusable knowledge here with `[LEARN:category]` tags.
Review before starting tasks. Keep under 200 lines.

## About This File

This is the **shared** project memory (committed to git).
Machine-specific paths and personal preferences go in `personal-memory.md` (gitignored).

---

## Workflow Patterns

- [LEARN:workflow] Requirements spec catches ambiguity, reduces rework 30-50%. Use for complex/ambiguous tasks.
- [LEARN:workflow] Spec-then-plan protocol: MUST/SHOULD/MAY with clarity status (CLEAR/ASSUMED/BLOCKED).
- [LEARN:workflow] Context survival before compression: MEMORY.md + session log + plan on disk + open questions documented.
- [LEARN:workflow] Plan-first for non-trivial tasks (>3 files, >1 hour, multi-step). Save plans to quality_reports/plans/.
- [LEARN:workflow] Pipeline tracing before modifying scripts: check upstream inputs AND downstream consumers.

## Code Standards

- [LEARN:stata] All Stata paths via globals from 00_run.do. Never hardcode absolute paths.
- [LEARN:stata] params.do holds all research parameters. Check before using hardcoded values.
- [LEARN:stata] Use reghdfe for high-dimensional FE. eststo/esttab for tables. graph export for figures.
- [LEARN:python] PEP 8 compliance. Type hints on public functions. Relative paths via pathlib.Path.
- [LEARN:python] matplotlib + seaborn for figures. pandas for data. statsmodels/linearmodels for regression.

## Quality Standards

- [LEARN:quality] 80/90/95 thresholds: commit/PR/excellence.
- [LEARN:quality] Publication figures: 300 DPI, explicit dimensions, vector (PDF) preferred.
- [LEARN:quality] Every script run produces a log in output/logs/ via run_all.sh. Always read the log.

## Execution Discipline

- [LEARN:execution] Run scripts via `./run_all.sh` -- direct invocation scatters logs to the project root with no timestamp.
- [LEARN:execution] SAS exit codes lie. A clean exit can hide `ERROR:` in the log. Always `grep -c "^ERROR" <log>` after every SAS run.
- [LEARN:execution] Stata `set more off` at the top of every .do file, or batch runs hang waiting for `--more--`.
- [LEARN:execution] Python: use the project conda env, not system Python. Hardcode the env path in `run_all.sh` so coauthors don't import the wrong packages.

## SAS / WRDS

- [LEARN:sas] Heavy WRDS jobs (TAQ pulls, long CTM loops, large rsubmit bodies > ~100 lines) must use SSH + `qsas`, not `rsubmit`. SAS/CONNECT deadlocks on TBUFSIZE buffer exhaustion when the rsubmit body is large.
- [LEARN:wrds] First WRDS connection of the day requires Duo 2FA push approval on phone. Subsequent connections same day skip Duo.
- [LEARN:wrds] WRDS exit 112 + 0s wallclock + no log = SAS kernel init failure on a bad compute node. Resubmit with `qsub -l h=!nodename.wharton.private` to exclude the broken host. SGE retry alone doesn't help (it re-runs on the same node).
- [LEARN:wrds] WRDS `proc upload`/`proc download` MUST be inside an `rsubmit`/`endrsubmit` block. Outside, they fail silently with a misleading error.
- [LEARN:wrds] Tilde (`~`) does not always expand inside SAS code. Prefer absolute paths like `/home/INSTITUTION/username/...` for WRDS file output.
- [LEARN:sas] `code/sas/sas_retry_wrapper.sh` retries SAS on exit 112 with 60s backoff (up to 3 attempts). Upload to WRDS home once, reuse across jobs.

## Anti-Patterns (avoid these)

- [LEARN:antipattern] Hardcoded absolute paths inside individual scripts. Always use globals (`$root` / `$data`) defined once in `00_run.do`.
- [LEARN:antipattern] Trusting a coauthor's "this works on my machine." Verify by running `./run_all.sh --all` end-to-end before claiming reproducibility.
- [LEARN:antipattern] Editing a script without tracing its downstream consumers in `pipeline.md`. Use `/check` first.
- [LEARN:antipattern] Committing `autoexec.sas`, `.env`, or anything with real credentials. Confirm `.gitignore` covers them and `git status` does not list them.

## Skill Creation

- [LEARN:skills] Trigger phrases matter in skill descriptions -- include specific scenarios when skill applies.
- [LEARN:skills] Skills need Instructions + Examples + Troubleshooting to be useful.

<!-- Add project-specific learnings below as you work -->
