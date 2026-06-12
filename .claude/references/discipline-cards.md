# Discipline Cards

Short reference cards naming each discipline's dominant paper-type frequencies, top journals, preregistration norms, and method conventions. Read by `/research-ideation`, `/interview-me`, `/preregister`, and the `editor` agent (in `/review-paper --peer`) when the user gives a `paper_type` or domain hint without naming a target journal.

**Scope.** This template ships three cards: **finance**, **accounting**, and **economics** — the template's home disciplines. (Other social sciences are out of scope here.) To add a discipline, copy a card, fill the four fields, and reference the new short-slug from [`journal-profiles.md`](journal-profiles.md) and `methods-referee.md`.

**Maintenance.** When you add a journal profile to `journal-profiles.md`, cross-reference it here. When you add a paper type to `methods-referee.md`, cross-reference it here.

---

## Finance (`fin`)

**Paper-type frequencies (rough share of empirical work in top finance journals).**

| Type | Share | Notes |
|---|---|---|
| Reduced-form | ~60% | Panel regressions, DiD around shocks/regulations, IV, event studies, RD. The dominant mode. |
| Asset-pricing test | ~20% | Cross-sectional sorts, factor-model alphas (FF3/FF5/q-factor), time-series predictability, GMM. |
| Structural | ~10% | Dynamic corporate finance, structural IO of financial markets, estimated equilibrium models. |
| Theory + empirics | ~7% | A model with a sharp prediction plus an empirical test of it. |
| Descriptive | ~3% | New measure / new data / stylized-fact documentation. |

**Dominant journals (shipped in `journal-profiles.md`).** JF, JFE, RFS (top-3); JFQA; Management Science (Finance dept.). General-interest econ (AER, QJE) for broad-appeal work.

**Preregistration norms.**
- **Observational / archival (the vast majority):** preregistration is **uncommon**; credibility comes from research design, robustness batteries, and an honest specification grid rather than a pre-analysis plan.
- **Experiments (lab / field / survey in finance):** OSF / AsPredicted increasingly used; not a hard requirement.
- **Replication packages:** **mandatory reproduction archive at acceptance** at JF (AFA), JFE, RFS (RFS Data Editors + Dataverse), Review of Finance, and Management Science (INFORMS). Proprietary-data (CRSP/Compustat/IBES/TAQ) exemption: deposit code + cleared outputs + access instructions. Run `/replication-package` (gates on `/audit-reproducibility`).

**Method conventions.**
- Significance stars: **used** (typical floor `* p<0.10, ** p<0.05, *** p<0.01`); SE *or* t-stats in parentheses — state which in the note. (Contrast: AEA econ journals use **no** stars.)
- Standard errors: clustered at the level the key regressor / treatment varies; two-way (firm and time) clustering standard for panels (Petersen 2009); Newey-West / Hansen-Hodrick for overlapping long-horizon returns.
- Returns: merge CRSP **delisting returns**; point-in-time membership (no survivorship); match the abnormal-return benchmark to the claim (DGTW / factor alpha / characteristic-matched).
- Code: Stata, Python, SAS, Julia, R all accepted; replication packages must be self-contained and deterministic (set the seed).

**Cross-references.** `methods-referee.md` paper types: reduced-form, asset-pricing-test, structural, theory+empirics, descriptive. `journal-profiles.md`: JF, JFE, RFS, JFQA, MS (+ AER, QJE).

---

## Accounting (`acct`)

**Paper-type frequencies (rough share of empirical work in top accounting journals).**

| Type | Share | Notes |
|---|---|---|
| Reduced-form (archival) | ~65% | Capital-markets, disclosure, earnings/accruals, analyst, audit, tax; panel and DiD-around-regulation designs. |
| Experimental | ~15% | Behavioral / judgment-and-decision-making (audit, managerial); lab experiments with human subjects. |
| Analytical | ~10% | Information-economics / contracting models; sometimes paired with an empirical test. |
| Theory + empirics | ~7% | A model prediction tested on archival data. |
| Descriptive | ~3% | New measure / textual-disclosure construction / data documentation. |

**Dominant journals (shipped in `journal-profiles.md`).** JAR, TAR, JAE (top-3); Review of Accounting Studies. Management Science (Accounting dept.) and general-interest econ for cross-over work.

**Preregistration norms.**
- **Registered Reports:** the **Journal of Accounting Research** runs a Registered Reports conference track (first accounting journal to adopt it) — a genuine option for pre-committed archival designs. Use `/preregister`.
- **Experiments:** OSF / AsPredicted increasingly expected for behavioral work.
- **Observational / archival:** preregistration uncommon outside the JAR track; credibility from design + robustness.
- **Replication / data:** **mixed.** JAR and Review of Accounting Studies operate code/data-sharing policies; **The Accounting Review (AAA)** strongly *encourages* public data and requires author **vouching for data integrity** (not a public archive); **JAE (Elsevier)** *encourages, not requires*. A data-availability statement is expected everywhere.

