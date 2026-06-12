---
name: build-report
description: |
  Build a publication-style HTML results report (heatmaps + full AEA regression
  tables) that mirrors the LaTeX manuscript look, with clickable heatmap-to-table
  links and a fail-cell audit.
  Triggers: "build report", "html report", "results report", "regression report",
  "StoryReport", "RobustnessReport", "ProbeReport".
  Use whenever results need to be assembled into a shareable HTML document for a
  coauthor, meeting, or review.
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---

# Build Report

Assemble regression results into a self-contained HTML report whose look mirrors
the LaTeX manuscript (serif body, booktabs horizontal rules only, AEA `Notes:`
blocks, two-line `coef` / `(t)` cells, focal terms shaded by sign x significance).

**Do not hand-roll CSS or table HTML.** All look-and-feel lives in the reusable
module `code/python/report_lib.py` -- import it and call its functions so every
report stays visually and structurally identical. Start from the runnable
reference builder `templates/report-builder-template.py`.

## When to use

A report needs this skill when it has BOTH a scan-friendly heatmap (one t-stat
per cell) AND detail-rich full tables (multi-coefficient breakdown per
combination). If it has only one of the two, the grid CSS still helps but the
clickable-link step is unnecessary.

## Canonical structure (in this order)

1. **Title + date subtitle** -- `<h1>` + `<p class="sub">` with: N regressions,
   commit SHA, branch, and a one-line pipeline/spec citation.
2. **Executive summary** -- a single `finding_box(...)` (green) with the headline.
   No top-N table.
3. **TOC** -- `toc([(anchor, label), ...])`.
4. **Variable definitions** -- focal var(s), the `&Delta;Shock` (state it is a
   CHANGE, not a level), controls, horizon definitions.
5. **Heatmaps** -- group related heat tables with `heat_grid([...])` (packs 2-3
   per row). Each colored cell is built with `hcell(t, anchor=anchor_id(...))`.
6. **Model spec** -- `model_box(...)` with the estimating equation.
7. **Full AEA tables** -- one `aea_table(...)` per combination, wrapped in an
   `<div class="aea-grid">`. Each table's `anchor=` MUST equal the matching heat
   cell's link (build both from `anchor_id(...)` with the same keys, same order).
   When tables live in `<details>`, use `<details open>` so `:target` auto-scrolls.
8. **Reading guide** -- `shape-guide`/`finding` box: primary vs secondary cell,
   the |t| thresholds (1.645 / 1.96 / 2.576), the 2-way `[t]` robustness rule,
   and a multiple-testing caution.
9. **Caveats + provenance footer** -- bulleted caveats with citations (Petersen
   2009 RFS; Cameron-Gelbach-Miller 2011), then `provenance_footer({...})`
   (commit, branch, results CSV, do-files / scripts).

## Table & report conventions (see `.claude/rules/report-conventions.md`)

- ONE manuscript-spec main column: industry+time FE, firm cluster, **level** DV.
  Do not show fm/2w or ind/firm grids side by side in the main tables.
- Full tables show the **Controls** block (focal terms on top, a labeled Controls
  block below, then N + adj-R^2) -- not just the focal coefficients.
- **t-statistics in parentheses, never standard errors.** Coef + stars on top,
  `(t)` below; add `[t2]` (2-way) only via `dual_cluster=True`.
- Label changes vs levels explicitly: write `&Delta;X` for a change/shock; `&times;`
  for an interaction. Never leave a regressor's level/change status ambiguous.
- Consolidated robustness: 2-way cluster, firm-FE, and change-DVs as EXTRA t
  columns in one compact section -- not separate full grids.
- **Full tables for ALL tests** -- never abbreviate later tests into summary rows.

## Versioning (`vN`) -- never modify a prior report

Each major revision = a NEW builder + a NEW output file
(`build_<topic>_report_v2.py` -> `<Topic>Report_v2.html`). Copy the prior builder
as the starting template, preserve reused section HTML byte-for-byte, add new
sections. Leave `v1` frozen as a reference point; a coauthor may have it open.

## Fail-cell audit (run before delivery)

Missing/non-PSD heat cells render as `class="fail"` (gray `.`). They must be
filled or explicitly justified:

```bash
grep -o 'class="fail"' output/<Topic>Report_vN.html | wc -l    # count missing cells
```

If the count is non-zero: locate the missing combinations, run the fill
regression(s) to populate the results CSV, rebuild, and re-audit. Repeat until
the count is zero (or each remaining `fail` is documented as genuinely
non-estimable, e.g. a non-PSD 2-way variance).

## Clickable-heatmap requirement (MANDATORY when both present)

Every colored heat cell links to its full table, and every full table is reached
from a heat cell. Enforce it in code, then verify before delivery:

```python
import report_lib as R
counts = R.verify_anchor_links("output/<Topic>Report_vN.html")   # raises on any
# broken (a link with no table) or orphan (a table no heat cell points at)
print(counts)   # {'links': N, 'ids': N, 'broken': [], 'orphans': []}
```

Or from the shell:

```bash
python -c "import sys; sys.path.insert(0,'code/python'); import report_lib as R; \
print(R.verify_anchor_links('output/<Topic>Report_vN.html'))"
```

Required result: zero broken links, zero orphan ids.

## Workflow

1. Copy `templates/report-builder-template.py` to
   `code/python/build_<topic>_report_v1.py`.
2. Point `RESULTS_CSV` at your results (schema documented at the top of the
   template) and set `DVS`, `HORIZONS`, `SAMPLE`, `SENTIMENT`, `CTRL_LABELS`.
3. Build the heat-grid and the full AEA tables (reuse the template's section
   builders; add sections as needed).
4. Run it: `python code/python/build_<topic>_report_v1.py`.
5. Fail-cell audit (`grep class="fail"`) -> fill -> re-audit until zero.
6. Confirm `report_lib.verify_anchor_links` passes (the builder already calls it).
7. Open the HTML, sanity-check a few cells link to the right tables, deliver.

## Key files

| File | Role |
|------|------|
| `code/python/report_lib.py` | Reusable module: CSS + cell/table/grid/anchor/verify functions. Single source of the look. |
| `templates/report-builder-template.py` | Runnable reference builder (copy & adapt). |
| `.claude/rules/report-conventions.md` | The one-spec / controls / t-in-parens / `vN` / clickable rules. |

## Verification

- `python code/python/report_lib.py` prints `OK` (smoke test, 0 broken/orphan).
- The builder prints `broken=0, orphans=0`.
- `grep -c 'class="fail"'` on the output is 0 (or every `fail` is documented).
