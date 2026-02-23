#!/bin/bash
# run_all.sh -- Master execution script
# Usage: ./run_all.sh "01_import.do"    (single Stata step)
#        ./run_all.sh "15_figures.py"   (single Python step)
#        ./run_all.sh --all             (full pipeline)

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$PROJECT_ROOT/output/logs"
STATA_SCRIPTS="$PROJECT_ROOT/code/stata"
PYTHON_SCRIPTS="$PROJECT_ROOT/code/python"

# --- CONFIGURE THESE ---
# Windows:
# STATA_PATH="/c/Program Files/Stata18/StataMP-64.exe"
# macOS:
# STATA_PATH="/Applications/Stata/StataSE.app/Contents/MacOS/stata-se"
# Linux:
# STATA_PATH="/usr/local/stata-mp/stata-mp"
STATA_PATH="stata-mp"  # Default: assumes Stata is in PATH

PYTHON_PATH="$(which python 2>/dev/null || which python3 2>/dev/null || echo 'python')"
# ------------------------

# Ensure log directory exists
mkdir -p "$LOG_DIR"

timestamp() {
    date "+%Y-%m-%d_%H%M%S"
}

run_stata() {
    local script="$1"
    local script_base
    script_base=$(basename "$script" .do)
    local logfile="$LOG_DIR/${script_base}_$(timestamp).log"

    local script_dir="$STATA_SCRIPTS"
    if [[ ! -f "$script_dir/$script" ]]; then
        script_dir="$PROJECT_ROOT/code/programs"
    fi

    echo "Running Stata: $script"
    echo "Log: $logfile"

    "$STATA_PATH" -b do "$script_dir/$script" 2>&1 | tee "$logfile"
    local exit_code=${PIPESTATUS[0]}

    if [[ -f "$script_dir/${script_base}.log" ]]; then
        cp "$script_dir/${script_base}.log" "$logfile"
    fi

    echo "Exit code: $exit_code"
    return $exit_code
}

run_python() {
    local script="$1"
    local script_base
    script_base=$(basename "$script" .py)
    local logfile="$LOG_DIR/${script_base}_$(timestamp).log"

    local script_dir="$PYTHON_SCRIPTS"
    if [[ ! -f "$script_dir/$script" ]]; then
        script_dir="$PROJECT_ROOT/code/programs"
    fi

    echo "Running Python: $script"
    echo "Log: $logfile"

    "$PYTHON_PATH" "$script_dir/$script" 2>&1 | tee "$logfile"
    local exit_code=${PIPESTATUS[0]}
    echo "Exit code: $exit_code"
    return $exit_code
}

run_script() {
    local script="$1"
    case "$script" in
        *.do)  run_stata "$script" ;;
        *.py)  run_python "$script" ;;
        *)     echo "Unknown file type: $script"; exit 1 ;;
    esac
}

if [[ "${1:-}" == "--all" ]]; then
    echo "=== Running full pipeline ==="
    # Add pipeline steps here in order:
    # run_script "01_import.do"
    # run_script "05_merge.do"
    # run_script "10_summary_stats.do"
    # run_script "15_figures.py"
    # run_script "20_estimation.do"
    # run_script "25_robustness.do"
    echo "=== Pipeline complete ==="
elif [[ -n "${1:-}" ]]; then
    run_script "$1"
else
    echo "Usage: $0 <script_name> | --all"
    echo ""
    echo "Examples:"
    echo "  $0 01_import.do"
    echo "  $0 15_figures.py"
    echo "  $0 --all"
    exit 1
fi