**Method conventions.**
- Significance stars: **used** (`* p<0.10, ** p<0.05, *** p<0.01`); **one-tailed** tests are accepted for *signed* (directional) predictions if stated — a convention distinct from finance/econ.
- Standard errors: two-way (firm and year) clustering standard for capital-markets panels; correct for cross-sectional and time dependence.
- Variable construction: standard accruals / earnings-quality / disclosure measures should be built the canonical way and cited; rule out look-ahead from restated/backfilled fundamentals (point-in-time Compustat).
- Code: Stata and SAS dominant; Python rising for textual-analysis (10-K/8-K) work; R present.

**Cross-references.** `methods-referee.md` paper types: reduced-form, experimental, analytical (theory), theory+empirics, descriptive. `journal-profiles.md`: JAR, TAR, JAE, RAStudies, MS.

---

## Economics (`econ`)

**Paper-type frequencies (rough share of empirical work in top-5 journals).**

| Type | Share | Notes |
|---|---|---|
| Reduced-form | ~55% | DiD, IV, RD, event study, synthetic control. The dominant mode. |
| Structural | ~20% | DSGE, GE, IO empirical. Concentrated in macro / IO / labour. |
| Theory + empirics | ~15% | Theory-paper-with-empirical-test or empirical-paper-with-theory-section. |
| Descriptive | ~5% | Measurement / data-construction. Often the AEA P&P route. |
| Formal-theory | ~5% | Pure theory (micro, IO, contracts). More common in ECMA / TE / JET. |

**Dominant journals (shipped in `journal-profiles.md`).** AER, QJE (the two shipped); the other top-5 (JPE, ECMA, ReStud) and AEA P&P for descriptive/measurement work. Finance/accounting papers reach AER/QJE when the question is general-interest.

**Preregistration norms.**
- **Field experiments / RCTs:** mandatory in the **AEA RCT Registry** since 2018 for AEA-journal submission. Use `/preregister --style aea-rct`.
- **Lab experiments:** OSF / AsPredicted increasingly common; not yet uniformly required.
- **Observational / archival:** preregistration uncommon; pre-analysis plans appearing in some applied-micro corners.
- **Replication packages:** **AEA Data and Code Availability Standard (DCAS)** under the AEA Data Editor — complete openICPSR deposit + data-availability statement + code reproducing every number, at acceptance. Econometrica / ReStud enforce comparable archives.

**Method conventions.**
- Significance stars: AEA journals do **NOT** use stars in tables (AEA style) — SE in parentheses. (Contrast: finance/accounting *do* use stars.) Some non-AEA econ journals still allow them.
- Standard errors: clustered at the treatment-assignment level; Conley / spatial SEs for spatial data; wild-cluster bootstrap for few clusters.
- Code: R, Stata, Python, Julia all accepted; replication packages must be self-contained and deterministic (set the seed).

**Cross-references.** `methods-referee.md` paper types: reduced-form, structural, theory+empirics, descriptive, formal-theory. `journal-profiles.md`: AER, QJE.

---

## How skills consume these cards

- **`/research-ideation`** — when the user names a topic without a discipline, the skill may infer one from context (citation style, vocabulary). The card supplies the default `paper_type` distribution to bias hypothesis generation.
- **`/interview-me`** — the paper-type question uses the card's frequency table to order the option list (most-likely-first per discipline).
- **`/preregister`** — `--style` defaults to the card's preregistration-norms suggestion (e.g., `aea-rct` for econ field experiments; the JAR Registered Reports track for accounting archival designs).
- **`editor`** (`/review-paper --peer`) — when the user gives `--peer` without naming a specific journal but with a discipline hint, the editor uses the card's "Dominant journals" list as the candidate set and asks for clarification.

---

## Adding a new discipline card

Copy this template:

```markdown
## [Discipline name] (`short-slug`)

**Paper-type frequencies.**
| Type | Share | Notes |
|---|---|---|
| ... |

**Dominant journals (shipped in `journal-profiles.md`).** [list]. [Optional: subfield outlets.]

**Preregistration norms.**
- [registry / replication-archive conventions per study type]

**Method conventions.**
- [significance stars / SE conventions / replication norms / dominant code language]

**Cross-references.** `methods-referee.md` paper types: [list]. `journal-profiles.md`: [list].
```

Then:

1. Add the card section above (alphabetically by short-slug).
2. Add concrete journal profiles to `journal-profiles.md` for at least the top-3 journals.
3. Add paper types to `methods-referee.md` if your field uses categories not already there.
4. Cross-reference the new short-slug from `/research-ideation` and `/interview-me` if those skills should respect the new defaults.

---

## Where this file lives

- **File:** `.claude/references/discipline-cards.md`
- **Schema parallel:** [`journal-profiles.md`](journal-profiles.md) (per-journal) and [`audit-pet-peeves.md`](audit-pet-peeves.md) (living-catalogue format).
- **Consumed by:** `/research-ideation`, `/interview-me`, `/preregister`, `editor` agent.
