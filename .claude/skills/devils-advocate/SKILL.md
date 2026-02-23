---
name: devils-advocate
description: Challenge research design with 5-7 critical questions. Checks identification strategy, data adequacy, and potential threats to validity.
disable-model-invocation: true
argument-hint: "[manuscript section or research design description]"
allowed-tools: ["Read", "Grep", "Glob"]
---

# Devil's Advocate Review

Critically examine a research design and challenge it with 5-7 specific questions.

**Philosophy:** "We arrive at the best possible research design through active dialogue."

---

## Setup

1. **Read the target file** (the manuscript section or research design)
2. **Read related materials** (pipeline.md, params.do, existing results)
3. If applicable, **check related literature** in `master_supporting_docs/`

---

## Challenge Categories

Generate 5-7 challenges from these categories:

### 1. Identification Challenges
> "Could this correlation be driven by X rather than your proposed mechanism?"

### 2. Data Adequacy Challenges
> "Is your sample large enough / representative enough to detect this effect?"

### 3. Specification Challenges
> "What happens if you use alternative functional form / different controls / different FEs?"

### 4. External Validity Challenges
> "Would this result generalize beyond your specific setting?"

### 5. Measurement Challenges
> "Is your outcome variable actually measuring what you claim it measures?"

### 6. Alternative Explanation Challenges
> "Here are 2 other mechanisms that could explain your results."

### 7. Policy Relevance Challenges
> "Even if the effect is causal, does the magnitude matter for policy?"

---

## Output Format

```markdown
# Devil's Advocate: [Research Design / Section]

## Challenges

### Challenge 1: [Category] -- [Short title]
**Question:** [The specific question]
**Why it matters:** [What could go wrong if not addressed]
**Suggested resolution:** [Specific action -- test, robustness check, discussion]
**Severity:** [High / Medium / Low]

[Repeat for 5-7 challenges]

## Summary Verdict
**Strengths:** [2-3 things done well]
**Critical changes:** [0-2 changes before submitting]
**Suggested improvements:** [2-3 nice-to-have improvements]
```

---

## Principles

- **Be specific:** Reference exact specifications and data features
- **Be constructive:** Every challenge has a suggested resolution
- **Be honest:** If the design is sound, say so
- **Prioritize:** Identification threats > measurement issues > presentation
- **Think like a skeptical referee**
