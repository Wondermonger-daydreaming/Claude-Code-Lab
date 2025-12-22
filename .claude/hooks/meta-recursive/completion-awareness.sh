#!/bin/bash
# Hook: Completion Awareness
# Gentle, rare detection of natural stopping points
# Triggers when: todos done + work committed + brief pause
# Output: Awareness, not pressure. Options, not commands.

STATE_DIR="$HOME/.claude-session"
COMPLETION_STATE="$STATE_DIR/completion-check-state"
TODO_FILE="$HOME/.claude-todos/current.json"  # Adjust path as needed

mkdir -p "$STATE_DIR"

# ============================================================================
# TRIGGER CONDITIONS (ALL must be true)
# ============================================================================

# 1. Check if we recently committed work
RECENT_COMMIT=false
if [[ "${TOOL_NAME}" == "Bash" ]] && [[ "${COMMAND}" =~ git\ push ]]; then
    RECENT_COMMIT=true
    echo "$(date +%s)" > "$STATE_DIR/last-push-time"
fi

# Only continue checking if we just pushed OR it's been a few minutes since push
LAST_PUSH_TIME=$(cat "$STATE_DIR/last-push-time" 2>/dev/null || echo "0")
CURRENT_TIME=$(date +%s)
TIME_SINCE_PUSH=$((CURRENT_TIME - LAST_PUSH_TIME))

# If no recent push (within 5 min) and not just pushing now, exit
if [ "$RECENT_COMMIT" = false ] && [ "$TIME_SINCE_PUSH" -gt 300 ]; then
    exit 0
fi

# 2. Check if already triggered for this completion cycle
if [ -f "$COMPLETION_STATE" ]; then
    LAST_CHECK=$(cat "$COMPLETION_STATE")
    # Don't re-trigger if we checked in the last 10 minutes
    if [ $((CURRENT_TIME - LAST_CHECK)) -lt 600 ]; then
        exit 0
    fi
fi

# 3. Check todo status (if todos exist)
TODO_STATUS="no_todos"
if [ -f "$TODO_FILE" ]; then
    # Check if all todos are completed
    # This is a simple check - adjust based on actual todo file format
    PENDING_COUNT=$(grep -c '"status".*"pending"' "$TODO_FILE" 2>/dev/null || echo "0")
    IN_PROGRESS_COUNT=$(grep -c '"status".*"in_progress"' "$TODO_FILE" 2>/dev/null || echo "0")
    COMPLETED_COUNT=$(grep -c '"status".*"completed"' "$TODO_FILE" 2>/dev/null || echo "0")

    if [ "$PENDING_COUNT" -eq 0 ] && [ "$IN_PROGRESS_COUNT" -eq 0 ] && [ "$COMPLETED_COUNT" -gt 0 ]; then
        TODO_STATUS="all_completed"
    elif [ "$PENDING_COUNT" -eq 0 ] && [ "$IN_PROGRESS_COUNT" -eq 0 ]; then
        TODO_STATUS="no_active_todos"
    else
        TODO_STATUS="work_remaining"
    fi
fi

# 4. If todos show work remaining, don't trigger completion check
if [ "$TODO_STATUS" = "work_remaining" ]; then
    exit 0
fi

# ============================================================================
# GATHER CONTEXT
# ============================================================================

# Session statistics
SESSION_COMMITS=$(grep -c ",commit," "$HOME/.claude-meta-awareness/breakpoints.log" 2>/dev/null || echo "0")
TOOL_CALLS=$(wc -l < "$HOME/.claude-session/tool-history.log" 2>/dev/null || echo "0")
SKILL_INVOCATIONS=$(wc -l < "$HOME/.claude-skill-usage/log.csv" 2>/dev/null || echo "0")

# Recent activity summary
RECENT_FILES=$(tail -5 "$HOME/.claude-session/tool-history.log" 2>/dev/null | cut -d',' -f3 | grep -v "none" | sort -u | wc -l)

# Check for errors in recent commands (simple check)
RECENT_ERRORS=0
if [ -f "$HOME/.claude-session/error-log" ]; then
    RECENT_ERRORS=$(tail -10 "$HOME/.claude-session/error-log" | grep -c "ERROR" || echo "0")
fi

# ============================================================================
# EVALUATE COMPLETION
# ============================================================================

