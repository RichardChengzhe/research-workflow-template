---
name: capture-environment
description: Snapshot the computational environment for a replication package — detects the analysis stack (Stata / Python / SAS) and emits the right artifacts (Stata version + ado/plus package list, Python requirements.txt / environment.yml / uv.lock + python --version, SAS version + WRDS macro inventory), records seeds and RNG, optionally writes a pinning Dockerfile for the Python layer, and produces a paste-ready "Computational requirements" block. Use when user says "capture the environment", "snapshot my dependencies", "pin the versions", "make a requirements.txt", "make this reproducible", or before releasing a replication package to openICPSR / the AEA Data Editor.
argument-hint: "[project-dir] [--docker] [--no-verify] (project-dir defaults to repo root)"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash"]
effort: medium
---

# `/capture-environment` — snapshot the computational environment

A replication package that runs on the author's laptop in 2026 and nowhere else in 2029 is not reproducible. This skill captures the *exact* computational environment — language versions, package/ado versions, seeds, RNG kind, and (optionally) the OS layer — so a referee, the AEA Data Editor, or future-you can reconstruct it. It detects which stack the project uses and emits the artifacts that stack's ecosystem expects, then verifies the lockfile installs clean where possible.

**Core principle:** Pin everything a result depends on. Display rounding aside, a re-run on a pinned environment should reproduce the paper to the [`replication-protocol.md`](../../rules/replication-protocol.md) tolerances — *byte-identical* on the Python layer when the optional Dockerfile is used.

## When to use

- **Before releasing a replication package** to openICPSR, Zenodo, Dataverse, or a journal archive — the AEA Data Editor / DCAS standard expects a documented, version-pinned environment.
- **Before submission**, alongside [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) — that skill checks the *numbers*; this one captures the *environment* those numbers were produced in (its `sessionInfo.txt` requirement is satisfied by this skill).
- **After adding or upgrading a package** mid-project — re-snapshot so the lockfile doesn't drift from what the code actually loads.
- **When handing a project to a co-author or RA** who needs to reconstruct your stack ([`/coauthor-brief`](../coauthor-brief/SKILL.md) carries this snapshot).

## Inputs

- `$0` — project directory. Defaults to the repo root. The skill looks under `code/stata/`, `code/python/`, `code/sas/`.
- `--docker` — also emit a `Dockerfile` pinning OS + Python version + system libraries (Python layer only; Stata/SAS are licensed and not redistributable).
- `--no-verify` — skip Phase 3 (the best-effort clean-install check). Useful in CI or when the toolchain isn't installed locally.

## Workflow

### Phase 0: Detect the stack

Glob for stack signals and decide which capture paths to run (a project is usually multi-language here — SAS/WRDS extract → Stata estimation → Python figures):

| Signal | Stack | Capture path |
|---|---|---|
| `code/stata/*.do`, `00_run.do`, `params.do` | **Stata** | version + ado list |
| `code/python/*.py`, `*.ipynb`, `pyproject.toml`, `requirements.txt`, `environment.yml`, `uv.lock` | **Python** | pip / conda / uv |
| `code/sas/*.sas`, `autoexec.sas` | **SAS** | version + WRDS macro inventory |

If no signal is found, report and stop — there is no environment to capture.

### Phase 1: Capture per language

**Stata** — Stata has no lockfile, so capture the closest equivalents (mirrors [`replication-protocol.md`](../../rules/replication-protocol.md) "Environment pinning"):
- The pinned `version` line each `.do` declares (e.g. `version 18`) — grep `code/stata/*.do` and report the version actually pinned. Flag any `.do` missing a `version` line.
- An ado/plus package inventory: a small `.do` that runs `which` on the user-installed commands the pipeline uses (`reghdfe`, `ftools`, `ivreg2`, `estout`/`esttab`, `rdrobust`, `csdid`, `boottest`, `rwolf`, …) plus `ado dir` and `about`, logged to `output/logs/sessionInfo.txt`. List every `ssc install` / `net install` so a replicator can rebuild the ado tree.
- A note that Stata version pinning is *semantic* (`version 18` fixes command behavior), not a binary pin — the Dockerfile cannot help here because Stata is licensed and not redistributable. Record the exact Stata version + flavor (SE/MP/IC) + update level in the report so a replicator can match it.

