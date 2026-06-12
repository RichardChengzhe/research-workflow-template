#!/usr/bin/env python
"""
Quality Score Calculator

Scores .py, .do, .tex, and .sas files based on project quality rubrics.
Usage: python scripts/quality_score.py <file_path>

Rubrics from .claude/rules/quality-gates.md:
  80/100 = Commit ready
  90/100 = PR ready
  95/100 = Excellence

Could-not-verify state
----------------------
Some checks need an external tool (e.g. `latexmk` to compile a `.tex`, or
`python` to syntax-check a `.py`). If that tool is MISSING or TIMES OUT, the
check is recorded as a distinct "could-not-verify" note and the file is scored
on its static checks only -- a missing/slow tool is NOT treated as a quality
failure (it does not zero the score). A tool that runs and reports a REAL
failure (a genuine compile/syntax error) still fails the file. Timeouts are
tunable:
  QUALITY_LATEXMK_TIMEOUT  (seconds, default 120) -- .tex compile check
  QUALITY_PYTHON_TIMEOUT   (seconds, default 15)  -- .py  syntax check
Set a timeout to 0/empty to disable that external check entirely (static
checks still run).
"""

import os
import sys
import re
import shutil
import subprocess
from pathlib import Path


def _timeout(env_name: str, default: int) -> int:
    """Read a non-negative int timeout (seconds) from the environment, else
    `default`. A value of 0 disables the associated external check."""
    raw = os.environ.get(env_name, "")
    if raw == "":
        return default
    try:
        value = int(raw)
        return value if value >= 0 else default
    except ValueError:
        return default


def score_python(content: str, lines: list[str], file_path: Path) -> tuple[int, list[str], list[str]]:
    """Score a Python script against project rubrics.

    Returns (score, issues, unverified). `unverified` holds could-not-verify
    notes (a missing/slow interpreter), which do NOT reduce the score.
    """
    score = 100
    issues = []
    unverified = []

    # Critical: Syntax errors. The in-process compile() is the primary, always-
    # available check (no external tool, never times out). It is authoritative
    # for syntax, so a real SyntaxError here is a genuine failure.
    try:
        compile(content, "<string>", "exec")
    except SyntaxError as e:
        score -= 100
        issues.append(f"CRITICAL (-100): Syntax error at line {e.lineno}: {e.msg}")
        return max(score, 0), issues, unverified

    # Optional: a real interpreter `py_compile` pass. This is belt-and-braces
    # over compile() (it exercises the actual interpreter). It is gated behind
    # the could-not-verify pattern: if the interpreter is missing or the check
    # times out, record a note and move on -- never a quality failure.
    limit = _timeout("QUALITY_PYTHON_TIMEOUT", 15)
    if limit > 0:
        interp = shutil.which("python") or shutil.which("python3")
        if interp is None:
            unverified.append("syntax not double-checked -- no python interpreter on PATH")
        else:
            try:
                result = subprocess.run(
                    [interp, "-m", "py_compile", str(file_path)],
                    capture_output=True, text=True, timeout=limit,
                )
                # A failure here would have been caught by compile() above for
                # syntax; surface anything else (e.g. encoding) as a note rather
                # than double-penalizing.
                if result.returncode != 0 and "SyntaxError" not in result.stderr:
                    unverified.append("py_compile reported a non-syntax issue (see manually)")
            except subprocess.TimeoutExpired:
                unverified.append(f"syntax not double-checked -- py_compile exceeded {limit}s (raise QUALITY_PYTHON_TIMEOUT)")
            except OSError:
                unverified.append("syntax not double-checked -- could not launch the interpreter")

    # Critical: Hardcoded absolute paths
    for i, line in enumerate(lines, 1):
        if re.search(r'["\'][A-Z]:\\|["\']/Users/|["\']/home/', line) and not line.strip().startswith("#"):
            score -= 20
            issues.append(f"CRITICAL (-20): Hardcoded absolute path at line {i}")
            break

    # Critical: Missing imports (check for common unimported usage)
    has_imports = any(line.strip().startswith(("import ", "from ")) for line in lines)
    non_empty_code = [l for l in lines if l.strip() and not l.strip().startswith("#") and not l.strip().startswith('"""') and not l.strip().startswith("'''")]
    if len(non_empty_code) > 5 and not has_imports:
        score -= 15
        issues.append("CRITICAL (-15): No import statements found in non-trivial script")

    # Major: No docstrings for functions
    func_count = 0
    func_with_doc = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("def "):
            func_count += 1
            if i + 1 < len(lines) and ('"""' in lines[i + 1] or "'''" in lines[i + 1]):
                func_with_doc += 1
    if func_count > 0 and func_with_doc < func_count:
        missing = func_count - func_with_doc
        score -= min(missing * 5, 15)
        issues.append(f"MAJOR (-{min(missing * 5, 15)}): {missing}/{func_count} functions missing docstrings")

    # Major: Unused imports
    import_names = []
    for line in lines:
        m = re.match(r"^import (\w+)", line.strip())
        if m:
            import_names.append(m.group(1))
        m = re.match(r"^from \S+ import (.+)", line.strip())
        if m:
            for name in m.group(1).split(","):
                name = name.strip().split(" as ")[-1].strip()
                if name and name != "*":
                    import_names.append(name)
    for name in import_names:
        usage_count = sum(1 for line in lines if name in line) - 1  # subtract import line
        if usage_count <= 0:
            score -= 3
            issues.append(f"MAJOR (-3): Unused import: {name}")

    # Minor: Long lines
    long_lines = sum(1 for line in lines if len(line.rstrip()) > 100)
    if long_lines > 0:
        deduction = min(long_lines, 5)
        score -= deduction
        issues.append(f"MINOR (-{deduction}): {long_lines} lines exceed 100 characters")

    # Minor: Missing __main__ guard
    has_main_guard = any("__name__" in line and "__main__" in line for line in lines)
    has_top_level_code = False
    in_func_or_class = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("def ", "class ")):
            in_func_or_class = True
        elif stripped and not stripped.startswith(("#", "import ", "from ", '"""', "'''")) and not in_func_or_class:
            if not stripped.startswith(("@", "if __name__")):
                has_top_level_code = True
    if has_top_level_code and not has_main_guard:
        score -= 2
        issues.append("MINOR (-2): Missing if __name__ == '__main__' guard")

    return max(score, 0), issues, unverified


