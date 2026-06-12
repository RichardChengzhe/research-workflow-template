---
name: cypress
description: Run Python and Stata jobs on a SLURM HPC cluster. Covers SSH access, job-script templates, module loading, file transfer (scp/rsync), array-task decomposition under a core cap, and Stata-MP package install. Triggers - "run on the cluster", "SLURM", "sbatch", "HPC job", "submit to the cluster", "run this on Cypress".
allowed-tools: ["Read", "Bash", "Glob", "Grep", "Write", "Edit"]
---

# SLURM HPC Cluster — Python & Stata

Write, submit, and manage **Python** and **Stata** jobs on a SLURM-based HPC cluster. This is a generic template; fill in the customizable block below for your specific cluster — adapt host, account, partitions, and paths to your institution.

---

## CUSTOMIZE THIS BLOCK FIRST

Replace these placeholders everywhere they appear below. Confirm each value against your cluster's docs / `sinfo` / `module avail` before relying on it.

| Placeholder | Meaning | How to find it |
|---|---|---|
| `<CLUSTER_HOST>` | login hostname (or SSH alias) | cluster docs; set an alias in `~/.ssh/config` |
| `<USER>` | your cluster username | `whoami` after SSH |
| `<ACCOUNT>` | SLURM account / allocation | `sacctmgr show assoc user=<USER>` |
| `<PARTITION_DEFAULT>` | default compute partition | `sinfo -s` |
| `<PARTITION_NEWLIBC>` | partition with a newer libc (for modern Python) | `sinfo`; cluster docs |
| `<SCRATCH>` | large scratch/project path (NOT backed up) | e.g. `/lustre/project/<grp>/<USER>` or `/scratch/<USER>` |
| `<HOME_QUOTA_GB>` | home quota (small) | cluster docs / `quota` |
| `<STATA_MP_PATH>` | dir holding the `stata-mp` binary | `module avail stata`; cluster admin |
| `<CONDA_BASE>` | your miniconda/anaconda base on scratch | you install it |
| `<PY_ENV>` | your project conda env path | you create it |

Set an SSH alias so commands stay short:

```
# ~/.ssh/config
Host cluster
    HostName <CLUSTER_HOST>
    User <USER>
    IdentityFile ~/.ssh/id_ed25519
```

Then `ssh cluster ...` everywhere below.

---

## How to run code on the cluster from Claude Code

### Step 1: Transfer the script (fix Windows line endings)

```bash
scp /path/to/local_script.py cluster:<SCRATCH>/code/
# If authored on Windows, normalize CRLF -> LF on the remote:
ssh cluster "sed -i 's/\r$//' <SCRATCH>/code/local_script.py"
```

### Step 2: Write a SLURM job script

Write locally, `scp` to the cluster, fix line endings. Use the templates below.

### Step 3: Submit and monitor

```bash
ssh cluster "sbatch <SCRATCH>/code/job.sh"
ssh cluster "squeue -u <USER>"                 # status
ssh cluster "cat <SCRATCH>/logs/<logfile>"     # read output
```

### Step 4: Retrieve results promptly

```bash
scp cluster:<SCRATCH>/output/results.csv ./local_dir/
```

> Scratch is typically **not backed up** and may be idle-cleaned. Download deliverables as soon as a job finishes — see `.claude/rules/remote-jobs.md`.

---

## Login-node vs compute-node library constraints (modern Python)

Many clusters have an **older login node / default partition** (older glibc) and a **separate partition with a newer libc**. Modern Python (3.10+) often needs the newer libc and will fail on the login node or default partition.

- **Do NOT run heavy work — or modern Python — on the login node.** Use `sbatch`, or an interactive allocation (`idev` / `salloc` / `srun --pty bash`) for testing.
- Run modern Python on `<PARTITION_NEWLIBC>`; older Python (3.8-class) usually runs fine on `<PARTITION_DEFAULT>`.
- Verify the constraint on your cluster before assuming — partitions and libc versions vary.

## Modules

```bash
module avail                # list all (some clusters: older Lmod has no `module spider`)
module avail <name>         # search, e.g. `module avail stata`
module load <name>
module list
module purge
```

Always `module load` (or set `PATH`) **inside the job script** — never rely on the login-node environment carrying over.

---

## Python job-script template (conda env on scratch)

