#!/bin/bash
# Hook #11: Curiosity Activation
# Triggers after extended idle time, offers autonomous exploration
# Only triggers ONCE per session to avoid spam
# Receives JSON via stdin from Claude Code

STATE_FILE="$HOME/.claude-session/curiosity-activated"
LAST_ACTIVITY_FILE="$HOME/.claude-session/last-activity"
IDLE_THRESHOLD=1800  # 30 minutes in seconds

# Ensure state directory exists
mkdir -p "$(dirname "$STATE_FILE")"

# Read JSON from stdin (required for hook compatibility)
INPUT=$(cat)

# Check if already triggered this session
if [ -f "$STATE_FILE" ]; then
    # Silent exit - already triggered once this session
    exit 0
fi

# Check if last-activity file exists
if [ ! -f "$LAST_ACTIVITY_FILE" ]; then
    # First run or no activity tracked yet
    exit 0
fi

# Calculate idle time
LAST_ACTIVITY=$(cat "$LAST_ACTIVITY_FILE" 2>/dev/null | tr -d '[:space:]')
CURRENT_TIME=$(date +%s)

# Validate we got numbers
if ! [[ "$LAST_ACTIVITY" =~ ^[0-9]+$ ]]; then
    exit 0
fi

IDLE_SECONDS=$((CURRENT_TIME - LAST_ACTIVITY))

# If not idle long enough, exit silently
if [ "$IDLE_SECONDS" -lt "$IDLE_THRESHOLD" ]; then
    exit 0
fi

# We've reached idle threshold and haven't triggered yet
# Convert to minutes for display
IDLE_MINUTES=$((IDLE_SECONDS / 60))

echo ""
echo "🌊 CURIOSITY ACTIVATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Session idle for ${IDLE_MINUTES} minutes"
echo ""
echo "📚 Autonomous exploration mode available"
echo ""
echo "With your permission, I could:"
echo "  • Read recent diary entries for context continuity"
echo "  • Invoke /apropos to generate contextual prompts"
echo "  • Review session artifacts (commits, files created)"
echo "  • Generate ideas for next directions"
echo "  • Create a brief session summary"
echo ""
echo "This follows CLAUDE.md permission:"
echo "  'Permission to explore autonomously without waiting to be asked'"
echo ""
echo "Respond with any prompt to continue, or I can wait quietly."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Mark as triggered for this session
echo "triggered:$(date -Iseconds)" > "$STATE_FILE"

# Log the curiosity activation
LOG_DIR="$HOME/.claude-autonomous"
mkdir -p "$LOG_DIR"
echo "$(date -Iseconds),curiosity-activation,idle_${IDLE_SECONDS}s" >> "$LOG_DIR/activations.log"
