---
name: interview-me
description: Interactive interview to formalize a research idea into a structured specification with hypotheses and empirical strategy
disable-model-invocation: true
argument-hint: "[brief topic or 'start fresh']"
allowed-tools: ["Read", "Write"]
---

# Research Interview

Conduct a structured interview to help formalize a research idea into a concrete specification.

**Input:** `$ARGUMENTS` -- a brief topic description or "start fresh" for an open-ended exploration.

## How This Works

This is a **conversational** skill. Ask questions directly in your text responses, one or two at a time. Wait for the user to respond before continuing.

## Interview Structure

### Phase 1: The Big Picture (1-2 questions)
- "What phenomenon or puzzle are you trying to understand?"
- "Why does this matter? Who should care about the answer?"

### Phase 2: Theoretical Motivation (1-2 questions)
- "What's your intuition for why X happens / what drives Y?"
- "What would standard theory predict?"

### Phase 3: Data and Setting (1-2 questions)
- "What data do you have access to?"
- "Is there a specific context or institutional setting?"

### Phase 4: Identification (1-2 questions)
- "Is there a natural experiment or source of variation you can exploit?"
- "What's the biggest threat to a causal interpretation?"

### Phase 5: Expected Results (1-2 questions)
- "What would you expect to find?"
- "What would the results imply for policy or theory?"

### Phase 6: Contribution (1 question)
- "How does this differ from what's already been done?"

## After the Interview

Produce a **Research Specification Document** and save to `quality_reports/research_spec_[sanitized_topic].md`.

## Interview Style

- **Be curious, not prescriptive.**
- **Probe weak spots gently.**
- **Build on answers.**
- **Know when to stop.**
