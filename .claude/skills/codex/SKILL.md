---
name: codex
description: Delegate a self-contained coding or refactoring task to the OpenAI Codex CLI running on a ChatGPT subscription (not an API key), or drive Codex interactively. Covers subscription login, the non-interactive `codex exec` recipe that keeps the OS sandbox on, the silent approval-prompt hang, and bounding the run so it cannot orphan. Triggers - "delegate to Codex", "use Codex", "run codex exec", "have GPT write this", "offload coding to GPT", "Codex on my subscription".
allowed-tools: ["Read", "Bash"]
---

# Codex — delegate coding to GPT on a ChatGPT subscription

Run OpenAI's **Codex CLI** as a second coding agent powered by your **ChatGPT subscription** (Plus/Pro/Business/Edu/Enterprise) instead of a metered API key. Two modes:

- **Interactive** — you drive Codex directly: run `codex` inside a project folder.
- **Delegated** — Claude (the orchestrator) hands Codex a self-contained task via `codex exec`, reads the result, and verifies it. This is the mode this skill exists for: offload a chunk to GPT on the subscription while Claude stays in the lead.

> Codex is GPT; Claude Code is Claude. Delegating to Codex spends **subscription** quota (a rolling ~5-hour window plus a weekly cap) — not API dollars, and not Claude usage.

---

## CUSTOMIZE THIS BLOCK FIRST

Verify these on the machine you are on before relying on them.

| Placeholder | Meaning | How to find it |
|---|---|---|
| `<CODEX>` | path to the `codex` binary | `Get-Command codex` (PowerShell) / `which codex` (bash) |
| `<MODEL>` | Codex model in use | printed in the `codex exec` stderr header (e.g. `gpt-5.5`) |

Office PC (example, verified 2026-06): `<CODEX>` = `C:\Users\cli33\AppData\Local\Programs\OpenAI\Codex\bin\codex.exe`, on PATH, `codex-cli 0.139.0`, `<MODEL>` = `gpt-5.5`.

---

## 1. One-time: log in on the subscription

```
codex login                 # opens a browser; sign in with ChatGPT
codex login --device-auth   # headless / SSH boxes (home, mac, cluster): open URL + enter code
codex login status          # must print:  Logged in using ChatGPT
```

Credentials sit in plaintext at `~/.codex/auth.json` (Windows: `C:\Users\<you>\.codex\auth.json`) — treat it like a password. `codex login status` printing **"Logged in using ChatGPT"** confirms the subscription (not an API key) is in use.

## 2. Delegated run — the verified recipe

```
codex exec -s workspace-write -c approval_policy=never -C <project-dir> --skip-git-repo-check -o <out.md> -
```

Feed the task on **stdin** (the trailing `-`). Then read `<out.md>` (Codex's final message) and **verify the result yourself** — re-run the script, check the log — never trust the summary.

What each piece does, and why it matters:

- `-s workspace-write` — sandbox **stays on**; writes are confined to the working dir + temp (see Gotchas).
- `-c approval_policy=never` — non-interactive; without it `codex exec` **hangs forever** waiting for an approval it can never receive (see Gotchas).
- `-C <project-dir>` — Codex's working root. Point it at `code/` or `scratch/`, never the home root.
- `-o <out.md>` — capture Codex's final message to a file for Claude to read back.
- non-git folders — the recipe adds the skip-git-repo-check flag (most research subdirs are not git repos).

### Bound the run (Windows PowerShell) — so a hang cannot orphan

```powershell
$codex = '<CODEX>'                                   # full path to codex.exe
$dir   = '<project-dir>'
$pfile = Join-Path $env:TEMP 'codex_prompt.txt'
Set-Content $pfile -NoNewline -Encoding utf8 'YOUR TASK HERE'
$cx = @('exec','-s','workspace-write','-c','approval_policy=never','-C',$dir,
        '--skip-git-repo-check','--color','never','-o',(Join-Path $dir '_codex_last.md'),'-')
$p = Start-Process $codex -ArgumentList $cx -NoNewWindow -PassThru -RedirectStandardInput $pfile `
       -RedirectStandardOutput (Join-Path $env:TEMP 'cx_out.txt') `
       -RedirectStandardError  (Join-Path $env:TEMP 'cx_err.txt')
try { Wait-Process -Id $p.Id -Timeout 180 -ErrorAction Stop } catch { Stop-Process -Id $p.Id -Force }  # hard kill by PID
```

mac / Linux: wrap the same `codex exec ...` in `timeout 180 codex exec ...` so it cannot run unbounded.

## 3. When to delegate (and when not)

Delegate when the task is **self-contained and worth a round-trip**: scaffold a script, a mechanical refactor, a first-pass implementation you want from a second model, or to conserve Claude usage on a long job. For a three-line edit, Claude is faster doing it directly.

This obeys the repo's discipline: keep `data/raw/` **read-only**; do not let Codex touch `params.do`, `00_run.do`, the I/O graph, or `CLAUDE.md` without break-the-glass; and **verify after** every delegated run (read the log, check the outputs) exactly as for any pipeline step. Near sensitive data (WRDS credentials, Dropbox manuscripts), start read-only or on a copy until you trust the loop.

## Gotchas

| Symptom | Cause / Fix |
|---|---|
| `codex exec` hangs forever — zero files, near-zero CPU | The default approval gate with no terminal to answer it. Set `approval_policy=never`. Folder **trust does NOT bypass approval** — only the policy does. |
| Reached for the full-bypass flag to get autonomy | That flag turns the **sandbox off**, and Claude Code's auto-mode classifier **blocks it**. Use `-s workspace-write` (sandbox on) instead. |
| A hung Codex kept running for hours | Tool/timeout kills do not always reap the child. **Bound every run** with `Start-Process -PassThru` + `Wait-Process -Timeout`, and kill **by PID** — not by name (don't nuke a separate interactive session). |
| Prompt with quotes/spaces gets mangled as an argument | Feed the prompt on **stdin** (`-`). And `approval_policy=never` works unquoted — non-TOML values fall back to a literal string. |
| Delegation triggers a Claude Code permission prompt each time | Each `codex exec` is an autonomous (sandboxed) loop. To stop re-prompting, add a scoped `Bash` permission rule (a standing authorization you opt into). |

## See also

- [/cypress](../cypress/SKILL.md) — the other external-compute target (SLURM HPC); same "verify the output, never trust a clean exit" discipline.
- OpenAI Codex docs at `developers.openai.com/codex` — `auth`, and `config-reference` for `approval_policy` / `sandbox_mode`.
