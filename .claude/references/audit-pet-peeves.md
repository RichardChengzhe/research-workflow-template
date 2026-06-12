# Audit Pet Peeves — classes of error our reviews keep missing

**Purpose.** A living catalogue of recurring defects — in the *empirical analysis* and in the *workflow repo's own docs* — that careful reviewers (a referee, a co-author, a review bot) have caught and we want every audit agent to inherit as prior knowledge.

**Principle.** Each class of bug we see = one entry. **Grow the file, don't rewrite it.** Mechanical checks close the obvious holes; this file closes the subtler ones that require judgment.

**How to use.** When writing a `code-reviewer`, `domain-reviewer`, `methods-referee`, or `deep-audit` agent prompt, say "read `.claude/references/audit-pet-peeves.md` and explicitly check for each applicable class before reporting clean." When triaging a new finding, decide: new class (add an entry) or existing class re-surfacing (bump the evidence list).

The file has two parts: **A — empirical-research pet peeves** (the methodology defects that sink a finance/accounting paper) and **B — workflow-infra pet peeves** (drift in the template's own skills/rules/docs).

---

# Part A — Empirical-research pet peeves (finance / accounting / econ)

These are the threats a `methods-referee` or `domain-reviewer` must rule out before reporting clean. Each is a *threat to a conclusion*, in the `change_my_mind` spirit of [`orchestration-schemas.md`](orchestration-schemas.md).

## A1. Look-ahead bias / peeking (using information not available at the trade/decision date)

**Pattern.** A signal is constructed with data that was not public at the time it is used to sort firms or predict returns: a fiscal-year accounting variable used in the month *before* the 10-K/annual report was filed; analyst consensus stamped at the period-end rather than the actual I/B/E/S statistical-period date; a "current" index constituent list applied to past dates (constituent look-ahead); standardizing a variable by its **full-sample** mean/SD when a real-time sort could only use the trailing window.

**How to catch.** Trace every right-hand-side variable to the date it became knowable. Accounting data: enforce the standard lag (e.g., returns from July of year t+1 for fiscal year t, à la Fama-French; or a documented reporting-lag/filing-date gap). I/B/E/S: use the statistical period / activation date, not the period-end. Sorts: confirm the breakpoints use only past data. Standardization: a full-sample z-score in a *predictive* regression is a look-ahead unless the interaction coefficient is invariant to the rescaling (then it's cosmetic — say so explicitly).

**When to apply.** Any return-prediction sort, any panel where the timing of information matters, any "real-time" claim.

## A2. Wrong clustering level (standard errors not matched to the dependence structure)

**Pattern.** SEs clustered by firm only when treatment is assigned at the **state×year** (or industry, or cohort) level; clustering by firm when the shock is common to all firms in a period (cross-sectional dependence ⇒ cluster by time, or two-way); a single-dimension cluster where Petersen (2009) shows the panel needs two-way (firm *and* time). Under-clustering inflates t-stats; the headline result can be an artifact of the wrong SE.

**How to catch.** Identify the level at which the key regressor varies / treatment is assigned — that is the minimum cluster level. For panels with both firm persistence and common time shocks, expect two-way (firm and time) clustering and check the result survives it. Watch for "too few clusters" (e.g., <~30–50 states): the cluster-robust asymptotics fail; ask for wild-cluster bootstrap.

**When to apply.** Every panel regression. The modal reviewer objection in finance/accounting after "endogeneity."

## A3. Overlapping-return overlap (long-horizon returns with overlapping windows)

**Pattern.** Long-horizon (k-month/quarter) cumulative returns or BHARs regressed on a predictor using **overlapping** windows, with plain or even Newey-West SEs that under-correct the induced MA(k−1) autocorrelation. Hansen-Hodrick / Newey-West with too-short a lag, or none, overstates significance; overlapping long-horizon regressions are a known source of spurious predictability.

**How to catch.** If returns overlap, the SE must correct for the overlap (Newey-West/Hansen-Hodrick with lag ≥ horizon−1, or non-overlapping windows, or a bootstrap). Cross-check: does the result survive non-overlapping horizons? Long-horizon BHAR also needs the right benchmark and a skewness-aware test (see A8).

**When to apply.** Any predictive regression at horizon > 1 period; long-window event studies.

## A4. Data snooping / p-hacking / specification search

**Pattern.** The reported specification is one survivor of many silently-tried alternatives (FE combinations, control sets, winsorization cutoffs, subsamples, horizon choices, variable transforms). A single t = 2.1 that only appears under one of dozens of forks is not evidence. "We also tried X" appears only when X worked.

**How to catch.** Ask for the specification *grid*, not the winning cell. Is the headline robust across the reasonable FE/control/winsorization choices, or fragile to one? Are the winsorization cutoffs (1%/99%) and sample screens pre-committed and standard, or tuned? Prefer a result that holds across a documented battery to one that needs exactly one parameterization. For genuinely exploratory work, a pre-registration / Registered Report (JAR track) or a hold-out sample is the credible answer.

**When to apply.** Any result where many forks were available — which is nearly all of them.

## A5. Uncontrolled multiple testing (many hypotheses, no adjustment)

**Pattern.** Dozens of DVs × horizons × subgroups tested, significance read off the cells that cross |t|>2, with no account for how many tests were run. With 100 independent tests at the 5% level, ~5 are "significant" by chance; a battery that finds 8 of 192 cells significant is *below* chance, not a discovery.

**How to catch.** Count the tests. Compare the number of "hits" to the false-positive rate the test count implies. For an explicit family, apply a multiple-testing correction (Bonferroni/Holm; Benjamini-Hochberg FDR; or the Harvey-Liu-Zhu (2016) haircut for asset-pricing factors). Distinguish a *pre-specified* primary test (no penalty) from *post-hoc* mining of a grid (penalty). A heat-map of t-stats is a multiple-testing surface — judge it as one.

**When to apply.** Any battery / grid / "we ran many DVs" design. (See the template's own report-grid conventions.)

## A6. Delisting / survivorship / backfill bias

**Pattern.** A return sample that drops delisted firms (or sets the delisting-month return to missing) overstates returns and understates risk — distress/bankruptcy delistings carry large negative returns. Survivorship: conditioning on firms that exist at the end of the sample. Backfill / incubation: a database (notably hedge-fund and some fundamentals data) backfilling history for newly added entities inflates early performance.

**How to catch.** Confirm CRSP **delisting returns** are merged (and the delisting-bias adjustment for missing performance-related delisting codes, e.g., the −30%/−55% conventions or the Shumway adjustment). Check the sample is built forward (point-in-time membership), not on end-of-sample survivors. For fundamentals, confirm no look-ahead from restated/backfilled values (point-in-time Compustat).

**When to apply.** Any CRSP return study; any performance claim; any database with entity backfill.

## A7. Bad merge / identifier drift (silent row loss or wrong-firm matches)

**Pattern.** Merging CRSP↔Compustat on a recoded/sequential key instead of the canonical link (`ccmxpf_lnkhist` / PERMNO↔GVKEY with link-date validity); keying on a `egen group` numeric id that is assigned *per build* (same number = different firm across builds); CUSIP changes over time matched without `nameenddt` validity; a many-to-many merge that silently duplicates rows; an inner join that drops the firms the result depends on (sample-selection bias from the merge itself).

**How to catch.** Use the canonical linking table with date-validity bounds. For cross-build diagnostics, key on a stable string id (`gvkey_str` × date), never a per-build numeric id. Report merge diagnostics: N before/after, match rate, and `_merge` distribution. Construct sample-defining filters (winsorization, rank/quintile breakpoints, treatment flags) **after** all merges, never on the broader pre-merge population (post-merge construction prevents selection-inflated rates).

**When to apply.** Every WRDS merge; every cross-dataset join.

## A8. Wrong benchmark / abnormal-return model for the test

**Pattern.** "Abnormal" returns measured against a benchmark that doesn't match the test: raw returns called alpha; a market-model alpha where a size/value/momentum adjustment is needed; characteristic-sorted portfolios compared without DGTW/size-B/M adjustment; a long-window BHAR with a symmetric t-test despite the known right-skew of long-horizon abnormal returns; an event study whose estimation window overlaps the event or contaminating events.

**How to catch.** Match the benchmark to the claim: a factor-model alpha needs the right factors (and a defensible factor set — FF3/FF5/q-factor); cross-sectional characteristic tests need a characteristic-matched benchmark; long-horizon abnormal returns need calendar-time portfolios or a skewness-adjusted/bootstrapped test. Event studies: clean estimation window, no event overlap, correct event date.

**When to apply.** Any "alpha"/"abnormal return"/CAR/BHAR claim; any factor regression.

## A9. Mechanical / fundamentals confound in a returns claim (DR vs. CF)

**Pattern.** A return pattern attributed to a discount-rate / taste / mispricing channel without ruling out that *realized fundamentals* moved (a cash-flow story), or vice versa. A "the market reprices X" claim that is silent on whether X's earnings/sales actually changed.

**How to catch.** Ask whether the competing channel is tested and excluded — e.g., do realized fundamentals (sales growth, profitability, SUE) move with the sort, or are they flat (favoring a discount-rate/taste reading)? A by-elimination argument needs the eliminated channel *measured*, not asserted.

**When to apply.** Any paper claiming a specific economic channel behind a return pattern.

## A10. Generated-regressor / EIV uncertainty ignored

**Pattern.** A right-hand-side variable that is itself an *estimate* (a first-stage fitted value, a text-based sentiment score, a factor loading, a predicted probability) used in a second-stage regression with SEs that ignore the first-stage estimation error (the Pagan generated-regressor problem). Understates the true uncertainty.

**How to catch.** When a regressor is a generated quantity, the second-stage SEs must account for it (bootstrap the whole two-step procedure, or a Murphy-Topel / GMM correction). At minimum, flag it and check robustness to the first-stage uncertainty. Classical measurement error in an RHS variable attenuates toward zero (a *lower-bound* argument is legitimate — but state it).

**When to apply.** Any two-step estimator; any constructed/estimated regressor (sentiment, betas, propensity scores).

---

# Part B — Workflow-infra pet peeves (the template's own skills / rules / docs)

Drift patterns that review bots catch in the workflow repository itself. Mechanical checks (e.g. an integrity script) close the obvious ones; these are the judgment-requiring residue. (R-/Quarto-specific peeves from the upstream source are dropped — this template is Stata/Python/SAS + LaTeX.)

## B1. Frontmatter ↔ body tool parity

**Pattern.** A skill/agent body says "spawn `claim-verifier` via `Task` with `context: fork`" (or "use the `Monitor` tool", or `Edit`/`Write`/`WebFetch`/`NotebookEdit`) but the named tool is missing from the frontmatter `tools:` / `allowed-tools:` list. The documented capability can't actually run.

**How to catch.** For **every** tool name mentioned in a body (`Task`, `Bash`, `Edit`, `Write`, `Read`, `Grep`, `Glob`, `WebFetch`, `WebSearch`, `Monitor`, `NotebookEdit`, …), verify it appears in the frontmatter tool list. Maintain a known-tool list rather than hard-coding `Task`; new Anthropic tools ship faster than the check.

**When to apply.** Any new/modified skill or agent that invokes a tool it didn't previously use.

## B2. `argument-hint` ↔ body flag parity / unimplemented promised flag

**Pattern.** A body documents `--no-verify` / `--peer` / `--diff` but the `argument-hint` doesn't advertise it (users can't discover it), OR a rule/skill references a flag of another skill (`pass --foo to /skill`) that the target skill doesn't actually parse.

**How to catch.** When a body documents `--flag`, confirm `argument-hint` lists it. When *referencing* another skill's flag, grep that skill's `argument-hint` + body to confirm the flag exists.

**When to apply.** Any body that documents or cross-references a `--flag`.

## B3. Broken internal markdown anchors

**Pattern.** A link to `agent.md#category-11-numerical-discipline` where the actual heading anchorizes to something else (`### 11. NUMERICAL DISCIPLINE` → `11-numerical-discipline`). Renaming a heading silently breaks every anchor into it.

**How to catch.** For each `[text](path#anchor)`, resolve `path` and check `anchor` against a GitHub-flavored-markdown anchorize of the target's headings. Always re-check after renaming a heading.

**When to apply.** Any doc change, especially heading renames.

## B4. Rule ↔ skill / agent ↔ skill scope contradiction

**Pattern.** A rule's `paths:` claims a skill runs the rule, but the skill's body doesn't implement it (silent rule↔implementation drift). Or an agent scope note says "for slides, not manuscripts" while listing a manuscript skill as a user — internally contradictory.

**How to catch.** For each rule that names a skill in scope, confirm the skill's body actually mentions the rule's mechanism. For agent scope notes, cross-check every listed user-skill against the scope claim; a multi-artifact agent calling itself "single-artifact" is the bug.

**When to apply.** When a rule expands its `paths:`, or when adding a scope note to an agent.

## B5. Enumerative summary / count drift (whack-a-mole)

**Pattern.** A summary paragraph, README tagline, CHANGELOG lede, or `description:` field drifts from the body across time; surgical one-phrase fixes introduce a new drift in the same paragraph. Bare count shorthands (`27/13/22/6`) reorder and rot; stale counts hide outside the canonical phrasing (`N specialized agents`, `reviewed by N agents`); appendix "All Skills/Agents" tables tabulate a different N than the lede claims.

**How to catch.** Two review-bot flags on the same summary paragraph ⇒ rewrite it structurally (abstract-up), don't patch (per [`summary-parity.md`](../rules/summary-parity.md)). Use only the canonical labeled form `N skills / M agents / K rules / L hooks`. On any count change, grep the whole tree for the **old** value in *all* modifier contexts, and row-count the appendix tables against `ls .claude/{skills,agents,rules}/`. **Do not** update historical CHANGELOG entries — past-version counts are snapshots and must stay as shipped.

**When to apply.** Any count change; any CHANGELOG lede / README / `description:` edit.

## B6. Stale docstring / behavioral-contract ↔ implementation drift

**Pattern.** A function/hook docstring claims behavior the code no longer has ("blocks Claude from stopping" when it's now stderr-only; "fail-open on parse errors" when a narrow `except OSError` lets `UnicodeDecodeError` hard-fail; "argument-hint ↔ body … and vice versa" when only one direction is implemented; "exits 1 on P0" when it exits 1 on P0 *or* P1).

**How to catch.** Extract every behavioral claim from a docstring (blocks / fails / exits N on X / returns Y / bidirectional / fail-open) and verify the control flow matches. For fail-open file readers, confirm realistic failure modes are caught (`OSError`, `UnicodeError`, `JSONDecodeError`) with explicit `encoding="utf-8"`. Re-read the docstring whenever you change a return/side-effect path. Especially critical for audit/gate infra — a bug here undermines everything it checks.

**When to apply.** Any function/script whose docstring makes a behavioral claim.

## B7. Daemon phrasing for patterns that aren't daemons

**Pattern.** Docs say "go through the orchestrator" / "the orchestrator activates" as if it were a runtime service. The orchestrator is a *pattern* specific skills implement, not a daemon you invoke.

**How to catch.** Grep for daemon-like verbs ("invoke the X", "X activates when", "X runs after Y") applied to patterns/rules/protocols. When "X" is a pattern/rule/protocol the phrasing is wrong; when "X" is a hook/service/skill it may be right.

**When to apply.** Anywhere the orchestrator or a protocol/pattern is described, especially after reframing work.

## B8. `CronCreate` for long-delay autonomous work

**Pattern.** Using `CronCreate` (tied to the local Claude Code REPL's event loop) for work that must fire > 10 minutes later. If the session dies (rate limit, closed panel, machine sleep), the cron dies with it; the plan survives on disk but the trigger doesn't.

**How to catch.** Any `CronCreate` with delay > 10 minutes: ask "will the session definitely be running at fire time?" If not, use **Claude Code Routines** (run on Anthropic's web infra, REPL-independent) for overnight/scheduled/AFK work. Rule of thumb: `CronCreate` for minutes within an active session, Routines for hours.

**When to apply.** Any scheduling decision, especially when the user will be away.

## B9. Dead config-map / registry entries that imply false coverage

**Pattern.** A keyword dict, path-pattern list, or rule-reference registry has entries that no execution path reaches (e.g. a rule-keyword entry for a rule whose scope frontmatter never fires the check). A future maintainer assumes the entry exercises coverage it doesn't.

**How to catch.** When adding an entry to any `{key: config}` map, trace at least one input that reaches it. Dead entries are worse than omissions — remove them or document why they're parked.

**When to apply.** Editing any config map, path-pattern list, or reference registry.

---

## Meta — how this file is maintained

- After any review (referee, co-author, or bot) catches something an audit agent missed, append a new entry or extend an existing one with the new evidence — **grow, don't rewrite**.
- When a class becomes mechanically checkable, note it but keep the entry — it's still useful reviewer context.
- Target ≤ 12 entries per part; if a part hits ~15, merge related classes or archive resolved ones to a `_resolved.md` sibling.
- Reference this file from the `deep-audit`, `code-reviewer`, `domain-reviewer`, and `methods-referee` prompts so the relevant part loads.
- Link from MEMORY.md `[LEARN]` entries when a specific lesson ties to an entry here.