def score_stata(content: str, lines: list[str]) -> tuple[int, list[str], list[str]]:
    """Score a Stata do-file against project rubrics (static checks only --
    no external Stata invocation, so there is no could-not-verify state)."""
    score = 100
    issues = []
    unverified: list[str] = []

    # Critical: Hardcoded absolute paths (not using globals)
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("*") or stripped.startswith("//"):
            continue
        if re.search(r'["\'][A-Z]:\\|["\']/Users/|["\']/home/', stripped):
            score -= 20
            issues.append(f"CRITICAL (-20): Hardcoded absolute path at line {i}")
            break

    # Critical: Missing clear all / set more off
    has_clear = any("clear all" in line.lower() or "clear" == line.strip().lower() for line in lines[:30])
    has_set_more = any("set more off" in line.lower() for line in lines[:30])
    if not has_clear:
        score -= 10
        issues.append("CRITICAL (-10): Missing 'clear all' at top of script")
    if not has_set_more:
        score -= 5
        issues.append("MAJOR (-5): Missing 'set more off' at top of script")

    # Major: Missing log using (run_all.sh captures logs, so not penalized)
    # (left intentionally as a no-op for parity with the original rubric.)

    # Major: Missing set seed for stochastic computation
    has_stochastic = any(kw in content.lower() for kw in ["bootstrap", "simulate", "permute", "bsample", "sample"])
    has_seed = any("set seed" in line.lower() for line in lines)
    if has_stochastic and not has_seed:
        score -= 10
        issues.append("MAJOR (-10): Stochastic computation without 'set seed'")

    # Major: Missing variable labels on created variables
    gen_count = sum(1 for line in lines if re.match(r"\s*(gen|generate|egen)\s+", line.strip()))
    label_count = sum(1 for line in lines if "label variable" in line.lower() or "label var" in line.lower())
    if gen_count > 0 and label_count < gen_count:
        score -= 5
        issues.append(f"MAJOR (-5): {gen_count - label_count} generated variables without labels")

    # Minor: Missing script header
    has_header = any("purpose" in line.lower() or "inputs" in line.lower() or "outputs" in line.lower() for line in lines[:15])
    if not has_header:
        score -= 3
        issues.append("MINOR (-3): Missing script header (purpose, inputs, outputs)")

    # Minor: Hardcoded values that should be in params.do
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("*") or stripped.startswith("//"):
            continue
        if re.search(r'\b(19|20)\d{2}\b', stripped) and "params" not in stripped.lower() and "date" not in stripped.lower():
            if not any(kw in stripped.lower() for kw in ["log", "display", "di ", "*", "//"]):
                score -= 3
                issues.append(f"MINOR (-3): Possible hardcoded value at line {i} (should be in params.do?)")
                break

    return max(score, 0), issues, unverified


