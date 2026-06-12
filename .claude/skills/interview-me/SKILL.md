---
name: interview-me
description: Interactive interview to formalize a research idea into a structured specification with hypotheses and empirical strategy
disable-model-invocation: true
argument-hint: "[brief topic or 'start fresh'] [--no-verify]"
allowed-tools: ["Read", "Write", "Task"]
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

## Post-Flight Verification (MANDATORY when the spec cites sources)

If the Research Specification Document references **any papers, datasets, or institutional facts** asserted as true, run the Post-Flight Verification protocol from [`.claude/rules/post-flight-verification.md`](../../rules/post-flight-verification.md) before handing the spec back:

1. Extract every citation / dataset / factual claim the spec asserts (skip the user's own opinions and forward-looking design choices).
2. Write one specific verification question per claim.
3. Spawn `claim-verifier` via `Task` with `subagent_type=claim-verifier` and `context=fork`, passing the claims + questions + source pointers. The fresh fork is the CoVe independence trick.
4. Reconcile: PASS -> return as-is; PARTIAL -> flag unverified claims; FAIL -> correct the affected text (max 2 attempts) before surfacing a warning.

Opt-out: `--no-verify` skips Post-Flight. If the spec cites no external sources, Post-Flight is a no-op.