**Python** — emit whichever matches the project's existing tooling (do not invent a new one):
- `uv.lock` (preferred when `pyproject.toml` + `uv` present — fully-resolved, hashed, cross-platform): `uv lock` / `uv export --format requirements-txt > requirements.txt`.
- `requirements.txt` via `pip freeze` (or `python -m pip freeze`) for a venv/pip project — pin `==` exactly.
- `environment.yml` via `conda env export --no-builds` for a conda project. (This template's default is the project conda env.)
Always also record the interpreter version (`python --version`) in the report.

**SAS** — SAS has no lockfile either; capture the version and the dependency surface:
- The SAS version + maintenance level (`%put &sysvlong;` / Proc Product_Status → `output/logs/sas_version.txt`).
- The WRDS macro / autoexec inventory: which `%include`-d macros and WRDS libnames the pipeline uses, and **which steps require a live WRDS connection (Duo)** rather than a deposited extract — those steps re-pull licensed data and cannot be reproduced offline.
- Note that SAS is licensed and not containerizable; record the version + platform so a replicator can match it.

*(R is not a primary stack here. If an R-only robustness step exists — e.g. HonestDiD via the `honestdid` Stata package's R backend — snapshot it with `renv::snapshot()` → `renv.lock` and `sessionInfo()` → `output/logs/sessionInfo_R.txt` for that sub-step only.)*

### Phase 1b: Record seeds and RNG

Grep the analysis scripts for the master seed and RNG kind so the "Computational requirements" block can state them:
- **Stata**: `set seed` and `set sortseed` (sort-stability matters for any tie-broken operation; record both).
- **Python**: `numpy.random.default_rng(seed)` / `random.seed()` / framework seeds.
- **SAS**: the `seed=` argument on any `proc surveyselect` / `ranuni`-family call; a fixed seed for any bootstrap.

If the pipeline does randomized work (bootstrap, simulation, permutation/randomization inference, resampling) and **no** seed is found, surface it as a WARNING — an unseeded random result is not reproducible. The multiplier-bootstrap inference in [`did-conventions.md`](../../rules/did-conventions.md) makes this non-optional for DiD work.

### Phase 2: Dockerfile (only with `--docker`)

Emit a `Dockerfile` for the **Python layer** (the only redistributable stack here):
- `FROM python:<X.Y.Z>-slim`, `COPY requirements.txt` / `uv.lock`, `RUN pip install -r requirements.txt` (or `uv sync --frozen`), plus `apt-get install` for any system libs the packages need.
- Pin a digest where possible (`FROM image@sha256:…`) so the base image can't drift.
- **Stata / SAS** → cannot pin the licensed binary; emit a comment block documenting the expected Stata version + flavor and SAS version, and leave the install/license step to the replicator (point at the AEA's guidance on Stata images).

### Phase 3: Verify the lockfile installs clean (best-effort; skip with `--no-verify`)

Attempt a clean restore in a throwaway location and report PASS / FAIL — never overwrite the working environment:
- **Python**: `uv sync --frozen` / `pip install --dry-run -r requirements.txt` into a fresh venv.
- **Docker** (if `--docker`): `docker build` the Python image.
- **Stata / SAS**: no clean-install check possible (licensed); instead verify the `which` inventory ran without `command ... not found`, i.e. every pipeline ado/macro is actually installed.

A FAIL here means the lockfile references a package version that can't be resolved (yanked release, private remote, platform-specific wheel). Report it; do not auto-edit the lockfile.

### Phase 4: Report

Print a paste-ready block and write it to `output/computational_requirements.md`:

```markdown
## Computational requirements

**Software:** Stata 18.0 SE (update 2026-01-15); Python 3.12.3; SAS 9.4M7 (WRDS)
**OS used:** Windows 11 (x64) — Dockerfile pins python:3.12-slim for the figure layer
**Key Stata packages:** reghdfe 6.x, ftools, estout, csdid, boottest (full list in output/logs/sessionInfo.txt)
**Key Python packages:** pandas 2.x, numpy, pyarrow (full list in requirements.txt)
**Random seeds:** set seed 12345 / set sortseed 12345 (Stata); np.random.default_rng(20260609) (figures)
**WRDS dependency:** code/sas/0_pull_*.sas require a live WRDS/Duo connection (re-pull licensed data)
**Approx. runtime:** [author confirms — e.g. ~25 min, 8-core MP]
**Lockfiles in package:** requirements.txt, output/logs/sessionInfo.txt, output/logs/sas_version.txt[, Dockerfile]
```

Pre-fill software/package/seed lines from the captured artifacts; leave runtime for the author to confirm.

## Output / artifacts

| Stack | Files written |
|---|---|
| Stata | `output/logs/sessionInfo.txt` (version + ado list) |
| Python | `requirements.txt` *or* `environment.yml` *or* `uv.lock` (matching project tooling) |
| SAS | `output/logs/sas_version.txt` (version + WRDS macro inventory) |
| Any (`--docker`) | `Dockerfile` (Python layer) |
| Always | `output/computational_requirements.md` (the paste-ready block) |

## Exit behavior

- **All captures succeeded, verify PASS (or `--no-verify`):** exit 0, requirements block printed.
- **A missing-seed WARNING on a randomized pipeline:** exit 0 with the warning surfaced — reproducibility is compromised but the snapshot still wrote.
- **Verify FAIL (Python lockfile won't resolve, or a pipeline ado/macro is not installed):** exit 1, so the skill can gate a pre-release `/commit`. Report the unresolvable package; do not silently "fix" the lockfile.
- **No stack detected in Phase 0:** exit 1 with the directories searched.

## Cross-references

- [`.claude/rules/replication-protocol.md`](../../rules/replication-protocol.md) — the tolerance contract a pinned environment is meant to reproduce; its "Environment pinning (mandatory)" section is what the Stata/Python/SAS paths implement.
- [`.claude/rules/python-stata-conventions.md`](../../rules/python-stata-conventions.md) — `version`-pinning + seed + output-path conventions this skill reads.
- [`.claude/rules/confidential-data.md`](../../rules/confidential-data.md) — when raw data is restricted/licensed, the *environment* still ships even though the data does not; coordinate the README's "data availability" section with this block.
- [`.claude/skills/audit-reproducibility/SKILL.md`](../audit-reproducibility/SKILL.md) — consumes the `sessionInfo.txt` this skill produces; run it after.
- [`.claude/skills/replication-package/SKILL.md`](../replication-package/SKILL.md) — the deposit this snapshot goes into (its Phase 2 prefers this skill).
- [`.claude/skills/data-analysis/SKILL.md`](../data-analysis/SKILL.md) — the pipeline whose environment this snapshots.
- [AEA Data Editor checklist](https://aeadataeditor.github.io/) / [openICPSR](https://www.openicpsr.org/) / [DCAS](https://datacodestandard.org/) — the external standards this skill targets.

## What this skill does NOT do

- **Re-run your analysis or check your numbers.** It captures the environment; [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) verifies the manuscript's numeric claims against the outputs.
- **Package or de-identify data.** Lockfiles describe software, not data. Disclosure avoidance, de-identification, and data-availability statements are out of scope — see [`confidential-data.md`](../../rules/confidential-data.md).
- **Upgrade or "fix" your dependencies.** It records what the code currently uses. If a verify FAIL surfaces a yanked version, you decide whether to pin an alternative.
- **Pin a Stata or SAS binary.** Both are licensed and not redistributable; the skill records the exact version/flavor/update so a replicator can match it, but cannot containerize them.
