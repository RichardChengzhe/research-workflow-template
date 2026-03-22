---
paths:
  - "data/**"
  - "code/**"
---

# Data Management Protocol

## Directory Structure

```
data/
├── raw/           <- READ-ONLY source data. NEVER modify.
│   ├── source_a/
│   ├── source_b/
│   └── README.md  <- Documents all sources
└── processed/     <- Derived datasets created by scripts
```

## Raw Data Rules

1. **NEVER modify files in `data/raw/`** -- this is enforced by the protect-files hook
2. **Document every raw data source** in `data/raw/README.md`
3. **Raw data is excluded from git** -- managed externally (Dropbox, cloud, etc.)
4. **Before reading restricted data**, confirm with user it's safe to access

## Naming Conventions

### Processed Data Files
- Format: `[description]_[version].dta` or `.csv` or `.pkl`
- Examples: `source_a_clean.dta`, `analysis_sample_v2.dta`
- Include creation date in file metadata, not filename

### Scripts
- Numbered by pipeline step: `01_import.do`, `05_merge.do`, `10_summary.do`
- Gaps between numbers (01, 05, 10, 15, 20, 25) for easy insertion
- Prefix matches pipeline.md step numbers

## Merge Documentation

When merging datasets, document in the script header AND in pipeline.md:

```stata
* Merge: source_a_clean.dta (N=XXX) x source_b_clean.dta (N=YYY)
* Key: id + year
* Expected: M:1 merge
* Result: N=ZZZ observations, XX% matched
merge m:1 id year using "$processed/source_b_clean.dta"
tab _merge
assert _merge != 1  // all source_a obs should match
```

## Pipeline Integrity

- Every processed data file must be traceable to a script in `pipeline.md`
- Every script's inputs and outputs must be documented in its header
- Use `/check` to verify all files exist and dependencies are satisfied
