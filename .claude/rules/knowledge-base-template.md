---
paths:
  - "manuscript/**/*.tex"
  - "code/**/*.do"
  - "code/**/*.py"
  - "code/**/*.sas"
---

# Project Knowledge Base: [YOUR PROJECT NAME]

<!-- Fill in the tables below with YOUR project-specific content.
     Claude reads this before constructing variables, writing tables, or drafting claims.
     This is the project's single source of truth for notation, variables, data, and known traps.
     Keep it current -- a stale registry is worse than none. -->

## Notation Registry

| Symbol | Meaning | LaTeX | Anti-Pattern (do not write) |
|--------|---------|-------|------------------------------|
| | | | |

## Variable / Estimand Registry

The canonical definition of every constructed variable and every reported estimand.

| Name | Definition (exact) | Source / formula | Constructed in | Notes (scaling, winsorization, units) |
|------|--------------------|------------------|----------------|----------------------------------------|
| | | | | |

## Data-Source Registry

| Source | Coverage (years, universe) | Key id(s) | Merge key | Access / license notes |
|--------|----------------------------|-----------|-----------|------------------------|
| | | | | |

## Sample Construction

| Step | Filter applied | Rows after | Rationale |
|------|----------------|-----------:|-----------|
| 0 | Raw extract | | |
| 1 | | | |

## Specification Registry

The headline specification(s) every table is compared against.

| Table | Outcome | Treatment / focal regressor | Fixed effects | Clustering | Sample |
|-------|---------|------------------------------|---------------|-----------|--------|
| | | | | | |

## Tolerance Thresholds

| Quantity | Tolerance | Rationale |
|----------|-----------|-----------|
| Point estimates | | |
| Standard errors | | |
| Sample sizes (N) | Exact | No reason for a difference |

## Anti-Patterns (Don't Do This)

| Anti-Pattern | What Happened | Correction |
|--------------|---------------|-----------|
| | | |

## Code Pitfalls (Stata / Python / SAS)

| Bug | Impact | Fix |
|-----|--------|-----|
| | | |

<!-- For DiD / event-study projects, also register: group variable (first-treated period), never-treated coding,
     control-group choice (never- vs not-yet-treated), and the aggregation used for the headline ATT.
     See .claude/rules/did-conventions.md. -->
