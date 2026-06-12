# Journal Profile Template

Copy this block into `.claude/references/journal-profiles.md` (under the appropriate field/region section) and fill in every field. Weights for the 6 dispositions must sum to 1.0.

```markdown
### Journal Full Name (SHORT)

**Short name:** `SHORT`

**Focus.** [1-2 sentences: what this journal publishes and what it does NOT publish.]

**Bar.** [1-2 sentences: what it takes to clear the desk. Mention acceptance rate if known.]

**Domain-referee adjustments.**
- Contribution 30 → [new] ([reason])
- Lit positioning 25 → [new] ([reason])
- Substance 20 → [new] ([reason])
- External validity 15 → [new] ([reason])
- Fit 10 → [new] ([reason])

**Methods-referee adjustments.**
- Identification [default] → [new] ([reason, e.g., "identification bar is higher at this journal"])
- Replication [default] → [new] ([reason, e.g., "mandatory reproduction archive at acceptance"])
- [Paper-type-specific: e.g., "If paper type is `structural`: Parameter ID 30 → 35"]

**Typical concerns.** (3-5 direct-quote questions this journal's referees ask)
- "[Quote]"
- "[Quote]"
- "[Quote]"

**Referee-pool weights.** (must sum to 1.0)
- STRUCTURAL: 0.__
- CREDIBILITY: 0.__
- MEASUREMENT: 0.__
- POLICY: 0.__
- THEORY: 0.__
- SKEPTIC: 0.__

**Data / AI policy.** [Reproducibility-archive posture and generative-AI-use posture, each with a "verify at submission" flag. E.g., "Mandatory reproduction archive at acceptance (verify on the journal's Data and Code Sharing Policy page); AI-use disclosure required for substantive content (verify current policy)." These are *priors for referee calibration*, not compliance statements — see the currency caveat in `journal-profiles.md`.]

**Table format override.** [Optional: any journal-specific formatting rule. E.g., "No significance stars", "Three-decimal point estimates", or "t-statistics in parentheses, not standard errors". Leave "None specific" if no override.]

---
```

## Disposition reference

The 6 dispositions used across the `--peer` pipeline:

| Disposition | Prior |
|---|---|
| STRUCTURAL | "Where's the mechanism? Where's the model?" |
| CREDIBILITY | "Show me pre-trends. What's the experiment / clean shock?" |
| MEASUREMENT | "How is this constructed? What about attrition / construct validity / look-ahead?" |
| POLICY | "Does this apply outside your sample / period? So what?" |
| THEORY | "What does the theory predict?" |
| SKEPTIC | "What would make this go away?" |

These dispositions are deliberately field-general. For a discipline outside finance/accounting/econ, they should still apply — adjust the weights, not the labels.

## Paper types

The `methods-referee` agent branches on paper type. The default types (empirical-finance-centric) are:

- `reduced-form` — DiD, IV, RD, event study, panel with fixed effects, etc.
- `structural` — structural estimation, GMM, calibrated GE / asset-pricing models, etc.
- `theory+empirics` — theoretical model with an empirical test of its predictions.
- `descriptive` — measurement, data construction, pattern documentation (e.g., a new sentiment/text measure validated against returns).

To add a paper type, duplicate the matching rubric block in `.claude/agents/methods-referee.md` and edit the dimension weights.

## Cross-references

- `.claude/references/journal-profiles.md` — the live calibration file (finance / accounting / econ venues).
- `.claude/agents/editor.md` — reads profiles, draws referee dispositions.
- `.claude/skills/review-paper/SKILL.md` — entry point for `--peer [SHORT]`.
- `.claude/skills/submission-disclosures/SKILL.md` — turns the data/AI-policy line into a submission-ready disclosure.
