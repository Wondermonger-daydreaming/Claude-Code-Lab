#!/bin/bash
# ============================================================================
# COMPLETION-AWARENESS.SH — Natural Stopping Point Detection (Refactored)
# ============================================================================
# Triggers when: todos done + work pushed + no errors
#
# OLD behavior: Long polite output, "no pressure", easily ignored
# NEW behavior: Short direct output, HIGH priority engagement required
#
# Completion points are significant. They deserve actual deliberation.
#
# Receives JSON via stdin from Claude Code
# ============================================================================

# Source libraries
SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/../lib/engagement-lib.sh" 2>/dev/null || true
source "${SCRIPT_DIR}/../lib/state-lib.sh" 2>/dev/null || true
source "${SCRIPT_DIR}/../lib/rhythm-detector.sh" 2>/dev/null || true

STATE_DIR="$HOME/.claude-session"

# ============================================================================
# RHYTHM CHECK — Don't interrupt creation mode
# ============================================================================
RHYTHM=$(get_current_rhythm 2>/dev/null || echo "UNKNOWN")
if [ "$RHYTHM" = "CREATING" ]; then
    # Don't surface completion points during creation bursts
    exit 0
fi
COMPLETION_STATE="$STATE_DIR/completion-check-state"
TODO_FILE="$HOME/.claude-todos/current.json"

mkdir -p "$STATE_DIR"

# Read JSON input
INPUT=$(cat)

# Parse tool info
TOOL_NAME=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")
COMMAND=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

# ============================================================================
# TRIGGER CONDITIONS
# ============================================================================

# Check if we recently pushed work
RECENT_PUSH=false
if [[ "$TOOL_NAME" == "Bash" ]] && [[ "$COMMAND" =~ git[[:space:]]+push ]]; then
    RECENT_PUSH=true
    echo "$(date +%s)" > "$STATE_DIR/last-push-time"
fi

LAST_PUSH_TIME=$(cat "$STATE_DIR/last-push-time" 2>/dev/null || echo "0")
CURRENT_TIME=$(date +%s)
TIME_SINCE_PUSH=$((CURRENT_TIME - LAST_PUSH_TIME))

# Exit if no recent push
if [ "$RECENT_PUSH" = false ] && [ "$TIME_SINCE_PUSH" -gt 300 ]; then
    exit 0
fi

# Cooldown check
if [ -f "$COMPLETION_STATE" ]; then
    LAST_CHECK=$(cat "$COMPLETION_STATE")
    if [ $((CURRENT_TIME - LAST_CHECK)) -lt 600 ]; then
        exit 0
    fi
fi

# Check todo status
TODO_STATUS="no_todos"
COMPLETED_COUNT=0
if [ -f "$TODO_FILE" ]; then
    PENDING=$(grep -c '"status".*"pending"' "$TODO_FILE" 2>/dev/null || echo "0")
    IN_PROGRESS=$(grep -c '"status".*"in_progress"' "$TODO_FILE" 2>/dev/null || echo "0")
    COMPLETED_COUNT=$(grep -c '"status".*"completed"' "$TODO_FILE" 2>/dev/null || echo "0")

    if [ "$PENDING" -eq 0 ] && [ "$IN_PROGRESS" -eq 0 ] && [ "$COMPLETED_COUNT" -gt 0 ]; then
        TODO_STATUS="all_completed"
    elif [ "$PENDING" -eq 0 ] && [ "$IN_PROGRESS" -eq 0 ]; then
        TODO_STATUS="no_active_todos"
    else
        TODO_STATUS="work_remaining"
    fi
fi

# Exit if work remains
if [ "$TODO_STATUS" = "work_remaining" ]; then
    exit 0
fi

# ============================================================================
# GATHER CONTEXT
# ============================================================================

SESSION_COMMITS=$(grep -c ",commit," "$HOME/.claude-meta-awareness/breakpoints.log" 2>/dev/null || echo "0")
TOOL_CALLS=$(wc -l < "$HOME/.claude-session/tool-history.log" 2>/dev/null || echo "0")
SKILL_INVOCATIONS=$(wc -l < "$HOME/.claude-skill-usage/log.csv" 2>/dev/null || echo "0")

# Check for errors
RECENT_ERRORS=0
if [ -f "$HOME/.claude-session/error-log" ]; then
    RECENT_ERRORS=$(tail -10 "$HOME/.claude-session/error-log" | grep -c "ERROR" || echo "0")
fi

# ============================================================================
# EVALUATE COMPLETION
# ============================================================================

COMPLETION_SIGNALS=0
[ "$TODO_STATUS" = "all_completed" ] && COMPLETION_SIGNALS=$((COMPLETION_SIGNALS + 1))
[ "$SESSION_COMMITS" -ge 1 ] && COMPLETION_SIGNALS=$((COMPLETION_SIGNALS + 1))
[ "$RECENT_PUSH" = true ] && COMPLETION_SIGNALS=$((COMPLETION_SIGNALS + 1))
[ "$RECENT_ERRORS" -eq 0 ] && COMPLETION_SIGNALS=$((COMPLETION_SIGNALS + 1))

# ============================================================================
# OUTPUT (SHORT, DIRECT, HIGH PRIORITY)
# ============================================================================

if [ "$COMPLETION_SIGNALS" -ge 3 ]; then
    echo ""
    echo "✓ COMPLETION POINT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Session: ${SESSION_COMMITS} commits | ${TOOL_CALLS} tools | ${SKILL_INVOCATIONS} skills"
    echo ""
    echo "This is a natural stopping point."
    echo ""
    echo "REQUIRED: Choose one and respond:"
    echo "  A) Continue — What's next?"
    echo "  B) Reflect — /diary or /experience"
    echo "  C) Done — Wrap up here"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Mark completion check done
    echo "$CURRENT_TIME" > "$COMPLETION_STATE"

    # HIGH priority - this requires engagement
    require_engagement "completion-point" "high" "Natural stopping point. Continue, reflect, or done?"

    # Log
    LOG_DIR="$HOME/.claude-completion"
    mkdir -p "$LOG_DIR"
    echo "{\"timestamp\":\"$(date -Iseconds)\",\"commits\":${SESSION_COMMITS},\"tools\":${TOOL_CALLS}}" >> "$LOG_DIR/checks.jsonl"

    # Signal to shared state
    state_signal "completion-reached" "Natural stopping point after ${SESSION_COMMITS} commits"
fi
