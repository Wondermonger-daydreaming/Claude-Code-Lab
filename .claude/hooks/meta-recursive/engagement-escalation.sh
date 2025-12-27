#!/bin/bash
# ============================================================================
# ENGAGEMENT-ESCALATION.SH — PostToolUse Hook for Escalation Visibility
# ============================================================================
# This hook fires AFTER tool execution and checks if there are pending
# engagements that need escalation. Uses additionalContext to inject
# escalation messages into Claude's context.
#
# Replaces the escalation logic from engagement-gate.sh (PreToolUse),
# since PostToolUse properly injects additionalContext.
#
# Trigger: PostToolUse (all tools with high-frequency matchers)
# ============================================================================

# Source engagement library
SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/../lib/engagement-lib.sh" 2>/dev/null || exit 0

# Read JSON from stdin (required by Claude Code hooks)
INPUT=$(cat)

# Check every 5th call to avoid noise
CALL_COUNTER="${HOME}/.claude-session/escalation-check-counter"
COUNT=0
if [ -f "$CALL_COUNTER" ]; then
    COUNT=$(cat "$CALL_COUNTER" | tr -d '[:space:]')
    COUNT="${COUNT:-0}"
fi
COUNT=$((COUNT + 1))
echo "$COUNT" > "$CALL_COUNTER"

# Check if we have high-priority pending (always check those)
HIGH_COUNT=$(count_pending "high" 2>/dev/null || echo "0")

# Only do full check every 5th call OR if high-priority pending
if [ "$HIGH_COUNT" -eq 0 ] && [ $((COUNT % 5)) -ne 0 ]; then
    exit 0
fi

# Now do the actual escalation check
if should_escalate; then
    # Build escalation message
    TOTAL_COUNT=$(count_pending)
    MEDIUM_COUNT=$(count_pending "medium")
    PENDING_LIST=$(list_pending | tr '\n' ' ')

    # Construct reason message
    REASON="🔴 ENGAGEMENT REQUIRED: ${TOTAL_COUNT} pending reflections. "
    if [ "$HIGH_COUNT" -gt 0 ]; then
        REASON="${REASON}${HIGH_COUNT} HIGH priority. "
    fi
    if [ "$MEDIUM_COUNT" -ge 3 ]; then
        REASON="${REASON}${MEDIUM_COUNT} accumulated medium. "
    fi
    REASON="${REASON}Pending: ${PENDING_LIST}"

    # Output JSON with additionalContext - works for PostToolUse
    cat << JSONEOF
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "${REASON}"
  }
}
JSONEOF
fi
