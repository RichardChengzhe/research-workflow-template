#!/usr/bin/env bash
#
# Install the repo's version-controlled git hooks (run once per clone).
#
# Points git at `.githooks/` so `git commit` runs the pre-commit quality
# gate (surface-sync + quality score >= 80). The hook lives in version
# control, so it stays in sync across machines and forks -- unlike
# `.git/hooks/`, which is local and never committed.
#
# Cross-platform: plain bash, Git-Bash compatible on Windows.
#
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

if [ ! -d .githooks ]; then
    echo "install-hooks: .githooks/ not found at repo root" >&2
    exit 1
fi

chmod +x .githooks/* 2>/dev/null || true
git config core.hooksPath .githooks

echo "OK core.hooksPath -> .githooks"
echo "  Every 'git commit' now runs surface-sync + quality (>=80) gates"
echo "  on staged .py/.do/.tex files."
echo "  Bypass once:  SKIP_QUALITY_GATE=1 git commit ...   (quality only)"
echo "                git commit --no-verify ...           (all hooks)"
echo "  Uninstall:    git config --unset core.hooksPath"
