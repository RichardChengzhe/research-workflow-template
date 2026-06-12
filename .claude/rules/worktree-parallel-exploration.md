# Worktree-Based Parallel Exploration

**Rule for ceteris-paribus exploration via git worktrees.** Run ONE isolated change per worktree+branch, keep everything else identical to the baseline, then cherry-pick the winners back to the main branch. This gives clean apples-to-apples comparisons (one variable changed) without polluting the main working tree or risking a wrong-branch commit.

Use this whenever you want to test a single design choice (a new control, an alternative measure, a different sample window, an estimation tweak) against an unchanged baseline.

---

## 1. Where worktrees live

- Put worktrees in a **dedicated sibling directory**, e.g. `<drive>:/worktrees/<repo>-<branch-tail>` (Windows) or `~/worktrees/<repo>-<branch-tail>` (POSIX). A subdirectory inside the project root is also acceptable.
- **NEVER** create a worktree as a sibling of a **cloud-synced** repo root (Dropbox / OneDrive / Google Drive). A sibling under the synced root pollutes the drive root and makes the cloud client sync every build artifact on every run, generating large, useless sync churn.
- Naming: branch `explore/<name>` → worktree dir `<...>/worktrees/<repo>-<name-with-dashes>`. Use dashes, not slashes or underscores, in the directory tail.
- If a worktree was created in the wrong place, relocate with `git worktree move <old> <new>` (preserves commits) rather than deleting and re-adding.

## 2. Always write INTO the worktree's own path

Worktrees share one `.git/` but each has its **own working tree and branch checkout**. Writing to an **absolute path that points at the main repo** lands the change on the **main branch**, not the worktree's branch — silently. You lose isolation and may commit on the wrong branch or miss the change entirely.

- The probe prompt always names the worktree path at the top. Use **that path** as the root for every Read / Write / Edit / output path.
- Absolute output paths inside scripts (`outdir`, `graph export`, `esttab using`, SAS `%let outdir=`) must point at the **worktree's** `data/` / `output/`, not the main repo's.
- **Pre-flight before any long-running command** (SAS, Stata, Python): confirm you are on the right tree.
  ```bash
  cd "<worktree path>" && git branch --show-current && ls <a-file-you-just-edited>
  ```

## 3. Copy gitignored credentials into the worktree

Gitignored runtime files do **not** propagate via `git worktree add`/`move`. Copy any credential or config the worktree needs on first use, e.g. `autoexec.sas` (WRDS password), `.env`, API-key files, local `params`/path overrides. Without them, remote jobs (SAS/WRDS) fail to authenticate or write to the wrong directory.

## 4. Wire large gitignored data into the worktree via junction + hard-link (no copy)

Gitignored data (`data/`, `temp/`, large `output/` subdirs) is **empty** in a fresh worktree. Do **not** copy gigabytes. Instead link back to the main repo:

- **Directory junction** for a subdir that has **no tracked content** (e.g. `temp/`, `output/logs/`, a new gitignored output subdir).
- **File hard-link** for individual gitignored files that sit in a **mixed-content** directory (one whose parent also holds tracked files — junctioning the whole dir would overlay the tracked files).

On Windows, **use PowerShell** (`New-Item -ItemType Junction` for dirs, `fsutil hardlink create` / `New-Item -ItemType HardLink` for files). Do **NOT** use `cmd mklink` from Git Bash (the `//c` path conversion breaks the cmd arg parsing) and do **NOT** use `ln -s` on Git Bash without Developer Mode (fails silently). On POSIX, a bind mount or `ln` (symlink for dirs, hard link for same-filesystem files) is the equivalent.

```powershell
# Windows pattern (run via: powershell.exe -NoProfile -Command "...")
$wt   = "<drive>:\worktrees\<repo>-<tail>"
$main = "<drive>:\<path to main repo>"
Set-Location $wt
# Junctions for empty/untracked subdirs
foreach ($sub in @('temp','output\logs')) {
    $p = Join-Path $wt $sub; $t = Join-Path $main $sub
    if (-not (Test-Path $p)) { New-Item -ItemType Junction -Path $p -Target $t | Out-Null }
}
# Hard links for individual gitignored files in tracked-content dirs (same volume only)
$src = Join-Path $main 'data\sub\big_input.parquet'
$dst = Join-Path $wt   'data\sub\big_input.parquet'
if ((Test-Path $src) -and (-not (Test-Path $dst))) {
    New-Item -ItemType HardLink -Path $dst -Target $src | Out-Null
}
```

Gotchas:
- `New-Item -ItemType Junction` requires the target path **not** to exist yet — guard with `Test-Path` or `Remove-Item` first.
- Hard links require source and destination on the **same volume**.
- `git status` stays clean after junctions/hard-links — they don't pollute the tree. Hard links share an inode (zero extra disk).
- Removing a junction/hard-link removes only the link entry, never the underlying target/file.

## 5. One isolated change → cherry-pick winners

- Make exactly **one** substantive change per worktree+branch; keep specs, FE, clustering, sample, and seeds **identical** to the baseline so any difference is attributable to that one change.
- Reproduce the baseline in the worktree first (a "gate" run) and confirm it matches the published/baseline numbers byte-for-byte before trusting the experimental result.
- When a probe wins, **cherry-pick** the specific commit(s) back onto the main branch rather than merging the whole exploratory branch. Discard losers (delete the branch + worktree; remove its junctions/hard-links).

## See also

- `.claude/skills/worktree-probe/SKILL.md` — scaffolds one probe end-to-end (worktree + data wiring + creds + branch + run + report).
- `.claude/rules/remote-jobs.md` — discipline for the long remote jobs a probe often launches.
