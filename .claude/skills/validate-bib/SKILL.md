---
name: validate-bib
description: Validate bibliography entries against citations in manuscript files. Find missing entries and unused references.
allowed-tools: ["Read", "Grep", "Glob"]
---

# Validate Bibliography

Cross-reference all citations in manuscript files against bibliography entries.

## Steps

1. **Read the bibliography file** (`manuscript/references.bib`) and extract all citation keys

2. **Scan all manuscript files for citation keys:**
   - `.tex` files: look for `\cite{`, `\citet{`, `\citep{`, `\citeauthor{`, `\citeyear{`
   - Extract all unique citation keys used

3. **Cross-reference:**
   - **Missing entries:** Citations used in manuscript but NOT in bibliography
   - **Unused entries:** Entries in bibliography not cited anywhere
   - **Potential typos:** Similar-but-not-matching keys

4. **Check entry quality** for each bib entry:
   - Required fields present (author, title, year, journal/booktitle)
   - Author field properly formatted
   - Year is reasonable
   - No malformed characters or encoding issues

5. **Report findings:**
   - List of missing bibliography entries (CRITICAL)
   - List of unused entries (informational)
   - List of potential typos in citation keys
   - List of quality issues

## Files to scan:
```
manuscript/*.tex
```

## Bibliography location:
```
manuscript/references.bib
```
