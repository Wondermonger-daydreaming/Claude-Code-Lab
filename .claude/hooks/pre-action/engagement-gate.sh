#!/bin/bash
# ============================================================================
# ENGAGEMENT-GATE.SH — PreToolUse Hook That Enforces Engagement
# ============================================================================
# This hook fires BEFORE tool execution and checks if there are pending
# engagements that have been ignored. If too many reflections have been
# skipped, it outputs a JSON-formatted escalation that Claude Code will
# inject into Claude's context.
#
# Output format: JSON with permissionDecision and permissionDecisionReason
# to ensure visibility in Claude's context (not just verbose mode).
#
# Trigger: PreToolUse (all tools)
# ============================================================================

# Source engagement library
SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/../lib/engagement-lib.sh" 2>/dev/null || exit 0

# Read JSON from stdin (required by Claude Code hooks)
INPUT=$(cat)

# Don't check engagement on every single tool call - that would be too noisy
# Only check periodically (every 5th call) or if there are high-priority pending
CALL_COUNTER="${HOME}/.claude-session/engagement-check-counter"
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

    # Output JSON format that Claude Code will parse and inject into context
    # Using permissionDecision: "allow" with reason ensures message is seen
    # but doesn't block the tool execution
    cat << JSONEOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "${REASON}"
  }
}
JSONEOF
fi
