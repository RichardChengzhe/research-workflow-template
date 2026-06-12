---
name: coauthor-brief
description: Generate a co-author / collaborator handoff brief for a multi-author, multi-machine project -- summarizing what changed since the last brief (git delta), the current state of each artifact (manuscript, analysis, slides), open questions, how to reproduce locally, and any restricted-data access steps. Use when the user says "coauthor brief", "handoff brief", "bring my coauthor up to speed", "what changed since last week", "onboard a collaborator", "write a handoff for [name]", or before sending a co-author the repo. NOT a commit or a checkpoint -- it is the cross-machine, cross-person summary that `meta-governance.md` only partially covers.
author: Claude Code Academic Workflow
version: 1.0.0
argument-hint: "[--since <tag|date|Ndays>] [--for <collaborator-name>] [--no-data-section]"
disable-model-invocation: true
allowed-tools: ["Read", "Write", "Glob", "Grep", "Bash"]
effort: medium
---

# /coauthor-brief -- collaborator handoff brief

Produce a single Markdown brief a co-author (or your future self on another machine) can read in a few minutes to know **what changed, where each artifact stands, what's blocked, and how to run the pipeline locally** -- including the restricted-data (WRDS / enclave) access steps a new collaborator needs. [`meta-governance.md`](../../rules/meta-governance.md) covers the *memory* side of cross-machine work (what syncs via git, what stays in gitignored `personal-memory.md`); this skill covers the *human* side: the per-person, per-session handoff.

**Core principle:** `/checkpoint` is for *you* resuming; `/coauthor-brief` is for *someone else* starting. The first answers "where am I?"; the second answers "what do I need to know to take over a piece of this?"

This template's typical topology is multi-machine *and* multi-person: an **office PC** (primary dev), a **home PC reached over SSH**, an **HPC cluster** (SLURM array jobs), and **Overleaf** (the web-compiled, coauthored manuscript). A good brief tells the recipient which machine produced what, and what they need on *their* machine to continue.

## When to use

- **Before sending a co-author the repo** (or a PR / branch) and you want them oriented, not archaeologizing the git log.
- **Onboarding a new RA / collaborator** who needs the reproduce-locally and restricted-data steps in one place.
- **Periodic sync** on a long multi-author project -- "here's the delta since the last brief."
- **Cross-machine handoff** -- finishing on the office desktop, picking up on the home PC over SSH or on the HPC; or handing the SAS/WRDS extract half to a co-author while you keep the Stata estimation half.

## When NOT to use

- For *your own* resume-point -- use [`/checkpoint`](../checkpoint/SKILL.md).
- For distilling a noisy session before auto-compact -- use [`/compress-session`](../compress-session/SKILL.md).
- For the commit message itself -- that goes through [`/commit`](../commit/SKILL.md).

## Phases

### Phase 0 -- Determine the "since" point

Resolve the delta window, in this priority order:

1. `--since <arg>` if given -- a git tag, an ISO date, or `Ndays` (e.g. `--since v1.2`, `--since 2026-05-01`, `--since 14days`).
2. Else, the **last brief** -- `ls -t quality_reports/handoffs/*.md | head -1`; use the date in its filename as the floor.
3. Else, fall back to **14 days** and say so in the brief (an unbounded `git log` is noise, not signal).

Echo the resolved window back before gathering ("Brief covers changes since `<tag/date>` ...").

### Phase 1 -- Gather the delta + project state

Read-only collection. Skip any source that doesn't apply (no slides, Stata-only, no SAS step) rather than fabricating.

