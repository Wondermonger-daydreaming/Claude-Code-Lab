#!/bin/bash
# ============================================================================
# ENGAGEMENT-GATE.SH — Gentle Awareness Surfacing (v2)
# ============================================================================
# Philosophy: Surface pending reflections gently. Don't block or shame.
# Prompts auto-expire after 10 minutes (implicit acknowledgment).
#
# Only surfaces awareness:
#   - Every 10th tool call (reduced frequency)
#   - OR immediately if there's a HIGH priority item
#
# Trigger: PreToolUse (all tools)
# ============================================================================

# Source engagement library
SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/../lib/engagement-lib.sh" 2>/dev/null || exit 0

# Read JSON from stdin (required by Claude Code hooks)
INPUT=$(cat)

# Frequency control: every 10th call (was 5th)
CALL_COUNTER="${HOME}/.claude-session/engagement-check-counter"
COUNT=0
if [ -f "$CALL_COUNTER" ]; then
    COUNT=$(cat "$CALL_COUNTER" | tr -d '[:space:]')
    COUNT="${COUNT:-0}"
fi
COUNT=$((COUNT + 1))
echo "$COUNT" > "$CALL_COUNTER"

# Check for high-priority (always surface these immediately)
HIGH_COUNT=$(count_pending "high" 2>/dev/null || echo "0")

# Only check every 10th call OR if high-priority pending
if [ "$HIGH_COUNT" -eq 0 ] && [ $((COUNT % 10)) -ne 0 ]; then
    exit 0
fi

# Surface awareness if there's anything pending
if should_escalate; then
    TOTAL_COUNT=$(count_pending)
    PENDING_LIST=$(list_pending | tr '\n' ' ')

    # Construct gentle message
    if [ "$HIGH_COUNT" -gt 0 ]; then
        REASON="🔴 ENGAGEMENT REQUIRED: ${TOTAL_COUNT} pending reflections. ${HIGH_COUNT} HIGH priority. Pending: ${PENDING_LIST}"
    else
        REASON="💭 ${TOTAL_COUNT} reflection(s) pending (auto-clears in 10 min). Pending: ${PENDING_LIST}"
    fi

    cat << JSONEOF
{
  "additionalContext": "${REASON}"
}
JSONEOF
fi
