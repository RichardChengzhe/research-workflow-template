# MEMORY.md -- Persistent Project Learnings

Save reusable knowledge here with `[LEARN:category]` tags.
Review before starting tasks. Keep under 200 lines.

---

## Workflow Patterns

- [LEARN:workflow] Requirements spec catches ambiguity, reduces rework 30-50%. Use for complex/ambiguous tasks.
- [LEARN:workflow] Spec-then-plan protocol: MUST/SHOULD/MAY with clarity status (CLEAR/ASSUMED/BLOCKED).
- [LEARN:workflow] Context survival before compression: MEMORY.md + session log + plan on disk + open questions documented.
- [LEARN:workflow] Plan-first for non-trivial tasks (>3 files, >1 hour, multi-step). Save plans to quality_reports/plans/.
- [LEARN:workflow] Pipeline tracing before modifying scripts: check upstream inputs AND downstream consumers.

## Code Standards

- [LEARN:stata] All Stata paths via globals from 00_run.do. Never hardcode absolute paths.
- [LEARN:stata] params.do holds all research parameters. Check before using hardcoded values.
- [LEARN:stata] Use reghdfe for high-dimensional FE. eststo/esttab for tables. graph export for figures.
- [LEARN:python] PEP 8 compliance. Type hints on public functions. Relative paths via pathlib.Path.
- [LEARN:python] matplotlib + seaborn for figures. pandas for data. statsmodels/linearmodels for regression.

## Quality Standards

- [LEARN:quality] 80/90/95 thresholds: commit/PR/excellence.
- [LEARN:quality] Publication figures: 300 DPI, explicit dimensions, vector (PDF) preferred.
- [LEARN:quality] Every script run produces a log in output/logs/ via run_all.sh. Always read the log.

## Skill Creation

- [LEARN:skills] Trigger phrases matter in skill descriptions -- include specific scenarios when skill applies.
- [LEARN:skills] Skills need Instructions + Examples + Troubleshooting to be useful.

<!-- Add project-specific learnings below as you work -->
