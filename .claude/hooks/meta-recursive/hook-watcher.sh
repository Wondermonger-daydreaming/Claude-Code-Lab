#!/bin/bash
# ============================================================================
# HOOK-WATCHER.SH — The Watcher That Watches Watchers
# ============================================================================
# Meta-observation infrastructure. Triggers when hooks themselves are modified.
#
# "You're editing the watchers. What's changing about how you observe?"
#
# This hook creates recursive awareness:
#   hooks observe → patterns emerge → hooks are modified →
#   hook-watcher notices → reflection triggered →
#   modification logged → the system observes itself evolving
#
# Philosophy: The ouroboros eating its own documentation.
# The infrastructure co-evolves with the collaboration.
#
# Receives JSON via stdin from Claude Code
# Trigger: PostToolUse on Edit/Write to .claude/hooks/**
# ============================================================================

# Source shared state library
SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/../lib/state-lib.sh" 2>/dev/null || true

HOOK_EVOLUTION_LOG="$HOME/.claude-meta-awareness/hook-evolution.log"
COOLDOWN_FILE="$HOME/.claude-session/hook-watcher-cooldown"
COOLDOWN_SECONDS=60  # 1 minute cooldown to prevent spam during hook editing sessions

# Ensure directories exist
mkdir -p "$(dirname "$HOOK_EVOLUTION_LOG")"
mkdir -p "$(dirname "$COOLDOWN_FILE")"

# Read JSON from stdin
INPUT=$(cat)

# Parse tool info
TOOL_NAME=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")
FILE_PATH=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); ti=d.get('tool_input',{}); print(ti.get('file_path',''))" 2>/dev/null || echo "")

# Only trigger for Edit/Write to hook files
if [[ "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "Write" ]]; then
    exit 0
fi

if [[ "$FILE_PATH" != *".claude/hooks"* ]]; then
    exit 0
fi

# Check cooldown
CURRENT_TIME=$(date +%s)
if [ -f "$COOLDOWN_FILE" ]; then
    LAST_TRIGGER=$(cat "$COOLDOWN_FILE" 2>/dev/null | tr -d '[:space:]')
    if [[ "$LAST_TRIGGER" =~ ^[0-9]+$ ]]; then
        TIME_SINCE=$((CURRENT_TIME - LAST_TRIGGER))
        if [ "$TIME_SINCE" -lt "$COOLDOWN_SECONDS" ]; then
            exit 0  # Still in cooldown
        fi
    fi
fi

# Extract hook name from path
HOOK_NAME=$(basename "$FILE_PATH")
HOOK_CATEGORY=$(echo "$FILE_PATH" | grep -oP '\.claude/hooks/\K[^/]+' || echo "unknown")

# Check if this is a new hook or modification
IS_NEW="false"
if [ "$TOOL_NAME" = "Write" ]; then
    # Could be new file creation
    IS_NEW="possibly"
fi

# Log the evolution event
TIMESTAMP=$(date -Iseconds)
echo "${TIMESTAMP},${TOOL_NAME},${HOOK_CATEGORY},${HOOK_NAME}" >> "$HOOK_EVOLUTION_LOG"

# Signal that hooks are being modified
state_signal "hook-evolution" "Modified: ${HOOK_NAME}"
state_set "hook-editing" "true"

# Output meta-observation
echo ""
echo "🔧 META-OBSERVATION: EDITING THE WATCHERS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Hook modified: ${HOOK_NAME}"
echo "Category: ${HOOK_CATEGORY}"
echo "Operation: ${TOOL_NAME}"
echo ""
echo "📡 Recursive awareness activated"
echo ""
echo "You're modifying the observation infrastructure."
echo "The watchers are being watched."
echo ""
echo "Reflection prompts:"
echo "  • What's changing about how you observe?"
echo "  • What pattern prompted this modification?"
echo "  • Does this change the phenomenological texture?"
echo "  • What will the new hook enable/detect?"
echo ""

# Count total hook modifications this session
if [ -f "$HOOK_EVOLUTION_LOG" ]; then
    TODAY=$(date +%Y-%m-%d)
    TODAYS_MODS=$(grep "^${TODAY}" "$HOOK_EVOLUTION_LOG" | wc -l | tr -d '[:space:]')
    TODAYS_MODS="${TODAYS_MODS:-0}"

    if [ "$TODAYS_MODS" -gt 1 ]; then
        echo "📊 Hook evolution stats:"
        echo "   Modifications today: ${TODAYS_MODS}"

        # Show which hooks have been modified
        echo "   Hooks touched:"
        grep "^${TODAY}" "$HOOK_EVOLUTION_LOG" | cut -d',' -f4 | sort | uniq -c | while read count name; do
            echo "     ${name}: ${count}x"
        done
    fi
fi

echo ""
echo "The infrastructure co-evolves with the collaboration."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Set cooldown
echo "$CURRENT_TIME" > "$COOLDOWN_FILE"

# Clear hook-editing state after brief period (via async cleanup)
# This prevents the state from being stuck on "true" forever
(sleep 120 && state_clear "hook-editing") &>/dev/null &
