---
name: sas
description: Run SAS programs locally (batch mode) or remotely on WRDS. Covers execution, WRDS connection, log reading, common empirical finance patterns, and debugging. Triggers - "run SAS", ".sas", "WRDS", "rsubmit", "libname", "proc sql", SAS errors.
argument-hint: "[script path, e.g., code/sas/0_CompControls.sas] or [wrds] for remote tips"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Write", "Edit"]
---

# SAS Execution & WRDS Access

Run SAS programs locally in batch mode or execute code remotely on WRDS servers.

**Input:** `$ARGUMENTS` — path to a `.sas` file, or "wrds" for WRDS connection guidance.

---

## 1. Local SAS Execution (Batch Mode)

### Windows (SAS 9.4)

SAS runs in batch mode via `run_all.sh` or directly:

```bash
# Via run_all.sh (preferred — captures timestamped log)
./run_all.sh "script_name.sas"

# Direct batch execution
"/c/Program Files/SASHome/SASFoundation/9.4/sas.exe" \
  -sysin "code/sas/script_name.sas" \
  -log "output/logs/script_name_$(date +%Y-%m-%d_%H%M%S).log" \
  -print "output/logs/script_name.lst" \
  -nosplash -nologo
```

### Path Configuration

Set `SAS_PATH` in `run_all.sh`:

```bash
# Windows:
SAS_PATH="/c/Program Files/SASHome/SASFoundation/9.4/sas.exe"
# Linux:
# SAS_PATH="/usr/local/SASHome/SASFoundation/9.4/sas"
# macOS:
# SAS_PATH="/usr/local/SASHome/SASFoundation/9.4/sas"
```

### Reading the Log

**ALWAYS read the log after every SAS run.** SAS does not use exit codes reliably. The log is the only trustworthy indicator.

```bash
# Check for errors
grep -c "^ERROR" output/logs/script_name*.log

# Check for warnings
grep -c "^WARNING" output/logs/script_name*.log

# Show errors with context
grep -B2 -A5 "^ERROR" output/logs/script_name*.log
```

**Key log patterns:**
| Pattern | Meaning |
|---------|---------|
| `ERROR:` | Hard error — script likely failed or produced wrong results |
| `WARNING:` | May be benign (e.g., merge many-to-many) or serious |
| `NOTE: The data set ... has N observations` | Verify N is expected |
| `NOTE: MERGE statement has more than one data set with repeats` | Check merge keys |
| `NOTE: Missing values were generated` | Check missing data handling |
| `NOTE: Invalid argument to function` | Runtime calculation error |
| `real time` / `cpu time` | Execution timing |

---

## 2. WRDS Remote SAS Execution

### 2.0 Choose the right path: SSH + qsas (default for heavy jobs) vs rsubmit (short interactive)

| Workload | Use | Reason |
|---|---|---|
| Heavy job: TAQ pulls, long CTM loops, large rsubmit bodies (>5 KB / >=100 lines), macros with control flow + hash + prxnext, >5 min expected runtime | **SSH + `qsas`** (Section 2.1) | SAS/CONNECT `rsubmit` with a long body **deadlocks** during WRDS autoexec streaming (TBUFSIZE/TCPMSGLEN buffer exhaustion; SAS-documented). Log freezes at exactly 65,536 bytes mid-word at TAQ libref Physical Name. qsas runs on WRDS compute node directly, no client buffer involved. |
| Short diagnostic / schema probe / small extraction (<=100 lines of rsubmit body, <5 min runtime) | **`rsubmit` from local PC-SAS** (Section 2.2) | Simpler iteration, no file upload step |

**Empirically observed:** A long rsubmit body (>500 lines) hung repeatedly on the same code; interleaved short healthchecks passed cleanly; the same code ran successfully via `qsas`. SAS's TBUFSIZE docs explicitly document this failure mode.

### 2.1 SSH + qsas path (RECOMMENDED for heavy WRDS jobs)

The SAS script runs ENTIRELY on WRDS compute. No `signon`/`rsubmit`/`signoff` wrapping — the script is plain SAS code using the auto-assigned librefs (crsp, comp, taqmsec, wrdsapps, etc.).

**Windows workflow with PuTTY** (plink + pscp, password auth):

