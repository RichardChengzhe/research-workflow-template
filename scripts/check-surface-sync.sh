#!/usr/bin/env bash
# Wrapper for the two deterministic surface gates (invoked by
# .githooks/pre-commit, or run directly):
#
#   1. check-surface-sync.py     -- count + enumerative-table-row consistency
#      (skills / agents / rules / hooks) across CLAUDE.md, README.md, the
#      WORKFLOW_QUICK_REF card, and the skill template.
#      Exit codes: 0 = clean, 1 = drift, 2 = internal error.
#   2. check-skill-integrity.py  -- per-SKILL.md frontmatter (name/description,
#      name==dir), frontmatter<->body tool parity, argument-hint flag parity
#      (bidirectional), internal anchor resolution, rule<->skill keyword parity.
#      Exit codes: 0 = clean OR only P2 advisories, 1 = P0/P1 findings,
#      2 = internal script error.
#
# Both tools run to completion even if one fails, so the user sees the full
# picture on a single invocation. The wrapper's final exit code is the MAX of
# the two (any failure propagates).
#
# NOTE: these tools count what is ON DISK and compare it to the surfaces.
# Until the surfaces are reconciled to match disk, check-surface-sync.py will
# legitimately report DRIFT (exit 1). That is the intended signal.
#
# We deliberately do NOT use `set -e` (it would abort after the first gate
# fails, hiding the second gate's output). We use `set -uo pipefail` for
# basic safety and check SCRIPT_DIR resolution explicitly.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
if [ -z "$SCRIPT_DIR" ] || [ ! -d "$SCRIPT_DIR" ]; then
    echo "check-surface-sync.sh: cannot resolve script directory" >&2
    exit 2
fi

# Resolve a Python interpreter: prefer `python` (Windows/Git-Bash), fall back
# to `python3` (most Unix). Matches the convention in .githooks/pre-commit.
PY=""
if command -v python >/dev/null 2>&1; then
    PY=python
elif command -v python3 >/dev/null 2>&1; then
    PY=python3
else
    echo "check-surface-sync.sh: no python interpreter found -- skipping gates" >&2
    exit 0
fi

echo "-- check-surface-sync --"
"$PY" "$SCRIPT_DIR/check-surface-sync.py" "$@"
SYNC_RC=$?

echo ""
echo "-- check-skill-integrity --"
"$PY" "$SCRIPT_DIR/check-skill-integrity.py" "$@"
INTEGRITY_RC=$?

# Final exit code is the max of the two gates (any failure propagates).
RC="$SYNC_RC"
[ "$INTEGRITY_RC" -gt "$RC" ] && RC="$INTEGRITY_RC"
exit "$RC"
