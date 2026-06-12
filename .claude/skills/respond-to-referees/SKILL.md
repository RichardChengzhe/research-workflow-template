---
name: respond-to-referees
description: Generate a structured response-to-referees document from a referee report and the revised manuscript. Maps each referee comment to the specific revision, classifies coverage (addressed / partially / deferred / disagreement), and drafts polite but firm responses. Use during the R&R (revise-and-resubmit) stage of paper revision at a finance/accounting journal.
argument-hint: "[referee-report-path] [revised-manuscript-path] [--no-verify]"
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash", "Task"]
effort: high
---

# Respond to Referees

Produce a complete response-to-referees document by cross-referencing the referee report against the revised manuscript. Classify every concern, draft a courteous response for each, and flag anything unaddressed before submission. Calibrated to the conventions of a top finance/accounting journal (*JF*, *RFS*, *JFE*, *JAR*, *TAR*, *JAE*): editors there expect the response letter to map one-to-one onto the report, point to specific tables/pages, and never hand-wave a deferral.

## Inputs

- `$0` — path to the referee report (often the editor's letter plus 1-3 referee reports concatenated)
- `$1` — path to the revised manuscript

Supported formats and how to read them. In the commands below, `FILE` stands for the input path being converted — either `$0` (referee report) or `$1` (revised manuscript). Always use `mktemp` for the temp file (not a predictable `/tmp/...` name) so paths with spaces and concurrent runs don't collide, and so untrusted `FILE` paths can't clobber other temp files via symlink races.

| Format | How to extract text |
| --- | --- |
| `.tex`, `.md`, `.txt` | Read directly with the `Read` tool. |
| `.pdf` | `TMP=$(mktemp --suffix=.txt) && pdftotext "FILE" "$TMP"` (poppler-utils; use `mktemp -t ...` on macOS if `--suffix` is unsupported). Grep `"$TMP"`. |
| `.docx` | `TMP=$(mktemp --suffix=.txt) && pandoc "FILE" -t plain -o "$TMP"` (or `docx2txt "FILE" "$TMP"`). Grep `"$TMP"`. |
| `.html` | `TMP=$(mktemp --suffix=.txt) && pandoc "FILE" -t plain -o "$TMP"`. Grep `"$TMP"`. |

If a required tool is missing or extraction fails, ask the user to provide a plain-text version (`.txt` or `.md`) and stop.

## Workflow

### Step 0: Convert Inputs to Plain Text

Before any parsing or grep, convert non-text inputs (`.pdf`, `.docx`, `.html`) to plain text using the table above. Keep both the temp text file (for grep) and the original (for citation page references). For a `.tex` manuscript, you can grep the source directly, but note table/figure numbers come from `\label{}` / `\ref{}`, not page numbers — capture the label and the section.

### Step 1: Parse the Referee Report

1. Read the report end-to-end.
2. Decompose into discrete numbered concerns. Common patterns:
   - Numbered or bulleted enumerations ("1.", "(a)", "Comment 1", etc.).
   - Section headers ("Major comments", "Minor comments").
   - Implicit concerns embedded in prose paragraphs — extract these too. Editors' cover letters often bury a make-or-break ask ("the identification needs a cleaner shock") in a single sentence.
3. For each concern, capture:
   - **Concern ID** (R{n}.{m} = referee n, comment m; use E.{m} for the editor's own asks)
   - **Severity** the referee assigned (major / minor / typographic)
   - **Verbatim quote** of the most representative sentence (~25 words max)
   - **One-line summary** in your own words

### Step 2: Locate Each Concern in the Revised Manuscript

For every concern:

1. Extract the key terms from the referee's wording (e.g. "clustered standard errors", "parallel trends", "pre-event CARs", "winsorization").
2. `Grep` the **plain-text version** of the revised manuscript for those terms (and synonyms). Note: Grep only works on text — if the original was any non-text format (for example, `.pdf`, `.docx`, or `.html`), grep the converted temp file from Step 0.
3. `Read` the surrounding context (±20 lines) to confirm the change addresses the concern. A new robustness table or an added paragraph in the identification section is the kind of evidence to point to.
4. Note the page/section/line numbers in the **original** file (or the `\label` of the table/figure) for the response document.

### Step 3: Classify Coverage

Assign one of four labels to each concern:

| Label | Meaning |
| --- | --- |
| **Addressed** | The revision directly resolves the concern with a specific change you can point to (a new table, a re-estimated specification, an added subsection). |
| **Partially addressed** | The revision moves in the requested direction but does not fully resolve the concern (e.g., added one robustness check when the referee asked for two; clustered one way when the referee wanted two-way). |
| **Deferred** | The revision does not change the manuscript on this point but the response will explain why (out of scope, a separate paper, a request that conflicts with another referee, data not available for the period). |
| **Disagreement** | The author respectfully disagrees with the referee's premise. The response will explain the reasoning (with a citation or a robustness result) and any compromise. |

If you cannot find any evidence of a revision OR a deliberate decision to defer/disagree, mark the concern **UNADDRESSED — REQUIRES AUTHOR INPUT** and surface it in the warning summary at the end.

### Step 4: Draft Each Response

For every concern, write a 3-6 sentence response in this structure:

1. **Acknowledge** the concern (one sentence, no paraphrasing flattery).
2. **State the change** (or the reason for not changing) — name the new table/figure/specification.
3. **Point to the location** in the revised manuscript (page, section, line range, or `Table N` / `Figure N` reference).
4. **(Optional) Justify** the choice if the change diverges from the referee's exact ask (e.g., "we report Newey-West rather than two-way clustering because the panel is monthly and the time dimension is short").

Tone conventions: courteous but firm; never defensive; never quote the referee back at length; use "we" for the author team; avoid "the referee is wrong" — prefer "we respectfully retain our original framing because…". When you disagree, win with evidence, not assertion: cite a paper, add a robustness column, or show the result is unchanged under the referee's preferred specification.

### Step 5: Produce the Response Document

Write the output to `response-to-referees.md` (matching the template filename) or a path the user specifies. Use the structure in [`templates/response-to-referees.md`](../../../templates/response-to-referees.md):

1. **Header** — journal, manuscript ID, revision round, date.
2. **Cover paragraph** — one paragraph thanking the editor and referees, summarizing the major changes at a high level (the 2-3 new analyses that move the paper).
3. **Per-referee sections** — for each referee, a numbered list of responses produced in Step 4. A common convention is to reproduce each comment in *italics* followed by the response in roman.
4. **Concern matrix** — at the end, a single table summarizing every concern, classification, and response location for editor convenience.

### Step 5.5: Post-Flight Verification (MANDATORY, CoVe)

The response document's most hallucination-prone content is the set of "we added X in Table Y / on page Z" claims. Hallucinating these gets a paper desk-rejected on sight — the editor checks. Before declaring the response document final, run the Post-Flight Verification protocol from [`.claude/rules/post-flight-verification.md`](../../rules/post-flight-verification.md).

**Steps:**

1. **Extract revision-location claims** — every "we added / we modified / we revised X (Table Y / page Z / Section N)" assertion in the response document.
2. **Generate verification questions** — "Does the revised manuscript actually contain the revision claimed at Table Y / page Z? Does it match the description?"
3. **Spawn `claim-verifier`** via `Task` with `subagent_type=claim-verifier` and `context=fork`. Hand it: the claims table, the verification questions, the path to the revised manuscript (and any cited estimation `.log`/`.tex` if the response quotes a new t-stat or coefficient). Do NOT include the response draft.
4. **Reconcile:** PASS → attach green block. PARTIAL / FAIL → rewrite the affected response entries using the verifier's evidence. A response that says "we added robustness check X in Table 7" when X is actually in Table 5 (or not at all) is worse than an honest "Deferred" classification.

Downgrade to the classification the evidence supports:

- Claim verified at location → `Addressed`
- Claim verified at a different location → update the location in the response
- Claim not verifiable in manuscript → downgrade to `Partially addressed` or `Deferred` with an honest rationale

Opt-out: `--no-verify` flag. Not recommended — the referee will run this check themselves.

### Step 6: Warning Summary (MANDATORY)

After the document is written, include this summary in your **final chat message to the user** (NOT inside the response document):

```
## Unaddressed concerns requiring author input

- R1.3: [summary] — no evidence of revision found
- R2.7: [summary] — flagged as deferred but no rationale yet drafted
```

If everything is covered, the final message should say `All concerns addressed or explicitly classified.`

## Output Files

- `response-to-referees.md` — the deliverable (filename matches `templates/response-to-referees.md`)
- (Optional) `response-to-referees-matrix.csv` — machine-readable concern-to-response mapping for tracking across revision rounds

## Pre-submission rehearsal

**Tip.** Before drafting your response, consider running `/review-paper --peer --r2 <journal>` on the *revised* manuscript first. It simulates the next referee round against your revisions — catching the "Resolved / Partial / Not addressed" classification mistakes before the real referee does. See [`.claude/skills/review-paper/SKILL.md`](../review-paper/SKILL.md).

## Cross-References

- For first-pass manuscript review **before** receiving referee comments, use `/review-paper`.
- For substantive content audits during revision (identification stress test, code-theory alignment), invoke the `domain-reviewer` agent or `/review-paper --peer <journal>`.
- For independent fact-checking of any new numeric claims you cite back to the referee, use `/verify-claims`.
- Save the response to `quality_reports/` if you want a permanent record alongside other quality reports.

## Verification

Before reporting completion:

1. Confirm every concern has a classification (no orphans).
2. Confirm every "Addressed" or "Partially addressed" classification cites a specific page/section/table/figure.
3. Confirm the warning summary was emitted (even if empty).
4. Confirm the cover paragraph names the journal and manuscript ID correctly.
