---
name: research-ideation
description: Generate structured research questions, testable hypotheses, and empirical strategies from a topic or dataset
disable-model-invocation: true
argument-hint: "[topic, phenomenon, or dataset description]"
allowed-tools: ["Read", "Grep", "Glob", "Write"]
---

# Research Ideation

Generate structured research questions, testable hypotheses, and empirical strategies from a topic, phenomenon, or dataset.

**Input:** `$ARGUMENTS` -- a topic (e.g., "minimum wage effects on employment"), a phenomenon (e.g., "why do firms cluster geographically?"), or a dataset description (e.g., "panel of US counties with pollution and health outcomes, 2000-2020").

---

## Steps

1. **Understand the input.** Read `$ARGUMENTS` and any referenced files. Check `master_supporting_docs/` for related papers.

2. **Generate 3-5 research questions** ordered from descriptive to causal:
   - **Descriptive:** What are the patterns?
   - **Correlational:** What factors are associated?
   - **Causal:** What is the effect?
   - **Mechanism:** Why does the effect exist?
   - **Policy:** What are the implications?

3. **For each research question, develop:**
   - **Hypothesis:** A testable prediction with expected sign/magnitude
   - **Identification strategy:** How to establish causality
   - **Data requirements:** What data would be needed?
   - **Key assumptions:** What must hold?
   - **Potential pitfalls:** Common threats to identification
   - **Related literature:** 2-3 papers using similar approaches

4. **Rank the questions** by feasibility and contribution.

5. **Save the output** to `quality_reports/research_ideation_[sanitized_topic].md`

---

## Principles

- **Be creative but grounded.** Push beyond obvious questions, but every suggestion must be empirically feasible.
- **Think like a referee.** For each causal question, immediately identify the identification challenge.
- **Consider data availability.** A brilliant question with no available data is not actionable.
- **Suggest specific datasets** where possible.
