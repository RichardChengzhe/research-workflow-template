#!/usr/bin/env python3
"""
check-skill-integrity -- deterministic parity checks on every
.claude/skills/*/SKILL.md. Runs in under a second; catches classes of bug
that an audit agent reading prose tends to miss. DYNAMIC: scans the repo on
disk, no hard-coded skill list.

Checks:
  1. Frontmatter present + name/description -- every SKILL.md must have YAML
     frontmatter with a `name` and a `description`, and `name` must equal the
     skill's directory name.
  2. Frontmatter <-> body tool parity -- `allowed-tools` in the frontmatter
     must cover every tool the body actually invokes (e.g. a body that spawns
     an agent "via Task" must declare Task).
  3. argument-hint <-> body flag parity (bidirectional) -- flags documented in
     the body (e.g. `--no-verify`) must appear in argument-hint, AND flags in
     argument-hint must be documented somewhere in the body. Stale hint flags
     mislead users as much as missing ones.
  4. Internal markdown anchor resolution -- every `[text](path#anchor)` link
     in the scanned surfaces must resolve to an actual heading.
  5. Rule paths/globs <-> skill implementation parity -- if a rule lists a
     skill in its `paths:`/`globs:` frontmatter, that skill must reference the
     rule's protocol keywords in its body.

Exit codes:
  0 = all checks pass, or only P2 advisories
  1 = one or more P0 or P1 findings (skill will misbehave at runtime, broken
      link, or a documented claim doesn't match implementation)
  2 = script error (the script itself crashed; per-file read errors are
      converted to P2 findings and do NOT exit 2)

Usage:
  python scripts/check-skill-integrity.py [--verbose]

Fail-open on parser errors: a corrupt/unparseable file prints a P2 warning
but does not fail the build.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parent.parent

# ---- Known tool names the harness exposes ------------------------------------

TOOLS = {
    "Task", "Bash", "Edit", "Write", "MultiEdit", "Read", "Grep", "Glob",
    "WebFetch", "WebSearch", "NotebookEdit",
}

# ---- Frontmatter parse -------------------------------------------------------

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body). Minimal YAML -- we only need
    `name:`, `description:`, `allowed-tools: [...]`, `argument-hint: "..."`,
    `paths:`/`globs:`."""
    m = FM_RE.match(text)
    if not m:
        return {}, text
    fm_raw = m.group(1)
    body = text[m.end():]
    fm: dict[str, object] = {}
    for line in fm_raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            continue
        if line[0] in " \t":  # list continuation -- handled by _parse_block_list
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            items = re.findall(r'"([^"]+)"', value)
            fm[key] = items
        elif value.startswith('"') and value.endswith('"'):
            fm[key] = value[1:-1]
        elif value in ("true", "false"):
            fm[key] = value == "true"
        elif value == "":
            fm[key] = _parse_block_list(fm_raw, key)
        else:
            fm[key] = value
    return fm, body


def _parse_block_list(fm_raw: str, key: str) -> list[str]:
    """Parse a YAML block list like:
        paths:
          - "foo"
          - "bar"
    """
    items: list[str] = []
    in_block = False
    for line in fm_raw.splitlines():
        if line.startswith(f"{key}:"):
            in_block = True
            continue
        if in_block:
            m = re.match(r"^\s+-\s+(.+)$", line)
            if m:
                v = m.group(1).strip().strip('"').strip("'")
                items.append(v)
            elif line.strip() and not line.startswith(" "):
                break
    return items


# ---- Check 0: Frontmatter present + name/description + dir match -------------

def check_frontmatter_basics() -> list[tuple[str, str, str]]:
    """Every SKILL.md needs frontmatter with `name` + `description`, and
    `name` must equal the parent directory name."""
    findings: list[tuple[str, str, str]] = []
    for skill_md in sorted(REPO.glob(".claude/skills/*/SKILL.md")):
        rel = skill_md.relative_to(REPO).as_posix()
        try:
            text = skill_md.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as e:
            findings.append(("P2", rel, f"unreadable: {e}"))
            continue
        fm, _ = parse_frontmatter(text)
        if not fm:
            findings.append(("P0", rel, "no YAML frontmatter block found"))
            continue
        name = fm.get("name")
        desc = fm.get("description")
        if not name:
            findings.append(("P0", rel, "frontmatter missing required `name`"))
        if not desc:
            findings.append(("P0", rel, "frontmatter missing required `description`"))
        dir_name = skill_md.parent.name
        if isinstance(name, str) and name and name != dir_name:
            findings.append((
                "P0", rel,
                f"frontmatter name {name!r} != directory name {dir_name!r}",
            ))
    return findings


