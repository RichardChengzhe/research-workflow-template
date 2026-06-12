# Preregistration Template

This template is consumed by `.claude/skills/preregister/SKILL.md`. It contains three style sections (OSF, AsPredicted, AEA RCT Registry). The skill picks one based on `--style` or the field default.

**Output convention.** The skill writes the chosen style's filled-in form to `quality_reports/preregistrations/YYYY-MM-DD_<slug>.md` (gitignored). The user uploads it to the registry; this template is *not* a registry submission tool.

**Field note (finance / accounting).** This template's home discipline runs as many *observational* preanalysis plans (a panel test on data the analyst has not yet examined for the focal hypothesis — e.g., a return predictability or event-study design) as it does randomised interventions. For the observational case, "sample" is the firm/period universe and the inclusion/exclusion filters; "randomisation" is N/A; the binding commitments are the directional hypothesis, the exact specification, the data-exclusion rules, and the inference threshold — all fixed *before* the realised outcome is examined. The OSF style below is the default for that case; AEA RCT is for actual field experiments.

**Annotation legend.** Each field is tagged with one of:

- **MUST** — registry-required; the document cannot be submitted without it.
- **SHOULD** — strongly recommended; reviewers expect it.
- **MAY** — optional; include if relevant.

For any **MUST** field that the input description doesn't supply, write `[CLARIFY: <specific question>]`. Do not fabricate.

---

## Style 1 — OSF (Open Science Framework)

The OSF "Preregistration" template. Default for broad social-science studies and for observational preanalysis plans (the common finance/accounting case). Upload at `osf.io/registries`.

```markdown
---
title: <Study title>
authors: <Author1, Author2, ...>
date: YYYY-MM-DD
version: 1
style: osf
source-spec: <path to quality_reports/specs/... if applicable>
---

# Preregistration — <Study title>

## 1. Study Information (MUST)

### 1.1 Title
<Concise title that names the design and outcome>

### 1.2 Authors
<List with affiliations>

### 1.3 Description
<2–4 sentence study summary: what, why, who, when>

### 1.4 Hypotheses (MUST — directional)
**H1.** <Directional claim, e.g., "Firms with higher treatment exposure earn higher abnormal returns following a positive shock than low-exposure firms">.
**H2.** <…>

## 2. Design (MUST)
- **Type:** experimental / quasi-experimental / observational panel
- **Manipulation (if any):** <description, or "N/A — observational">
- **Unit of analysis:** firm / firm-month / firm-event / individual / cluster
- **Randomisation / assignment:** <random assignment unit, OR the source of identifying variation for an observational design — e.g., a staggered policy shock, an event date>
- **Blinding:** <single / double / open / N/A>

## 3. Sampling Plan (MUST)
- **Population:** <who/which firms; universe and period>
- **Recruitment / data source:** <e.g., CRSP/Compustat/IBES merge; survey panel>
- **Target N:** <number, with justification>
- **Stopping rule:** <e.g., "all firm-months 2017–2025"; or for a survey "stop at N=1,200 or 4 weeks, whichever first">
- **Power / minimum detectable effect (MDE):** <assumed effect size OR the smallest effect the design can detect at the stated alpha and power; report alpha, power, and the resulting N or MDE>

## 4. Variables (MUST)
- **Primary outcome (Y):** <name, measurement, units>
- **Treatment / key regressor (T / X):** <name, levels or scaling, encoding; for an observational test, the focal characteristic and its lag structure to avoid look-ahead>
- **Pre-registered controls / fixed effects:** <list, including FE dimensions>

## 5. Analysis Plan (MUST)
- **Primary estimator:** <e.g., "panel OLS / reghdfe with firm and month fixed effects, standard errors clustered by firm">
- **Inference criterion:** <e.g., "two-sided alpha = 0.05; we conclude H1 supported if the coefficient on T is of the predicted sign and significant at this threshold">
- **Pre-registered specifications:** numbered (1, 2, 3) with explicit functional form, FE, and clustering for each
- **Multiple-testing correction (if H > 1):** <Bonferroni / Benjamini-Hochberg / none + justification>

## 6. Inference Criteria (MUST)
- **Confirmatory test of H1:** <exact decision rule>
- **What would make us reject H1:** <quantitative threshold>
- **Equivalence / "null is meaningful" test (if used):** <bounds>

## 7. Data Exclusions (MUST — ex ante)
- **Outliers / winsorization:** <e.g., "winsorize continuous variables at 1/99"; "exclude survey completions < 60 seconds">
- **Sample filters:** <e.g., "drop financials (SIC 6000–6999) and firms with share price < $1">
- **Other:** <rule>

## 8. Missing Data (MUST)
- **Treatment of missingness:** <listwise / multiple imputation / MAR assumption>
- **If MI: imputation model:** <specification>

## 9. Exploratory Analyses (MAY)
> Anything below this point is **exploratory** and not part of the confirmatory test.

- <Optional analyses, clearly labelled>

## 10. Other (MAY)
- **Have any of the focal data been examined already?** Yes / No (if yes: were the realised outcomes used to set H1? Disclose — examining the outcome first defeats the preregistration.)
- **Conflicts of interest:** <disclosure>
- **Funding source:** <disclosure>
```

---

## Style 2 — AsPredicted

