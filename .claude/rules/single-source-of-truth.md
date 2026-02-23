---
paths:
  - "manuscript/**"
  - "output/**"
---

# Single Source of Truth: Enforcement Protocol

**The manuscript `manuscript/main.tex` is the authoritative source for ALL claims and results.**

## The SSOT Chain

```
manuscript/main.tex (SOURCE OF TRUTH)
  ├── output/tables/*.tex (derived from Stata/Python scripts)
  ├── output/figures/*.pdf (derived from Stata/Python scripts)
  ├── manuscript/references.bib (shared bibliography)
  └── code/ (implements what the paper describes)

NEVER let code results and paper claims diverge.
ALWAYS update the paper when results change.
```

---

## Consistency Protocol

Before committing any change that affects results:

1. Run the relevant pipeline step(s) via `run_all.sh`
2. Check that output tables/figures are updated
3. Verify the manuscript references match the current output files
4. If a number in the paper text came from a table, verify it still matches

---

## Content Fidelity Checklist

```
[ ] Every \input{} table file exists and is current
[ ] Every \includegraphics{} figure file exists and is current
[ ] Numbers cited in text match the corresponding table cell
[ ] All citation keys resolve to bibliography entries
[ ] Notation is consistent throughout the paper
[ ] Abstract accurately reflects current results
```