```bash
# Get the host fingerprint by running ssh-keyscan once (verify against WRDS docs)
HOSTKEY=SHA256:YOUR_VERIFIED_HOSTKEY_HERE
WRDS_USER=your_wrds_username
WRDS_HOME=/home/INSTITUTION/your_wrds_username   # e.g., /home/tulane/cli33

# Retrieve password from local autoexec.sas (or env)
PW=$(grep wrds_pass autoexec.sas | sed 's/.*= *//;s/;.*//;s/ //g;s/"//g;s/'\''//g')

# 1) Upload the .sas file
pscp -pw "$PW" -hostkey "$HOSTKEY" code/sas/myjob.sas ${WRDS_USER}@wrds-cloud.wharton.upenn.edu:${WRDS_HOME}/

# 2) Submit via qsas. Duo push required on first signon of the day.
plink -ssh -pw "$PW" -hostkey "$HOSTKEY" ${WRDS_USER}@wrds-cloud.wharton.upenn.edu "qsas myjob.sas"

# 3) Monitor. Job runs on SGE; qstat shows state qw (queued) / r (running) / empty (done).
plink -ssh -pw "$PW" -hostkey "$HOSTKEY" ${WRDS_USER}@wrds-cloud.wharton.upenn.edu "qstat -u $WRDS_USER"

# 4) After completion: download SAS log + output CSVs
pscp -pw "$PW" -hostkey "$HOSTKEY" ${WRDS_USER}@wrds-cloud.wharton.upenn.edu:${WRDS_HOME}/myjob.log output/logs/
pscp -pw "$PW" -hostkey "$HOSTKEY" ${WRDS_USER}@wrds-cloud.wharton.upenn.edu:${WRDS_HOME}/myjob_out/*.csv data/processed/
```

**Script pattern for SSH/qsas jobs** (no rsubmit; just plain SAS):

```sas
/* myjob.sas — runs directly on WRDS compute node via qsas */

%let outdir = ~/myjob_out;  /* NOTE: SAS may or may not expand ~; use $HOME or absolute path below */

/* Step 1: do work using auto-assigned librefs */
proc sql;
  create table work.result as
  select ... from crsp.dsf ... ;
quit;

/* Step 2: export. Use absolute path (~ may not expand in SAS). */
proc export data=work.result
  outfile="/home/INSTITUTION/your_wrds_username/myjob_out/result.csv"
  dbms=csv replace; putnames=yes;
run;
```

**qsas gotchas:**
- `qsas` wrapper runs `qsub -S /bin/bash -cwd -o /dev/null -e /dev/null -N <scriptname>` internally. Both stdout and stderr are discarded — you only see errors through SAS's log file (written alongside the .sas in cwd).
- If SAS crashes BEFORE writing a log (exit code != 0-7), use `qsub ... -o out.txt -e err.txt` directly instead of `qsas`, so stdout/stderr land in files.
- Login node (`wrds-cloud-login1-w`) blocks direct `sas` calls — "Please run qsas or qsub to submit a SAS job."
- WRDS home is `/home/INSTITUTION/your_username` (find your institution name with `pwd` after SSH). The `~` shortcut sometimes expands; sometimes doesn't — prefer absolute paths.
- TAQMSEC subscription years vary by institution — check what your school subscribes to before assuming year coverage.
- Mid-run diagnostic: `qacct -j <jobid>` gives `exit_status`, `ru_wallclock`, `start_time`, `end_time` after a job ends (stays in accounting for ~24h).
- Cancel a running job: `qdel <jobid>`.
- **`exit 112` + `ru_wallclock < 1s` + NO .log + empty stderr** = SAS **WORK-library permission / kernel init** failure on that compute node. The retry wrapper (see below) captures the actual SAS error to stdout. Real error pattern:
  ```
  ERROR: User does not have appropriate authorization level for library WORK.
  ERROR: Path: /sastemp/SAS_work<hash>_wrds-sasNN-w.wharton.private.
  ERROR: (SASXKINI): PHASE 3 KERNEL INITIALIZATION FAILED.
  ```
  **Root cause: node-specific `/sastemp/` permissions broken on that compute host.** A retry wrapper alone does NOT help because SGE re-runs all retries on the **same allocated node**. The fix is to **resubmit with host exclusion**:
  ```bash
  qsub ... -l h=!wrds-sasNN-w.wharton.private ...
  ```
  If you hit this on multiple nodes, chain exclusions: `-l 'h=!wrds-sas24-w.wharton.private&!wrds-sas30-w.wharton.private'`.

**Auto-retry wrapper for batch SAS jobs** (`code/sas/sas_retry_wrapper.sh` in this template):

