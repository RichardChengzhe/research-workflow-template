---
paths:
  - "manuscript/**/*.tex"
  - "manuscript/**/*.bib"
  - "manuscript_tables/**"
---

# Manuscript ↔ Overleaf Sync Rule

Concise enforcement of the git / change-marking / reference-output discipline
for a **web-compiled, coauthored** manuscript (Overleaf git bridge or
equivalent). Full rationale and placeholders live in `manuscript/CLAUDE.md` —
this rule does not duplicate it. Complements the `content-invariants`,
`cross-artifact-review`, and `summary-parity` rules for claim ↔ output
consistency.

## Hard rules

1. **Pull before editing.** `git pull --no-rebase --no-edit` before touching
   any `.tex`/`.bib`. `git fetch` + check ahead/behind before every push — a
   coauthor may be live-editing the same file.
2. **Never auto-push; never `git add -A`.** Commit and stop; the author
   reviews and pushes. Stage only files you edited. Commit message:
   `claude: <section> — <summary>`.
3. **Change-mark every edit.** Additions → `\textcolor{red}{...}`; deletions →
   `\sout{...}` (never silent). Requires `xcolor` + `ulem` in the main file.
   Bulk-accept with `scripts/strip_redmarks.py` (brace-matched, **not** regex
   — a regex corrupts `$^{**}$` / `\citet{}` / nested braces).
4. **Table ↔ reference-output sync.** Changing any table's numbers REQUIRES,
   in the **same commit**: regenerate its reference file in
   `manuscript_tables/` *and* update `RESULTS_PROVENANCE.md` (table→generator
   map). On a dataset rebuild, refresh **all** reference files. Never
   hand-edit a number — rerun the generator.
5. **Don't compile locally** when the web editor is authoritative. Verify
   syntax by reading (balanced envs, matched braces, resolved
   `\ref`/`\cite`); state you confirmed by reading, not compiling.
6. **Reviews = propose only.** List concerns by severity (substantive →
   structural → line-edit); edit only after the author accepts.
7. **Never modify** `.sty`/`.cls`/template scaffolding, or the main file's
   preamble/author/abstract unless explicitly asked.

## Known gotcha

A web-bridge push can print `update_ref failed for ref ...origin/<branch>`
yet still **succeed**. Verify with `git ls-remote origin <branch>` vs
`git rev-parse HEAD`; if equal, the push is fine. Do not re-push. Clear a
false `[ahead N]` with `git update-ref` or `git fetch`.
