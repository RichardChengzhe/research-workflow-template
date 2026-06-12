---
name: permission-check
description: Diagnose why Claude Code is (or isn't) prompting for permission. By default reads only repo-local layers (CLI project, CLI project-local, VSCode workspace). Host-global layers (CLI user `~/.claude/`, VSCode user settings) are read ONLY when the user explicitly confirms -- those files may contain unrelated paths or secrets. Use when the user says "why is it asking me to approve?", "permission check", "why am I getting prompts?", "bypass isn't working", "check my permissions", or "why does the Stata/WRDS command keep prompting?". Read-only diagnostic.
argument-hint: "(no arguments)"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Permission Check

## Purpose

Surface the full permission-mode picture across every layer Claude Code honors, so the user can see at a glance why prompts are (or aren't) firing. Claude Code resolves permission mode from a layered stack; a single misconfigured layer produces silent overrides that are hard to debug by eye -- and in an empirical-finance workflow the symptom is usually a *specific* long-running command (a `Bash(stata ...)` batch run, a `Bash(sas ...)` / WRDS pull, a `Bash` HPC `ssh`/`scp`) that keeps prompting and stalls an otherwise-unattended pipeline.

## The layers (precedence: later wins)

1. **VSCode user settings** -- `%APPDATA%/Code/User/settings.json` (Windows), `~/Library/Application Support/Code/User/settings.json` (macOS), `~/.config/Code/User/settings.json` (Linux). Key: `claudeCode.initialPermissionMode`.
2. **VSCode workspace settings** -- `<repo>/.vscode/settings.json`. Same key. Wins over user.
3. **CLI user settings** -- `~/.claude/settings.json`. Key: `permissions.defaultMode`.
4. **CLI project settings** -- `<repo>/.claude/settings.json`. Same key + `permissions.allow` / `permissions.deny`. Wins over user.
5. **CLI project-local settings** -- `<repo>/.claude/settings.local.json` (gitignored; may not exist). Same keys. Wins over project.
6. **In-session mode** -- set at session start from layers 1-5, then mutable via `Shift+Tab` or `/permission-mode`. Authoritative until the session ends.

**Key insight:** `initialPermissionMode` only fires at session start. If you toggled mid-session (or the session started before a settings change), the file-level settings are correct but the *runtime* mode differs. That is the #1 source of "bypass isn't working" confusion.

> **Currency note:** the exact key names, the precedence order, and the available modes can drift between Claude Code releases. Treat the layer list above as a starting map and **verify against the live Claude Code settings docs** before asserting a precedence rule to the user (consistent with the [`model-routing.md`](../../rules/model-routing.md) "verify against live docs" discipline).

## Privacy contract

Host-global settings files (`~/.claude/settings.json`, VSCode user settings) may contain:
- Paths to unrelated projects.
- API keys, tokens, or provider credentials added outside this repo.
- Permission policies set by the user's org or employer.

This skill is designed for defense-in-depth: **Phase A runs automatically and reads only repo-local files.** Phase B reads host-global files **only after the user explicitly confirms** -- never silently. When reporting host-global layers, redact any key that is not directly relevant to `permissions.*` or `claudeCode.*`.

## Protocol

### Phase A: Repo-local layers (auto-runs)

Read these immediately -- they live in (or are gitignored inside) the repo and do not cross the trust boundary:

```bash
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"
VSCODE_WS="$ROOT/.vscode/settings.json"
CLI_PROJECT="$ROOT/.claude/settings.json"
CLI_LOCAL="$ROOT/.claude/settings.local.json"   # gitignored; often absent
```

For each file that exists, extract:
- **VSCode workspace:** `claudeCode.initialPermissionMode`, `claudeCode.allowDangerouslySkipPermissions`.
- **CLI project / project-local:** `permissions.defaultMode`, `permissions.allow`, `permissions.deny`.

Missing files are fine -- report "not present" rather than erroring (e.g. `.claude/settings.local.json` is gitignored and may legitimately not exist).

Print the resolved defaultMode from these layers alone. If that already explains the prompt behavior (e.g., CLI project-local has `defaultMode: "default"` while project has `bypassPermissions`), stop here and surface the diagnosis.

### Phase B: Host-global layers (requires explicit user confirmation)

If Phase A is inconclusive -- e.g., all repo-local layers agree on bypass but the user is still being prompted -- ask the user:

> "To complete the diagnosis I need to read two files outside this repo:
> - `~/.claude/settings.json` (CLI user-level)
> - your VSCode user settings (`%APPDATA%/Code/User/settings.json` on Windows; macOS/Linux vary)
>
> These may contain unrelated paths or secrets. I will redact any key that isn't in `permissions.*` or `claudeCode.*`. Proceed?"

Only after the user confirms, read:

```bash
# VSCode user settings (platform-dependent path; Windows first for this template)
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) VSCODE_USER="${APPDATA}/Code/User/settings.json" ;;
    Darwin)               VSCODE_USER="${HOME}/Library/Application Support/Code/User/settings.json" ;;
    Linux)                VSCODE_USER="${HOME}/.config/Code/User/settings.json" ;;
    *)                    VSCODE_USER="" ;;
esac

CLI_USER="${HOME}/.claude/settings.json"
```

When reporting their contents, **extract only the relevant keys**:
- CLI user: `permissions.defaultMode`, `permissions.allow`, `permissions.deny`.
- VSCode user: any key starting with `claudeCode.`.

Never print the full file. Redact everything else to `(other keys redacted)`.

### Step 2: Compute the resolved state

The resolved `defaultMode` is the value from the highest-precedence layer that sets it. Report:

- Which layer won the `defaultMode` contest.
- Merged `allow` list (union across CLI tiers).
- Merged `deny` list (union; any `deny` blocks the action even if allowed elsewhere).
- Whether VSCode says `bypass` but CLI says otherwise (or vice versa) -- a legitimate conflict to flag.

### Step 3: Report the runtime mode

The live in-session mode is shown by whatever status line the user has configured (Claude Code exposes the current mode in the UI; this template ships no status-line script of its own). Tell the user:

> "Your status line (if configured) shows the current in-session mode. If it disagrees with the resolved `defaultMode` above, you (or `Shift+Tab`) overrode it mid-session. Press `Shift+Tab` -- or run `/permission-mode` -- to cycle back."

If no status line is configured, say so and note that `/permission-mode` reports and sets the current mode.

### Step 4: Flag common failure modes

Check for and explicitly call out:

1. **Layer drift:** CLI project says bypass but CLI local says default -> local wins, explains the prompts.
2. **VSCode-only bypass:** VSCode layers say bypass but no CLI layer does -> terminal Claude Code will still prompt; the extension may or may not.
3. **Empty allowlist + default mode:** `defaultMode: "default"` with an empty `allow` -> every tool prompts, as designed.
4. **Stale session:** settings are correct but the user reports prompts -> almost always a session that pre-dates the change. Advise starting a new session (and reloading the VSCode window if using the extension).
5. **`deny` wins:** any match in a `deny` list blocks the tool regardless of `allow`. Rare but deadly.
6. **Over-narrow allow pattern (the finance-pipeline trap):** an `allow` entry like `Bash(stata:*)` won't match how the command is actually invoked (`Bash(./run_all.sh ...)`, `Bash(bash scripts/...)`, an `ssh`/`scp` to WRDS/HPC). The pattern must match the *literal command string* Claude runs -- a too-specific rule silently fails to pre-approve the long batch/remote job, which then prompts and stalls an unattended run. Surface the actual command and suggest a matching `allow` pattern (and consider the [`update-config`](../../skills) flow for adding it to the right settings layer).

## Output format

```
=== PERMISSION STATE ===

Layer 1 -- VSCode user:       (not present)
Layer 2 -- VSCode workspace:  (not present)
Layer 3 -- CLI user:          default
Layer 4 -- CLI project:       default                (allow: ["Bash(git status)", "Read(**)", ...])
Layer 5 -- CLI project-local: (not present)

Resolved defaultMode: default (set by Layer 4)
Merged allow:         Bash(git status), Read(**), ...
Merged deny:          (none)

=== RUNTIME ===

Check your configured status line for the current in-session mode (or run /permission-mode).
If it shows a different mode than the resolved default above, that's an in-session override (Shift+Tab).

=== DIAGNOSIS ===

The Stata batch command prompts because no allow rule matches it. Layer 4 allows
`Bash(stata:*)` but the pipeline runs `./run_all.sh "04_analysis.do"`, so the
match fails. Add an allow rule for the actual command (e.g. `Bash(./run_all.sh:*)`)
to .claude/settings.json (shared) or .claude/settings.local.json (machine-local).
```

If any layer disagrees, replace the diagnosis with the specific flagged issue.

## Notes

- This skill is **read-only**. It never modifies settings -- to *change* a permission, use the `/update-config` flow (or edit the appropriate settings layer by hand).
- If `$CLAUDE_PROJECT_DIR` is unset, fall back to `git rev-parse --show-toplevel`.
- Platform-aware: detect Windows (Git-Bash `MINGW`/`MSYS`) first for this template, then macOS / Linux for the VSCode user path.

## Cross-references

- [`.claude/rules/model-routing.md`](../../rules/model-routing.md) -- the "verify against live Claude Code docs before pinning" discipline the currency note follows.
- `/permission-mode` (built-in) -- reports and sets the live in-session mode; the runtime counterpart to this file-level diagnostic.