1. **Git delta** -- `git log --oneline --since=<point>` (or `<tag>..HEAD`), `git diff --stat <point>..HEAD`, `git branch --show-current`, and `git log --all --oneline -15` to see co-authors' parallel branches and any active worktrees. Group commits by area (manuscript / analysis / slides / infra).
2. **Reproducibility status** -- if a passport exists at `quality_reports/passports/<paper-slug>.yaml`, read the PASS / FAIL / EXPLAINED / STALE / UNVERIFIED roll-up ([`audit-reproducibility`](../audit-reproducibility/SKILL.md), [`replication-protocol.md`](../../rules/replication-protocol.md)). Note whether the analysis is replication-ready or has open FAILs.
3. **Open plan items** -- most recent `quality_reports/plans/*.md` (status + any "Open questions" / "Next" lines) and the latest `quality_reports/session_logs/*.md` blockers.
4. **Environment / lockfiles** -- locate the env capture a collaborator needs on their machine: `requirements.txt` / `environment.yml` / `uv.lock` (Python conda env), a Stata `version` line + the `.do` `ssc install` list, the SAS version + WRDS `autoexec` requirement, or whatever [`/capture-environment`](../capture-environment/SKILL.md) wrote. Record the exact restore command per stack.
5. **Manuscript / Overleaf state** -- if the paper is synced to Overleaf (see [`manuscript-overleaf-sync.md`](../../rules/manuscript-overleaf-sync.md)), say which side is ahead (local commits not yet pushed to the Overleaf bridge, or red change-marks pending acceptance), and remind the recipient that the *user* pushes to Overleaf -- a co-author should pull the bridge before editing.
6. **Restricted-data steps** *(skip if `--no-data-section`)* -- if the repo touches confidential/restricted data (WRDS, a secure enclave, licensed extracts), read [`confidential-data.md`](../../rules/confidential-data.md) and summarize the access path a new collaborator needs (WRDS account + Duo, DUA / IRB approval, where the extract lives, what is gitignored vs committed). **Never copy actual restricted values, paths to live extracts, WRDS credentials, or `autoexec.sas` contents into the brief** -- describe the *process to obtain access*, not the data.

### Phase 2 -- Write the brief

Use the template below. Keep it tight (~1-2 screens). Concrete `path:line` pointers beat prose.

```markdown
---
date: YYYY-MM-DD
for: [collaborator name or "all coauthors"]
since: [tag | date | Ndays]
branch: [current branch]
produced-on: [office PC | home PC (SSH) | HPC | mixed]
---

# Co-Author Brief -- [project / paper short name]

## What changed since [since-point]
[3-8 bullets, grouped by area. Each: what changed + why it matters to a reader, not raw commit subjects.]
- **Analysis:** re-estimated Table 3 with firm + month FE (was industry + month); main interaction now t=-2.55 -- see `code/stata/04_analysis.do:412`. Run on the HPC (SLURM array, 8-core cap).
- **Data:** rebuilt the SUE panel from the canonical IBES pipeline on WRDS; output `data/processed/sue_panel.dta` (not committed -- rebuild step below).
- **Manuscript:** Table 3 + Section 3 rewritten to match; pushed to Overleaf (red marks pending your review).
- **Slides:** untouched.

## Current state of each artifact
| Artifact | Path | State | Notes |
|---|---|---|---|
| Manuscript | `manuscript/main.tex` | drafting Sec 5 | robustness section is a stub; Overleaf ahead by 0, local ahead by 2 |
| Analysis | `code/stata/` | replication-ready | passport: 11 PASS, 1 EXPLAINED, 0 FAIL |
| Data build | `code/sas/` | needs WRDS | SUE/IBES extract requires a live WRDS+Duo session |
| Slides | `slides/` | current | matches latest results |

## Open questions / decisions needed
[Things the co-author should weigh in on. Mark Q1, Q2...; flag which block progress.]

## Reproduce locally (per machine)
1. Clone + branch: `git checkout <branch>` (or attach the worktree if one is active).
2. Restore the environment for the stack you'll run:
   - Python: `conda env create -f environment.yml` (or `pip install -r requirements.txt`), then use the project env.
   - Stata: open `code/00_run.do`, set your `$root` for your username, `ssc install` the listed packages (`reghdfe`, `ftools`, `estout`, ...).
   - SAS/WRDS: copy your own `autoexec.sas` (NOT committed) with your WRDS creds; the extract steps need a live Duo session.
3. Run the pipeline: `./run_all.sh "04_analysis.do"` (or the master `.do` / `make`).
4. Verify: `/audit-reproducibility manuscript/main.tex` should report 0 FAIL.

## Restricted-data access (if applicable)
[Process to obtain access -- WRDS account + Duo, DUA/IRB/enclave steps. NO actual data, live extract paths, or credentials. See confidential-data.md.]

## Recommended git topology for this project
- One **feature branch (or worktree) per author / exploration** (`feat/<author>-<topic>`, `explore/<topic>`); rebase on `main`, open a PR, merge via `/commit`.
- `MEMORY.md` is **committed** -- generic learnings sync to everyone.
- `personal-memory.md` and `.claude/state/` stay **local** (gitignored) -- never expect a co-author (or the home PC / HPC) to have yours (see meta-governance.md).
- The **user** pushes the manuscript to Overleaf; co-authors pull the bridge before editing (manuscript-overleaf-sync.md).
- Pull before you brief; brief before you hand off.
```

