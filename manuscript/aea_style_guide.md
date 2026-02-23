# AEA Style Guide Reference

Quick reference for American Economic Association formatting standards. Consult when editing `manuscript/main.tex`.

## Tables

- Use `booktabs` package (`\toprule`, `\midrule`, `\bottomrule`) -- no vertical lines
- Number tables sequentially (Table 1, Table 2, ...)
- Title above the table, notes below in `\threeparttable`
- Standard errors in parentheses below coefficients
- Significance stars: `* p<0.10, ** p<0.05, *** p<0.01`
- Include N, R-squared, and fixed effects indicators
- Align decimal points with `dcolumn` package

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
