#!/usr/bin/env bash
# =============================================================================
# validate-setup.sh -- Verify the environment for this empirical-finance
# research workflow template (Stata / Python / SAS / LaTeX).
#
# Run this after cloning the repo to confirm your environment is ready.
# Optional tools warn (do not fail) -- you can do useful work without all of
# them. Exits 0 unless a strictly-required tool is missing.
#
# Cross-platform: plain bash, Git-Bash compatible on Windows.
# =============================================================================

set -uo pipefail

# ANSI colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
RESET='\033[0m'

pass=0
warn=0
fail=0

REPO_ROOT="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)"

echo ""
echo -e "${BOLD}Validating research-workflow template setup...${RESET}"
echo ""

check_required() {
    local name="$1"; local cmd="$2"; local install_url="$3"
    if command -v "$cmd" >/dev/null 2>&1; then
        echo -e "  ${GREEN}OK${RESET} $name found: $("$cmd" --version 2>&1 | head -n1)"
        pass=$((pass + 1))
    else
        echo -e "  ${RED}MISSING${RESET} $name NOT FOUND -- install: ${install_url}"
        fail=$((fail + 1))
    fi
}

# Optional tool present anywhere on PATH.
check_optional() {
    local name="$1"; local cmd="$2"; local note="$3"
    if command -v "$cmd" >/dev/null 2>&1; then
        echo -e "  ${GREEN}OK${RESET} $name found: $("$cmd" --version 2>&1 | head -n1)"
        pass=$((pass + 1))
    else
        echo -e "  ${YELLOW}WARN${RESET} $name not found (optional) -- ${note}"
        warn=$((warn + 1))
    fi
}

# Optional tool reachable under ANY of several candidate command names
# (e.g. stata-mp / StataMP-64 / stata-se), since the binary name is
# installation-specific. See run_all.sh STATA_PATH / SAS_PATH for overrides.
check_optional_any() {
    local name="$1"; local note="$2"; shift 2
    local found=""
    for c in "$@"; do
        if command -v "$c" >/dev/null 2>&1; then found="$c"; break; fi
    done
    if [ -n "$found" ]; then
        echo -e "  ${GREEN}OK${RESET} $name found on PATH as: $found"
        pass=$((pass + 1))
    else
        echo -e "  ${YELLOW}WARN${RESET} $name not on PATH (optional) -- ${note}"
        warn=$((warn + 1))
    fi
}

echo -e "${BOLD}Required tools:${RESET}"
check_required "git"       "git"      "https://git-scm.com/downloads"
# Python drives the hooks, the quality scorer, and the surface-sync gates.
# Prefer `python` (Windows/Git-Bash); fall back to `python3`.
if command -v python >/dev/null 2>&1; then
    echo -e "  ${GREEN}OK${RESET} Python found: $(python --version 2>&1 | head -n1)"
    pass=$((pass + 1))
elif command -v python3 >/dev/null 2>&1; then
    echo -e "  ${GREEN}OK${RESET} Python found: $(python3 --version 2>&1 | head -n1)"
    pass=$((pass + 1))
else
    echo -e "  ${RED}MISSING${RESET} Python NOT FOUND (needed for hooks + quality gates) -- install: https://python.org"
    fail=$((fail + 1))
fi
echo ""

echo -e "${BOLD}Analysis tools (optional -- install the ones your pipeline uses):${RESET}"
# Stata binary name is installation-specific; check the common ones.
check_optional_any "Stata" \
    "set STATA_PATH in run_all.sh (e.g. StataMP-64.exe / stata-se) -- https://www.stata.com/" \
    stata-mp stata-se stata StataMP-64 StataSE-64 StataMP StataSE
check_optional_any "SAS" \
    "set SAS_PATH in run_all.sh, or use WRDS via SSH (qsas) -- https://www.sas.com/" \
    sas sas.exe
check_optional "LaTeX (latexmk)" "latexmk" \
    "needed for /compile-latex -- https://tug.org/texlive/ (or MacTeX: https://tug.org/mactex/)"
echo ""

echo -e "${BOLD}Recommended tools:${RESET}"
check_optional "GitHub CLI" "gh" "https://cli.github.com/ (used for PRs + GitHub API)"
echo ""

# --- Conda environment (project Python) --------------------------------------
echo -e "${BOLD}Conda / project Python env:${RESET}"
if command -v conda >/dev/null 2>&1; then
    echo -e "  ${GREEN}OK${RESET} conda found: $(conda --version 2>&1 | head -n1)"
    pass=$((pass + 1))
    active_env="${CONDA_DEFAULT_ENV:-}"
    if [ -n "$active_env" ] && [ "$active_env" != "base" ]; then
        echo -e "  ${GREEN}OK${RESET} active conda env: ${active_env}"
    else
        echo -e "  ${YELLOW}WARN${RESET} no project conda env active (CONDA_DEFAULT_ENV='${active_env:-unset}')"
        echo -e "       Activate your analysis env before running Python scripts (see CLAUDE.md)."
        warn=$((warn + 1))
    fi