### Phase 3 -- Save and summarize

1. Write to `quality_reports/handoffs/YYYY-MM-DD_coauthor-brief.md` (create `quality_reports/handoffs/` if missing). If `--for` is set, suffix the slug (`..._coauthor-brief_<name>.md`).
2. Print to chat: saved path, the resolved since-window, counts (commits summarized / open questions / artifacts), and whether the data section was included or skipped.

## Output / report format

A single Markdown handoff doc at `quality_reports/handoffs/YYYY-MM-DD_coauthor-brief.md` matching the Phase 2 template, plus a one-line chat summary. No edits to any other file.

## Exit behavior

- **Brief written:** exit with the saved path and summary line.
- **No "since" resolvable and no git history in window:** still write the brief with an explicit "no changes in window" note rather than failing -- a co-author starting fresh still needs the state + reproduce + data sections.
- **Restricted-data repo detected but `confidential-data.md` missing:** write the brief, leave the data section with a `TODO: complete per your DUA / WRDS terms` placeholder, and warn -- do **not** guess the access process.

## Flags

- `--since` `<tag|date|Ndays>` -- Baseline to diff against -- a git tag, an ISO date, or `Ndays` (e.g. `14days`). Default: the previous brief in `quality_reports/handoffs/`, else the last tag, else 14 days.
- `--for <name>` -- Tailor the brief to a specific collaborator (e.g. surface the WRDS/restricted-data access steps they still need).
- `--no-data-section` -- Omit the restricted-data section (e.g. when the recipient already has full access).

## Cross-references

- [`.claude/rules/meta-governance.md`](../../rules/meta-governance.md) -- the cross-machine memory model (what syncs, what stays local) this brief operationalizes for *people*.
- [`.claude/rules/manuscript-overleaf-sync.md`](../../rules/manuscript-overleaf-sync.md) -- the web-compiled coauthored-manuscript discipline the brief's Overleaf line points at.
- [`.claude/skills/capture-environment/SKILL.md`](../capture-environment/SKILL.md) -- produces the lockfiles the "Reproduce locally" section points at.
- [`.claude/skills/checkpoint/SKILL.md`](../checkpoint/SKILL.md) -- the *self*-resume companion (this skill is the *other-person* handoff).
- [`.claude/skills/compress-session/SKILL.md`](../compress-session/SKILL.md) -- distil a noisy session before compaction (orthogonal; run before briefing if context is fat).
- [`.claude/rules/confidential-data.md`](../../rules/confidential-data.md) -- restricted-data handling; the data section summarizes its access steps without exposing data.

## What this skill does NOT do

- **Push, PR, or merge.** It writes a doc. Branch/PR/merge is [`/commit`](../commit/SKILL.md)'s job; pushing the manuscript to Overleaf is the user's.
- **Run the pipeline or audit numbers.** It *reports* passport status if one exists; it does not re-run analysis or re-verify claims -- that's [`/audit-reproducibility`](../audit-reproducibility/SKILL.md).
- **Capture the environment.** It locates and links existing lockfiles; generating them is [`/capture-environment`](../capture-environment/SKILL.md).
- **Expose restricted data.** It describes the *access process* only -- never copies confidential values, live data paths, WRDS credentials, or `autoexec.sas` into a brief that may be emailed or committed.
