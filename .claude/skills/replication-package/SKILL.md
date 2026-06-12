---
name: replication-package
description: Assemble a submission-ready replication package to the AEA Data and Code Availability Standard (DCAS) / openICPSR / Social Science Reproduction Platform expectations — standard replication README, dataset manifest, computational-requirements capture, a Table/Figure → script:line map, and a confidential-data deposit plan. Use when user says "build the replication package", "prepare the openICPSR deposit", "make the AEA data and code package", "DCAS compliance", "assemble the deposit for the journal", or after a paper is accepted and the journal's data editor needs the package. NOT a numeric verifier — it calls /audit-reproducibility to confirm claims reproduce before packaging.
argument-hint: "[manuscript path] [outputs-dir] (outputs-dir defaults to output/)"
allowed-tools: ["Read", "Grep", "Glob", "Write", "Bash", "Task"]
effort: high
---

# Replication Package

Produce the deposit an economist hands a journal at acceptance: a directory tree (`data/`, `code/`, `output/`, `README`) plus a DCAS compliance checklist, built to the [AEA Data and Code Availability Standard](https://datacodestandard.org/), openICPSR deposit expectations, and the [Social Science Reproduction Platform](https://www.socialsciencereproduction.org/) reproduction protocol. This skill **moves the repo from auditing reproducibility to producing the deposit** — `/audit-reproducibility` proves the numbers; this skill packages everything a third party needs to regenerate them from scratch.

**Core principle:** the package is reproducible by a stranger with the data and the README — no tacit knowledge, no "ask the author" steps. Every table and figure maps to the exact script and line that produces it.

## When to use

- **At acceptance.** The journal's data editor (AEA, REStud, JPE, JF, RFS, JFE, ...) requests a DCAS-compliant deposit before the paper is typeset.
- **Before an openICPSR / Zenodo / Dataverse upload.** Build the tree and README once, locally, before the web upload.
- **Pre-submission dry run.** Catch the "I never wrote down where Table 3 comes from" gap while it is cheap to fix.
- **Confidential / licensed-data papers.** Produce the access-restricted-data note and a runnable-on-restricted-data package even when the data itself (CRSP/Compustat/IBES extracts, Census RDC, admin records) cannot be deposited.

## Inputs

- `$0` — path to the manuscript (`.tex`, `.md`, `.pdf`). Required (the source of the Table/Figure inventory). For this template the authoritative source is `manuscript/main.tex` plus the per-table `\input{}` files under `output/tables/`.
- `$1` — outputs directory. Defaults to `output/` (the template's `output/tables/`, `output/figures/`, `output/results/`, `output/logs/`). Recognised alternatives: any directory the user-built exhibits live in.

## Workflow

### Phase 0: Pre-flight — detect language(s) and outputs

1. Detect the analysis language(s) by scanning for `code/stata/*.do` (+ `params.do`, `00_run.do`), `code/python/*.py` (+ `requirements.txt` / `environment.yml` / `pyproject.toml` / `uv.lock`), and `code/sas/*.sas` (+ `autoexec.sas`). A project is usually **polyglot** here — SAS/WRDS extract → Stata estimation → Python figures. Record every detected language.
2. Locate the outputs directory (`$1`) and the **one-command entry point**: for this template that is `run_all.sh` driving the order in `pipeline.md` (e.g. `04_analysis.do` / `00_run.do`). For a pure-Stata package a `99_run_all.do` that `do`-s each numbered script in order serves the same role. If none exists, flag it — DCAS requires a single master script.
3. If `quality_reports/passports/<paper-slug>.yaml` exists, load it; its `claims:` entries are the authoritative Table/Figure → `source_file:source_line` map for Phase 1. `RESULTS_PROVENANCE.md` (the table→generator map, per [`manuscript-overleaf-sync.md`](../../rules/manuscript-overleaf-sync.md)) is the fallback when no passport exists.

### Phase 1: Generate the standard replication README

Write `replication_package/README.md` (the AEA template, fields below). Leave a `[FILL]` marker on any field you cannot infer — never fabricate a data source or license.

- **Overview / paper citation** — title, authors, abstract one-liner.
- **Data Availability Statement** — for each dataset: public / restricted / proprietary, and whether it is redistributed in the package. This is the single most-rejected DCAS field; be explicit. Licensed vendor feeds (CRSP, Compustat, IBES, TAQ) are **proprietary, not redistributed** — see Phase 5.
- **Dataset manifest** — a table, one row per file: `filename | description | source (URL/citation) | access (public / DUA / WRDS-licensed / purchase) | license | provided in package? (Y/N)`.
- **Computational requirements** — OS, software + versions (Stata SE/MP + update level, Python, SAS 9.4 + whether WRDS/Duo is needed), key packages/ado, approximate runtime, RAM, any HPC/cluster need.
- **Step-by-step run instructions** — the single master-script invocation (`./run_all.sh "04_analysis.do"` or `do code/stata/99_run_all.do`), then the expected outputs.
- **Table/Figure → script:line map** — one row per exhibit: `Exhibit | Program | Line | Output file`. Read from the passport / `RESULTS_PROVENANCE.md` if present; otherwise grep the manuscript for `\input{}` / `\includegraphics{}` and trace each `output/tables/tabN.tex` / `output/figures/figN.pdf` back to the `eststo`/`esttab` or `graph export` call in the producing `.do`. This map is what a reproducer follows; it is the heart of the package.

### Phase 2: Capture the computational environment

Generate the environment snapshot for each detected language. Prefer [`/capture-environment`](../capture-environment/SKILL.md) if available; otherwise produce them directly:

- **Stata** — confirm every `.do` pins `version NN` at the top (per [`python-stata-conventions.md`](../../rules/python-stata-conventions.md)); log the package inventory once with a small subroutine that writes `about`, `which reghdfe`, `which estout`, `which ivreg2`, `which csdid`, and `ado dir` to `output/logs/sessionInfo.txt`; list every `ssc install` / `net install` in the install step. Stata is licensed and **not** containerizable — record the exact version + flavor (SE/MP/IC) + update level.
- **Python** — `python --version` and a pinned `requirements.txt` (`pip freeze`, `==` exact), or the conda `environment.yml`, or `uv.lock` — whichever matches the project's existing tooling.
- **SAS** — record the SAS version and any WRDS macros `%include`-d; note which steps require WRDS/Duo and that those steps re-pull licensed data rather than reading a deposited extract.
- **Container (recommended by DCAS for non-trivial setups)** — scaffold a `Dockerfile` for the Python layer (pin `FROM python:<X.Y.Z>-slim` + `requirements.txt`); Stata/SAS binaries are licensed and documented, not imaged.
- *(R is not a primary stack here. If an R-only robustness check exists — e.g. HonestDiD — add `renv.lock` + `sessionInfo.txt` for that sub-step only.)*

### Phase 3: Confirm claims reproduce before packaging

Run [`/audit-reproducibility`](../audit-reproducibility/SKILL.md) `$0 $1` (passport-aware if the YAML exists).

- **Any FAIL** (out of tolerance, no named alternative) → **block**: do not assemble a package around numbers that do not reproduce. Surface the failing claims and stop.
- **EXPLAINED** (out of tolerance with a recorded named alternative) → allowed; carry the note into the README's known-discrepancies section.
- **All PASS / PASS + EXPLAINED** → proceed to Phase 4.

### Phase 4: Assemble the tree + DCAS checklist

Create the deposit skeleton (copy/symlink real files where they exist; leave `[FILL]` placeholders otherwise):

```
replication_package/
├── README.md                # Phase 1
├── data/
│   ├── raw/                 # as-obtained (or a pointer + DUA note if restricted/licensed)
│   └── processed/           # constructed analysis files (.dta)
├── code/                    # stata/ python/ sas/ + master script (run_all.sh / 99_run_all.do)
└── output/                  # tables/, figures/, logs/, sessionInfo.txt, requirements.txt[, Dockerfile]
```

Then emit the **DCAS compliance checklist** (`replication_package/DCAS_checklist.md`): Data Availability Statement present · every dataset has source + access + license · master script present and one-command · computational requirements stated · every Table/Figure mapped to program:line · no absolute/machine-specific paths in code (Stata paths via globals from `00_run.do`; Python via `pathlib`) · seeds set for any stochastic step (`set seed` / `set sortseed`; `np.random.default_rng`) · license file (a code license such as BSD/MIT + a data-usage statement). Mark each PASS / FAIL / `[FILL]`.

### Phase 5: Confidential / licensed-data handling

Per [`.claude/rules/confidential-data.md`](../../rules/confidential-data.md), scan the manifest for restricted, proprietary, or PII-bearing inputs (administrative records, IRS/Census RDC, proprietary panels, linked health data, **and licensed vendor feeds: CRSP, Compustat, IBES, TAQ**).

- **Never copy restricted or licensed data into `replication_package/data/`.** Replace it with a pointer: the provider, the application/DUA process (or WRDS subscription), the access cost, and the expected wait time.
- Generate `replication_package/data/access-restricted-data.md` — the access note a reproducer follows to obtain the same inputs (e.g. the WRDS query / library + the date range, so they can re-pull the licensed rows themselves).
- Confirm the **code still ships** (DCAS requires runnable-on-restricted-data code even when the data cannot be deposited — the SAS/Stata extract scripts ship with credentials gitignored), and that any committed derived extracts pass disclosure-avoidance (cell suppression / rounding) via [`/disclosure-check`](../disclosure-check/SKILL.md) before they enter `output/`.

## Output / Report format

Write `quality_reports/replication_package_[paper-slug].md`:

```markdown
# Replication Package: [Paper Title]
**Date:** [YYYY-MM-DD]  **Languages:** [Stata / Python / SAS]  **Deposit target:** [openICPSR / Zenodo / Dataverse]

## DCAS checklist
| Item | Status |
|---|---|
| Data Availability Statement | PASS / FAIL / [FILL] |
| Dataset manifest (source · access · license) | ... |
| One-command master script | ... |
| Computational requirements | ... |
| Table/Figure → program:line map | ... |
| No machine-specific paths · seeds set | ... |
| Reproducibility audit (Phase 3) | PASS / EXPLAINED-only / FAIL (blocker) |
| Confidential/licensed-data note (if applicable) | ... |

## Skeleton built at
replication_package/  (tree + README + checklist)

## Open [FILL] items
[one line per unresolved field]
```

## Exit behavior

- **All checklist items PASS (or PASS + `[FILL]`) and audit PASS/EXPLAINED-only:** exit 0; print the tree location and any `[FILL]` items for the author to complete.
- **Any audit FAIL (Phase 3):** exit 1; package assembly halts. Numbers that do not reproduce do not get deposited.
- **Restricted/licensed data detected but no access note generated:** exit 1 with the confidential-data blocker — packaging cannot proceed until Phase 5 runs.

## Cross-references

- [`.claude/rules/replication-protocol.md`](../../rules/replication-protocol.md) — tolerance contract + passport schema (the upstream verification this skill packages; its Phase 5 "Producing a Replication Package" is the producer stance behind this skill).
- [`.claude/skills/audit-reproducibility/SKILL.md`](../audit-reproducibility/SKILL.md) — the Phase 3 gate; proves claims reproduce.
- [`.claude/skills/capture-environment/SKILL.md`](../capture-environment/SKILL.md) — the Phase 2 environment snapshot.
- [`.claude/rules/confidential-data.md`](../../rules/confidential-data.md) — restricted/licensed-data deposit rules driving Phase 5.
- [`.claude/rules/manuscript-overleaf-sync.md`](../../rules/manuscript-overleaf-sync.md) — `RESULTS_PROVENANCE.md`, the table→generator map this skill reads.
- [`templates/passport-template.yaml`](../../../templates/passport-template.yaml) — source of the Table/Figure → program:line map when present.
- [`.claude/skills/data-analysis/SKILL.md`](../data-analysis/SKILL.md) — the Stata/Python pipeline whose outputs this skill packages.
- [`.claude/skills/preregister/SKILL.md`](../preregister/SKILL.md) — for RCTs, the PAP belongs in the deposit alongside the analysis.

## What this skill does NOT do

- **Verify the numbers.** That is `/audit-reproducibility` (called in Phase 3). This skill packages a *verified* result; it blocks rather than re-derives on FAIL.
- **Upload to the repository.** It builds the local tree and README; the author performs the openICPSR / Zenodo / Dataverse upload and gets the DOI. Web deposit is deliberately out of scope.
- **Judge the research.** Whether the identification strategy (DiD / event-study, IV, panel FE) is sound is a `/review-paper` question. A reproducible package can still house a flawed design.
- **De-identify your data.** It flags restricted/licensed inputs and refuses to deposit them; it does not run disclosure-avoidance algorithms on raw microdata — that is the author's (and the RDC's) responsibility. See [`/disclosure-check`](../disclosure-check/SKILL.md).