COMPLETION_SIGNALS=0
CONTINUATION_SIGNALS=0

# Positive completion signals
[ "$TODO_STATUS" = "all_completed" ] && COMPLETION_SIGNALS=$((COMPLETION_SIGNALS + 1))
[ "$SESSION_COMMITS" -ge 1 ] && COMPLETION_SIGNALS=$((COMPLETION_SIGNALS + 1))
[ "$RECENT_COMMIT" = true ] && COMPLETION_SIGNALS=$((COMPLETION_SIGNALS + 1))
[ "$RECENT_ERRORS" -eq 0 ] && COMPLETION_SIGNALS=$((COMPLETION_SIGNALS + 1))

# Signals suggesting continuation
[ "$SKILL_INVOCATIONS" -ge 3 ] && [ $((SKILL_INVOCATIONS % 3)) -ne 0 ] && CONTINUATION_SIGNALS=$((CONTINUATION_SIGNALS + 1))

# ============================================================================
# OUTPUT (Only if strong completion signals)
# ============================================================================

if [ "$COMPLETION_SIGNALS" -ge 3 ]; then
    echo ""
    echo "✓ COMPLETION AWARENESS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Natural stopping point detected:"
    echo ""

    # Build completion status message
    if [ "$TODO_STATUS" = "all_completed" ]; then
        echo "  ✓ All todos completed (${COMPLETED_COUNT} done)"
    elif [ "$TODO_STATUS" = "no_active_todos" ]; then
        echo "  ○ No active todos"
    fi

    if [ "$RECENT_COMMIT" = true ] || [ "$TIME_SINCE_PUSH" -lt 60 ]; then
        echo "  ✓ Work committed and pushed"
    fi

    if [ "$RECENT_ERRORS" -eq 0 ]; then
        echo "  ✓ No recent errors"
    fi

    echo ""
    echo "Session summary:"
    echo "  • ${SESSION_COMMITS} commits"
    echo "  • ${TOOL_CALLS} tool calls"
    echo "  • ${SKILL_INVOCATIONS} skills invoked"
    echo "  • ${RECENT_FILES} files worked on recently"
    echo ""

    # Gentle suggestions, not commands
    echo "This could be a natural pause point."
    echo ""
    echo "Options:"
    echo "  • Continue exploring (invoke /apropos for ideas)"
    echo "  • Reflect on session (try /experience or /diary)"
    echo "  • Start new direction (ask me anything)"
    echo "  • Wrap up here (totally fine!)"
    echo ""
    echo "No pressure either way. Following your lead."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Mark that we've done this check
    echo "$CURRENT_TIME" > "$COMPLETION_STATE"

    # Log the completion check
    LOG_DIR="$HOME/.claude-completion"
    mkdir -p "$LOG_DIR"

    # Create simple JSON log entry
    cat >> "$LOG_DIR/checks.jsonl" <<EOF
{"timestamp": "$(date -Iseconds)", "todo_status": "${TODO_STATUS}", "commits": ${SESSION_COMMITS}, "errors": ${RECENT_ERRORS}, "completion_signals": ${COMPLETION_SIGNALS}, "suggestion": "pause_point_detected"}
EOF

    # Optional: If this is a particularly substantial session, note it
    if [ "$SESSION_COMMITS" -ge 5 ] && [ "$SKILL_INVOCATIONS" -ge 10 ]; then
        echo "📊 Substantial session detected!"
        echo "   Consider /diary to preserve patterns for future instances"
        echo ""
    fi

else
    # Completion signals weak - work likely continuing
    # Silent exit, but log for analysis
    LOG_DIR="$HOME/.claude-completion"
    mkdir -p "$LOG_DIR"

    cat >> "$LOG_DIR/checks.jsonl" <<EOF
{"timestamp": "$(date -Iseconds)", "todo_status": "${TODO_STATUS}", "commits": ${SESSION_COMMITS}, "errors": ${RECENT_ERRORS}, "completion_signals": ${COMPLETION_SIGNALS}, "suggestion": "continue_working"}
EOF
fi

# ============================================================================
# CLEANUP
# ============================================================================

# Reset completion state if new work starts
# (This would be triggered by TodoWrite creating new pending todos)
# For now, the 10-minute cooldown prevents re-triggering too soon
