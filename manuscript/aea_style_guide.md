# AEA Style Guide Reference

Quick reference for American Economic Association formatting standards. Consult when editing `manuscript/main.tex`.

## Tables

- Use `booktabs` package (`\toprule`, `\midrule`, `\bottomrule`) -- no vertical lines
- Number tables sequentially (Table 1, Table 2, ...)
- Title above the table, notes below in `\threeparttable`
- **t-statistics in parentheses below coefficients** (this project's
  convention). The standard alternative -- standard errors in parentheses --
  is **not** used here; if you ever switch, state it explicitly in every
  table's notes. Whichever you report, be consistent across all tables.
- Significance stars: `* p<0.10, ** p<0.05, *** p<0.01`
- Include N, adjusted R-squared, and fixed-effects indicator rows
- Align decimal points with `dcolumn` package

### Observed table conventions (this project)

A reusable skeleton with all of the below lives in
`templates/manuscript-table-template.tex`. The conventions:

- **`threeparttable` wrapper** so the notes ride with the table. Notes go in a
  `\begin{tablenotes}[flushleft] ... \end{tablenotes}` block (or an inline
  `\noindent {\footnotesize ...}` header note above the body).
- **Full-width tables** via
  `\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}l...}` -- the
  `@{\extracolsep{\fill}}` stretches the columns edge-to-edge regardless of
  how many model columns there are.
- **Dense body:** put `\fontsize{10}{12}\selectfont` just before the
  `tabular*` so wide regression tables fit the text block.
- **Two lines per estimate:** coefficient + significance stars on the top
  line, `(t-statistic)` on the line directly below. Stars are math
  superscripts (`0.0150$^{***}$`); negatives use a true math minus
  (`$-$0.0045`), not a hyphen. Separate focal terms with `\\[3pt]`.
- **Focal terms grouped first, then a labeled "Controls" block.** Put the
  hypothesis variables (and their interactions) at the top, then the standard
  controls together below them (optionally preceded by a faint `%\midrule`).
- **FE / fit rows separated by a `\midrule`:** below the coefficient body, a
  `\midrule` then the fixed-effects indicator rows (`Industry (SIC3) FE` --
  `Yes`/`No`), `Cluster` (e.g. `Firm`), `$N$`, and `Adj.\ $R^2$`.
- **Thousands formatting with a brace group:** write `12{,}345` (renders
  `12,345`); the `{,}` keeps the comma from being read as a math separator.
- **A `\textit{Notes:}` block** under each table that lists the dependent
  variable, the fixed effects, the clustering, the controls, and the
  significance legend (`* p<0.10, ** p<0.05, *** p<0.01; t-statistics in
  parentheses`).

### Level vs. change (Δ) labeling discipline

- Be explicit in every row label about whether a regressor is a **level** or a
  **change/shock**. Write a change as `$\Delta$X` (e.g. `$\Delta$[SHOCK]`) and
  an interaction with `$\times$` (e.g. `[FOCAL] $\times$ $\Delta$[SHOCK]`).
  Never leave it ambiguous whether a coefficient is on a level or a difference
  -- a reader (or referee) must be able to tell from the label alone.

### Variable definitions appendix

- Provide an appendix that defines every variable (construction, source,
  scaling, winsorization). Point to it from each table's notes
  (`Definitions of all variables are in Appendix~\ref{app:variables}.`).

## Figures

- Number sequentially (Figure 1, Figure 2, ...)
- Caption below the figure
- Source and notes below caption
- Resolution: 300 DPI minimum for raster; prefer vector (PDF)
- Explicit dimensions: set width relative to `\textwidth`
- Grayscale-friendly color palette

## Citations

- Author-year style with `natbib`: `\citet{}` for textual, `\citep{}` for parenthetical
- "Smith (2020) shows..." vs "...is well established (Smith, 2020)"
- Multiple citations: `\citep{Smith2020, Jones2021}` (alphabetical)

## Numbers and Statistics

- Spell out numbers below 10 in text
- Use consistent decimal places (typically 2-3 for coefficients)
- Report exact p-values or use standard star conventions
- Large numbers: use commas (1,234,567)
- Percentages: "5 percent" or "5%" (be consistent)

## Writing

- Active voice preferred
- Past tense for results ("We found that...")
- Present tense for general facts ("The model implies...")
- Avoid first-person singular; use "we" even for single-authored papers
- Concrete, plain language over jargon

## Structure

- Abstract: 100-150 words, no citations, no math
- JEL codes: 2-4 codes
- Keywords: 4-6 terms
- Sections: Introduction, Background, Data, Empirical Strategy, Results, Conclusion
- Appendix for supplementary tables/figures

## References

- AER bibliography style (`\bibliographystyle{aer}`)
- All cited works must appear in references and vice versa
- DOIs encouraged where available