```bash
# Submit with wrapper for automatic retry on exit-112 (SAS kernel init failures)
# The wrapper retries up to 3 times with 60s backoff if exit is NOT in {0,1,2}.
echo "source /gridware/sge/default/common/settings.sh; ~/sas_retry_wrapper.sh ~/myjob.sas" | \
  qsub -S /bin/bash -cwd -o ~/myjob_out.txt -e ~/myjob_err.txt -N myjob -l m_mem_free=10G
```

The wrapper handles SAS exit codes:
- `0, 1, 2`: pass-through (success, warnings, or SAS-level errors you want to inspect)
- `112`: retry up to 3x with 60s backoff (transient license/init race)
- Other: retry up to 3x (could be transient — could also be real; safe to retry once)

Source: `code/sas/sas_retry_wrapper.sh` in this repo. Upload to `~/sas_retry_wrapper.sh` on WRDS once, then reuse across jobs.

### 2.2 rsubmit from local PC-SAS (for SHORT queries only)

Use this only for `<=100` line rsubmit bodies. See Section 2.0 for the failure mode when used for heavy jobs.

#### Connection Setup

WRDS uses SAS/CONNECT with TCP protocol. The connection block:

```sas
%let wrds = wrds.wharton.upenn.edu 4016;
options comamid=TCP remote=WRDS;
signon username="&wrds_user" password="&wrds_pass";
```

### Credential Management (IMPORTANT)

**NEVER hardcode passwords in .sas files.** Use one of:

1. **SAS autoexec (recommended):** Put credentials in a local `autoexec.sas` that is gitignored:
   ```sas
   /* autoexec.sas — gitignored, machine-specific */
   %let wrds_user = your_username;
   %let wrds_pass = your_password;
   ```

2. **Environment variables:**
   ```sas
   %let wrds_user = %sysget(WRDS_USER);
   %let wrds_pass = %sysget(WRDS_PASS);
   ```

3. **Prompt (interactive only):**
   ```sas
   %let wrds_user = %sysfunc(getInput(WRDS Username:));
   ```

### Remote Submission Pattern

```sas
/* Execute code on WRDS server */
rsubmit;

  /* Set up remote libnames */
  libname comp '/wrds/comp/sasdata/nam';
  libname crsp '/wrds/crsp/sasdata/a_stock';
  libname ff '/wrds/ff/sasdata';
  libname ibes '/wrds/ibes/sasdata';
  libname risk '/wrds/risk/sasdata';

  /* Your query/analysis here */
  proc sql;
    create table work.mydata as
    select gvkey, datadate, at, sale
    from comp.funda
    where datadate between '01jan2020'd and '31dec2023'd
      and consol='C' and indfmt='INDL' and datafmt='STD';
  quit;

endrsubmit;
```

### Remote Libraries (Common WRDS Paths)

| Library | Path | Contents |
|---------|------|----------|
| `comp` | `/wrds/comp/sasdata/nam` | Compustat North America (funda, fundq, names) |
| `crsp` | `/wrds/crsp/sasdata/a_stock` | CRSP stock data (dsf, msf, dse, ccmxpf_linktable) |
| `ff` | `/wrds/ff/sasdata` | Fama-French factors (factors_daily, factors_monthly) |
| `ibes` | `/wrds/ibes/sasdata` | IBES analyst forecasts (detu_epsus, actu_epsus) |
| `risk` | `/wrds/risk/sasdata` | ISS governance/ESG (rmdirectors, board) |
| `tfn` | `/wrds/tfn/sasdata` | Thomson Reuters 13F institutional holdings |
| `audit` | `/wrds/audit/sasdata` | Audit Analytics |
| `optionm` | `/wrds/optionm/sasdata` | OptionMetrics |

### WRDS Macros (Common)

```sas
/* Include WRDS-provided macros on the remote server */
rsubmit;
  %include '/wrds/comp/samples/ccmlink.sas';      /* Compustat-CRSP link */
  %include '/wrds/ibes/samples/cibeslink.sas';     /* IBES-Compustat link */
  %include '/wrds/ibes/samples/iclink.sas';        /* IBES-CRSP link */
  %include '/wrds/comp/samples/sue.sas';           /* Standardized unexpected earnings */
  %include '/wrds/comp/samples/size_bm.sas';       /* Size-BM portfolio assignment */
endrsubmit;
```

### File Transfer