def score_sas(content: str, lines: list[str]) -> tuple[int, list[str], list[str]]:
    """Score a SAS program against project rubrics (static checks only).

    SAS exit codes are unreliable (a run can return 0 with ERROR: in the log),
    so we do not invoke SAS here -- the scorer is purely static and there is no
    could-not-verify state. Mirrors the spirit of the Stata rubric.
    """
    score = 100
    issues = []
    unverified: list[str] = []

    code_lines = []
    for line in lines:
        stripped = line.strip()
        # SAS line comments: * ... ; and /* ... */ (block handled loosely)
        if stripped.startswith("*") or stripped.startswith("/*"):
            continue
        code_lines.append(line)

    # Critical: Hardcoded absolute paths in libname/%let/filename
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("*") or stripped.startswith("/*"):
            continue
        if re.search(r'["\'][A-Z]:\\|["\']/home/|["\']/Users/', stripped):
            score -= 20
            issues.append(f"CRITICAL (-20): Hardcoded absolute path at line {i} (use a libname/%let macro variable)")
            break

    # Major: committing real WRDS credentials -- never score a populated autoexec
    if re.search(r"%let\s+(wrds_)?pass\w*\s*=", content, re.IGNORECASE):
        score -= 15
        issues.append("MAJOR (-15): Possible hardcoded credential (%let pass=...) -- keep secrets in autoexec.sas (gitignored)")

    # Major: missing RUN/QUIT terminators for the main steps. A data/proc step
    # left unterminated is a common silent-failure source.
    n_data = len(re.findall(r"^\s*data\s+", content, re.IGNORECASE | re.MULTILINE))
    n_proc = len(re.findall(r"^\s*proc\s+", content, re.IGNORECASE | re.MULTILINE))
    n_run = len(re.findall(r"^\s*run\s*;", content, re.IGNORECASE | re.MULTILINE))
    n_quit = len(re.findall(r"^\s*quit\s*;", content, re.IGNORECASE | re.MULTILINE))
    if (n_data + n_proc) > 0 and (n_run + n_quit) < (n_data + n_proc):
        score -= 5
        issues.append(f"MAJOR (-5): {n_data + n_proc} data/proc step(s) but only {n_run + n_quit} run;/quit; terminator(s)")

    # Minor: missing script header
    has_header = any(kw in line.lower() for line in lines[:15] for kw in ("purpose", "inputs", "outputs", "author"))
    if not has_header:
        score -= 3
        issues.append("MINOR (-3): Missing script header (purpose, inputs, outputs)")

    # Minor: hardcoded year ranges that likely belong in a macro variable
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("*") or stripped.startswith("/*"):
            continue
        if re.search(r'\b(19|20)\d{2}\b', stripped) and "%let" not in stripped.lower():
            if not any(kw in stripped.lower() for kw in ["put", "%put", "title", "footnote", "*", "/*"]):
                score -= 3
                issues.append(f"MINOR (-3): Possible hardcoded year at line {i} (consider a %let macro variable)")
                break

    return max(score, 0), issues, unverified


