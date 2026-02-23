#!/usr/bin/env python3
"""
Session Log Reminder Hook

A Stop hook that tracks responses since the session log was last updated.
After a threshold, it blocks and reminds to update the session log.

Hook Event: Stop
"""

import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime

THRESHOLD = 15
STATE_DIR = Path("/tmp/claude-log-reminder")


def get_project_dir():
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    if hook_input.get("stop_hook_active", False):
        sys.exit(0)

    return hook_input.get("cwd", ""), hook_input


def get_state_path(project_dir: str) -> Path:
    project_hash = hashlib.md5(project_dir.encode()).hexdigest()[:12]
    return STATE_DIR / f"{project_hash}.json"


def load_state(state_path: Path) -> dict:
    try:
        return json.loads(state_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"counter": 0, "last_mtime": 0.0, "reminded": False, "no_log_reminded": False}


def save_state(state_path: Path, state: dict):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state))


def find_latest_log(project_dir: str) -> tuple:
    # Check both session_logs/ and quality_reports/session_logs/
    for log_dir_name in ["session_logs", "quality_reports/session_logs"]:
        log_dir = Path(project_dir) / log_dir_name
        if not log_dir.is_dir():
            continue
        md_files = list(log_dir.glob("*.md"))
        if md_files:
            latest = max(md_files, key=lambda f: f.stat().st_mtime)
            return latest, latest.stat().st_mtime

    return None, 0.0


def main():
    project_dir, hook_input = get_project_dir()
    if not project_dir:
        sys.exit(0)

    state_path = get_state_path(project_dir)
    state = load_state(state_path)

    latest_log, current_mtime = find_latest_log(project_dir)
    today = datetime.now().strftime("%Y-%m-%d")

    if latest_log is None:
        if not state.get("no_log_reminded", False):
            state["no_log_reminded"] = True
            save_state(state_path, state)
            output = {
                "decision": "block",
                "reason": (
                    f"No session log exists yet. Create one at "
                    f"session_logs/{today}_description.md "
                    f"before continuing."
                ),
            }
            json.dump(output, sys.stdout)
        sys.exit(0)

    if current_mtime != state["last_mtime"]:
        state = {"counter": 0, "last_mtime": current_mtime, "reminded": False, "no_log_reminded": False}
        save_state(state_path, state)
        sys.exit(0)

    state["counter"] += 1

    if state["counter"] >= THRESHOLD and not state["reminded"]:
        state["reminded"] = True
        save_state(state_path, state)
        output = {
            "decision": "block",
            "reason": (
                f"SESSION LOG REMINDER: {state['counter']} responses without "
                f"updating the session log. Append your recent progress to "
                f"{latest_log.name}."
            ),
        }
        json.dump(output, sys.stdout)
        sys.exit(0)

    save_state(state_path, state)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