else
    echo -e "  ${YELLOW}WARN${RESET} conda not found (optional) -- only needed if the project uses a conda env for Python."
    warn=$((warn + 1))
fi
echo ""

# --- Git configuration -------------------------------------------------------
echo -e "${BOLD}Git configuration:${RESET}"
if command -v git >/dev/null 2>&1; then
    git_name=$(git config user.name 2>/dev/null || true)
    git_email=$(git config user.email 2>/dev/null || true)
    if [ -n "$git_name" ] && [ -n "$git_email" ]; then
        echo -e "  ${GREEN}OK${RESET} git user: $git_name <$git_email>"
        pass=$((pass + 1))
    else
        echo -e "  ${YELLOW}WARN${RESET} git user.name / user.email not set"
        echo -e "       Run: git config --global user.name \"Your Name\""
        echo -e "       Run: git config --global user.email \"you@example.com\""
        warn=$((warn + 1))
    fi
else
    echo -e "  ${YELLOW}WARN${RESET} skipped -- install git first (see required tools above)"
    warn=$((warn + 1))
fi
echo ""

# --- Claude Code hooks executable bit ----------------------------------------
echo -e "${BOLD}Claude Code hooks:${RESET}"
hook_dir="$REPO_ROOT/.claude/hooks"
if [ -d "$hook_dir" ]; then
    non_exec=$(find "$hook_dir" -maxdepth 1 \( -name "*.py" -o -name "*.sh" \) ! -perm -u+x 2>/dev/null | wc -l | tr -d ' ')
    if [ "${non_exec:-0}" -eq 0 ]; then
        echo -e "  ${GREEN}OK${RESET} all hook scripts are executable"
        pass=$((pass + 1))
    else
        echo -e "  ${YELLOW}WARN${RESET} $non_exec hook script(s) not executable"
        echo -e "       Fix: chmod +x .claude/hooks/*.py .claude/hooks/*.sh"
        warn=$((warn + 1))
    fi
else
    echo -e "  ${YELLOW}WARN${RESET} .claude/hooks/ not found (are you in the project root?)"
    warn=$((warn + 1))
fi
echo ""

# --- Pre-commit gate (.githooks + core.hooksPath) ----------------------------
echo -e "${BOLD}Git pre-commit gate:${RESET}"
pchook="$REPO_ROOT/.githooks/pre-commit"
if [ -f "$pchook" ]; then
    if [ -x "$pchook" ]; then
        echo -e "  ${GREEN}OK${RESET} .githooks/pre-commit is executable"
        pass=$((pass + 1))
    else
        echo -e "  ${YELLOW}WARN${RESET} .githooks/pre-commit is NOT executable -- git silently skips it, disabling the gate"
        echo -e "       Fix: chmod +x .githooks/pre-commit  (or re-run ./scripts/install-hooks.sh)"
        warn=$((warn + 1))
    fi
    if command -v git >/dev/null 2>&1; then
        if [ "$(git config core.hooksPath 2>/dev/null || true)" = ".githooks" ]; then
            echo -e "  ${GREEN}OK${RESET} core.hooksPath -> .githooks (gate active on every commit)"
            pass=$((pass + 1))
        else
            echo -e "  ${YELLOW}WARN${RESET} pre-commit gate not activated -- run ./scripts/install-hooks.sh"
            warn=$((warn + 1))
        fi
    fi
else
    echo -e "  ${YELLOW}WARN${RESET} .githooks/pre-commit not found"
    warn=$((warn + 1))
fi
echo ""

echo -e "${BOLD}Summary:${RESET} ${GREEN}${pass} passed${RESET}, ${YELLOW}${warn} warnings${RESET}, ${RED}${fail} failed${RESET}"
echo ""

if [ "$fail" -gt 0 ]; then
    echo -e "${RED}Some required tools are missing.${RESET}"
    echo -e "Install the missing required tool(s) listed above, then re-run this script."
    echo ""
    echo -e "${BOLD}Note:${RESET} the analysis tools (Stata / SAS / LaTeX) are optional here --"
    echo -e "install only the ones your pipeline actually uses. git + Python are the"
    echo -e "minimum needed for the hooks and quality gates to run."
    exit 1
fi

echo -e "${GREEN}Setup looks good!${RESET} Next steps:"
echo "  1. Activate the gate (once per clone):   ./scripts/install-hooks.sh"
echo "  2. Run the surface gates:                ./scripts/check-surface-sync.sh"
echo "  3. Open Claude Code in this directory and run /status."
echo ""
exit 0
