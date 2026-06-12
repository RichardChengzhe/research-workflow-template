<!-- Schema adapted (with attribution) from Hugo Sant'Anna's clo-author
     (github.com/hugosantanna/clo-author); journal-calibration schema credit: Hugo Sant'Anna.
     Profiles below are finance/accounting/econ venues. -->

# Journal Profiles

Calibration data for the `/review-paper --peer [journal]` simulated peer-review pipeline. Each profile tells the `editor` agent how to select referees (disposition-pool weights), what concerns that journal typically emphasizes, and any journal-specific formatting / data-policy conventions.

**How this file is used.** The `editor` agent reads this file before each `--peer` run, picks the requested `[journal]`, and uses its Referee-pool weights + Typical concerns to select two referees with *different* dispositions and to seed their pet-peeve priors. `domain-referee` and `methods-referee` then apply this profile's re-weights.

**Field.** This file ships **finance / accounting** venues as the primary set (the template's home discipline), plus two general-interest **econ** profiles (AER, QJE) because finance/accounting papers are routinely sent there. To add a venue, copy a profile block, fill the schema, and reference it by the short name you define. See [Field adaptation](#field-adaptation).

> **Currency caveat (read before relying on any policy line below).** Journal **data-availability, replication-archive, and generative-AI-use policies change frequently** and several of the policies cited here were updated in 2024–2025. Every data/AI-policy line in this file is a *starting prior for referee calibration*, not an authoritative compliance statement — **verify the current policy on the journal's own "Guide for Authors" / "Data and Code Sharing Policy" page at submission time.** The pipeline only uses these to pick referee dispositions; the binding policy is always the journal's live page.

---

## Schema

Every profile has these fields:

- **Short name** — the string you pass to `--peer [name]` (e.g., `JF`, `TAR`).
- **Focus** — what the journal publishes; what it doesn't.
- **Bar** — what it takes to clear the desk; typical acceptance-rate context.
- **Domain-referee adjustments** — how the substance referee re-weights its dimensions for this journal (e.g., "Contribution 30 → 35").
- **Methods-referee adjustments** — how the methods referee re-weights (e.g., "Identification 35 → 40").
- **Typical concerns** — 3–5 direct-quote questions a referee at this journal will ask.
- **Referee-pool weights** — probability weights over the 6 dispositions (STRUCTURAL / CREDIBILITY / MEASUREMENT / POLICY / THEORY / SKEPTIC). The editor draws two *different* dispositions from this distribution.
- **Data / AI policy** — the reproducibility-archive and generative-AI-use posture, with a "verify at submission" flag.
- **Table format override** (optional) — any journal-specific formatting rule.

---

## Reproducibility-archive landscape (finance / accounting / econ)

The disciplines differ sharply in how hard they gate on a replication package — this is load-bearing for the methods referee's `Replication` weight.

- **Mandatory reproduction archive at acceptance** (a data editor verifies the package reproduces every number): the **major finance journals** — *Journal of Finance* (AFA Data and Code Sharing Policy), *Journal of Financial Economics* (JFE Data and Code Sharing Policy), *Review of Financial Studies* (RFS Data Editors + RFS Dataverse; updated policy applies to submissions conditionally accepted on/after **Oct 1, 2025**), *Review of Finance* — and **Management Science** (INFORMS Code and Data Disclosure Policy). *Journal of Accounting Research* runs a code-and-data-sharing policy plus a **Registered Reports** track (the first accounting journal to do so). Treat these like the econ AEA standard below: run [`/replication-package`](../skills/replication-package/SKILL.md) (which gates on [`/audit-reproducibility`](../skills/audit-reproducibility/SKILL.md)) before submission.
- **Encourage-but-not-require data sharing**: *The Accounting Review* (AAA — strongly encourages public data, requires author *vouching* for data integrity rather than a public archive) and *Journal of Accounting and Economics* (Elsevier — encourages data/code/materials sharing, not required). *Review of Accounting Studies* (Springer) follows the Springer research-data policy with a data-availability statement. For these, a missing archive is *not* a desk-level defect, but the integrity-vouching and a clear data-availability statement are expected.
- **Restricted / proprietary data** (CRSP, Compustat, IBES, TAQ, Capital IQ, bank-confidential): every policy above carves out an exemption — you deposit cleared **outputs + code + access instructions**, not the licensed data. Follow [`confidential-data.md`](../rules/confidential-data.md).

> **AEA Data Editor / DCAS policy (applies to AEA-imprint journals — AER, AEJ:*, JEL, JEP — if you target one).** Acceptance is conditional on a replication package that clears the **AEA Data and Code Availability Standard** under the Data Editor: a complete openICPSR deposit, a data-availability statement, and code that reproduces every reported number. Econometrica and ReStud enforce comparable archives at acceptance.

> **Generative-AI-use disclosure (all venues, fast-moving).** Across the major publishers (Elsevier, Wiley, Springer Nature, INFORMS, AAA), the converging norms are: **AI cannot be listed as an author**; authors are fully responsible for all content; **routine language polishing is typically exempt** while **substantive AI-assisted content generation must be disclosed**, usually in a dedicated statement naming the tool. Exact wording and thresholds differ by journal and change often — **verify the journal's current AI-use policy at submission** and write the disclosure to its template. See [`submission-disclosures`](../skills/submission-disclosures/SKILL.md).

---

## Finance

### Journal of Finance (JF)

**Short name:** `JF`

**Focus.** Flagship general finance (AFA). Asset pricing, corporate finance, banking, household finance, market microstructure. Rewards a clean, important question with a credible research design and an economically meaningful magnitude over methodological flash.

**Bar.** "The whole field will see this." Contribution must be crisp in one paragraph and matter beyond a subliterature. Top-3 finance journal; acceptance in the low single digits.

**Domain-referee adjustments.**
- Contribution 30 → 35 (importance bar is high)
- External validity 15 → 20 (does the result generalize beyond this sample/period?)

**Methods-referee adjustments.**
- Identification 35 → 40 (a credible design is load-bearing; "endogeneity" is the modal referee objection)
- Replication 5 → 10 (AFA Data and Code Sharing Policy is enforced at acceptance)

**Typical concerns.**
- "Is the question first-order for finance, or incremental to one subliterature?"
- "What is the identification, and what is the most obvious endogeneity / reverse-causality / omitted-variable threat?"
- "Are the standard errors clustered correctly for the panel, and does inference survive two-way clustering?"
- "Is the magnitude economically meaningful, or just statistically significant?"
- "Is the replication package complete enough for the AFA Data and Code policy?"

**Referee-pool weights.**
- CREDIBILITY: 0.35
- SKEPTIC: 0.20
- MEASUREMENT: 0.15
- STRUCTURAL: 0.15
- POLICY: 0.10
- THEORY: 0.05

**Data / AI policy.** AFA Data and Code Sharing Policy — reproduction package expected at acceptance (proprietary-data exemption: deposit code + access instructions). Standard publisher AI-disclosure norms. *Verify current at submission.*

**Table format override.** Significance stars conventional in finance (typically `* p<0.10, ** p<0.05, *** p<0.01`); SE or t-stats in parentheses (state which in the note). Report N, clustering, and FE for every regression.

---

### Journal of Financial Economics (JFE)

**Short name:** `JFE`

**Focus.** Top-3 finance (Elsevier). Strong corporate-finance and asset-pricing tradition; receptive to large-sample empirical work and to papers with a tight theory-to-test link. Less patient with a result that lacks an economic mechanism.

**Bar.** A clear contribution plus a defensible design. JFE referees push hard on whether the empirical pattern is the one the mechanism predicts.

**Domain-referee adjustments.**
- Contribution 30 → 33
- Substance 20 → 25 (the mechanism, not just the coefficient, must be convincing)

**Methods-referee adjustments.**
- Identification 35 → 40
- Robustness 15 → 18 (JFE referees expect the obvious alternative explanations addressed head-on)

**Typical concerns.**
- "What is the economic mechanism, and does the cross-sectional pattern line up with it?"
- "Is identification from a credible shock, or from a control-for-everything panel regression?"
- "Have the authors ruled out the leading alternative stories, or only the strawman?"
- "Is the sample/period selection innocuous, or could it drive the result (survivorship, delisting, data screens)?"

**Referee-pool weights.**
- CREDIBILITY: 0.30
- SKEPTIC: 0.20
- STRUCTURAL: 0.15
- MEASUREMENT: 0.15
- THEORY: 0.10
- POLICY: 0.10

**Data / AI policy.** JFE Data and Code Sharing Policy — reproduction package at acceptance (proprietary-data exemption applies). Standard publisher AI-disclosure norms. *Verify current at submission.*

**Table format override.** Significance stars conventional; report N, clustering, FE. Note the SE/t-stat choice.

---

### Review of Financial Studies (RFS)

**Short name:** `RFS`

**Focus.** Top-3 finance (SFS). Broad: asset pricing, corporate, banking, intermediation, fintech, household. Comparatively receptive to a structural model or a novel measurement contribution alongside reduced-form work.

**Bar.** A genuine advance in understanding, with a design a careful referee trusts. RFS runs an active Data Editors operation; a clean, reproducible package is part of the package.

**Domain-referee adjustments.**
- Contribution 30 → 33
- External validity 15 → 18

**Methods-referee adjustments.**
- Identification 35 → 38
- Replication 5 → 10 (RFS Data Editors verify reproduction; updated policy for submissions conditionally accepted on/after Oct 1, 2025)

**Typical concerns.**
- "What do we understand now that we didn't before — a new fact, a new mechanism, or a new measure?"
- "Is the identification or the structural assumption set credible and clearly stated?"
- "If this is a measurement contribution, is the measure validated against an external benchmark?"
- "Will the RFS Data Editors be able to reproduce every table from the package?"

**Referee-pool weights.**
- CREDIBILITY: 0.30
- MEASUREMENT: 0.20
- STRUCTURAL: 0.20
- SKEPTIC: 0.15
- THEORY: 0.10
- POLICY: 0.05

**Data / AI policy.** RFS Code and Data Sharing Policy — Data Editors reproduce the package at acceptance; deposit in RFS Dataverse + code in the RFS GitHub org (proprietary-data exemption applies). Updated policy applies to submissions conditionally accepted on/after **Oct 1, 2025**. Standard publisher AI-disclosure norms. *Verify current at submission.*

**Table format override.** Significance stars conventional; report N, clustering, FE.

---

### Journal of Financial and Quantitative Analysis (JFQA)

**Short name:** `JFQA`

**Focus.** Leading "second-tier-plus" finance journal (Cambridge UP / Michael G. Foster School). Empirical and quantitative finance across corporate, asset pricing, and microstructure. Receptive to solid, well-executed work that may be narrower than a JF/JFE/RFS lead paper.

**Bar.** A clean contribution with a sound design — the question need not be field-defining, but the execution must be tight and the result robust.

**Domain-referee adjustments.**
- Contribution 30 → 30 (unchanged; clarity over grand importance)
- Substance 20 → 22

**Methods-referee adjustments.**
- Identification 35 → 35 (unchanged)
- Robustness 15 → 20 (JFQA referees lean hard on robustness and specification sensitivity)

**Typical concerns.**
- "Is the result robust to obvious alternative specifications and subsamples?"
- "Is the contribution clearly delineated from the closest existing paper?"
- "Are the econometrics standard-correct (clustering, FE, overlapping-return overlap if long-horizon)?"
- "Is the economic magnitude reported and interpreted, not just the t-stat?"

**Referee-pool weights.**
- SKEPTIC: 0.25
- CREDIBILITY: 0.25
- MEASUREMENT: 0.15
- STRUCTURAL: 0.15
- THEORY: 0.10
- POLICY: 0.10

**Data / AI policy.** Code/data availability per journal guidance (lighter than the AFA/SFS data-editor model). Standard publisher AI-disclosure norms. *Verify current at submission.*

**Table format override.** Significance stars conventional; report N, clustering, FE.

---

## Accounting

### Journal of Accounting Research (JAR)

**Short name:** `JAR`

**Focus.** Top-3 accounting (Chicago Booth). Capital-markets / disclosure / financial-reporting / analyst / audit research; strong empirical-archival tradition and a methods-aware readership. Runs a **Registered Reports** conference track (first accounting journal to adopt it).

**Bar.** A clear contribution to an accounting question that a methods-literate referee finds credibly identified. JAR referees read the econometrics closely.

**Domain-referee adjustments.**
- Contribution 30 → 33
- Lit positioning 25 → 25 (unchanged; precise placement vs. the closest accounting papers)

**Methods-referee adjustments.**
- Identification 35 → 40 (the credibility bar is real; "what's the counterfactual?" is standard)
- Inference 20 → 22 (clustering level and cross-sectional/time dependence get scrutiny)

**Typical concerns.**
- "What is the research design's counterfactual, and is the identifying variation plausibly exogenous to the reporting choice?"
- "Are standard errors clustered at the level of the treatment, and is two-way (firm and time) clustering warranted?"
- "Is the disclosure / earnings / analyst measure construction standard, and is look-ahead bias ruled out?"
- "Would this be a candidate for the Registered Reports track, and if so does the design pre-commit to the tests?"

**Referee-pool weights.**
- CREDIBILITY: 0.35
- MEASUREMENT: 0.20
- SKEPTIC: 0.15
- STRUCTURAL: 0.10
- THEORY: 0.10
- POLICY: 0.10

**Data / AI policy.** JAR code-and-data-sharing policy; Registered Reports track for pre-committed designs. Standard publisher AI-disclosure norms. *Verify current at submission.*

**Table format override.** Significance stars conventional in accounting (`* p<0.10, ** p<0.05, *** p<0.01`); report N, clustering, FE; two-tailed unless one-tailed is justified by a signed prediction.

---

### The Accounting Review (TAR)

**Short name:** `TAR`

**Focus.** Flagship AAA journal. Broadest top accounting outlet — financial, managerial, audit, tax, AIS, and disclosure. Values a clear contribution to accounting thought; receptive to a wide range of methods (archival, experimental, analytical).

**Bar.** A contribution that accounting scholars across subfields recognize, with a design appropriate to the question. Strong demand for institutional grounding and a well-motivated hypothesis.

**Domain-referee adjustments.**
- Contribution 30 → 33
- Lit positioning 25 → 25 (unchanged)

**Methods-referee adjustments.**
- Identification 35 → 37
- Robustness 15 → 18

**Typical concerns.**
- "Is the hypothesis well-motivated by theory or institutional detail, not just an empirical regularity?"
- "Is the design appropriate to the question (archival vs. experimental vs. analytical)?"
- "Are the data integrity and variable construction vouched for, and is the data-availability statement complete?"
- "Does the paper speak to an audience beyond a single accounting subfield?"

**Referee-pool weights.**
- CREDIBILITY: 0.25
- MEASUREMENT: 0.20
- SKEPTIC: 0.20
- THEORY: 0.15
- STRUCTURAL: 0.10
- POLICY: 0.10

**Data / AI policy.** AAA policy — public data *strongly encouraged but not required*; authors must **vouch for data integrity** (more than one author recommended) and provide a data-availability statement. Standard publisher AI-disclosure norms. *Verify current at submission.*

**Table format override.** Significance stars conventional; report N, clustering, FE; one-tailed tests acceptable for signed predictions if stated.

---

### Journal of Accounting and Economics (JAE)

**Short name:** `JAE`

**Focus.** Top-3 accounting (Elsevier). Economics-based accounting research — contracting, disclosure, debt and equity markets, governance, with a strong theory-meets-archival tradition (the "Rochester" lineage). Expects an economic argument behind the empirics.

**Bar.** An economically grounded contribution. JAE referees want the theory or economic logic that motivates the test, not a data-mined association.

**Domain-referee adjustments.**
- Contribution 30 → 33
- Substance 20 → 28 (the economic argument / mechanism is load-bearing)

**Methods-referee adjustments.**
- Identification 35 → 38
- For `theory+empirics` papers: Prediction sharpness 25 → 30 (the empirical test should map to a stated prediction)

**Typical concerns.**
- "What is the economic argument, and does the empirical design test *that* prediction?"
- "Is the identifying variation credible, or is this a partial-correlation panel regression?"
- "Have the leading alternative economic explanations been ruled out?"
- "Is the result robust to standard accounting controls and to the obvious sample screens?"

**Referee-pool weights.**
- CREDIBILITY: 0.30
- THEORY: 0.20
- SKEPTIC: 0.15
- MEASUREMENT: 0.15
- STRUCTURAL: 0.10
- POLICY: 0.10

**Data / AI policy.** Elsevier policy — data/code/materials sharing *encouraged, not required*; a data-availability statement is expected. Standard publisher AI-disclosure norms. *Verify current at submission.*

**Table format override.** Significance stars conventional; report N, clustering, FE.

---

### Review of Accounting Studies (RAStudies)

**Short name:** `RAStudies`

**Focus.** Leading accounting journal (Springer). Capital-markets, valuation, disclosure, forecasting, and analytical accounting. Receptive to both empirical-archival and analytical work; a home for valuation- and forecasting-flavored papers.

**Bar.** A solid, well-identified contribution. Narrower-than-TAR scope is acceptable if the execution is clean and the contribution is clear.

**Domain-referee adjustments.**
- Contribution 30 → 30 (unchanged)
- Substance 20 → 23

**Methods-referee adjustments.**
- Identification 35 → 36
- Robustness 15 → 18

**Typical concerns.**
- "Is the contribution clearly distinguished from the nearest existing valuation/disclosure paper?"
- "Is the measure (e.g., forecast, accrual, valuation input) constructed in a standard, validated way?"
- "Is the design robust to specification and sample choices?"
- "If analytical, do the predictions have empirical content the paper (or a follow-up) could test?"

**Referee-pool weights.**
- CREDIBILITY: 0.25
- MEASUREMENT: 0.25
- SKEPTIC: 0.15
- THEORY: 0.15
- STRUCTURAL: 0.10
- POLICY: 0.10

**Data / AI policy.** Springer research-data policy — data-availability statement expected; sharing encouraged. Standard publisher AI-disclosure norms. *Verify current at submission.*

**Table format override.** Significance stars conventional; report N, clustering, FE.

---

## Interdisciplinary / management science

### Management Science (MS)

**Short name:** `MS`

**Focus.** Top interdisciplinary journal (INFORMS). Finance, accounting, operations, information systems, marketing, strategy, behavioral, and analytical work. The Finance and Accounting departments are well-regarded outlets for empirical finance/accounting that also speaks to a management-science audience.

**Bar.** A methodologically sound contribution with relevance beyond a single field. MS values a clear method and a generalizable insight; it enforces a code-and-data disclosure policy.

**Domain-referee adjustments.**
- Contribution 30 → 33
- External validity 15 → 20 (generalizability across settings is valued)

**Methods-referee adjustments.**
- Identification 35 → 38
- Replication 5 → 10 (INFORMS Code and Data Disclosure Policy)

**Typical concerns.**
- "Does the contribution generalize beyond the specific empirical setting?"
- "Is the method correct and clearly described, with the identification or model assumptions stated?"
- "Is the result robust, and is the economic/managerial magnitude interpreted?"
- "Is the code-and-data disclosure package complete per INFORMS policy?"

**Referee-pool weights.**
- CREDIBILITY: 0.25
- STRUCTURAL: 0.20
- MEASUREMENT: 0.20
- SKEPTIC: 0.15
- THEORY: 0.10
- POLICY: 0.10

**Data / AI policy.** INFORMS Code and Data Disclosure Policy — disclosure package expected (proprietary-data exemption applies). Standard publisher AI-disclosure norms. *Verify current at submission.*

**Table format override.** Significance stars conventional; report N, clustering, FE.

---

## Economics (general-interest cross-over targets)

Finance and accounting papers are routinely sent to general-interest econ journals. Two profiles for the most common targets; the AEA Data Editor / DCAS policy in the landscape section above governs the AEA-imprint outlets.

### American Economic Review (AER)

**Short name:** `AER`

**Focus.** General-interest economics across all fields. Strongest bar for substantive contribution and policy relevance. Favors credible identification + interpretable magnitudes + a clear narrative over technical novelty.

**Bar.** "The top-10 people in your field will read it." Topic must matter beyond specialists; contribution crisp in one paragraph.

**Domain-referee adjustments.**
- Contribution 30 → 35
- External validity 15 → 20
- Fit 10 → 5 (AER publishes across fields)

**Methods-referee adjustments.**
- Identification 35 → 40
- Replication 5 → 10 (AEA Data and Code Availability Policy is strict)

**Typical concerns.**
- "Is the research question important enough for a general-interest journal?"
- "Is the identification strategy credible to a skeptical non-specialist?"
- "Does the magnitude tell us something we didn't already know?"
- "Are the robustness checks addressing the obvious threats, or theater?"
- "Is the replication package complete enough for the AEA Data Editor?"

**Referee-pool weights.**
- CREDIBILITY: 0.30
- POLICY: 0.25
- STRUCTURAL: 0.15
- MEASUREMENT: 0.15
- THEORY: 0.05
- SKEPTIC: 0.10

**Data / AI policy.** AEA Data and Code Availability Standard (DCAS) under the AEA Data Editor — complete openICPSR deposit + data-availability statement + code reproducing every number, at acceptance. AEA AI-use disclosure per current AEA policy. *Verify current at submission.*

**Table format override.** **No significance stars** (AEA policy). SE in parentheses; indicate p-values in notes if needed.

---

### Quarterly Journal of Economics (QJE)

**Short name:** `QJE`

**Focus.** Identification-first empirical work and theory with sharp predictions. Taste for clever natural experiments, rich data, and economic insight over methodological flash.

**Bar.** Identification must be near-airtight. Willing to accept narrow settings if the design is exceptional; wants a paper teachable in a graduate class.

**Domain-referee adjustments.**
- Contribution 30 → 30 (unchanged)
- Substance 20 → 25 (taste matters — clever > competent)

**Methods-referee adjustments.**
- Identification 35 → 45 (the QJE house style)
- Robustness 15 → 10 (less tolerant of robustness-as-theater)

**Typical concerns.**
- "Is the research design genuinely clever, or yet another DiD?"
- "Does the first-stage / exclusion restriction / parallel-trends assumption have teeth?"
- "Would I teach this paper's identification strategy?"
- "What's the one-sentence economic insight here?"

**Referee-pool weights.**
- CREDIBILITY: 0.40
- STRUCTURAL: 0.20
- MEASUREMENT: 0.15
- POLICY: 0.10
- THEORY: 0.10
- SKEPTIC: 0.05

**Data / AI policy.** AEA Data and Code Availability Standard (DCAS) under the AEA Data Editor (QJE is Oxford UP but enforces a comparable archive). *Verify current at submission.*

**Table format override.** Three-decimal point estimates standard; SE in parentheses.

---

## Field adaptation

The profiles above are finance / accounting / econ. The **pipeline is field-agnostic** — nothing in `editor.md`, `domain-referee.md`, or `methods-referee.md` hard-codes a discipline. What varies by field is the journal profile.

**To adapt for a different field or to add a venue:**

1. Copy a profile block above into a new section (use `### Journal Name (SHORT)`).
2. Fill each schema field:
   - **Focus** — what the journal publishes (look at the last 6 months of the TOC).
   - **Bar** — acceptance-rate context + one sentence on what the editor wants.
   - **Domain-referee adjustments** — re-weight contribution / lit-positioning / substance / external validity / fit for this journal's taste.
   - **Methods-referee adjustments** — re-weight identification / robustness / inference / replication; rename paper types in `methods-referee.md` if your field uses different categories.
   - **Typical concerns** — distill 3–5 recurring referee questions from recent reviews or a colleague.
   - **Referee-pool weights** — the 6 dispositions are general; re-weight to what that journal's referees actually ask about. Weights sum to 1.0.
   - **Data / AI policy** — the reproducibility-archive and AI-use posture, with a "verify at submission" flag (these change often).
   - **Table format** — any field-specific convention.

**For non-finance paper types.** The `methods-referee.md` paper-type branching uses `reduced-form / structural / theory+empirics / descriptive / asset-pricing-test`. If your field uses different categories, edit `methods-referee.md` to add them and their dimension weights; keep the existing branches for finance/accounting/econ users.

---

## Cross-references

- `.claude/agents/editor.md` — reads this file before each `--peer` run.
- `.claude/agents/domain-referee.md` — applies domain-referee adjustments.
- `.claude/agents/methods-referee.md` — applies methods-referee adjustments.
- [`discipline-cards.md`](discipline-cards.md) — discipline-level paper-type frequencies, prereg norms, and method conventions the editor consults when given a discipline hint without a named journal.
- `.claude/skills/review-paper/SKILL.md` — `--peer [journal]` mode entry point.
- [`.claude/rules/confidential-data.md`](../rules/confidential-data.md) — restricted-data deposit pattern (CRSP/Compustat/IBES/TAQ exemptions).
- [`.claude/skills/replication-package/SKILL.md`](../skills/replication-package/SKILL.md) / [`.claude/skills/audit-reproducibility/SKILL.md`](../skills/audit-reproducibility/SKILL.md) — build + gate the package before submission.
