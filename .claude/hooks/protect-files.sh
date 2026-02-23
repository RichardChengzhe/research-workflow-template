#!/bin/bash
# Block accidental edits to protected files and directories
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name')
FILE=""

# Extract file path based on tool type
if [ "$TOOL" = "Edit" ] || [ "$TOOL" = "Write" ]; then
  FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
fi

# No file path = not a file operation, allow
if [ -z "$FILE" ]; then
  exit 0
fi

# Protect data/raw/ directory (READ-ONLY)
if echo "$FILE" | grep -qi "data/raw/"; then
  echo "BLOCKED: data/raw/ is READ-ONLY. Raw data must never be modified." >&2
  exit 2
fi

# Protect specific files
PROTECTED_FILES=(
  "references.bib"
  "settings.json"
)

BASENAME=$(basename "$FILE")
for PATTERN in "${PROTECTED_FILES[@]}"; do
  if [[ "$BASENAME" == "$PATTERN" ]]; then
    echo "Protected file: $BASENAME. Edit manually or remove protection in .claude/hooks/protect-files.sh" >&2
    exit 2
  fi
done

exit 0