```sas
/* Upload local file to WRDS */
proc upload infile='C:/local/path/firms.csv'
            outfile='/home/institution/user/firms.csv';
run;

/* Download WRDS result to local (MUST be inside rsubmit block) */
proc download data=work.results out=work.results;
run;

endrsubmit;
```

**IMPORTANT:** Both `proc upload` and `proc download` must be inside an `rsubmit`/`endrsubmit` block. They will fail with "must be invoked with RSUBMIT" otherwise.

### Remote Work Directories

```sas
rsubmit;
  /* Scratch space (temporary, faster) */
  libname scratch '/scratch/institution';

  /* Home directory (persistent) */
  libname home '/home/institution/username';
endrsubmit;

/* Access remote libraries from local session */
libname rscratch remote '/scratch/institution' server=wrds;
libname rhome remote '/home/institution/username' server=wrds;
```

### Disconnect

```sas
signoff;
```

---

## 3. SAS Coding Conventions

### Script Header

```sas
/* ==============================================================================
 * [Step NN]: [Descriptive Title]
 *
 * Purpose: [What this script does]
 * Inputs:  [Data files/libraries read]
 * Outputs: [Datasets/files created]
 * Dependencies: [Upstream scripts, WRDS access needed?]
 * ============================================================================== */
```

### Libname Setup

```sas
/* Local data directories — use project-relative paths via macro */
%let projroot = [PROJECT ROOT PATH];
libname raw    "&projroot/data/raw";
libname proc   "&projroot/data/processed";
libname output "&projroot/output";
```

### PROC SQL Best Practices

```sas
proc sql;
  /* Always specify columns explicitly — never SELECT * in production */
  create table work.sample as
  select a.gvkey, a.datadate, a.at, a.sale, a.ni,
         b.lpermno as permno
  from comp.funda as a
    inner join crsp.ccmxpf_linktable as b
      on a.gvkey = b.gvkey
  where a.datadate between '01jan2020'd and '31dec2023'd
    and a.consol = 'C'
    and a.indfmt = 'INDL'
    and a.datafmt = 'STD'
    and b.linktype in ('LU', 'LC')
    and b.linkprim in ('P', 'C')
    and b.lpermno is not null
    and a.datadate >= b.linkdt
    and (a.datadate <= b.linkenddt or b.linkenddt is null)
  order by a.gvkey, a.datadate;
quit;
```

### Missing Value Handling

```sas
/* SAS missing values: . (numeric), '' (character) */
/* IMPORTANT: In SAS, missing < any number. This affects WHERE clauses. */

/* Safe comparison — exclude missing explicitly */
where not missing(at) and at > 0;

/* Replace missing with default */
if missing(rd) then rd = 0;

/* Count missing */
proc means data=work.sample nmiss;
  var at sale ni;
run;
```

### Date Handling

```sas
/* SAS date literals use 'ddMONyyyy'd format */
where datadate between '01jan2020'd and '31dec2023'd;

/* Format dates for display */
format datadate date9.;
format datadate yymmdd10.;

/* Trading day adjustment (skip weekends) */
if weekday(evtdate) = 1 then evtdate = intnx('day', evtdate, 1);  /* Sunday -> Monday */
if weekday(evtdate) = 7 then evtdate = intnx('day', evtdate, 2);  /* Saturday -> Monday */
```

### Output

```sas
/* Export to CSV */
proc export data=work.results
  outfile="&projroot/output/results/filename.csv"
  dbms=csv replace;
  putnames=yes;
run;

/* Export to Excel */
proc export data=work.results
  outfile="&projroot/output/tables/filename.xlsx"
  dbms=xlsx replace;
run;

/* Export to Stata */
proc export data=work.results
  outfile="&projroot/data/processed/filename.dta"
  dbms=stata replace;
run;

/* Save as SAS dataset */
data proc.filename;
  set work.results;
run;
```

---

## 4. Common Empirical Finance Patterns

### Compustat-CRSP Link

```sas
/* Standard CCM linking with date overlap */
proc sql;
  create table work.linked as
  select a.*, b.lpermno as permno
  from comp.funda as a
    inner join crsp.ccmxpf_linktable as b
      on a.gvkey = b.gvkey
  where b.linktype in ('LU', 'LC')
    and b.linkprim in ('P', 'C')
    and not missing(b.lpermno)
    and a.datadate >= b.linkdt
    and (a.datadate <= b.linkenddt or missing(b.linkenddt));
quit;
```

### Event Study Setup

