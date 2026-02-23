#!/usr/bin/env python
"""
Quality Score Calculator

Scores .py, .do, and .tex files based on project quality rubrics.
Usage: python scripts/quality_score.py <file_path>

Rubrics from .claude/rules/quality-gates.md:
  80/100 = Commit ready
  90/100 = PR ready
  95/100 = Excellence
"""

import sys
import re
from pathlib import Path


def score_python(content: str, lines: list[str]) -> tuple[int, list[str]]:
    """Score a Python script against project rubrics."""
    score = 100
    issues = []

    # Critical: Syntax errors (can't fully check without running, but check imports)
    try:
        compile(content, "<string>", "exec")
    except SyntaxError as e:
        score -= 100
        issues.append(f"CRITICAL (-100): Syntax error at line {e.lineno}: {e.msg}")
        return max(score, 0), issues

    # Critical: Hardcoded absolute paths
    for i, line in enumerate(lines, 1):
        if re.search(r'["\'][A-Z]:\\|["\']/Users/|["\']/home/', line) and not line.strip().startswith("#"):
            score -= 20
            issues.append(f"CRITICAL (-20): Hardcoded absolute path at line {i}")
            break

    # Critical: Missing imports (check for common unimported usage)
    # Simplified: just check if file has any imports
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

    return max(score, 0), issues


def score_stata(content: str, lines: list[str]) -> tuple[int, list[str]]:
    """Score a Stata do-file against project rubrics."""
    score = 100
    issues = []

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

    # Major: Missing log using (check if run via run_all.sh handles this)
    has_log = any("log using" in line.lower() for line in lines)
    # Not penalizing if run_all.sh captures logs

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
        # Check for hardcoded year ranges, dates, etc.
        if re.search(r'\b(19|20)\d{2}\b', stripped) and "params" not in stripped.lower() and "date" not in stripped.lower():
            if not any(kw in stripped.lower() for kw in ["log", "display", "di ", "*", "//"]):
                score -= 3
                issues.append(f"MINOR (-3): Possible hardcoded value at line {i} (should be in params.do?)")
                break

    return max(score, 0), issues


def score_latex(content: str, lines: list[str]) -> tuple[int, list[str]]:
    """Score a LaTeX manuscript against project rubrics."""
    score = 100
    issues = []

    # Critical: Check for common LaTeX errors
    # (Can't fully compile-check, but check for common issues)

    # Critical: Undefined citations (check for \cite without matching bib entry)
    cite_keys = set()
    for line in lines:
        for m in re.finditer(r"\\cite[tp]?\{([^}]+)\}", line):
            for key in m.group(1).split(","):
                cite_keys.add(key.strip())

    # Check if bibliography file exists and has entries
    # (simplified: just count citations)
    if cite_keys:
        # Look for bib file
        bib_content = ""
        for bib_path in [Path("manuscript/references.bib"), Path("references.bib")]:
            if bib_path.exists():
                bib_content = bib_path.read_text()
                break

        if bib_content:
            for key in cite_keys:
                if key not in bib_content:
                    score -= 15
                    issues.append(f"CRITICAL (-15): Undefined citation: {key}")

    # Major: Check for overfull hbox indicators (very long lines in text)
    for i, line in enumerate(lines, 1):
        if len(line.rstrip()) > 200 and not line.strip().startswith("%"):
            score -= 5
            issues.append(f"MAJOR (-5): Very long line at {i} (potential overfull hbox)")
            break

    # Major: Claims without citations (paragraphs with factual claims but no \cite)
    # Simplified: check for TODO markers
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

    return max(score, 0), issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/quality_score.py <file_path>")
        print("Supported: .py, .do, .tex")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    ext = file_path.suffix.lower()
    if ext == ".py":
        score, issues = score_python(content, lines)
        file_type = "Python"
    elif ext == ".do":
        score, issues = score_stata(content, lines)
        file_type = "Stata"
    elif ext == ".tex":
        score, issues = score_latex(content, lines)
        file_type = "LaTeX"
    else:
        print(f"Unsupported file type: {ext}")
        print("Supported: .py, .do, .tex")
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

    print(f"\n{'=' * 60}")

    # Exit with appropriate code
    if score < 80:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
