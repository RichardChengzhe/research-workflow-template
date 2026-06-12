# CLAUDE.md — Manuscript (Overleaf-as-git-repo)

Instructions for working on the LaTeX manuscript when it is a **coauthored
paper synced through Overleaf's git bridge** (or any web-compiled, multi-author
`.tex` repo). Coauthors edit live in the web editor; you work locally and
pull/push. Treat every assumption here as load-bearing — getting the git
hygiene wrong destroys a coauthor's unsynced edits.

> If the manuscript is a plain local repo (no web editor, single author),
> the compile rule relaxes (you may build locally), but the git-hygiene,
> change-marking, and table-sync rules below still apply.

Cross-references: `.claude/rules/manuscript-overleaf-sync.md` (the enforced
rule), `manuscript/aea_style_guide.md` (formatting), and the
`content-invariants` / `cross-artifact-review` rules (claim ↔ output
consistency).

---

## Git workflow (mandatory)

- **Pull before you edit.** Before touching ANY `.tex` or `.bib`, run
  `git pull` (use `--no-rebase --no-edit` so coauthor commits merge rather
  than rebase). The web editor auto-commits coauthor changes continuously;
  skipping the pull manufactures avoidable line-by-line conflicts.
- **`git fetch` and check ahead/behind before every push.** A coauthor may
  be editing the SAME file in the web editor mid-session, so your local base
  goes stale fast. If your pending commit is now obsolete and would clobber
  their edit, do **not** blind-merge — inspect their commit
  (`git show <sha> -- [FILE]`), adopt their version, then re-apply only your
  specific change on top.
- **Never `git push` automatically.** Make the change, stage it, commit, then
  **stop**. The author reviews in the web editor and pushes. (If the author
  authorizes a push for a given session, that overrides this — per session
  only.)
- **Never `git add -A` and never stage files you did not edit.** Stage only
  the specific files you changed (`git add [FILE]`). Staging unrelated
  working-tree files can sweep a coauthor's half-synced edit into your commit.
- **Commit message convention:** `claude: <section> — <one-line summary>`
  (e.g. `claude: [4_Results.tex] — tighten Table 5 discussion`).

### Known web-bridge gotcha (don't misread it as failure)

Pushing to a web-editor git bridge frequently prints
`error: update_ref failed for ref 'refs/remotes/origin/[BRANCH]'` even though
the **push succeeded** (the remote ref advanced). This is a local
remote-tracking-ref artifact (often a cloud-sync client holding a lock on
`.git`), not a failed push. **Verify with `git ls-remote origin [BRANCH]`**
and compare to `git rev-parse HEAD`; if they match, the push is fine. Local
`git status` may falsely show `[ahead N]` — clear it with
`git update-ref refs/remotes/origin/[BRANCH] <sha>` (often needs a second
try as the lock clears) or `git fetch`. Do **not** conclude the push failed
and re-push.

---

## Change marking (mandatory)

Every edit must be visually distinguishable so the author can review it in the
web editor before accepting:

- **Additions / changed text:** wrap in `\textcolor{red}{...}`.
- **Deletions:** wrap the original in `\sout{...}` — never silently delete.

After review the author accepts (strip the markers) or reverts. To accept in
bulk, use `scripts/strip_redmarks.py` (a brace-matched stripper — a naive
regex corrupts nested braces like `$^{**}$`, `\citet{...}`, `\textit{...}`).

`\textcolor` requires `xcolor` and `\sout` requires `ulem`; both must be
loaded in the **main file** `[0_Main.tex]`. If they are already loaded, make
**no** preamble change. If they are not, ask the author before adding them —
do not edit the preamble unprompted (see "Never modify" below).

---

## Keeping tables in sync with reference outputs (mandatory)

A `manuscript_tables/` (or `results/`) directory holds the **canonical
regression outputs** — the literal numbers — for every printed table.
`manuscript_tables/RESULTS_PROVENANCE.md` maps each table to the script that
generated it (e.g. `tab:[label]` ← `[rebuild_manuscript.do]` →
`[coefs.csv]`). The printed table and its reference file must agree to the
last decimal.

- **Whenever you change a table's numbers** — any `tab:*` in `[N_Tables.tex]`
  or a section file — you **MUST**, in the **same commit**: (1) regenerate
  the corresponding reference file, and (2) update `RESULTS_PROVENANCE.md`. A
  manuscript table edit without a matching reference-output update is
  **incomplete**.
- **When the underlying dataset changes** (a rebuild / new vintage), refresh
  **all** reference files and the provenance header, not just the one table
  you touched.
- Never hand-edit a number in a table. Numbers come only from the generator
  named in `RESULTS_PROVENANCE.md`; rerun it.

This is the manuscript-side enforcement of "no claim without a current
reference output" (`content-invariants` / `cross-artifact-review`).

---

## Don't compile locally (when a web service compiles)

- Do **not** run `pdflatex` / `latexmk` here when the web editor is the
  authoritative compiler. The local TeX install may carry different package
  versions and produce misleading errors or a different PDF.
- If asked to "check it builds," say so explicitly: **verify syntax by
  reading** (balanced environments, matched braces, defined `\ref`/`\cite`
  keys), not by running LaTeX. State that you confirmed by reading, not
  compiling.

---

## Reviews (propose, don't edit)

When asked to review a section:

- **List concerns only — do not edit.** Use a numbered list grouped by
  severity: **substantive** (a claim/result issue) → **structural**
  (organization, missing piece) → **line-edit** (grammar, typo, notation).
- Only after the author accepts a concern: add a TODO, then make that one
  change (change-marked per above).

---

## Never modify

- `.sty` / `.cls` files and any journal/template scaffolding
  (`[journal.sty]`, sample/placeholder `.tex`). These are provided by the
  journal or template; editing them breaks the build or diverges from house
  style. **Never touch them.**
- The **main file** `[0_Main.tex]` (preamble, author list, abstract, package
  loads, bibstyle) — edit only when explicitly asked. Section files
  (`[1_Introduction.tex]` … `[7_Conclusion.tex]`) are the normal edit
  targets.

---

## Bibliography

- Add citations to `[Bibliography.bib]` and cite them in the section file **in
  the same commit**. Use the loaded citation style (`\citep{}` /
  `\citet{}` under `natbib`). Don't leave a `\cite` with no entry or an entry
  with no `\cite`.

## File-layout placeholders (fill in for your project)

| Placeholder | Meaning |
|-------------|---------|
| `[0_Main.tex]` | Orchestrator: preamble, title, `\input{}`s sections. Edit only if asked. |
| `[1_Introduction.tex]` … `[7_Conclusion.tex]` | Body sections — usual edit targets. |
| `[8_Appendices.tex]`, `[N_Tables.tex]`, `[10_Online_Appendices.tex]` | Appendices and tables. |
| `[Bibliography.bib]` | References. |
| `[journal.sty]`, sample/placeholder `.tex` | Template scaffolding — **never modify**. |
| `manuscript_tables/` + `RESULTS_PROVENANCE.md` | Canonical reference outputs + table→generator map. |
