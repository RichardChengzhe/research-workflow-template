---
name: visual-audit
description: Adversarial visual/legibility audit of publication figures produced by matplotlib (Python) or Stata graphics. Flags illegible axis/tick labels at print size, missing axis titles/units, color-only encodings that fail in grayscale, sub-300-DPI raster exports, overplotting, and chartjunk. Reads both the figure-generating source and the rendered file. Use when user says "visual audit", "check the figures", "are these legible?", "grayscale-safe?", "audit Figure N", or before submission. Does NOT check AEA table/caption formatting (use `output-critic` / `/fix-output`) or TikZ diagrams.
argument-hint: "[figure file, generating script, or 'all']"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Write", "Task"]
---

# Visual Audit of Publication Figures (matplotlib / Stata)

Perform a thorough legibility-and-design audit of the paper's figures. The lens is **visual correctness at journal print size**, not formatting compliance — that is the `output-critic` agent's job (AEA captions, `\includegraphics{}` resolution, the figure manifest). Run both; they catch different defects.

**Scope:** raster/vector figures in `output/figures/` (`.pdf`, `.png`, `.eps`, `.svg`) and the source that generates them — matplotlib in `code/**/*.py` and Stata `graph`/`twoway`/`graph export` commands in `code/**/*.do`. **Not** TikZ/PGFplots diagrams and **not** Beamer slides (use `slide-auditor` for decks).

## Why audit figures separately

A figure that looks fine on a 27-inch monitor is often unreadable in a printed two-column journal page or a grayscale printout. The recurring failures are mechanical and detectable: 6-pt tick labels, a blue/orange contrast that collapses to identical grays, a 150-DPI PNG that pixelates, a y-axis with no units. Referees and typesetters bounce these. Catch them before submission.

## Inputs

- `$ARGUMENTS` — one of:
  - a rendered figure path (`output/figures/fig_event_study.pdf`),
  - a generating script (`code/python/plot_event_study.py` or `code/stata/04_analysis.do`),
  - `all` — audit every figure in `output/figures/` and trace each back to its generator.

## Workflow

### Phase 0: Resolve targets and gather facts

1. Build the figure ↔ generator map. For each rendered figure, find the script that exports it (grep for the filename in `savefig(...)` / `graph export "...filename..."`).
2. **Inspect the rendered file directly.** Reading the image is the ground truth — a `Read` on a `.png`/`.pdf` shows you what the eye will see. Do this for every figure; do not audit from source alone.
3. **Pull objective facts from the file** where cheap:
   ```bash
   # raster DPI + pixel dimensions (ImageMagick, if available)
   identify -format "%f: %wx%h px, %x x %y DPI\n" output/figures/*.png 2>/dev/null
   # PDF: confirm it is vector (no giant embedded raster) and get the media box
   pdfinfo output/figures/fig.pdf 2>/dev/null | grep -E "Page size|Page rot"
   # is a "vector" PDF actually a wrapped bitmap? (large file + single image xobject is a smell)
   pdfimages -list output/figures/fig.pdf 2>/dev/null | head
   ```
   If these tools are absent, fall back to reading the source for the export settings (`dpi=`, format) and note that the file-level check was skipped.
4. **Read the generating source** for the settings the rendered file can't always reveal: figure size, font sizes, color specification, legend, and export DPI/format.

### Phase 1: Audit every figure across these dimensions

Severity tags: **CRITICAL** (illegible or wrong at print size — blocks submission), **MAJOR** (degrades comprehension), **MINOR** (polish).

#### 1. LEGIBILITY AT PRINT SIZE  (CRITICAL when it fails)
- Will axis-tick labels, axis titles, and in-plot annotations be readable when the figure is scaled to its `\includegraphics` width (often `\columnwidth` ~3.2 in, or `\textwidth` ~6.5 in)? Rule of thumb: effective font size on the printed page should be ~7-9 pt, never below ~6 pt.
- matplotlib: check `figsize`, `rcParams['font.size']` / `fontsize=` on labels/ticks, and whether `bbox_inches='tight'` is shrinking text further. A `figsize=(12,8)` figure shrunk into one column makes 10-pt fonts tiny.
- Stata: check `graphregion`/`xsize`/`ysize`, `labsize()`/`labsize()` on axis labels and ticks; default Stata label sizes often print small.

#### 2. AXES, UNITS, AND SCALE  (MAJOR-CRITICAL)
- Both axes have a title with **units** (e.g., "Cumulative abnormal return (bps)", "Event month relative to t=0"). A bare "CAR" with no unit is a finding.
- Tick density is sane (not 30 overlapping date ticks; not 2 ticks on a continuous axis).
- Scale honesty: a truncated y-axis that exaggerates an effect is flagged; a dual y-axis is flagged unless clearly justified. Log scales are labeled as such.
- Zero/reference lines drawn where they aid reading (e.g., a horizontal line at 0 for an event-study CAR plot; the event date marked).

