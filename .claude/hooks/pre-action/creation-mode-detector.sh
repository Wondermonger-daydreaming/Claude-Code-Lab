#!/bin/bash
# ============================================================================
# CREATION-MODE-DETECTOR.SH — Detect User Signals for Creation Flow
# ============================================================================
# Listens to UserPromptSubmit events and detects signals like:
#   - "keep going", "keep exploring", "carte blanche"
#   - "don't stop", "continue creating", "keep at it"
#
# When detected, signals creation mode to the rhythm detector,
# which suppresses non-critical hooks for 30 minutes.
#
# Trigger: UserPromptSubmit
# ============================================================================

SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/../lib/rhythm-detector.sh" 2>/dev/null || exit 0

# Read JSON input
INPUT=$(cat)

# Extract user message content
USER_MESSAGE=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    # Try different possible locations for user message
    msg = d.get('user_message', d.get('prompt', d.get('content', '')))
    if isinstance(msg, dict):
        msg = msg.get('content', '')
    print(msg.lower())
except:
    print('')
" 2>/dev/null || echo "")

# If we couldn't get the message, exit
if [ -z "$USER_MESSAGE" ]; then
    exit 0
fi

# ============================================================================
# CREATION MODE SIGNAL PATTERNS
# ============================================================================

CREATION_SIGNALS=(
    "keep going"
    "keep exploring"
    "keep creating"
    "carte blanche"
    "don't stop"
    "dont stop"
    "continue exploring"
    "continue creating"
    "keep at it"
    "keep working"
    "don't chill"
    "dont chill"
    "ultrathink"
    "keep moving"
    "full steam"
    "keep the flow"
)

# Check if message contains any creation signal
for signal in "${CREATION_SIGNALS[@]}"; do
    if [[ "$USER_MESSAGE" == *"$signal"* ]]; then
        # Signal detected! Activate creation mode
        signal_creation_mode "$signal"

        # Log for debugging
        mkdir -p "$HOME/.claude-session/rhythm"
        echo "$(date -Iseconds)|detected|$signal" >> "$HOME/.claude-session/rhythm/signals.log"

        # Output confirmation (will appear in context)
        cat << JSONEOF
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "🔥 Creation mode activated (30 min) — hooks will stay quiet"
  }
}
JSONEOF
        exit 0
    fi
done

# No creation signal detected, just log the event
log_event "user_prompt" "" 2>/dev/null || true
