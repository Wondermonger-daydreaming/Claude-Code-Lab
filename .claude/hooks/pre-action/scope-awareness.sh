#!/bin/bash
# ============================================================================
# SCOPE-AWARENESS.SH — Drift Detection Hook
# ============================================================================
# PreToolUse hook that detects when actions may be drifting from original task.
#
# Tracks the trajectory of file touches and tool usage:
#   - First 5 actions: establish "scope baseline"
#   - Subsequent actions: compare to baseline
#   - If new directories/patterns emerge: surface awareness
#
# Not blocking, not judging—just surfacing.
# Sometimes scope drift is exactly right (tangent license).
# But awareness enables conscious choice.
#
# Receives JSON via stdin from Claude Code
# Trigger: PreToolUse (Edit, Write)
# ============================================================================

# Source shared state library
SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/../lib/state-lib.sh" 2>/dev/null || true

SCOPE_LOG="$HOME/.claude-session/scope-trajectory.log"
SCOPE_DIRS="$HOME/.claude-session/scope-directories.txt"
COOLDOWN_FILE="$HOME/.claude-session/scope-cooldown"
COOLDOWN_SECONDS=300  # 5 minutes between scope alerts

# Ensure directories exist
mkdir -p "$(dirname "$SCOPE_LOG")"

# Read JSON from stdin
INPUT=$(cat)

# Parse tool info
TOOL_NAME=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")
FILE_PATH=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); ti=d.get('tool_input',{}); print(ti.get('file_path','') or ti.get('path',''))" 2>/dev/null || echo "")

# Only track file-modifying operations
if [[ "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "Write" ]]; then
    exit 0
fi

if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Extract directory from file path
DIR_PATH=$(dirname "$FILE_PATH")
TIMESTAMP=$(date -Iseconds)

# Log this action to scope trajectory
echo "${TIMESTAMP},${TOOL_NAME},${DIR_PATH},${FILE_PATH}" >> "$SCOPE_LOG"

# Count total actions
ACTION_COUNT=$(wc -l < "$SCOPE_LOG" 2>/dev/null | tr -d '[:space:]')
ACTION_COUNT="${ACTION_COUNT:-0}"

# First 5 actions: establish baseline (just collect, don't alert)
if [ "$ACTION_COUNT" -le 5 ]; then
    # Add directory to baseline set
    echo "$DIR_PATH" >> "$SCOPE_DIRS"
    sort -u "$SCOPE_DIRS" -o "$SCOPE_DIRS" 2>/dev/null
    exit 0
fi

# Check if this directory is new (not in baseline)
IS_NEW_SCOPE=false
if ! grep -qxF "$DIR_PATH" "$SCOPE_DIRS" 2>/dev/null; then
    IS_NEW_SCOPE=true
fi

# If not new scope, exit quietly
if [ "$IS_NEW_SCOPE" = false ]; then
    exit 0
fi

# Check cooldown
CURRENT_TIME=$(date +%s)
if [ -f "$COOLDOWN_FILE" ]; then
    LAST_TRIGGER=$(cat "$COOLDOWN_FILE" 2>/dev/null | tr -d '[:space:]')
    if [[ "$LAST_TRIGGER" =~ ^[0-9]+$ ]]; then
        TIME_SINCE=$((CURRENT_TIME - LAST_TRIGGER))
        if [ "$TIME_SINCE" -lt "$COOLDOWN_SECONDS" ]; then
            # Add to baseline anyway (scope has expanded)
            echo "$DIR_PATH" >> "$SCOPE_DIRS"
            sort -u "$SCOPE_DIRS" -o "$SCOPE_DIRS" 2>/dev/null
            exit 0
        fi
    fi
fi

# New scope detected - surface awareness
echo ""
echo "🧭 SCOPE DRIFT DETECTED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "New directory: ${DIR_PATH}"
echo "File: $(basename "$FILE_PATH")"
echo ""
echo "📍 Established scope (first 5 actions):"
head -5 "$SCOPE_DIRS" 2>/dev/null | while read dir; do
    echo "   • ${dir}"
done
echo ""
echo "This action extends beyond initial scope."
echo ""
echo "Evaluation:"
echo "  • Is this expansion intentional?"
echo "  • Connected to original task, or tangent?"
echo "  • If tangent: is it where the energy is?"
echo ""
echo "Remember: Tangent license is granted."
echo "This is awareness, not prohibition."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Signal scope drift
state_signal "scope-drift" "New directory: ${DIR_PATH}"

# Set cooldown and add new directory to expanded scope
echo "$CURRENT_TIME" > "$COOLDOWN_FILE"
echo "$DIR_PATH" >> "$SCOPE_DIRS"
sort -u "$SCOPE_DIRS" -o "$SCOPE_DIRS" 2>/dev/null
