---
name: run
description: Execute a pipeline step via run_all.sh or MCP Stata. Reads the log and summarizes results. Use to run analysis scripts.
argument-hint: "[script_name.do or script_name.py or script_name.sas or --all]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Run Pipeline Step

Execute a pipeline step, read the log, and summarize results.

**Input:** `$ARGUMENTS` -- script name (e.g., `01_import_capital_iq.do`), or `--all` for full pipeline, or `--from <step>` for partial.

## Steps

1. **Identify the script:**
   - If `$ARGUMENTS` is provided, use it
   - If not specified, ask which step to run

2. **Pre-flight checks:**
   - Confirm script exists in `code/stata/`, `code/python/`, or `code/sas/`
   - Confirm input files exist (check script header for inputs)
   - Check `code/stata/params.do` for current parameter values

3. **Execute:**

```bash
./run_all.sh "$ARGUMENTS"
```

4. **Read the log:**
   - Find the most recent log in `output/logs/` for this script
   - Read the full log
   - Check for errors (Stata: `r(NNN)` codes; Python: tracebacks; SAS: `ERROR:` lines — exit codes unreliable)
   - Check for warnings
   - SAS: if script uses WRDS (`rsubmit`), remind user to approve Duo push on phone

5. **Summarize results:**
   - Report success/failure
   - Key output statistics (N observations, coefficients, etc.)
   - Any warnings or unexpected behavior
   - List output files created

6. **Identify downstream impacts:**
   - Check `pipeline.md` for scripts that depend on this step's output
   - Tell the user which downstream steps may need re-running

## Important

- **ALWAYS read the log.** Never assume success.
- **Report what the log shows** -- don't summarize from memory.
- After running, check that output files exist and have non-zero size.