# ---- Check 1: Frontmatter <-> body tool parity ------------------------------

TOOL_INVOCATION_PATTERNS = {
    # Task is the most common missing-permission bug (a skill promises to
    # spawn a sub-agent via Task but forgets to declare Task in allowed-tools).
    "Task": [
        r"\bvia\s+`?Task`?\b",
        r"\bsubagent_type\s*=",
        r"\bspawn\b[^.\n]{0,80}\bvia\s+Task\b",
        r"`Task`\s+with\b",
        r"\bTask:\s*subagent_type",
        r"\bTask\s+tool\b",
    ],
    # Edit/Write/MultiEdit require explicit "use X tool" or imperative
    # language -- prose like "edit the file" shouldn't match.
    "Edit": [r"`Edit`\s+tool\b", r"\bEdit\s+tool\b"],
    "Write": [r"`Write`\s+tool\b", r"\bWrite\s+tool\b"],
    "MultiEdit": [r"`MultiEdit`\s+tool\b"],
    "NotebookEdit": [r"\bNotebookEdit\b"],
    # WebSearch/WebFetch deliberately omitted: a skill body describing a
    # forked agent's use of WebSearch is NOT the skill invoking it directly,
    # and prose mentions dominate. Read/Grep/Glob/Bash similarly omitted --
    # too many false positives from prose and illustrative bash fences.
}


def tools_invoked_in_body(body: str) -> set[str]:
    """Tools whose invocation patterns appear in the skill body."""
    found: set[str] = set()
    for tool, patterns in TOOL_INVOCATION_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, body):
                found.add(tool)
                break
    return found


def check_tool_parity() -> list[tuple[str, str, str]]:
    """Return list of (severity, file, msg)."""
    findings: list[tuple[str, str, str]] = []
    for skill_md in sorted(REPO.glob(".claude/skills/*/SKILL.md")):
        try:
            text = skill_md.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as e:
            findings.append((
                "P2",
                skill_md.relative_to(REPO).as_posix(),
                f"unreadable: {e}",
            ))
            continue
        fm, body = parse_frontmatter(text)
        allowed = set(fm.get("allowed-tools") or [])
        invoked = tools_invoked_in_body(body)
        missing = invoked - allowed
        if missing:
            findings.append((
                "P0",
                skill_md.relative_to(REPO).as_posix(),
                f"body invokes {sorted(missing)} but frontmatter allowed-tools "
                f"is {sorted(allowed)}",
            ))
    return findings


# ---- Check 2: argument-hint <-> body flag parity ----------------------------

FLAG_RE = re.compile(r"--[a-z][a-z0-9-]*\b(?!=)")
# Word boundary + negative lookahead for `=`: skill flags are boolean, not
# `--suffix=.txt`-style kwargs.


