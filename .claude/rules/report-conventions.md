---
paths:
  - "code/python/build_*report*.py"
  - "code/python/report_lib.py"
  - "templates/report-builder-template.py"
  - "output/**/*Report*.html"
---

# HTML Results-Report Conventions

Conventions for the project's HTML results reports (heatmaps + full regression
tables). The look mirrors the LaTeX manuscript and is enforced in code by
`code/python/report_lib.py`. See the `build-report` skill for the build workflow.

## One manuscript-spec main column

Main tables show exactly ONE specification column = the manuscript spec:
**industry + time fixed effects** (e.g. `absorb(sic3 mdate)`), **firm-clustered**
standard errors, and a **level** dependent variable. Do NOT place fm/2w or
ind/firm spec grids side by side in the main tables -- that is too much to digest.

## Show the Controls block

Full tables show the controls, not just the focal terms. Layout: focal /
hypothesis terms on top (shaded by sign x significance), then a labeled
**Controls** block, then a midrule, then `N` and adjusted `R^2`. Use
`report_lib.aea_table(rows=[...])` with `control: True` on control rows.

## t-statistics in parentheses -- never standard errors

Each estimate is two lines: coefficient + significance stars on top, `(t)` below.
Report t-stats, not SEs. Stars: `*` p<0.10, `**` p<0.05, `***` p<0.01
(|t| thresholds 1.645 / 1.96 / 2.576).

## Label changes vs levels explicitly

Write `&Delta;X` for a change / shock variable and `&times;` for an interaction
(e.g. `Treat &times; &Delta;Shock`). Never leave a regressor's level-vs-change
status ambiguous in a row label or a note. **Levels are the default** for
outcomes that have a level/change choice; changes are robustness.

## Consolidated robustness section

Put 2-way clustering (firm + time), firm-FE, and change-DV variants in ONE
compact section as EXTRA t-stat columns under the headline coefficient
(Default t | 2-way t | firm-FE t | Change-DV t) -- not as separate full-table
grids. In the AEA tables, the inline 2-way `[t]` is rendered via
`aea_table(..., dual_cluster=True)`.

## Full tables for ALL tests

Every test/section gets a full regression table with all coefficients. Do not
abbreviate later tests into summary rows just because earlier ones were full.

## Each major revision = a new `vN` report

Substantive revisions create a NEW builder + output
(`build_<topic>_report_v2.py` -> `<Topic>Report_v2.html`); the prior version
stays frozen as a reference point. Never edit a prior report's builder or HTML.

## Clickable heatmaps are mandatory (when both present)

When a report has BOTH heatmaps AND full tables, every colored heat cell links to
its full table and every full table is reachable from a heat cell. Build the heat
cell's `anchor=` and the table's `anchor=` from `report_lib.anchor_id(...)` with
the same keys in the same order, and run `report_lib.verify_anchor_links(path)`
before delivery (zero broken links, zero orphan ids). Also audit fail cells:
`grep -c 'class="fail"'` on the output must be 0 (or each `fail` documented).
