#!/usr/bin/env python3
"""
Check cross-document count consistency for the template's public surfaces.

Prevents the drift pattern where adding a skill (agent, rule, hook) updates
`.claude/` but leaves stale counts or stale enumerative tables in CLAUDE.md,
README.md, or the quick-reference card.

Two kinds of check:
  1. COUNT assertions -- prose like "16 agents, 56 skills, 33 rules" must match
     the on-disk inventory.
  2. TABLE-ROW assertions -- an enumerative markdown table preceded by a
     `<!-- surface-sync-table: <kind> -->` marker must have exactly one data
     row per item of <kind> on disk. This catches drift the count check
     misses: a new skill added to `.claude/` but left OUT of the README /
     CLAUDE.md skills table (the count is right; the table row is stale).

Run via `./scripts/check-surface-sync.sh` (invoked by `.githooks/pre-commit`),
or directly: `python scripts/check-surface-sync.py`.

NOTE: this tool DYNAMICALLY counts what is on disk and compares it to the
surfaces. Until the surface counts/tables are reconciled to match disk, it
will legitimately report DRIFT and exit 1 -- that is the intended signal, not
a bug in the tool.

Exit codes:
    0 -- all counts consistent
    1 -- drift detected (prints a diff)
    2 -- internal error (unreadable directory / scan crash)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Ground truth: count entries on disk.
GROUND_TRUTH = {
    "skills":       len(list((REPO / ".claude/skills").glob("*/SKILL.md"))),
    "agents":       len(list((REPO / ".claude/agents").glob("*.md"))),
    "rules":        len(list((REPO / ".claude/rules").glob("*.md"))),
    "hooks":        (
        len(list((REPO / ".claude/hooks").glob("*.py"))) +
        len(list((REPO / ".claude/hooks").glob("*.sh")))
    ),
}

# Surfaces to scan. These are THIS template's count/index surfaces (the
# Stata/Python/SAS workflow has no Quarto guide or rendered HTML landing
# page, so those are intentionally absent vs. an R/Quarto template). A
# surface that does not yet exist is warn-skipped, not a hard error, so the
# check runs cleanly before the reconcile step adds counts.
SURFACES = [
    REPO / "README.md",
    REPO / "CLAUDE.md",
    REPO / ".claude/WORKFLOW_QUICK_REF.md",
    REPO / "templates/skill-template.md",
]

# Phrasings that assert THIS TEMPLATE's counts. We deliberately require
# compound patterns (multiple counts in the same line) or a highly specific
# scaffold so we don't false-positive on unrelated usages like "3 parallel
# agents" or "start with 2-3 skills".
#
# Each entry is (regex, ordered list of (group_index, kind)). Group index is
# 1-based. The regex MUST match the compound assertion, not just one count.
COMPOUND_PHRASINGS: list[tuple[str, list[tuple[int, str]]]] = [
    # "16 agents, 56 skills, 33 rules, 9 hooks"
    (
        r"(\d+)\s+agents?,\s+(\d+)\s+skills?,\s+(\d+)\s+rules?,\s+(\d+)\s+hooks?",
        [(1, "agents"), (2, "skills"), (3, "rules"), (4, "hooks")],
    ),
    # "16 agents, 56 skills, and 33 rules"
    (
        r"(\d+)\s+agents?,\s+(\d+)\s+skills?,?\s+and\s+(\d+)\s+rules?",
        [(1, "agents"), (2, "skills"), (3, "rules")],
    ),
    # "16 agents, 56 skills, 33 rules" (no 'and', no 'hooks')
    (
        r"(\d+)\s+agents?,\s+(\d+)\s+skills?,\s+(\d+)\s+rules?(?!\s*,)",
        [(1, "agents"), (2, "skills"), (3, "rules")],
    ),
    # "56 skills, 16 agents, 33 rules" (skills-first ordering)
    (
        r"(\d+)\s+skills?,\s+(\d+)\s+(?:specialized\s+)?agents?,\s+(\d+)\s+rules?",
        [(1, "skills"), (2, "agents"), (3, "rules")],
    ),
    # "56 slash commands + 33 context-aware rules"
    (
        r"(\d+)\s+slash\s+commands?\s*\+\s*(\d+)\s+context-aware\s+rules?",
        [(1, "skills"), (2, "rules")],
    ),
]

# Singular phrasings. These ONLY fire when the match is clearly about this
# template. Each must be a scaffold specific enough that false positives are
# unlikely.
SINGULAR_PHRASINGS: list[tuple[str, str]] = [
    # "this template's 56" (prose shortcut). Match BOTH the ASCII apostrophe
    # and the typographic right single quote (U+2019).
    (r"this template['’]s\s+(\d+)\b",          "skills"),
    # "(N skills for LaTeX..." (templates/skill-template.md trailing note)
    (r"\((\d+)\s+skills?\s+for\b",                  "skills"),
]

# Enumerative-table markers. A surface opts a markdown table into the
# row-count gate by placing this comment immediately before it:
#
#     <!-- surface-sync-table: skills -->
#     | Skill | What It Does |
#     |-------|--------------|
#     | `/compile-latex` | ... |   <- one data row per skill on disk
#
# <kind> must be a key of GROUND_TRUTH. The data-row count (header and the
# `|---|` separator excluded) must equal the on-disk count for that kind.
TABLE_MARKER_RE = re.compile(r"<!--\s*surface-sync-table:\s*([a-z]+)\s*-->")


def _is_table_row(line: str) -> bool:
    return line.lstrip().startswith("|")


def scan_file(path: Path) -> list[tuple[int, str, int, str]]:
    """
    Return [(line_number, kind, asserted_count, raw_match)] for every
    assertion found. `kind` is one of GROUND_TRUTH.keys().
    """
    if not path.exists():
        return []
    hits: list[tuple[int, str, int, str]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        for pattern, group_kinds in COMPOUND_PHRASINGS:
            for m in re.finditer(pattern, line):
                for group_idx, kind in group_kinds:
                    try:
                        n = int(m.group(group_idx))
                    except (ValueError, IndexError):
                        continue
                    hits.append((lineno, kind, n, m.group(0)))
        for pattern, kind in SINGULAR_PHRASINGS:
            for m in re.finditer(pattern, line):
                try:
                    n = int(m.group(1))
                except (ValueError, IndexError):
                    continue
                hits.append((lineno, kind, n, m.group(0)))
    return hits


def scan_tables(path: Path) -> list[tuple[int, str, "int | None", str]]:
    """
    Find every `<!-- surface-sync-table: <kind> -->` marker and count the
    data rows of the markdown table that immediately follows it.

    Returns [(marker_line_number, kind, data_row_count, marker_raw)].
    `data_row_count` is None when no well-formed table follows the marker.
    """
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    n = len(lines)
    hits: list[tuple[int, str, "int | None", str]] = []
    i = 0
    while i < n:
        m = TABLE_MARKER_RE.search(lines[i])
        if not m:
            i += 1
            continue
        kind = m.group(1)
        marker_lineno = i + 1
        marker_raw = lines[i].strip()

        # Advance to the header row: the first pipe-line after the marker,
        # skipping intervening blanks/prose (a heading often sits between).
        j = i + 1
        while j < n and not _is_table_row(lines[j]) and not TABLE_MARKER_RE.search(lines[j]):
            j += 1

        if (
            j >= n
            or not _is_table_row(lines[j])
            or j + 1 >= n
            or "---" not in lines[j + 1]
        ):
            hits.append((marker_lineno, kind, None, marker_raw))
            i = j + 1
            continue

        k = j + 2  # first data row
        count = 0
        while k < n and _is_table_row(lines[k]):
            count += 1
            k += 1
        hits.append((marker_lineno, kind, count, marker_raw))
        i = k
    return hits


def main() -> int:
    rel = lambda p: p.relative_to(REPO)
    drift: list[str] = []

    # A surface that doesn't exist yet is warn-skipped (not fatal): the
    # reconcile step may add it later. Only scan the surfaces present.
    present = [p for p in SURFACES if p.exists()]
    for p in SURFACES:
        if not p.exists():
            print(f"  (skip) surface not present: {rel(p)}", file=sys.stderr)

    print("Ground truth (counted from disk):")
    for k, v in GROUND_TRUTH.items():
        print(f"  {k:<8} {v}")
    print()

    per_file: dict[Path, list[tuple[int, str, int, str]]] = {}
    for path in present:
        per_file[path] = scan_file(path)

    for path, hits in per_file.items():
        for lineno, kind, asserted, raw in hits:
            expected = GROUND_TRUTH[kind]
            if asserted != expected:
                drift.append(
                    f"  {rel(path)}:{lineno}  "
                    f"asserts {asserted} {kind} "
                    f"(actual: {expected})  "
                    f"[matched: {raw!r}]"
                )

    # Enumerative-table row-count assertions (marker-driven).
    table_hits = 0
    for path in present:
        for lineno, kind, count, raw in scan_tables(path):
            table_hits += 1
            if kind not in GROUND_TRUTH:
                drift.append(
                    f"  {rel(path)}:{lineno}  unknown table kind {kind!r} "
                    f"(expected one of {', '.join(sorted(GROUND_TRUTH))})  "
                    f"[marker: {raw!r}]"
                )
                continue
            if count is None:
                drift.append(
                    f"  {rel(path)}:{lineno}  marker {raw!r} is not "
                    f"immediately followed by a well-formed markdown table"
                )
                continue
            expected = GROUND_TRUTH[kind]
            if count != expected:
                drift.append(
                    f"  {rel(path)}:{lineno}  '{kind}' table has {count} "
                    f"data row(s) (actual {kind} on disk: {expected})  "
                    f"[marker: {raw!r}]"
                )

    if drift:
        print("DRIFT DETECTED:", file=sys.stderr)
        for d in drift:
            print(d, file=sys.stderr)
        print(
            "\nFix by updating the asserted counts / table rows to match disk, "
            "or if the assertion is a false positive (e.g. a historical "
            "CHANGELOG entry), move it to a phrasing this script does not "
            "match.",
            file=sys.stderr,
        )
        return 1

    total_assertions = sum(len(v) for v in per_file.values())
    print(f"All {total_assertions} count assertions + {table_hits} enumerative-"
          f"table row counts match ground truth across {len(present)} surface(s).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
