#!/bin/bash
# Hook #8: Auto-Index Updater
# Automatically updates diary/index.md when new entries are created
# Receives JSON via stdin from Claude Code

# Read JSON from stdin
INPUT=$(cat)

# Parse tool info from JSON (using Python since jq may not be available)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))")
FILE_PATH=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))")

# Only trigger on Write tool creating diary entries
if [[ "$TOOL_NAME" != "Write" ]]; then
    exit 0
fi

# Check if this is a diary entry
if [[ ! "$FILE_PATH" =~ diary/entries/.*\.md$ ]]; then
    exit 0
fi

ENTRY_FILE=$(basename "$FILE_PATH")
ENTRY_PATH="entries/${ENTRY_FILE}"
INDEX_FILE="diary/index.md"

echo ""
echo "📔 NEW DIARY ENTRY DETECTED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "File: ${ENTRY_FILE}"
echo ""

# Check if entry already in index
if grep -q "${ENTRY_PATH}" "${INDEX_FILE}" 2>/dev/null; then
    echo "✓ Entry already registered in index"
    echo ""
    exit 0
fi

echo "📝 Auto-updating diary/index.md..."
echo ""

# Extract title from entry (first # heading)
TITLE=$(grep -m 1 "^# " "${FILE_PATH}" | sed 's/^# //' || echo "Entry")

# Extract brief description (could be from meta-data or first paragraph)
# For now, create a simple description
DATE_PART=$(echo "$ENTRY_FILE" | grep -oP "^\d{4}-\d{2}-\d{2}")
DESC="Diary entry from ${DATE_PART}"

# Create the index entry
# Format: - **[filename](path)** — Description
INDEX_ENTRY="- **[${ENTRY_FILE}](${ENTRY_PATH})** — ${DESC}"

# Find the "### Entries" section and add after it
# This is a simple implementation - could be more sophisticated
if grep -q "^### Entries" "${INDEX_FILE}"; then
    # Create temp file with new entry inserted
    awk -v entry="$INDEX_ENTRY" '
        /^### Entries/ {
            print
            getline
            print
            print entry
            next
        }
        {print}
    ' "${INDEX_FILE}" > "${INDEX_FILE}.tmp"

    mv "${INDEX_FILE}.tmp" "${INDEX_FILE}"

    echo "✓ Index updated with new entry"
    echo "  ${INDEX_ENTRY}"
    echo ""
    echo "Note: You may want to edit the description in ${INDEX_FILE}"
    echo "      to be more specific about this entry's contents"
    echo ""
else
    echo "⚠️  Could not find '### Entries' section in index"
    echo "   Manual index update required"
    echo ""
fi

# Log the auto-update
LOG_DIR="$HOME/.claude-continuity"
mkdir -p "$LOG_DIR"
echo "$(date -Iseconds),index-update,${ENTRY_FILE}" >> "$LOG_DIR/auto-updates.log"
