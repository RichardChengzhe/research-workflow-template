---
paths:
  - "code/**"
  - "pipeline.md"
---

# Pipeline Integrity Protocol

## Break the Glass Rule

**Before modifying ANY of the following, STOP and warn the user:**

1. **I/O graph changes** -- adding/removing/renaming scripts, changing what they read/write
2. **Pipeline order changes** -- modifying execution order in `00_run.do` or `run_all.sh`
3. **Parameter changes** -- modifying values in `params.do`
4. **Instruction changes** -- modifying `CLAUDE.md`

**Tell the user exactly what you plan to change and what it affects downstream.**
Use language like: "This changes the pipeline -- everything downstream of this step will be affected. Are you sure?"

## Pipeline Tracing

Before modifying any script, trace its dependencies in both directions:

### Upstream
- What data files does this script read?
- What scripts created those files?
- Are those upstream scripts up to date?

### Downstream
- What files does this script produce?
- What scripts or manuscript sections consume those files?
- Will downstream steps need re-running?

### How to Trace
1. Read the script header (inputs/outputs documented there)
2. Check `pipeline.md` for the dependency graph
3. Search manuscript for `\input{}` and `\includegraphics{}` references to outputs

## Adding New Steps

Use `/add-step` to scaffold new pipeline steps. This ensures:
- Script is created with proper header
- `pipeline.md` is updated
- `00_run.do` is updated (commented out)
- `run_all.sh` is updated (commented out)

## Verification After Changes

After modifying a pipeline step:
1. Re-run the modified script via `run_all.sh`
2. Check the log for errors
3. Identify and re-run downstream steps
4. Verify manuscript still compiles
