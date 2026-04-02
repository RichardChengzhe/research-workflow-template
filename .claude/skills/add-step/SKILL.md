---
name: add-step
description: Scaffold a new pipeline step. Creates script file, updates pipeline.md, 00_run.do, and run_all.sh. Use when adding new analysis steps.
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob"]
---

# Add Pipeline Step

Scaffold a new pipeline step with all necessary documentation and integration.

## Steps

1. **Gather information** (ask user if not provided):
   - Step number (suggest the next available number with a gap)
   - Script name and language (Stata, Python, or SAS)
   - Brief description of what the step does
   - Input files
   - Expected output files

2. **Create the script file** with a standard header:

**For Stata (`code/stata/NN_description.do`):**
```stata
* ==============================================================================
* [Step NN]: [Descriptive Title]
*
* Purpose: [What this script does]
* Inputs:  [Data files read]
* Outputs: [Files created]
* Dependencies: [Upstream scripts]
* ==============================================================================

clear all
set more off

* Load globals from master do-file
do "$stata/00_run.do"

* --- Main code here ---

```

**For Python (`code/python/NN_description.py`):**
```python
"""
[Step NN]: [Descriptive Title]

Purpose: [What this script does]
Inputs:  [Data files read]
Outputs: [Files created]
Dependencies: [Upstream scripts]
"""

from pathlib import Path
import pandas as pd

# --- Main code here ---

```

**For SAS (`code/sas/NN_description.sas`):**
```sas
/* ==============================================================================
 * [Step NN]: [Descriptive Title]
 *
 * Purpose: [What this script does]
 * Inputs:  [Data files/libraries read]
 * Outputs: [Datasets/files created]
 * Dependencies: [Upstream scripts, WRDS access needed?]
 * ============================================================================== */

%let projroot = [PROJECT ROOT PATH];
libname raw    "&projroot/data/raw";
libname proc   "&projroot/data/processed";

/* --- Main code here --- */

```

3. **Update `pipeline.md`:**
   - Add the step to the Pipeline Tree in the correct position
   - Add to the Script Status table
   - Add to the Data Files table if it creates new data
   - Add to the Manuscript Figure Manifest if it creates figures/tables

4. **Update `code/stata/00_run.do`:**
   - Add a commented-out `do` line in the correct position

5. **Update `run_all.sh`:**
   - Add a commented-out `run_script` line in the `--all` section

6. **Show the user everything** before writing.

## Important

- **This changes the pipeline** -- "break the glass" rule applies
- Show all proposed changes to the user before writing
- Use step number gaps (01, 05, 10, 15, 20, 25) for easy future insertion