def check_flag_parity() -> list[tuple[str, str, str]]:
    """Bidirectional argument-hint <-> body flag parity.

    Forward (body -> hint): count a flag as documented only when it appears in
    a clear option-documentation context:
      (a) first code-span in a markdown table row: `| `--flag` | ...`
      (b) explicit opt-out language: "`--flag` opts out", "skip with `--flag`"
      (c) a bullet/number list item starting with the flag.
    Prose mentions, shell-example flags, and other skills' flags are ignored.

    Reverse (hint -> body): a flag advertised in argument-hint must appear
    somewhere in the body as a code-span (more permissive than forward).
    """
    findings: list[tuple[str, str, str]] = []
    other_skill_flag_re = re.compile(r"/[\w-]+\s+--[\w-]+")
    table_first_cell_flag_re = re.compile(r"^\s*\|\s*`(--[a-z][a-z0-9-]*)`")
    list_item_flag_re = re.compile(r"^\s*(?:-|\d+\.)\s*`(--[a-z][a-z0-9-]*)`")
    opt_context_re = re.compile(
        r"\b(opt(?:s|-ing|-out|\s+out)|skip(?:s|ping)?|disabl|turn\s+off|"
        r"bypass|disable|the\s+(?:flag|opt))\b",
        re.IGNORECASE,
    )
    code_flag_re = re.compile(r"`(--[a-z][a-z0-9-]*)`")
    any_code_flag_re = re.compile(r"`(--[a-z][a-z0-9-]*)`")
    for skill_md in sorted(REPO.glob(".claude/skills/*/SKILL.md")):
        try:
            text = skill_md.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as e:
            findings.append((
                "P2",
                skill_md.relative_to(REPO).as_posix(),
                f"unreadable: {e}",
            ))
            continue
        fm, body = parse_frontmatter(text)
        hint = fm.get("argument-hint") or ""
        if not isinstance(hint, str):
            continue
        hint_flags = set(FLAG_RE.findall(hint))
        documented_flags: set[str] = set()
        for line in body.splitlines():
            cleaned = other_skill_flag_re.sub("", line)
            if "(future)" in cleaned.lower() or "not yet" in cleaned.lower():
                continue
            m_table = table_first_cell_flag_re.match(cleaned)
            m_list = list_item_flag_re.match(cleaned)
            if m_table:
                documented_flags.add(m_table.group(1))
            elif m_list:
                documented_flags.add(m_list.group(1))
            elif opt_context_re.search(cleaned):
                for cf in code_flag_re.findall(cleaned):
                    documented_flags.add(cf)
        missing_from_hint = {f for f in documented_flags - hint_flags if len(f) > 3}
        if missing_from_hint:
            findings.append((
                "P2",
                skill_md.relative_to(REPO).as_posix(),
                f"body documents {sorted(missing_from_hint)} as option flags "
                f"but argument-hint is {hint!r}",
            ))
        body_mentioned_flags = set(any_code_flag_re.findall(body))
        stale_in_hint = {f for f in hint_flags - body_mentioned_flags if len(f) > 3}
        if stale_in_hint:
            findings.append((
                "P2",
                skill_md.relative_to(REPO).as_posix(),
                f"argument-hint advertises {sorted(stale_in_hint)} but the "
                f"body never mentions those flags -- stale or unimplemented",
            ))
    return findings


# ---- Check 3: Internal markdown anchor resolution ---------------------------

ANCHOR_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+#[^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)(?:\s*\{#([^}]+)\})?\s*$", re.MULTILINE)


def anchorize(title: str) -> str:
    """GitHub-flavored-markdown anchor: lowercase, spaces->dashes, strip most
    punctuation except dashes and underscores. Accented chars kept."""
    s = title.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s+", "-", s)
    return s


def collect_anchors(md: Path) -> set[str]:
    try:
        text = md.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return set()
    anchors: set[str] = set()
    for m in HEADING_RE.finditer(text):
        explicit = m.group(3)
        title = m.group(2).strip()
        if explicit:
            anchors.add(explicit)
        anchors.add(anchorize(title))
    return anchors


FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def strip_code(text: str) -> str:
    """Blank out fenced code blocks and inline code spans so downstream
    regexes don't match illustrative examples. Replaces with spaces to
    preserve line numbers."""
    def blank(m: "re.Match") -> str:
        return " " * len(m.group(0))
    text = FENCE_RE.sub(blank, text)
    text = INLINE_CODE_RE.sub(blank, text)
    return text


def check_anchor_resolution() -> list[tuple[str, str, str]]:
    findings: list[tuple[str, str, str]] = []
    scan_roots = [
        REPO / ".claude",
        REPO / "templates",
        REPO / "CHANGELOG.md",
        REPO / "README.md",
        REPO / "CLAUDE.md",
        REPO / "MEMORY.md",
        REPO / "pipeline.md",
    ]
    mds: list[Path] = []
    for root in scan_roots:
        if root.is_file() and root.suffix == ".md":
            mds.append(root)
        elif root.is_dir():
            mds.extend(root.rglob("*.md"))
    for md in sorted(mds):
        try:
            raw = md.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as e:
            findings.append((
                "P2",
                md.relative_to(REPO).as_posix(),
                f"unreadable: {e}",
            ))
            continue
        text = strip_code(raw)
        for m in ANCHOR_LINK_RE.finditer(text):
            target = m.group(2)
            if target.startswith("http") or target.startswith("#"):
                continue
            path_part, _, anchor = target.partition("#")
            if not anchor:
                continue
            target_path = (md.parent / path_part).resolve()
            try:
                target_path.relative_to(REPO)
            except ValueError:
                continue
            if not target_path.exists() or not target_path.is_file():
                findings.append((
                    "P1",
                    md.relative_to(REPO).as_posix(),
                    f"link target {path_part!r} does not exist",
                ))
                continue
            anchors = collect_anchors(target_path)
            if anchor not in anchors:
                findings.append((
                    "P1",
                    md.relative_to(REPO).as_posix(),
                    f"anchor #{anchor} not found in {path_part}",
                ))
    return findings


