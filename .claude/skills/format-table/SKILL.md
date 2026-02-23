---
name: format-table
description: Format Stata regression output as a publication-ready LaTeX table. Handles esttab output, adds proper formatting, and saves to output/tables/.
argument-hint: "[table description or estimation results to format]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob"]
---

# Format Publication-Ready Table

Format Stata regression output as a publication-ready LaTeX table following AEA style.

**Input:** `$ARGUMENTS` -- description of the table to format, or path to existing esttab output.

## Steps

1. **Identify the source:**
   - If `$ARGUMENTS` points to an existing `.tex` file, read it
   - If it describes results to format, locate the relevant .ster files or log output

2. **Apply AEA formatting standards** (from `manuscript/aea_style_guide.md`):
   - Use `booktabs` package (`\toprule`, `\midrule`, `\bottomrule`)
   - No vertical lines
   - Standard errors in parentheses below coefficients
   - Significance stars: `* p<0.10, ** p<0.05, *** p<0.01`
   - Include N, R-squared, and fixed effects indicators
   - Align decimal points with `dcolumn` where appropriate

3. **Wrap in threeparttable** for notes:

```latex
\begin{table}[htbp]
\centering
\begin{threeparttable}
\caption{[Descriptive Title]}
\label{tab:[label]}
\begin{tabular}{l*{N}{D{.}{.}{-1}}}
\toprule
 & \multicolumn{1}{c}{(1)} & \multicolumn{1}{c}{(2)} \\
 & \multicolumn{1}{c}{[Dep Var]} & \multicolumn{1}{c}{[Dep Var]} \\
\midrule
[Content]
\midrule
Observations & [N] & [N] \\
R-squared & [R2] & [R2] \\
Fixed Effects & [Yes/No] & [Yes/No] \\
\bottomrule
\end{tabular}
\begin{tablenotes}
\small
\item \textit{Notes:} Standard errors clustered at [level] in parentheses.
* p<0.10, ** p<0.05, *** p<0.01.
\end{tablenotes}
\end{threeparttable}
\end{table}
```

4. **Save to** `output/tables/[table_name].tex`

5. **Verify** the table compiles within the manuscript

## Stata esttab Reference

For generating the raw table from Stata:
```stata
eststo clear
eststo: reghdfe $outcome_var treatment $controls, absorb($fe_vars) vce(cluster $cluster_var)
eststo: reghdfe $outcome_var treatment $controls more_controls, absorb($fe_vars) vce(cluster $cluster_var)
esttab using "$tables/table_name.tex", replace ///
    booktabs se star(* 0.10 ** 0.05 *** 0.01) ///
    title("Table Title") label ///
    stats(N r2, labels("Observations" "R-squared"))
```

## Important

- Follow `manuscript/aea_style_guide.md` for all formatting decisions
- Every table must be self-contained (reader can understand without text)
- Include clear column headers and row labels