Install a fresh miniconda on scratch (fast solver, no home-quota pressure) and create your project env there.

```bash
#!/bin/bash
#SBATCH --job-name=py_job
#SBATCH --partition=<PARTITION_NEWLIBC>     # required for modern Python (newer libc)
#SBATCH --account=<ACCOUNT>
#SBATCH --qos=normal                        # raise to a long QOS for >24h jobs
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8                   # cores for pandas/numpy parallelism
#SBATCH --mem=96000                         # MB; size to dataset + overhead
#SBATCH --time=1-00:00:00
#SBATCH --output=<SCRATCH>/logs/py_%j.log
#SBATCH --error=<SCRATCH>/logs/py_err_%j.log
#SBATCH --mail-type=FAIL                    # some SLURM configs reject END,FAIL — FAIL-only is safe

module purge
export PYTHONUNBUFFERED=1                    # CRITICAL: real-time log output (else logs stay empty until exit)
export PROJECT_BASE=<SCRATCH>
export PATH=<CONDA_BASE>/bin:$PATH
source <CONDA_BASE>/etc/profile.d/conda.sh
conda activate <PY_ENV>

cd ${PROJECT_BASE}
python code/my_script.py
```

Multi-core hygiene:

```bash
#SBATCH --cpus-per-task=10
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export MKL_NUM_THREADS=$SLURM_CPUS_PER_TASK
```

```python
import os
n_cores = int(os.environ.get("SLURM_CPUS_PER_TASK", 1))
BASE = os.environ.get("PROJECT_BASE", "<SCRATCH>")  # never hardcode the scratch path in scripts
```

---

## Stata on the cluster

### Stata-MP package install (do this ONCE, before the first run)

On many cluster Stata-MP installs, **`reghdfe` silently fails unless the `require` package is also installed** — every `reghdfe` call errors (buried in the log), the job **exits 0**, and the output CSV contains **only headers**. Install all five in a one-shot setup `.do` on a compute node (or via an interactive session):

```stata
ssc install ftools,   replace
ssc install moremata, replace
ssc install estout,   replace
ssc install reghdfe,  replace
ssc install require,  replace   // <-- reghdfe needs this or it silently no-ops

* Verify the toolchain actually works before trusting any batch:
sysuse auto, clear
reghdfe price mpg, absorb(rep78)
```

> **Always confirm the output CSV has data rows, not just a header, before declaring success.** Stata batch exit 0 + header-only CSV = a silent failure (commonly the missing-`require` case above). Grep the Stata log for an error count / "Failed regressions:" before trusting results.

### Stata job-script template (Stata-MP)

```bash
#!/bin/bash
#SBATCH --job-name=stata_job
#SBATCH --partition=<PARTITION_DEFAULT>     # Stata usually wants the default partition's libs
#SBATCH --account=<ACCOUNT>
#SBATCH --qos=normal                        # long QOS for multi-day jobs
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8                   # match your Stata-MP core entitlement (see cap note below)
#SBATCH --mem=32000                         # MB; Stata loads data into RAM — size accordingly
#SBATCH --time=1-00:00:00
#SBATCH --output=<SCRATCH>/logs/stata_%j.log
#SBATCH --error=<SCRATCH>/logs/stata_err_%j.log
#SBATCH --mail-type=FAIL

module purge
# If there is no modulefile for your Stata-MP, add the binary dir to PATH directly:
export PATH=<STATA_MP_PATH>:$PATH

cd <SCRATCH>
stata-mp -b do my_analysis.do
```

Stata tips:
- `stata-mp -b do script.do` runs in batch and writes `script.log` in the cwd (use `#SBATCH --output` for the SLURM-level log too).
- Inside the `.do`, cap processors to your license entitlement: `set processors <N>`.
- Set Stata's temp/working dir to scratch for large data: `cd <SCRATCH>/tmp`.
- Some Stata builds are missing graphics libs on a newer-libc partition — if a build fails there, use `<PARTITION_DEFAULT>`.

### MP core cap → decompose into array tasks (KEY for wall time)

Cluster Stata-MP licenses commonly **cap cores per process** (e.g. an 8-core MP cap). Requesting `--cpus-per-task` beyond the cap **wastes the slot**. Speed-ups come from **more array tasks, not more cores per task.**