The 9-question AsPredicted form (aspredicted.org). Designed for lab/survey experiments and short studies. Upload at `aspredicted.org/create.php`.

```markdown
---
title: <Study title>
date: YYYY-MM-DD
style: aspredicted
source-spec: <path>
---

# AsPredicted — <Study title>

## 1. Have any data been collected for this study yet? (MUST)
<Yes — describe pilot status / No>

## 2. What's the main question being asked or hypothesis being tested? (MUST — directional)
<H1: directional claim>

## 3. Describe the key dependent variable(s) specifying how they will be measured. (MUST)
<Y, with measurement and units>

## 4. How many and which conditions will participants be assigned to? (MUST)
<List conditions, randomisation procedure, allocation ratio>

## 5. Specify exactly which analyses you will conduct to examine the main question/hypothesis. (MUST)
<Estimator, primary specification, inference rule>

## 6. Describe exactly how outliers will be defined and handled, and your precise rule(s) for excluding observations. (MUST)
<Ex-ante rules>

## 7. How many observations will be collected, or what will determine sample size? (MUST)
<Target N or stopping rule, with power / MDE justification>

## 8. Anything else you would like to pre-register? (MAY)
<Robustness specs, secondary outcomes, equivalence tests>

## 9. Name (NOTE: this is for the study, not the paper). (MUST)
<short codename>
```

---

## Style 3 — AEA RCT Registry

The American Economic Association RCT Registry (socialscienceregistry.org). **Required** for AEA-journal submission of any randomised intervention since 2018. Upload at `socialscienceregistry.org/trials/create`. (For a *non-experimental* finance/econ preanalysis plan, use the OSF style above — the AEA registry is for randomised trials.)

```markdown
---
title: <Trial title>
investigators: <PI names + affiliations>
date: YYYY-MM-DD
style: aea-rct
source-spec: <path>
---

# AEA RCT Registry — <Trial title>

## Trial Information (MUST)
- **Status:** Not yet on the air / In development / On going / Completed
- **Start date:** YYYY-MM-DD
- **End date (planned):** YYYY-MM-DD
- **Geographic region:** <Country, sub-national region>

## Intervention (MUST)
- **Description:** <what is delivered, by whom, when>
- **Comparison group(s):** <pure control / placebo / active control>
- **Implementation partners:** <NGO, government agency, etc.>

## Primary Outcomes (MUST)
- **Y1 (primary):** <name, measurement, time of measurement>
- **Y2 (secondary, optional):** <…>

## Primary Hypotheses (MUST — directional)
**H1.** <Directional claim about Y1 under T vs C>

## Sample (MUST)
- **Target N:** <number>
- **Eligibility criteria:** <inclusion / exclusion>
- **Randomisation unit:** individual / household / village / school / clinic / firm
- **Randomisation method:** <stratified, paired, blocked, simple>
- **Allocation ratio:** <e.g., 1:1>

## Power Calculation (SHOULD)
- **Assumed effect size / minimum detectable effect (MDE):** <SD units>
- **Alpha / power:** <0.05 / 0.80>
- **Resulting N (and ICC if clustered):** <…>

## Pre-Analysis Plan (MAY — attach as PDF)
- **Estimator:** <ANCOVA / DiD / cluster-robust OLS>
- **Specifications:** numbered, with controls and fixed effects listed
- **Multiple testing:** <correction or family-wise rule>
- **Heterogeneity analyses:** <pre-specified subgroups>
- **Sensitivity / robustness:** <bounds analysis, alternative SEs, attrition adjustments>

## IRB / Ethical Approval (MUST for AEA submission)
- **IRB:** <institution>
- **Approval number:** <#>
- **Date of approval:** YYYY-MM-DD

## Data Sharing (SHOULD)
- **Public data plan:** <yes / no / restricted>
- **Replication code:** <will be deposited at the AEA data archive (openICPSR) at acceptance — see the AEA Data and Code Availability Policy>

## Conflicts of Interest (MUST)
<Disclosure>

## Funding (MUST)
<Source(s)>
```

---

## Style mapping (cross-registry)

For users who need to publish under one registry but report results under another's conventions, the rough mapping is:

| OSF section | AsPredicted question | AEA RCT field |
|---|---|---|
| 1.4 Hypotheses | Q2 | Primary Hypotheses |
| 2 Design | Q4 (conditions) | Intervention |
| 3 Sampling Plan | Q7 | Sample + Power Calc |
| 4 Variables | Q3 (DV) | Primary Outcomes |
| 5 Analysis Plan | Q5 | Pre-Analysis Plan |
| 7 Data Exclusions | Q6 | (in PAP attachment) |
| 6 Inference Criteria | (implicit in Q5) | (in PAP attachment) |

The mapping is approximate — registries differ in granularity. When in doubt, use the registry's native template directly.

---

## Where this template lives

- **File:** `templates/preregistration-template.md`
- **Consumed by:** `.claude/skills/preregister/SKILL.md`
- **Output:** `quality_reports/preregistrations/YYYY-MM-DD_<slug>.md` (gitignored)
- **Pairs with:** `.claude/skills/power-analysis/SKILL.md` (compute the MDE / target N the plan commits to).
- **Registry URLs:** OSF (osf.io/registries), AsPredicted (aspredicted.org), AEA RCT (socialscienceregistry.org)