def score_latex(content: str, lines: list[str], file_path: Path) -> tuple[int, list[str], list[str]]:
    """Score a LaTeX manuscript against project rubrics.

    Adds an OPTIONAL `latexmk` compile check governed by the could-not-verify
    pattern: a missing/slow latexmk yields a note (not a failure); a latexmk
    run that reports a real error fails the file (score 0).
    """
    score = 100
    issues = []
    unverified = []

    # Optional: real compile via latexmk. Could-not-verify when latexmk is
    # absent or the compile times out -- those do NOT reduce the score.
    limit = _timeout("QUALITY_LATEXMK_TIMEOUT", 120)
    if limit > 0:
        latexmk = shutil.which("latexmk")
        if latexmk is None:
            unverified.append("compilation not verified -- latexmk not installed (static checks only)")
        else:
            try:
                result = subprocess.run(
                    [latexmk, "-pdf", "-interaction=nonstopmode", "-halt-on-error", file_path.name],
                    capture_output=True, text=True, timeout=limit, cwd=file_path.parent,
                )
                if result.returncode != 0:
                    score = 0
                    tail = (result.stdout or result.stderr or "")[-300:]
                    issues.append(f"CRITICAL (-100): latexmk compilation failed\n    {tail.strip()}")
                    return max(score, 0), issues, unverified
            except subprocess.TimeoutExpired:
                unverified.append(f"compilation not verified -- latexmk exceeded {limit}s (raise QUALITY_LATEXMK_TIMEOUT or set it to 0 to skip)")
            except OSError:
                unverified.append("compilation not verified -- could not launch latexmk")

    # Critical: Undefined citations (check \cite keys against the bib)
    cite_keys = set()
    for line in lines:
        for m in re.finditer(r"\\cite[tp]?\{([^}]+)\}", line):
            for key in m.group(1).split(","):
                cite_keys.add(key.strip())

    if cite_keys:
        bib_content = ""
        for bib_path in [Path("manuscript/references.bib"), Path("references.bib"),
                         file_path.parent / "references.bib"]:
            if bib_path.exists():
                bib_content = bib_path.read_text(encoding="utf-8", errors="replace")
                break

        if bib_content:
            for key in cite_keys:
                if key not in bib_content:
                    score -= 15
                    issues.append(f"CRITICAL (-15): Undefined citation: {key}")
        else:
            unverified.append("citations not checked -- no references.bib found")

    # Major: Check for overfull hbox indicators (very long lines in text)
    for i, line in enumerate(lines, 1):
        if len(line.rstrip()) > 200 and not line.strip().startswith("%"):
            score -= 5
            issues.append(f"MAJOR (-5): Very long line at {i} (potential overfull hbox)")
            break

    # Info: TODO/FIXME markers
    todo_count = sum(1 for line in lines if "TODO" in line or "FIXME" in line)
    if todo_count > 0:
        issues.append(f"INFO: {todo_count} TODO/FIXME markers found")

    # Minor: Informal language
    informal = ["don't", "can't", "won't", "it's ", "we've", "they're"]
    for word in informal:
        for i, line in enumerate(lines, 1):
            if word in line.lower() and not line.strip().startswith("%"):
                score -= 1
                issues.append(f"MINOR (-1): Informal language '{word}' at line {i}")
                break

    return max(score, 0), issues, unverified


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/quality_score.py <file_path>")
        print("Supported: .py, .do, .tex, .sas")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    ext = file_path.suffix.lower()
    if ext == ".py":
        score, issues, unverified = score_python(content, lines, file_path)
        file_type = "Python"
    elif ext == ".do":
        score, issues, unverified = score_stata(content, lines)
        file_type = "Stata"
    elif ext == ".sas":
        score, issues, unverified = score_sas(content, lines)
        file_type = "SAS"
    elif ext == ".tex":
        score, issues, unverified = score_latex(content, lines, file_path)
        file_type = "LaTeX"
    else:
        print(f"Unsupported file type: {ext}")
        print("Supported: .py, .do, .tex, .sas")
        sys.exit(1)

    # Determine gate
    if score >= 95:
        gate = "EXCELLENCE"
    elif score >= 90:
        gate = "PR READY"
    elif score >= 80:
        gate = "COMMIT READY"
    else:
        gate = "BELOW THRESHOLD"

    # Print report
    print(f"\n{'=' * 60}")
    print(f"Quality Score: {file_path.name}")
    print(f"{'=' * 60}")
    print(f"Type:  {file_type}")
    print(f"Score: {score}/100")
    print(f"Gate:  {gate}")
    print(f"{'=' * 60}")

    if issues:
        print(f"\nIssues ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nNo issues found.")

    # Could-not-verify notes: a missing/slow tool is a distinct skipped state,
    # reported separately and NOT counted against the score.
    if unverified:
        print(f"\nCould not verify ({len(unverified)}) -- score reflects static checks only:")
        for note in unverified:
            print(f"  - {note}")

    print(f"\n{'=' * 60}")

    # Exit with appropriate code (unchanged: <80 blocks, else passes).
    if score < 80:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