# ---- Check 4: Rule paths <-> skill implementation parity --------------------

RULE_KEYWORDS: dict[str, list[str]] = {
    # Only rules whose scope actually targets skill files belong here. A rule
    # targeting content files (.tex, .do, .py) is not checkable with this
    # protocol -- those rules apply to content authors, not skill authors.
    "post-flight-verification.md": ["claim-verifier", "Post-Flight"],
    "summary-parity.md": [],  # empty = explicitly skipped; applies to edits
    # Add more as new rules ship that include `.claude/skills/*/SKILL.md`
    # in their paths: or globs: frontmatter.
}


def check_rule_skill_parity() -> list[tuple[str, str, str]]:
    """For each rule with a non-empty keyword list, iterate its scope
    frontmatter (`paths:` or `globs:`). For each pattern that targets skill
    files, verify the matching skills reference at least one keyword."""
    findings: list[tuple[str, str, str]] = []
    for rule_md in sorted(REPO.glob(".claude/rules/*.md")):
        rule_name = rule_md.name
        keywords = RULE_KEYWORDS.get(rule_name)
        if keywords is None or not keywords:
            continue
        try:
            rule_text = rule_md.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        fm, _ = parse_frontmatter(rule_text)
        scope = (fm.get("paths") or []) + (fm.get("globs") or [])
        if not isinstance(scope, list):
            continue
        for pattern in scope:
            if not isinstance(pattern, str):
                continue
            if ".claude/skills/" not in pattern:
                continue
            for skill_md in REPO.glob(pattern):
                try:
                    skill_text = skill_md.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    continue
                if not any(kw in skill_text for kw in keywords):
                    findings.append((
                        "P0",
                        skill_md.relative_to(REPO).as_posix(),
                        f"rule {rule_name} lists this skill in paths:/globs: "
                        f"but the skill body contains none of {keywords}",
                    ))
    return findings


# ---- Runner ------------------------------------------------------------------

def _fmt(findings: Iterable[tuple[str, str, str]]) -> str:
    by_sev: dict[str, list[tuple[str, str]]] = {"P0": [], "P1": [], "P2": []}
    for sev, path, msg in findings:
        by_sev.setdefault(sev, []).append((path, msg))
    out: list[str] = []
    for sev in ("P0", "P1", "P2"):
        rows = by_sev.get(sev) or []
        if not rows:
            continue
        out.append(f"\n{sev}: {len(rows)} finding(s)")
        for path, msg in rows:
            out.append(f"  {path}")
            out.append(f"    {msg}")
    return "\n".join(out) if out else ""


def main() -> int:
    verbose = "--verbose" in sys.argv
    all_findings: list[tuple[str, str, str]] = []
    for name, fn in [
        ("frontmatter basics", check_frontmatter_basics),
        ("tool parity", check_tool_parity),
        ("flag parity", check_flag_parity),
        ("anchor resolution", check_anchor_resolution),
        ("rule-skill parity", check_rule_skill_parity),
    ]:
        try:
            findings = fn()
        except Exception as e:
            print(f"script error in {name}: {e}", file=sys.stderr)
            return 2
        if verbose:
            print(f"{name}: {len(findings)} finding(s)")
        all_findings.extend(findings)
    p0 = sum(1 for f in all_findings if f[0] == "P0")
    p1 = sum(1 for f in all_findings if f[0] == "P1")
    if not all_findings:
        print("check-skill-integrity: all checks pass")
        return 0
    report = _fmt(all_findings)
    print("check-skill-integrity findings:" + report)
    return 1 if p0 or p1 else 0


if __name__ == "__main__":
    sys.exit(main())
