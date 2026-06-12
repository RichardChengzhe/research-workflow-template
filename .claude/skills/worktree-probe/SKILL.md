---
name: worktree-probe
description: Scaffold one ceteris-paribus exploration end-to-end in an isolated git worktree, then cherry-pick or discard. Triggers - "probe", "ceteris paribus", "isolated experiment", "worktree experiment", "test one change against the baseline", "spin up a probe".
argument-hint: "[short-name and the single change to test, e.g. 'add-momentum-control momentum x shock interaction']"
allowed-tools: ["Read", "Bash", "Glob", "Grep", "Write", "Edit"]
---

# Worktree Probe — One Isolated Change, End to End

Scaffold a **single ceteris-paribus experiment** in its own git worktree + branch: everything stays identical to the baseline except **one** change, so any difference in results is attributable to that change. When it wins, cherry-pick the commit back to the main branch; when it loses, discard cleanly.

**Read `.claude/rules/worktree-parallel-exploration.md` first** — this skill is the executable scaffold for that rule.

**Input:** `$ARGUMENTS` — a short dash-name for the probe plus a one-line description of the single change to test.

---

## When to use

- Testing one design choice against an unchanged baseline: a new control, an alternative measure/proxy, a different sample window or filter, an estimation tweak (FE, clustering, winsorization), a robustness variant.
- NOT for multi-change refactors or anything that touches the shared pipeline order — those go through the normal plan-first workflow.

## Steps

### 1. Name the probe

```
branch         = probe/<short-name>           (or explore/<short-name>)
worktree dir   = <worktrees-root>/<repo>-<short-name>
```

`<worktrees-root>` is a dedicated sibling dir (e.g. `<drive>:/worktrees`), **never** a sibling of a cloud-synced (Dropbox/OneDrive) repo root. Use dashes in the tail.

### 2. Create the worktree + branch

```bash
MAIN="<absolute path to main repo>"
WT="<worktrees-root>/<repo>-<short-name>"
cd "$MAIN"
git worktree add -b probe/<short-name> "$WT"   # new branch off current HEAD
cd "$WT" && git branch --show-current           # confirm: probe/<short-name>
```

### 3. Wire gitignored DATA into the worktree (junction + hard-link, no copy)

A fresh worktree's `data/`, `temp/`, large `output/` subdirs are **empty**. Link back to the main repo instead of copying gigabytes. On Windows use **PowerShell** (not `cmd mklink`, not Git-Bash `ln -s`):

```bash
powershell.exe -NoProfile -Command "
\$wt   = '<drive>:\worktrees\<repo>-<short-name>'
\$main = '<drive>:\<path to main repo>'
Set-Location \$wt
# Junction untracked subdirs
foreach (\$sub in @('temp','output\logs')) {
    \$p = Join-Path \$wt \$sub; \$t = Join-Path \$main \$sub
    if (-not (Test-Path \$p)) { New-Item -ItemType Junction -Path \$p -Target \$t | Out-Null }
}
# Hard-link individual gitignored files that live in tracked-content dirs (same volume only)
\$src = Join-Path \$main 'data\sub\big_input.parquet'
\$dst = Join-Path \$wt   'data\sub\big_input.parquet'
if ((Test-Path \$src) -and (-not (Test-Path \$dst))) {
    New-Item -ItemType HardLink -Path \$dst -Target \$src | Out-Null
}
"
```

- **Junction** dirs with no tracked content; **hard-link** individual gitignored files in mixed-content dirs (junctioning the whole dir would overlay tracked files).
- Junction target must not pre-exist (`Test-Path` guard); hard links need same-volume source/dest.
- POSIX equivalent: bind mount or `ln` (symlink dirs, hard-link same-fs files).

### 4. Copy gitignored CREDENTIALS into the worktree

Gitignored runtime/credential files do NOT follow `git worktree add`. Copy what the probe needs on first use:

```bash
cp "$MAIN/autoexec.sas" "$WT/"   # WRDS password (if the probe runs SAS/WRDS)
cp "$MAIN/.env"         "$WT/"   # API keys / local config, if present
# also any local params/path-override file the pipeline reads
```

### 5. Reproduce the baseline FIRST (gate run)

Before making the change, run the baseline inside the worktree and confirm it matches the published/baseline numbers **byte-for-byte**. This proves the worktree is wired correctly (data linked, creds present) and gives a clean reference. If the gate doesn't reproduce, fix the wiring before going further — do not interpret a probe whose baseline doesn't match.

### 6. Make the SINGLE change, run, collect artifacts

- Edit **only inside the worktree's working tree** — every Read/Write/Edit and every script output path (`outdir`, `esttab using`, SAS `%let outdir=`) must point at `$WT/...`, never the main repo. An absolute main-repo path silently lands the change on the **main** branch.
- Pre-flight any long run: `cd "$WT" && git branch --show-current && ls <file-you-just-edited>`.
- Change exactly one thing; keep specs, FE, clustering, sample, and seeds identical to the gate.
- For long remote runs (HPC/WRDS/batch), follow `.claude/rules/remote-jobs.md` (poll/monitor; download before cleanup).
- Save results to the worktree (e.g. `output/` or `explorations/<short-name>/`) and write a short report: the one change, gate-vs-probe comparison of the focal estimate(s), and a keep/discard recommendation.

### 7. Commit on the probe branch

```bash
cd "$WT"
git add <only the files you changed + result artifacts>   # never `git add -A` blindly
git commit -m "probe(<short-name>): <one-line change> — <headline result>"
```

### 8. Decide: cherry-pick winner OR discard

**Winner** — cherry-pick the specific commit onto the main branch (don't merge the whole exploratory branch):

```bash
cd "$MAIN"
git checkout <main-branch>
git cherry-pick <probe commit sha>
```

**Loser / done** — tear down (remove junctions/hard-links first, then the worktree + branch):

```bash
powershell.exe -NoProfile -Command "
Set-Location '<drive>:\worktrees\<repo>-<short-name>'
Remove-Item temp, output\logs -Force -ErrorAction SilentlyContinue          # junctions: removes link only
Remove-Item 'data\sub\big_input.parquet' -Force -ErrorAction SilentlyContinue  # hard link: removes link only
"
cd "$MAIN"
git worktree remove "$WT"            # add --force if the tree is dirty and you mean to discard
git branch -D probe/<short-name>     # if abandoning the branch entirely
```

Removing a junction or hard-link removes only the link entry — never the underlying target directory or file in the main repo.

## Notes

- One probe = one change. If you find yourself changing two things, split into two probes.
- The gate (step 5) is not optional — a probe whose baseline doesn't reproduce is uninterpretable.
- See also: `.claude/rules/worktree-parallel-exploration.md` (the rule), `.claude/rules/remote-jobs.md` (long remote runs), `.claude/rules/exploration-fast-track.md` (the lighter 60/100 exploration threshold).