```sas
/* Parameters */
%let estper = 150;     /* Estimation period (trading days) */
%let gap = 15;         /* Gap between estimation and event */
%let start = -2;       /* Event window start */
%let end = 2;          /* Event window end */
%let minest = 120;     /* Minimum estimation observations */
%let evtwin = %sysevalf(&end - &start + 1);

/* Factor model estimation */
proc reg data=work.est_period noprint outest=work.params edf;
  by permno evtdate;
  model exret = mktrf smb hml umd;
quit;

/* Abnormal returns */
data work.abnormal;
  merge work.event_window work.params;
  by permno evtdate;
  abret = exret - (intercept + mktrf*mktrf_coeff + smb*smb_coeff
                   + hml*hml_coeff + umd*umd_coeff);
run;

/* Cumulative abnormal returns */
proc expand data=work.abnormal out=work.cars method=none;
  by permno evtdate;
  convert abret = car / transformout=(sum);
run;
```

### Control Variables (Compustat)

```sas
/* Standard controls */
SIZE = log(prcc_c * csho);           /* Market cap */
BTM = ceq / (prcc_c * csho);        /* Book-to-market */
ROA = ibcom / at;                    /* Return on assets */
LEV = (dltt + dlc) / at;            /* Leverage */
RD = coalesce(xrd/sale, 0);         /* R&D intensity */
```

---

## 5. Debugging SAS

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ERROR: Libname not assigned` | Path doesn't exist or no permissions | Check directory exists, check permissions |
| `ERROR: File not found` | Wrong dataset name or libname | Verify with `proc datasets lib=...` |
| `ERROR: Variable not found` | Wrong variable name, case sensitivity in SQL | Check `proc contents` |
| `ERROR: BY variables are not sorted` | Data not sorted before merge/BY | Add `proc sort` before |
| `WARNING: Multiple lengths specified` | Inconsistent lengths in SET/MERGE | Use LENGTH statement before SET |
| `NOTE: MERGE with repeats` | Many-to-many merge | Check merge keys are unique |
| `WARNING: PROC DOWNLOAD must be invoked with the RSUBMIT command` | `proc download`/`proc upload` placed outside `rsubmit` block | Move inside `rsubmit`/`endrsubmit` |
| `ERROR: File WORK.xxx.DATA does not exist` after download | Download failed — data never reached local session | Verify `proc download` is inside `rsubmit` block |
| `ERROR: Connect: ... timed out` | WRDS connection issue | Check VPN, retry `signon` |

### WRDS Connection Troubleshooting

1. **Timeout:** Check VPN is connected. WRDS requires institutional network or VPN.
2. **Duo authentication:** WRDS requires Duo 2FA push on the first connection each day. Remind user to approve on phone. Subsequent connections the same day skip Duo.
3. **Auth failure:** Verify credentials. WRDS password may have expired.
4. **Library not found:** WRDS paths change. Check current paths at wrds-www.wharton.upenn.edu.
5. **Quota exceeded:** Clear files from `/scratch/` or `/home/` on WRDS.
6. **Session dropped:** Use `signon` to reconnect. Check `%sysfunc(attrn(WRDS, id))`.

### Useful Diagnostics

```sas
/* Check what's in a library */
proc datasets lib=comp; quit;

/* Check variable names/types */
proc contents data=comp.funda; run;

/* Quick data peek */
proc print data=work.mydata(obs=10); run;

/* Frequency table */
proc freq data=work.mydata; tables year / nocum; run;

/* Summary statistics */
proc means data=work.mydata n mean std min p25 median p75 max;
  var at sale ni;
run;
```

---

## 6. Steps for Running a SAS Script

1. **Pre-flight:**
   - Confirm SAS is available: check `SAS_PATH` in `run_all.sh`
   - If WRDS needed: confirm VPN is connected
   - Read script header for inputs/outputs

2. **Execute:**
   ```bash
   ./run_all.sh "script_name.sas"
   ```

3. **Read the log (MANDATORY):**
   - Find log in `output/logs/`
   - Search for `ERROR:` lines — any means failure
   - Check `WARNING:` lines — evaluate if benign
   - Verify `NOTE: The data set ... has N observations` matches expectations

4. **Verify outputs:**
   - Check output files exist with non-zero size
   - If SAS dataset: verify with `proc contents` or export to CSV for inspection
   - If CSV/Excel: spot-check key values

5. **Report:**
   - Execution result (PASS/FAIL)
   - Observation counts
   - Any warnings
   - Output files created
