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

### Connection Setup

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
%let evtwin = %eval(&end - &start + 1);

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
| `ERROR: Connect: ... timed out` | WRDS connection issue | Check VPN, retry `signon` |

### WRDS Connection Troubleshooting

1. **Timeout:** Check VPN is connected. WRDS requires institutional network or VPN.
2. **Auth failure:** Verify credentials. WRDS password may have expired.
3. **Library not found:** WRDS paths change. Check current paths at wrds-www.wharton.upenn.edu.
4. **Quota exceeded:** Clear files from `/scratch/` or `/home/` on WRDS.
5. **Session dropped:** Use `signon` to reconnect. Check `%sysfunc(attrn(WRDS, id))`.

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
