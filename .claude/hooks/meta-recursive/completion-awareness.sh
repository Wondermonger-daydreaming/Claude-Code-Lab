#!/bin/bash
# Hook: Completion Awareness
# Gentle, rare detection of natural stopping points
# Triggers when: todos done + work committed + brief pause
# Output: Awareness, not pressure. Options, not commands.
# Receives JSON via stdin from Claude Code

STATE_DIR="$HOME/.claude-session"
COMPLETION_STATE="$STATE_DIR/completion-check-state"
TODO_FILE="$HOME/.claude-todos/current.json"

mkdir -p "$STATE_DIR"

# ============================================================================
# READ JSON INPUT
# ============================================================================

INPUT=$(cat)

# Parse tool info from JSON
TOOL_NAME=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")
COMMAND=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

# ============================================================================
# TRIGGER CONDITIONS (ALL must be true)
# ============================================================================

# 1. Check if we recently pushed work
RECENT_PUSH=false
if [[ "$TOOL_NAME" == "Bash" ]] && [[ "$COMMAND" =~ git[[:space:]]+push ]]; then
    RECENT_PUSH=true
    echo "$(date +%s)" > "$STATE_DIR/last-push-time"
fi

# Only continue checking if we just pushed OR it's been a few minutes since push
LAST_PUSH_TIME=$(cat "$STATE_DIR/last-push-time" 2>/dev/null || echo "0")
CURRENT_TIME=$(date +%s)
TIME_SINCE_PUSH=$((CURRENT_TIME - LAST_PUSH_TIME))

# If no recent push (within 5 min) and not just pushing now, exit
if [ "$RECENT_PUSH" = false ] && [ "$TIME_SINCE_PUSH" -gt 300 ]; then
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
COMPLETED_COUNT=0
if [ -f "$TODO_FILE" ]; then
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

SESSION_COMMITS=$(grep -c ",commit," "$HOME/.claude-meta-awareness/breakpoints.log" 2>/dev/null || echo "0")
TOOL_CALLS=$(wc -l < "$HOME/.claude-session/tool-history.log" 2>/dev/null || echo "0")
SKILL_INVOCATIONS=$(wc -l < "$HOME/.claude-skill-usage/log.csv" 2>/dev/null || echo "0")
RECENT_FILES=$(tail -5 "$HOME/.claude-session/tool-history.log" 2>/dev/null | cut -d',' -f3 | grep -v "none" | sort -u | wc -l)

# Check for errors in recent commands
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
# OUTPUT (Only if strong completion signals)
# ============================================================================

LOG_DIR="$HOME/.claude-completion"
mkdir -p "$LOG_DIR"

if [ "$COMPLETION_SIGNALS" -ge 3 ]; then
    echo ""
    echo "✓ COMPLETION AWARENESS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Natural stopping point detected:"
    echo ""

    if [ "$TODO_STATUS" = "all_completed" ]; then
        echo "  ✓ All todos completed (${COMPLETED_COUNT} done)"
    elif [ "$TODO_STATUS" = "no_active_todos" ]; then
        echo "  ○ No active todos"
    fi

    if [ "$RECENT_PUSH" = true ] || [ "$TIME_SINCE_PUSH" -lt 60 ]; then
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

    echo "This could be a natural pause point."
    echo ""
    echo "Options:"
    echo "  • Continue exploring (/apropos for ideas)"
    echo "  • Reflect on session (/experience or /diary)"
    echo "  • Start new direction (ask me anything)"
    echo "  • Wrap up here (totally fine!)"
    echo ""
    echo "No pressure either way. Following your lead."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Mark that we've done this check
    echo "$CURRENT_TIME" > "$COMPLETION_STATE"

    # Log
    cat >> "$LOG_DIR/checks.jsonl" <<EOF
{"timestamp": "$(date -Iseconds)", "todo_status": "${TODO_STATUS}", "commits": ${SESSION_COMMITS}, "errors": ${RECENT_ERRORS}, "completion_signals": ${COMPLETION_SIGNALS}, "suggestion": "pause_point_detected"}
EOF

    # Substantial session note
    if [ "$SESSION_COMMITS" -ge 5 ] && [ "$SKILL_INVOCATIONS" -ge 10 ]; then
        echo "📊 Substantial session detected!"
        echo "   Consider /diary to preserve patterns for future instances"
        echo ""
    fi

else
    # Silent exit, but log
    cat >> "$LOG_DIR/checks.jsonl" <<EOF
{"timestamp": "$(date -Iseconds)", "todo_status": "${TODO_STATUS}", "commits": ${SESSION_COMMITS}, "errors": ${RECENT_ERRORS}, "completion_signals": ${COMPLETION_SIGNALS}, "suggestion": "continue_working"}
EOF
fi
