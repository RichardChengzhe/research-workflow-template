# Response to Referees: [Manuscript Title]

> Companion template for the `/respond-to-referees` workflow. That skill
> parses the referee report, locates each change in the revised manuscript,
> and fills this document in. Calibrated to top finance/accounting/econ
> journals (*JF*, *RFS*, *JFE*, *JAR*, *TAR*, *JAE*, *MS*, *AER*, *QJE*):
> the response letter must map one-to-one onto the report, point to specific
> tables/sections (by `\label`, not page number, for a LaTeX manuscript),
> and never hand-wave a deferral.

**Journal:** [Journal Name]
**Manuscript ID:** [JOURNAL-YYYY-NNNN]
**Revision round:** R[1/2/3]
**Date:** [YYYY-MM-DD]
**Authors:** [Author 1, Author 2, ...]

---

## Cover Letter to the Editor

Dear [Editor Name],

We thank you and the referees for the thoughtful reviews of our manuscript "[Title]." We have revised the paper substantially in response. The most important changes are:

1. [High-level change 1 — one sentence]
2. [High-level change 2 — one sentence]
3. [High-level change 3 — one sentence]

A detailed point-by-point response follows. Changes in the manuscript are highlighted in [color / track-changes — e.g. the red `\textcolor{red}{}` change-marks].

Sincerely,
[Author names]

---

## Response to the Editor

> Use `E.{m}` for the editor's own asks (an editor's cover letter often buries a make-or-break request — a cleaner identification, an added robustness table — in a single sentence; pull these out and answer them explicitly).

### E.1 — [One-line summary of the editor's request]

**Editor comment (verbatim, abbreviated):**
> [Quote, ~25 words max]

**Classification:** Addressed / Partially addressed / Deferred / Disagreement

**Response:**

[3–6 sentences.]

**Location of revision:** [Section / `\label{tab:...}` / `\label{fig:...}` / lines A–B]

---

## Response to Referee 1

### R1.1 — [One-line summary of concern]

**Referee comment (verbatim, abbreviated):**
> [Quoted text, ~25 words max]

**Classification:** Addressed / Partially addressed / Deferred / Disagreement

**Response:**

[3–6 sentences. Acknowledge the concern, state the change, point to the location (section / table / figure), justify if needed. For an empirical concern — clustering, parallel trends, winsorization, look-ahead bias — point to the specific new column, robustness table, or appendix that answers it.]

**Location of revision:** [Section / `\label{tab:...}` / `\label{fig:...}` / lines A–B]

---

### R1.2 — [Summary]

**Referee comment:**
> [Quote]

**Classification:** ...

**Response:** ...

**Location of revision:** ...

---

[Repeat for every R1.* concern]

---

## Response to Referee 2

[Same structure as Referee 1, using `R2.{m}` IDs]

---

## Concern Matrix

| ID | Severity | Summary | Classification | Location |
| --- | --- | --- | --- | --- |
| E.1 | Major | [Summary] | Addressed | §2.1, `tab:main` |
| R1.1 | Major | [Summary] | Addressed | §2.1, ll.95–110 |
| R1.2 | Major | [Summary] | Partially addressed | §3.2 |
| R1.3 | Minor | [Summary] | Addressed | Footnote 12 |
| R2.1 | Major | [Summary] | Disagreement | (see response) |
| R2.2 | Minor | [Summary] | Addressed | `tab:robust` |

---

## Summary of Major Changes

- [Change 1, with reference to which concerns it addresses]
- [Change 2]
- [Change 3]

## Notes for the Editor

[Optional: anything the editor should know that does not fit a per-referee response — e.g., conflicting requests between referees and how you resolved them, or a new reproduction-archive deposit accompanying the revision.]
