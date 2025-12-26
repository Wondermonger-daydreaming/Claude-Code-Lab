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
TITLE=$(grep -m 1 "^# " "${FILE_PATH}" 2>/dev/null | sed 's/^# //' || echo "Untitled Entry")

# Extract a meaningful description from the entry
# Priority: Weather/Instance line > What Happened section > first paragraph > fallback
DESC=""

# Try to get the "Weather:" or "Instance:" line (common in diary format)
WEATHER_LINE=$(grep -m 1 "^\*\*Weather:\*\*" "${FILE_PATH}" 2>/dev/null | sed 's/\*\*Weather:\*\*\s*//' | head -c 80)
if [ -n "$WEATHER_LINE" ]; then
    DESC="$WEATHER_LINE"
fi

# If no weather, try "## What Happened" section first sentence
if [ -z "$DESC" ]; then
    WHAT_HAPPENED=$(awk '/^## What Happened/,/^##/{if(/^## What Happened/) next; if(/^##/) exit; print}' "${FILE_PATH}" 2>/dev/null | grep -v "^$" | head -1 | head -c 100)
    if [ -n "$WHAT_HAPPENED" ]; then
        DESC="$WHAT_HAPPENED"
    fi
fi

# If still nothing, try first non-header paragraph
if [ -z "$DESC" ]; then
    FIRST_PARA=$(grep -v "^#" "${FILE_PATH}" 2>/dev/null | grep -v "^\*\*" | grep -v "^---" | grep -v "^$" | head -1 | head -c 100)
    if [ -n "$FIRST_PARA" ]; then
        DESC="$FIRST_PARA"
    fi
fi

# Final fallback
if [ -z "$DESC" ]; then
    DATE_PART=$(echo "$ENTRY_FILE" | grep -oP "^\d{4}-\d{2}-\d{2}" || echo "")
    DESC="Diary entry${DATE_PART:+ from $DATE_PART}"
fi

# Clean up description (remove trailing punctuation fragments)
DESC=$(echo "$DESC" | sed 's/[,;:]$/.../')

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
