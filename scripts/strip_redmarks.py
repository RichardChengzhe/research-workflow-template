#!/usr/bin/env python3
"""Strip change-marking macros from LaTeX manuscript files (the "accept" step).

Removes the two change-marking wrappers used when editing a coauthored
manuscript (see ``manuscript/CLAUDE.md`` and
``.claude/rules/manuscript-overleaf-sync.md``):

* ``\\textcolor{red}{...}``  -> keep the inner content (accept the addition)
* ``\\sout{...}``            -> delete wrapper AND content (accept the deletion)

Why this is NOT a regex
-----------------------
A naive pattern such as ``\\textcolor{red}{([^}]*)}`` stops at the FIRST
closing brace and therefore corrupts any cell containing nested braces --
table values like ``$^{**}$``, citations like ``\\citet{Key2024}``, or
``\\textit{...}``. A single table row frequently carries several
``\\textcolor{red}{...}`` wrappers. This module instead walks the string
character by character, tracking brace DEPTH, and removes only the wrapper
plus its matching close brace, leaving nested content byte-for-byte intact.

Verification discipline
------------------------
After a pass the script re-counts the markers by OCCURRENCE (``str.count``,
not line count -- a row can hold 3-4 marks) and asserts the residual is
zero. It iterates to a fixpoint so any nested wrapper is caught, and reads/
writes with ``newline=''`` so line endings are preserved.

Usage
-----
    python strip_redmarks.py PATH [--dry-run] [--quiet]

PATH may be a single ``.tex`` file or a directory (processed recursively
over every ``*.tex`` it contains).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Wrapper prefixes we know how to strip. The two KEEP forms delimit their
# kept content with DIFFERENT braces, so each records which brace closes the
# wrapper (a regex cannot make this distinction -- that is the whole point):
#   * \textcolor{red}{CONTENT}  -- the wrapper closes with the brace opened by
#     the prefix's own trailing "{"; the leading "{red}" argument is balanced
#     and irrelevant. "group_open" = "trailing": match from the last prefix char.
#   * {\color{red} CONTENT}     -- CONTENT lives directly inside the OUTERMOST
#     brace, which is the prefix's leading "{". "group_open" = "leading":
#     match from the first prefix char (index i).
# Each entry: (prefix, group_open) where group_open in {"leading","trailing"}.
KEEP_PREFIXES = (
    (r"\textcolor{red}{", "trailing"),  # red addition -> keep inner content
    (r"{\color{red} ", "leading"),      # \color form  -> keep inner content
)
DROP_PREFIXES = (
    r"\sout{",             # struck text   -> drop inner content too
)

# Flat tuple of every marker prefix string, for occurrence counting.
_ALL_PREFIXES = tuple(p for p, _ in KEEP_PREFIXES) + DROP_PREFIXES


def _find_match(text: str, open_idx: int) -> int:
    """Return index of the brace that closes the group opened at ``open_idx``.

    ``text[open_idx]`` must be the opening ``{``. Raises ``ValueError`` if the
    braces are unbalanced (truncated input / malformed source).
    """
    depth = 0
    i = open_idx
    n = len(text)
    while i < n:
        c = text[i]
        if c == "\\":          # skip escaped char (e.g. \{ \} \% \\)
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f"unbalanced braces starting at index {open_idx}")


def _strip_once(text: str) -> str:
    """One left-to-right pass: unwrap KEEP wrappers, delete DROP wrappers."""
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        matched = False
        # KEEP: remove the wrapper but keep its inner content. The brace that
        # closes the wrapper depends on the form (see KEEP_PREFIXES comment).
        for pre, group_open in KEEP_PREFIXES:
            if text.startswith(pre, i):
                content_start = i + len(pre)
                if group_open == "trailing":
                    open_idx = content_start - 1      # prefix's own trailing "{"
                else:  # "leading": the outermost "{" at the prefix start
                    open_idx = i
                close = _find_match(text, open_idx)
                out.append(text[content_start:close])
                i = close + 1
                matched = True
                break
        if matched:
            continue
        # DROP: remove the prefix, its content, and its matching close brace.
        for pre in DROP_PREFIXES:
            if text.startswith(pre, i):
                close = _find_match(text, i + len(pre) - 1)
                i = close + 1
                matched = True
                break
        if matched:
            continue
        out.append(text[i])
        i += 1
    return "".join(out)


def _count_markers(text: str) -> int:
    """Count remaining wrappers by occurrence (a line may hold several)."""
    return sum(text.count(p) for p in _ALL_PREFIXES)


def strip_text(text: str, max_passes: int = 50) -> tuple[str, int]:
    """Strip all wrappers to a fixpoint.

    Returns ``(clean_text, markers_removed)``. Raises ``RuntimeError`` if a
    nonzero residual remains after ``max_passes`` (signals malformed input).
    """
    before = _count_markers(text)
    for _ in range(max_passes):
        if _count_markers(text) == 0:
            break
        text = _strip_once(text)
    residual = _count_markers(text)
    if residual != 0:
        raise RuntimeError(f"residual markers remain after {max_passes} passes: {residual}")
    return text, before - residual


def _iter_tex(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(path.rglob("*.tex"))
    return [path]


def process_file(path: Path, dry_run: bool, quiet: bool) -> int:
    """Strip one file; return markers removed. Writes in place unless --dry-run."""
    # newline='' on READ too: Path.read_text has no newline kwarg (3.12), and
    # universal-newline mode would silently rewrite CRLF -> LF on read, so a
    # CRLF file would be normalized even when zero markers are present. Read
    # and write with newline='' to round-trip line endings byte-for-byte.
    with open(path, "r", encoding="utf-8", newline="") as fh:
        raw = fh.read()
    clean, removed = strip_text(raw)
    if not quiet:
        action = "would remove" if dry_run else "removed"
        print(f"{path}: {action} {removed} marker(s)")
    if removed and not dry_run:
        # newline='' so existing CR/LF/CRLF are written back unchanged.
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(clean)
    return removed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", type=Path, help="a .tex file or a directory of .tex files")
    ap.add_argument("--dry-run", action="store_true", help="report counts; write nothing")
    ap.add_argument("--quiet", action="store_true", help="suppress per-file output")
    args = ap.parse_args(argv)

    if not args.path.exists():
        ap.error(f"path does not exist: {args.path}")

    files = _iter_tex(args.path)
    if not files:
        print(f"no .tex files found under {args.path}", file=sys.stderr)
        return 1

    total = sum(process_file(f, args.dry_run, args.quiet) for f in files)
    if not args.quiet:
        verb = "would remove" if args.dry_run else "removed"
        print(f"total: {verb} {total} marker(s) across {len(files)} file(s)")
    return 0


def _self_test() -> None:
    """Round-trip a nested-brace sample that a naive regex would corrupt."""
    sample = (
        r"Value \textcolor{red}{0.0150$^{***}$} from "
        r"\textcolor{red}{\citet{Smith2024}} and a "
        r"\sout{stale 0.0019$^{**}$} clause; "
        r"plain {braced} text and an {\color{red} inline edit} stays."
    )
    expected = (
        r"Value 0.0150$^{***}$ from "
        r"\citet{Smith2024} and a "
        r" clause; "
        r"plain {braced} text and an inline edit stays."
    )
    clean, removed = strip_text(sample)
    assert clean == expected, f"\nGOT:  {clean!r}\nWANT: {expected!r}"
    assert removed == 4, f"expected 4 markers removed, got {removed}"
    assert _count_markers(clean) == 0
    print("self-test OK (4 markers stripped, nested braces preserved)")


if __name__ == "__main__":
    # `python strip_redmarks.py --self-test` runs the embedded sanity check;
    # any other invocation goes to the normal CLI.
    if "--self-test" in sys.argv:
        _self_test()
    else:
        raise SystemExit(main())
