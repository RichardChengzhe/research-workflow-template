---
paths:
  - "code/**"
  - "manuscript/**"
  - "output/**"
---

# Task Completion Verification Protocol

**At the end of EVERY task, Claude MUST verify the output works correctly.** This is non-negotiable.

Verification has **two faces**:

1. **Execution verification** — did the script run, did the file get created, are the numbers sane? (per file type, below). This is the *mechanical* check.
2. **Post-flight claim verification** — do the *factual claims* in any text output (a summary, a memo, a literature note, a "we added X on page Y" assertion) actually hold against their sources? (the anti-hallucination check, below). This is the *factual* check.

Both run before a task is reported complete.

## For Stata .do Files:
1. Run via `./run_all.sh "script_name.do"`
2. Read the log file in `output/logs/`
3. Check for errors, warnings, unexpected output
4. Verify output files (.dta, .tex, .pdf, .ster) were created with non-zero size
5. Spot-check estimates for reasonable magnitude
6. Report verification results

## For Python Scripts:
1. Run `python code/python/script_name.py`
2. Check exit code (0 = success)
3. Verify output files were created
4. Check for warnings in stdout/stderr
5. Report verification results

## For SAS .sas Files:
1. Run via `./run_all.sh "script_name.sas"`
2. Read the log file in `output/logs/`
3. Search for `ERROR:` lines (any = failure)
4. Check `WARNING:` lines and evaluate significance
5. Verify observation counts in `NOTE:` lines match expectations
6. Verify output files (.sas7bdat, .csv, .xlsx, .dta) were created with non-zero size
7. Note: SAS exit codes are unreliable — the log is authoritative. (When running on WRDS, remember some output lands in `.lst`, not `.log`.)
8. If script uses WRDS (`rsubmit`): remind user to approve Duo push on phone
9. Report verification results

## For LaTeX Manuscript:
1. Compile with `latexmk -pdf manuscript/main.tex`
2. Check for errors and warnings
3. Grep for undefined citations
4. Grep for overfull hbox warnings
5. Verify PDF was generated
6. Report verification results

## For Output Tables:
1. Verify the .tex file exists and has content
2. Check that it compiles within the manuscript
3. Spot-check a few values against the Stata/Python log

## Post-Flight Claim Verification (anti-hallucination)

When a task's output contains **factual claims that can be independently checked against a source** — citations ("Author (Year) shows X"), existence claims ("dataset X has field Y"), numeric facts pulled into prose, named entities, or negative-literature claims ("no prior work studies X") — run a post-flight check **before returning to the user**:

1. **Extract** the verifiable claims (skip opinions, forward-looking suggestions, and definitions Claude introduced itself).
2. **Verify in fresh context.** Spawn a forked verifier (`Task` with `context: fork`, e.g. the `verifier` / `claim-verifier` agent) handed the claims + source pointers but **not** the draft. Forking removes the draft from the verifier's context so it cannot self-confirm (the Chain-of-Verification independence trick).
3. **Reconcile.** PASS → return as-is; PARTIAL (some unverifiable, no hard discrepancies) → return with explicit uncertainty flags; FAIL (a claim contradicts the source) → regenerate the affected section, max 2 attempts, then surface remaining discrepancies as a warning block.

**Fail-closed:** if the verifier errors out or times out, do **not** silently ship — flag the output as provisional/unchecked. Hallucination discipline matters most precisely when things go sideways.

The full protocol, the per-skill applicability table, the structured output block, and the `--no-verify` opt-out live in [`post-flight-verification.md`](post-flight-verification.md). This is *not* a substitute for execution verification above — both run.

## Common Pitfalls:
- **Assuming success**: Always verify output files exist AND contain correct content. Never trust a reported exit code over the log; SAS exit codes in particular lie.
- **Stale outputs**: After modifying a script, re-run it before verifying.
- **Log location**: Logs go to `output/logs/`, not the script directory. For WRDS SAS, also check `.lst`.
- **Shipping unverified claims**: A clean compile does not make the *prose* true. Run the post-flight check on factual text.

## Verification Checklist:
```
[ ] Output file created successfully
[ ] No compilation/execution errors
[ ] Log file reviewed for warnings (SAS: ERROR/WARNING/NOTE; log is authoritative)
[ ] Output values are reasonable
[ ] Factual claims in any text output post-flight-verified (or flagged provisional)
[ ] Reported results to user
```
