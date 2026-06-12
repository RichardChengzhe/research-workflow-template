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
- [LEARN:stata] Git-Bash -> Stata needs BOTH `MSYS_NO_PATHCONV=1` AND `cygpath -w` on pwd-derived paths (silent r(601) otherwise). Use `-e` (not `-b`) for Windows batch. End every `.do` with `exit, clear STATA`.
- [LEARN:hpc] Stata-MP on a cluster needs reghdfe+ftools+estout+moremata+`require` — reghdfe silently no-ops without `require`.

## SAS / WRDS

- [LEARN:sas] Heavy WRDS jobs (TAQ pulls, long CTM loops, large rsubmit bodies > ~100 lines) must use SSH + `qsas`, not `rsubmit`. SAS/CONNECT deadlocks on TBUFSIZE buffer exhaustion when the rsubmit body is large.
- [LEARN:wrds] First WRDS connection of the day requires Duo 2FA push approval on phone. Subsequent connections same day skip Duo.
- [LEARN:wrds] WRDS exit 112 + 0s wallclock + no log = SAS kernel init failure on a bad compute node. Resubmit with `qsub -l h=!nodename.wharton.private` to exclude the broken host. SGE retry alone doesn't help (it re-runs on the same node).
- [LEARN:wrds] WRDS `proc upload`/`proc download` MUST be inside an `rsubmit`/`endrsubmit` block. Outside, they fail silently with a misleading error.
- [LEARN:wrds] Tilde (`~`) does not always expand inside SAS code. Prefer absolute paths like `/home/INSTITUTION/username/...` for WRDS file output.
- [LEARN:sas] `code/sas/sas_retry_wrapper.sh` retries SAS on exit 112 with 60s backoff (up to 3 attempts). Upload to WRDS home once, reuse across jobs.
- [LEARN:wrds] Modern CRSP v2 / CIZ can reach a later year than legacy CRSP/TAQ link tables — check max(date) on BOTH before choosing. Some WRDS results land in `.lst`, not `.log`.
- [LEARN:wrds] `qhold`/`qrls` promotes a critical-path job past your own queued jobs. A refresh-lagged metadata table (e.g. stocknames) can lag "today"; a `>= current_year` filter then silently returns 0 rows — guard with `>= year-1` + a bail-out.

## Anti-Patterns (avoid these)

- [LEARN:antipattern] Hardcoded absolute paths inside individual scripts. Always use globals (`$root` / `$data`) defined once in `00_run.do`.
- [LEARN:antipattern] Trusting a coauthor's "this works on my machine." Verify by running `./run_all.sh --all` end-to-end before claiming reproducibility.
- [LEARN:antipattern] Editing a script without tracing its downstream consumers in `pipeline.md`. Use `/check` first.
- [LEARN:antipattern] Committing `autoexec.sas`, `.env`, or anything with real credentials. Confirm `.gitignore` covers them and `git status` does not list them.

## Skill Creation

- [LEARN:skills] Trigger phrases matter in skill descriptions -- include specific scenarios when skill applies.
- [LEARN:skills] Skills need Instructions + Examples + Troubleshooting to be useful.

## Git Worktrees & Parallel Exploration
- [LEARN:worktree] Ceteris-paribus exploration on isolated git worktrees: put worktrees in a dedicated sibling dir (e.g. `<drive>:/worktrees/<repo>-<branch>`), NEVER inside a cloud-synced (Dropbox/OneDrive) repo root. Always write INTO the worktree's own path — absolute main-repo paths silently land on the wrong branch. Copy gitignored creds (autoexec.sas/.env) into the worktree; wire large gitignored data via an OS junction + hard-link (no GB duplication). One isolated change per worktree+branch; cherry-pick winners. See rules/worktree-parallel-exploration.md + skill worktree-probe.

## Remote / Long-Running Jobs
- [LEARN:remote] HPC/WRDS/batch jobs > ~10 min: never passively wait — poll via a self-paced loop or cron, download outputs before remote scratch cleanup. Under a per-job core cap, wall-time comes from MORE array tasks, not more cores/task. See rules/remote-jobs.md + skill cypress.

## Data / Merge Discipline
- [LEARN:data] A numeric `egen group` id is assigned per build — the SAME id denotes DIFFERENT entities across two builds. Key cross-build merges on the STRING identifier x date, never the numeric group id.
- [LEARN:data] Construct rank / treatment / dummy measures AFTER all merges and control filters. Building on a broader population then dropping rows inflates group rates via sample-selection bias.

## Research-Design Discipline
- [LEARN:research] Verify a new DV/IV/measure against the published source + data docs BEFORE writing code — do not draft specifications from memory (training data is stale; citations drift).
- [LEARN:research] Don't declare a cited resource dead on one failed fetch — run the retrieval ladder (direct -> Wayback -> headless browser -> mirrors -> author) first.
- [LEARN:subagents] Always audit an implementer subagent with a SEPARATE model reading literal file bytes and RUNNING verification commands — never trust the implementer's self-summary.

<!-- Add project-specific learnings below as you work -->