#### 3. COLOR AND GRAYSCALE-SAFETY  (CRITICAL when color is the only encoding)
- **Grayscale test.** Will the series remain distinguishable when printed in black and white? If categories are separated by hue alone (default matplotlib C0/C1/C2; Stata default scheme colors), that is a CRITICAL finding — add a redundant encoding (line style: solid/dashed/dotted; marker shape; direct labels).
  ```bash
  # quick grayscale proof for a raster figure
  convert output/figures/fig.png -colorspace Gray /tmp/fig_gray.png 2>/dev/null && echo "wrote /tmp/fig_gray.png — read it and confirm series are still separable"
  ```
- **Colorblind safety.** Avoid red/green as the sole contrast. Prefer a colorblind-safe palette (matplotlib `tab10`/`viridis`/`cividis`; Stata `s2color` is weak — consider `plotplain`/`white_tableau` from `blindschemes`, or set explicit `lcolor()`/`lpattern()`).
- Sufficient contrast against a white background; no neon/pastel that washes out in print.

#### 4. RESOLUTION AND FORMAT  (CRITICAL for raster below threshold)
- Vector (`.pdf`/`.eps`) is preferred for line/scatter plots — it never pixelates. Flag a raster `.png` used where vector was available.
- If raster is necessary (heatmaps, dense scatter), **>= 300 DPI** at final print size. matplotlib: `savefig(..., dpi=300)`. A `dpi=72`/`dpi=100` export is a CRITICAL finding.
- A "PDF" that is just a wrapped low-res bitmap (caught by `pdfimages -list`) is treated as raster — apply the DPI rule.

#### 5. DATA-INK / OVERPLOTTING  (MAJOR-MINOR)
- Overplotting: thousands of opaque points hiding the mass — recommend `alpha`, hexbin/2-D density, or a binned scatter (a `binscatter`-style summary is standard in finance).
- Chartjunk: 3-D bars, heavy gridlines, redundant legends, background fills, boxed-in plot frames that add ink without information.
- Legend placed over data; series order in legend not matching plot order.

#### 6. CONSISTENCY ACROSS THE PAPER'S FIGURES  (MAJOR)
- Same construct → same color/linestyle across all figures (e.g., the treated group is always the solid dark line).
- Consistent fonts, figure aspect ratios, and axis conventions across the figure set, so the paper reads as one document.

### Phase 2: Report

Write `quality_reports/visual_audit_[stem].md` (or `..._all.md`), organized **by figure**, each finding with severity, the evidence (what you saw in the rendered file and/or the source line), and a **least-destructive remedy first** recommendation.

```markdown
# Visual Audit: <figure or 'all'>

**Date:** YYYY-MM-DD
**Figures audited:** N
**Findings:** <total> (<C> CRITICAL, <Mj> MAJOR, <Mn> MINOR)

## Figure: output/figures/fig_event_study.pdf  (generator: code/python/plot_event_study.py)

| Sev | Dimension | Evidence | Remedy |
|-----|-----------|----------|--------|
| CRITICAL | Color/grayscale | Treated vs control separated by hue only; identical in grayscale proof | Add lpattern (solid/dashed) + markers; keep color as redundant |
| CRITICAL | Resolution | PNG exported at dpi=100 (savefig line 88) | Export PDF (vector) or dpi=300; line/scatter → prefer PDF |
| MAJOR | Axes/units | y-axis labeled "CAR", no unit | "Cumulative abnormal return (bps)" |
| MINOR | Data-ink | Heavy gridlines dominate | ax.grid(alpha=0.3) or drop |

## Cross-figure consistency
- [e.g., treated group is dark-solid in Fig 7 but light-dashed in Fig 8 — unify.]
```

### Phase 3 (optional): hand off to a fixer / formatter

This skill **reports**; it does not edit. To act on findings:
- For figure-*formatting* against AEA style (caption, `\includegraphics` path, manifest), run the `output-critic` → `output-fixer` loop via `/fix-output`.
- For the *generating code* (changing `dpi=`, `lpattern()`, axis labels), edit the matplotlib/Stata source and **re-export**, then re-run `/visual-audit` to confirm.

## Remedy priority (least-destructive first)

When a figure is cramped or unreadable, prefer changes that preserve the data:
1. Increase font sizes (labels, ticks, annotations) — usually the real fix.
2. Add the missing redundant encoding (linestyle/marker) rather than just changing colors.
3. Switch raster → vector, or raise DPI, before resizing.
4. Reduce tick density / declutter (drop gridlines, move legend) before shrinking the plot.
5. Re-aspect the figure to its print width (`figsize`/`xsize,ysize`) so nothing is scaled down on the page.
6. Last resort: drop a series or split into panels — only when the figure is genuinely overloaded.

## When NOT to use

- TikZ/PGFplots diagrams (different toolchain; out of scope).
- Beamer slide decks (use `slide-auditor`).
- Table formatting (use `output-critic` / `/fix-output`).

## Cross-references

- `.claude/agents/output-critic.md` — AEA formatting/caption/path/manifest compliance for tables AND figures (complementary lens).
- `.claude/skills/fix-output/SKILL.md` — the output-critic → output-fixer adversarial loop.
- `manuscript/aea_style_guide.md` — figure conventions (vector preferred, 300 DPI minimum, standalone caption).
- `.claude/skills/seven-pass-review/SKILL.md` — Lens 4 does a shallow figure check and defers the deep audit here.
