#!/bin/bash
# Save a context snapshot to the session log before compaction
INPUT=$(cat)
TRIGGER=$(echo "$INPUT" | jq -r '.trigger // "unknown"')

echo "=== CONTEXT COMPRESSION IMMINENT ==="
echo ""
echo "Context Survival Checklist:"
echo "  [ ] MEMORY.md updated with [LEARN] entries"
echo "  [ ] Session log current (last 10 minutes)"
echo "  [ ] Active plan saved to quality_reports/plans/"
echo "  [ ] Open questions documented"
echo ""
echo "Critical info saved? Compression in progress..."
echo ""

# Find most recent session log (check both locations)
for LOG_DIR in "$CLAUDE_PROJECT_DIR/session_logs" "$CLAUDE_PROJECT_DIR/quality_reports/session_logs"; do
  LATEST_LOG=$(ls -t "$LOG_DIR"/*.md 2>/dev/null | head -1)
  if [ -n "$LATEST_LOG" ]; then
    {
      echo ""
      echo "---"
      echo "**Context compaction ($TRIGGER) at $(date '+%H:%M')**"
      echo "Check git log and quality_reports/plans/ for current state."
    } >> "$LATEST_LOG"
    break
  fi
done

exit 0
