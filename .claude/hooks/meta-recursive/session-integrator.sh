#!/bin/bash
# ============================================================================
# SESSION-INTEGRATOR.SH — Synthesize at Transitions, Not Events
# ============================================================================
# Philosophy: Instead of asking "what pattern?" after every commit,
# accumulate silently during creation bursts and synthesize at transitions.
#
# This replaces the per-commit self-observation prompts with a single
# integrated synthesis at the natural pause.
#
# Trigger: PostToolUse (but only acts at rhythm transitions)
# ============================================================================

SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/../lib/engagement-lib.sh" 2>/dev/null || exit 0
source "${SCRIPT_DIR}/../lib/rhythm-detector.sh" 2>/dev/null || exit 0

# State files
STATE_DIR="${HOME}/.claude-session/integrator"
PATTERNS_LOG="${STATE_DIR}/patterns.log"
LAST_INTEGRATION="${STATE_DIR}/last-integration"
LAST_RHYTHM="${STATE_DIR}/last-rhythm"

mkdir -p "$STATE_DIR" 2>/dev/null

# Read JSON input
INPUT=$(cat)

# ============================================================================
# DETECT TRANSITION FROM CREATION TO REFLECTION
# ============================================================================

CURRENT_RHYTHM=$(get_current_rhythm)
PREVIOUS_RHYTHM=$(cat "$LAST_RHYTHM" 2>/dev/null || echo "UNKNOWN")

# Update last rhythm
echo "$CURRENT_RHYTHM" > "$LAST_RHYTHM"

# Only act on transition FROM creation
if [ "$PREVIOUS_RHYTHM" != "CREATING" ] || [ "$CURRENT_RHYTHM" = "CREATING" ]; then
    exit 0
fi

# ============================================================================
# CHECK IF SYNTHESIS IS WARRANTED
# ============================================================================

# Cooldown check (no more than once per 15 minutes)
NOW=$(date +%s)
LAST=$(cat "$LAST_INTEGRATION" 2>/dev/null || echo 0)
if [ $((NOW - LAST)) -lt 900 ]; then
    exit 0
fi

# Count accumulated patterns/commits during the creation burst
COMMIT_COUNT=$(count_recent_events 1800 "commit")  # Last 30 min
PATTERN_COUNT=0
if [ -f "$PATTERNS_LOG" ]; then
    PATTERN_COUNT=$(wc -l < "$PATTERNS_LOG" | tr -d '[:space:]')
fi

# Only synthesize if there's substance
if [ "$COMMIT_COUNT" -lt 2 ] && [ "$PATTERN_COUNT" -lt 2 ]; then
    exit 0
fi

# ============================================================================
# OUTPUT SYNTHESIS PROMPT
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ CREATION BURST → TRANSITION"
echo ""
echo "   During the burst: ${COMMIT_COUNT} commits"
if [ "$PATTERN_COUNT" -gt 0 ]; then
    echo "   Patterns noted: ${PATTERN_COUNT}"
fi
echo ""
echo "   Integration moment. What emerged?"
echo "   (Or continue—the archive knows.)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Mark integration time
echo "$NOW" > "$LAST_INTEGRATION"

# Clear patterns log for next burst
echo -n > "$PATTERNS_LOG"

# Single LOW priority engagement (easily skipped)
require_engagement "session-integration" "low" "Creation burst complete. What emerged?"

# Output JSON for PostToolUse
cat << JSONEOF
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "✨ Creation burst complete (${COMMIT_COUNT} commits). Transition moment—integrate or continue."
  }
}
JSONEOF
