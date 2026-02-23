---
name: compile-latex
description: Compile the manuscript with latexmk. Use when compiling the paper.
argument-hint: "[optional: specific .tex file, defaults to manuscript/main.tex]"
allowed-tools: ["Read", "Bash", "Glob"]
---

# Compile LaTeX Manuscript

Compile the research paper using latexmk with full citation resolution.

## Steps

1. **Determine the target file:**
   - If `$ARGUMENTS` is provided, use it
   - Otherwise, default to `manuscript/main.tex`

2. **Compile with latexmk:**

```bash
cd manuscript && latexmk -pdf main.tex
```

**Alternative (manual 3-pass):**
```bash
cd manuscript
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

3. **Check for warnings:**
   - Grep output for `Overfull \\hbox` warnings
   - Grep for `undefined citations` or `Label(s) may have changed`
   - Report any issues found

4. **Report results:**
   - Compilation success/failure
   - Number of overfull hbox warnings
   - Any undefined citations
   - PDF page count

## Why latexmk?
latexmk automatically determines how many passes are needed and runs bibtex when required.

## Important
- Run from the `manuscript/` directory
- The bibliography file `references.bib` must be in `manuscript/`
- Output tables are included via `\input{../output/tables/...}`
- Output figures are included via `\includegraphics{...}` with `\graphicspath{{../output/figures/}}`
