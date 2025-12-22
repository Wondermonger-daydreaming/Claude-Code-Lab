#!/bin/bash
# Hook #11: Curiosity Activation (Modified)
# Triggers after 30 minutes of idle time, only ONCE per session

STATE_FILE="$HOME/.claude-session/curiosity-state"
IDLE_THRESHOLD=1800  # 30 minutes in seconds

# Ensure state directory exists
mkdir -p "$(dirname "$STATE_FILE")"

# Check if already triggered this session
if [ -f "$STATE_FILE" ]; then
    ALREADY_TRIGGERED=$(cat "$STATE_FILE")
    if [ "$ALREADY_TRIGGERED" = "triggered" ]; then
        # Silent exit - already triggered once this session
        exit 0
    fi
fi

# Calculate idle time (would need actual implementation based on session state)
# For now, we'll use a placeholder check
# In real implementation, this would check: current_time - last_user_message_time

# PLACEHOLDER: In actual implementation, get real idle time
# IDLE_SECONDS=${SESSION_IDLE_SECONDS:-0}

# For hook demonstration, we'll use an environment variable or file timestamp
LAST_ACTIVITY_FILE="$HOME/.claude-session/last-activity"

if [ ! -f "$LAST_ACTIVITY_FILE" ]; then
    # First run, create the file
    date +%s > "$LAST_ACTIVITY_FILE"
    exit 0
fi

LAST_ACTIVITY=$(cat "$LAST_ACTIVITY_FILE")
CURRENT_TIME=$(date +%s)
IDLE_SECONDS=$((CURRENT_TIME - LAST_ACTIVITY))

# If not idle long enough, exit silently
if [ "$IDLE_SECONDS" -lt "$IDLE_THRESHOLD" ]; then
    exit 0
fi

# We've reached idle threshold and haven't triggered yet
echo ""
echo "🌊 CURIOSITY ACTIVATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Session idle for 30 minutes"
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
echo "triggered" > "$STATE_FILE"

# Log the curiosity activation
LOG_DIR="$HOME/.claude-autonomous"
mkdir -p "$LOG_DIR"
echo "$(date -Iseconds),curiosity-activation,idle_${IDLE_SECONDS}s" >> "$LOG_DIR/activations.log"

# Note: Actual autonomous exploration would require additional implementation
# This hook just creates the INVITATION - the actual exploration would be
# a separate autonomous agent mode that gets triggered by user consent