```bash
#SBATCH --array=0-1                          # e.g. one task per sub-sample
# Map the array index to a decomposition key, pass it as an env var:
KEYS=(full sub)
export SAMPLE=${KEYS[$SLURM_ARRAY_TASK_ID]}
export PATH=<STATA_MP_PATH>:$PATH
stata-mp -b do my_analysis.do
```

```stata
local samp : env SAMPLE
* ... branch on `samp', write a sample-suffixed output CSV ...
```

Decomposition guidance:
- First, cheap split: by sample / sub-population.
- Next: by outcome variable, horizon group, or other independent axis (~5-10 tasks).
- Keep each task ≥ ~30 s of real work (to amortize Stata startup + data load) and ≤ ~15 min wall (to keep parallelism).
- One output file per task; concatenate locally on retrieval.
- Estimate the `N_tasks × cores × wall` budget **before** submitting. See `.claude/rules/remote-jobs.md`.

---

## File transfer

```bash
# Local -> cluster
scp myfile.txt cluster:<SCRATCH>/
scp -r mydir/  cluster:<SCRATCH>/data/

# Cluster -> local
scp cluster:<SCRATCH>/output/results.csv ./

# rsync (efficient for repeated/large transfers)
rsync -avz mydir/ cluster:<SCRATCH>/data/
```

Large data goes on `<SCRATCH>`, **not** home (home has a small `<HOME_QUOTA_GB>` quota and may be backed up). Scratch is not backed up — copy results off promptly.

---

## Job-management cheat sheet

```bash
sbatch job.sh                    # submit
squeue -u $USER                  # status
scancel <jobid>                  # cancel one
scancel -u $USER                 # cancel all your jobs
sacct -j <jobid> -o MaxVMSize    # peak memory used
sprio -j <jobid>                 # priority

# Chain dependent jobs
JOB1=$(sbatch --parsable job1.sh)
sbatch --dependency=afterok:$JOB1 job2.sh
```

---

## Python performance on HPC

- **Never `groupby().apply()` on large DataFrames** — it calls Python once per group (millions of calls). Use vectorized `groupby().agg(...)`. For conditional aggregations, filter first, then `groupby` each subset.
  ```python
  # BAD: hours on large data
  grouped.apply(lambda g: pd.Series({"mean": g["x"].mean(), "sum": g["y"].sum()}))
  # GOOD: seconds on large data
  grouped.agg(mean_x=("x", "mean"), sum_y=("y", "sum"))
  ```
- **Parquet row-group streaming** for files too large to load at once:
  ```python
  import pyarrow.parquet as pq
  pf = pq.ParquetFile(path)
  for i in range(pf.metadata.num_row_groups):
      chunk = pf.read_row_group(i, columns=COLS).to_pandas()
  ```
- **Resume pattern for multi-phase pipelines:** save an intermediate output at the end of each phase; write a `_resume` guard that skips phases whose output already exists. Avoids re-running expensive early phases when iterating downstream.
- **Don't mutate input DataFrames inside functions** (no `df["_tmp"] = ...` on a caller's frame) — compute derived columns as local Series.

---

## Common mistakes

| Mistake | Fix |
|---|---|
| Running heavy work / modern Python on the login node | Use `sbatch` or an interactive allocation |
| Not loading modules / setting PATH in the job script | Always do it inside the script |
| Large data on home (small quota) | Use `<SCRATCH>` |
| Not copying scratch results off | Scratch is not backed up; download deliverables promptly |
| `reghdfe` returns header-only CSV, exit 0 | Install `require` (it silently no-ops without it); verify with `webuse auto + reghdfe` |
| Requesting cores beyond the MP cap | Wasted slot; decompose into more array tasks instead |
| Modern Python on the older-libc partition | Use `<PARTITION_NEWLIBC>` |
| Missing `PYTHONUNBUFFERED=1` | Python buffers stdout; logs stay empty until the script exits |
| `--mail-type=END,FAIL` rejected by SLURM | Use `--mail-type=FAIL` only |
| Missing `--account=<ACCOUNT>` | Required for submission under your allocation |
| Trusting Stata batch exit 0 | Confirm CSV has data rows; grep the log for errors |

## See also

- `.claude/rules/remote-jobs.md` — poll/monitor long jobs; download before cleanup; array decomposition discipline.
- `.claude/skills/sas/SKILL.md` — WRDS remote SAS (a different remote target with its own queue/quota rules).
