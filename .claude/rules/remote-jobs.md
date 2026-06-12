# Long-Running Remote / Async Jobs

**Discipline for any remote or async job whose wall time exceeds ~10 minutes** — HPC SLURM jobs, WRDS `qsub`/`qsas`, batch LLM APIs, or any multi-hour remote compute. **Never passively wait** between user prompts: schedule polling and/or auto-monitoring, and download outputs promptly before remote cleanup.

---

## Why this matters

1. **Remote storage gets cleaned up.** Scratch spaces, batch-API output buckets, and quota-limited home dirs have retention/idle-cleanup policies. A finished job whose output you didn't download in time = lost data and re-run cost.
2. **Passive waiting wastes the session.** Idling between prompts burns context on nothing. The work should advance on its own — check status, pull new outputs, push the pipeline forward without being asked.

## What to do

- **If the session is active** (user still engaged): set up a self-paced polling loop (e.g. a `/loop`-style dynamic poll) that wakes periodically, OR auto-monitor in-context. Tune the interval to the job:
  - long multi-hour wait → infrequent idle ticks (e.g. ~20-30 min)
  - a critical job near completion → tighten (e.g. ~10 min)
  - actively downloading / final stretch → frequent (e.g. ~5 min)
- **If the session may close before the job finishes**: schedule a **cron job** (a persistent scheduled task) instead of an in-session loop, so monitoring survives the session ending.
- **Always auto-monitor batch jobs you submit.** When you fire a batch (e.g. an LLM Batch API submission), immediately create the recurring status check in the same turn — the user should not have to ask. On completion, automatically run the download → parse → downstream steps, then delete the monitor.

Each wake-up must: **(a)** check job status, **(b)** download any newly available outputs immediately, **(c)** advance the pipeline if enough data has arrived, **(d)** tune the next interval based on what's about to happen.

## HPC: plan array-task decomposition up front (core cap → more tasks)

Before submitting an HPC job, **plan the decomposition for wall time.** Most cluster MP licenses/allocations **cap cores per task** (e.g. an 8-core MP cap), so requesting more cores per task beyond the cap wastes the slot. **Wall-time speed-ups come from splitting work across more array tasks, not more cores per task.**

- First, cheap split: by sample / sub-population (near-free; low data-reload cost).
- Next: by outcome variable, horizon group, or other independent axis (~5-10 tasks).
- Keep each task **long enough to amortize startup** (≥ ~30 s of real work) and **short enough to keep parallelism** (≤ ~15 min wall).
- Pass decomposition keys as env vars mapped from the array index; write one output file per task; concatenate locally on retrieval.
- Estimate the `N_tasks × cores × wall` budget **before** submitting. Refactoring mid-run is cheap: cancel → rewrite → resubmit (killing seconds of state) beats leaving a 10-100× speed-up on the table.

## Anti-pattern

> "Jobs submitted, session ending, the user will pick up later." — acceptable only in the last few minutes of an active session. For multi-hour waits, set up the loop or cron **before** ending, and remember the **retrieval** step also needs auto-monitoring — don't just submit and walk away.

## See also

- `.claude/skills/cypress/SKILL.md` — SLURM job scripts, array decomposition, file transfer, monitoring commands.
- `.claude/skills/sas/SKILL.md` §7 — WRDS queue management (`qhold`/`qrls`), scratch-by-default, refresh-lag guards.
