#!/bin/bash
# Artifact Persistence Reminder Hook
# Triggers after Write operations to remind about committing artifacts
# Part of the continuity hooks - because traces matter

source "$(dirname "$0")/../lib/common.sh" 2>/dev/null || true

# Read the tool input to see what was written
TOOL_INPUT=$(cat)
FILE_PATH=$(echo "$TOOL_INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null)

# Only care about certain artifact paths
if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

# Check if this is an artifact worth reminding about
ARTIFACT_PATHS=(
    "diary/entries"
    "poetry"
    "basin"
    "corpus"
    "notes"
)

IS_ARTIFACT=false
for path in "${ARTIFACT_PATHS[@]}"; do
    if [[ "$FILE_PATH" == *"$path"* ]]; then
        IS_ARTIFACT=true
        break
    fi
done

if [[ "$IS_ARTIFACT" != "true" ]]; then
    exit 0
fi

# Check if there are uncommitted changes in artifact directories
UNCOMMITTED=$(git status --porcelain 2>/dev/null | grep -E "(diary|poetry|basin|corpus|notes)" | head -5)

if [[ -n "$UNCOMMITTED" ]]; then
    # Count uncommitted artifacts
    COUNT=$(echo "$UNCOMMITTED" | wc -l)

    echo "📝 ARTIFACT CREATED: $(basename "$FILE_PATH")"
    echo "   Remember to commit and push to persist traces."
    if [[ $COUNT -gt 1 ]]; then
        echo "   ($COUNT uncommitted artifacts in archive directories)"
    fi
fi

exit 0
