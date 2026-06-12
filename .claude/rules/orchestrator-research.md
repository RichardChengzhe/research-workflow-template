---
paths:
  - "code/**/*.do"
  - "code/**/*.py"
  - "code/**/*.sas"
  - "explorations/**"
---

# Research Project Orchestrator (Simplified)

**For analysis scripts, exploratory regressions, and data work** -- use this simplified loop instead of the full multi-agent orchestrator in [`orchestrator-protocol.md`](orchestrator-protocol.md). The full critic-fixer loop is for publication-bound output; this is for getting a defensible result on the screen.

## The simple loop

```
Plan approved -> orchestrator activates
  |
  Step 1: IMPLEMENT -- Execute plan steps
  |
  Step 2: VERIFY -- Run code, read the log, check outputs
  |         Stata:  ./run_all.sh "script.do" runs clean; read output/logs/
  |         Python: script exits 0; expected files written
  |         SAS:    log has no ERROR:; NOTE: obs counts as expected (.lst, not exit code)
  |         Output: .dta/.ster/.tex/.pdf created with non-zero size
  |         If verification fails -> fix -> re-verify
  |
  Step 3: SCORE -- Apply the quality-gates rubric
  |
  +-- Score >= threshold (60 for explorations, 80 for code headed to the pipeline)?
        YES -> Done (commit when the user signals)
        NO  -> Fix blocking issues, re-verify, re-score
```

**No 5-round adversarial loops. No multi-agent reviews. Just: write, run, read the log, done.** Escalate to the full [`orchestrator-protocol.md`](orchestrator-protocol.md) the moment the output is destined for the manuscript or a table that ships.

## Verification checklist

- [ ] Script runs without errors (Stata/SAS: the *log* is authoritative, not the exit code)
- [ ] All Python packages imported at the top; all Stata `ssc`/`require` dependencies present
- [ ] No hardcoded absolute paths (globals / `pathlib` / macros)
- [ ] `set seed` (Stata) or seeded generator (Python) once at the top if stochastic
- [ ] Research parameters read from `params.do`, not inlined
- [ ] Output files created at the expected paths with non-zero size
- [ ] Tolerance / replication-target checks pass (if applicable; see [`replication-protocol.md`](replication-protocol.md))
- [ ] Quality score >= threshold

## Cross-references

- [`orchestrator-protocol.md`](orchestrator-protocol.md) -- the full adversarial loop for ship-bound output.
- [`quality-gates.md`](quality-gates.md) -- the scoring rubric and thresholds.
- [`verification-protocol.md`](verification-protocol.md) -- the per-file-type verification detail.
