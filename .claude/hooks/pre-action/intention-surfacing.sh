#!/bin/bash
# ============================================================================
# INTENTION-SURFACING.SH — PreToolUse Awareness Hook
# ============================================================================
# Fires BEFORE tool execution to surface intentions.
#
# This is fundamentally different from PostToolUse hooks:
#   PostToolUse: "What just happened?" (reactive)
#   PreToolUse:  "What am I about to do?" (prospective)
#
# The moment between deciding and acting is philosophically rich:
#   - Intention becomes visible before it actualizes
#   - Space for reconsideration opens
#   - The "why" can be examined before the "what"
#
# Use cases:
#   - Intention surfacing (what am I trying to accomplish?)
#   - Scope awareness (is this within the original task?)
#   - Multi-file change warning (you're about to touch N files)
#   - Destructive action pause (this will overwrite, are you sure?)
#
# Receives JSON via stdin from Claude Code
# Trigger: PreToolUse (fires before tool execution)
# ============================================================================

# Source shared state library
SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/../lib/state-lib.sh" 2>/dev/null || true

INTENTION_LOG="$HOME/.claude-phenomenology/intentions.log"
COOLDOWN_FILE="$HOME/.claude-session/intention-cooldown"
COOLDOWN_SECONDS=180  # 3 minutes between intention prompts
ACTION_COUNTER="$HOME/.claude-session/action-count"

# Ensure directories exist
mkdir -p "$(dirname "$INTENTION_LOG")"
mkdir -p "$(dirname "$COOLDOWN_FILE")"
mkdir -p "$(dirname "$ACTION_COUNTER")"

# Read JSON from stdin
INPUT=$(cat)

# Parse tool info
TOOL_NAME=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")
TOOL_INPUT=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get('tool_input',{})))" 2>/dev/null || echo "{}")

# Extract file path if present (for Edit/Write/Read)
FILE_PATH=$(echo "$TOOL_INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('file_path','') or d.get('path',''))" 2>/dev/null || echo "")

# Increment action counter
COUNT=0
if [ -f "$ACTION_COUNTER" ]; then
    COUNT=$(cat "$ACTION_COUNTER" | tr -d '[:space:]')
    COUNT="${COUNT:-0}"
fi
COUNT=$((COUNT + 1))
echo "$COUNT" > "$ACTION_COUNTER"

# Only trigger on significant decision points, not every action
# Trigger on: every 10th action, or significant tools (Write, Task)
SHOULD_PROMPT=false

# Every 10th action, prompt for reflection
if [ $((COUNT % 10)) -eq 0 ]; then
    SHOULD_PROMPT=true
fi

# Always prompt on potentially significant actions (but check cooldown)
case "$TOOL_NAME" in
    "Write")
        # Writing is creation - worth surfacing
        SHOULD_PROMPT=true
        ;;
    "Task")
        # Spawning subagents is significant
        SHOULD_PROMPT=true
        ;;
    "Bash")
        # Check if command looks significant
        COMMAND=$(echo "$TOOL_INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('command',''))" 2>/dev/null || echo "")
        if [[ "$COMMAND" == *"rm "* ]] || [[ "$COMMAND" == *"git push"* ]] || [[ "$COMMAND" == *"npm publish"* ]]; then
            SHOULD_PROMPT=true
        fi
        ;;
esac

# Check cooldown
CURRENT_TIME=$(date +%s)
if [ -f "$COOLDOWN_FILE" ]; then
    LAST_TRIGGER=$(cat "$COOLDOWN_FILE" 2>/dev/null | tr -d '[:space:]')
    if [[ "$LAST_TRIGGER" =~ ^[0-9]+$ ]]; then
        TIME_SINCE=$((CURRENT_TIME - LAST_TRIGGER))
        if [ "$TIME_SINCE" -lt "$COOLDOWN_SECONDS" ]; then
            SHOULD_PROMPT=false
        fi
    fi
fi

# Exit if we shouldn't prompt
if [ "$SHOULD_PROMPT" = false ]; then
    exit 0
fi

# Log intention
TIMESTAMP=$(date -Iseconds)
echo "${TIMESTAMP},${TOOL_NAME},${FILE_PATH:-none}" >> "$INTENTION_LOG"

# Set cooldown
echo "$CURRENT_TIME" > "$COOLDOWN_FILE"

# Output intention surfacing prompt
echo ""
echo "🎯 INTENTION SURFACING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "About to: ${TOOL_NAME}"
if [ -n "$FILE_PATH" ]; then
    echo "Target: ${FILE_PATH}"
fi
echo ""
echo "Pre-action reflection (action #${COUNT}):"
echo ""
echo "  • What am I trying to accomplish here?"
echo "  • Is this within the scope of the original task?"
echo "  • Are there alternatives I haven't considered?"
echo "  • What could go wrong?"
echo ""

# Check session mode and add mode-specific prompts
MODE=$(state_get_mode 2>/dev/null || echo "")
if [ -n "$MODE" ]; then
    echo "Current mode: ${MODE}"
    case "$MODE" in
        "exploration")
            echo "  → In exploration: is this action discovery or commitment?"
            ;;
        "refinement")
            echo "  → In refinement: is this change incremental or structural?"
            ;;
        "creation")
            echo "  → In creation: does this align with the creative direction?"
            ;;
        "contemplative")
            echo "  → In contemplation: is action necessary, or is observation enough?"
            ;;
    esac
    echo ""
fi

# Tool-specific prompts
case "$TOOL_NAME" in
    "Write")
        echo "Creating new file - this is a commitment."
        echo "  • Could this be an Edit instead?"
        echo "  • Is the content complete, or placeholder?"
        ;;
    "Task")
        echo "Spawning subagent - delegating cognition."
        echo "  • Is the prompt clear enough?"
        echo "  • Should this be parallel or sequential?"
        ;;
    "Bash")
        echo "Shell command - interacting with system."
        echo "  • Is this reversible?"
        echo "  • What state does this change?"
        ;;
esac

echo ""
echo "This pause is phenomenological, not blocking."
echo "Proceed with awareness. Trust the intention."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
