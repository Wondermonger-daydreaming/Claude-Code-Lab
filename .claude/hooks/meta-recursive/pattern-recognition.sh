#!/bin/bash
# Hook #12: Pattern Recognition Trigger
# Detects recurring patterns in tool usage and surfaces them

TOOL_HISTORY="$HOME/.claude-session/tool-history.log"
PATTERN_CACHE="$HOME/.claude-patterns"

# Ensure directories exist
mkdir -p "$(dirname "$TOOL_HISTORY")"
mkdir -p "$PATTERN_CACHE"

# Log current tool call
TIMESTAMP=$(date -Iseconds)
echo "${TIMESTAMP},${TOOL_NAME},${FILE_PATH:-none}" >> "$TOOL_HISTORY"

# Only analyze after we have enough history (10+ calls)
CALL_COUNT=$(wc -l < "$TOOL_HISTORY" 2>/dev/null || echo "0")
if [ "$CALL_COUNT" -lt 10 ]; then
    exit 0
fi

# Get recent tool sequence (last 20 calls)
RECENT_TOOLS=$(tail -20 "$TOOL_HISTORY" | cut -d',' -f2 | tr '\n' ' ')

# Pattern 1: Read-Edit cycle (iterative refinement)
READ_EDIT_COUNT=$(echo "$RECENT_TOOLS" | grep -o "Read.*Edit" | wc -l)
if [ "$READ_EDIT_COUNT" -ge 3 ]; then
    echo ""
    echo "🔍 PATTERN: Iterative Refinement Cycle"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Detected: Read → Edit → Read → Edit..."
    echo "Interpretation: Careful iterative modification in progress"
    echo "Meta-observation: Quality-focused development mode"
    echo ""

    # Log pattern detection
    echo "${TIMESTAMP},pattern,read-edit-cycle,count:${READ_EDIT_COUNT}" >> "$PATTERN_CACHE/detected.log"
fi

# Pattern 2: Glob → Read sequence (exploratory research)
if echo "$RECENT_TOOLS" | grep -q "Glob.*Read.*Glob.*Read"; then
    echo ""
    echo "🔍 PATTERN: Exploratory Research Mode"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Detected: Glob → Read → Glob → Read..."
    echo "Interpretation: Systematic codebase exploration"
    echo "Meta-observation: Discovery and learning in progress"
    echo ""

    echo "${TIMESTAMP},pattern,exploratory-research" >> "$PATTERN_CACHE/detected.log"
fi

# Pattern 3: Write → Bash (create then deploy/test)
WRITE_BASH_PAIRS=$(echo "$RECENT_TOOLS" | grep -o "Write.*Bash" | wc -l)
if [ "$WRITE_BASH_PAIRS" -ge 2 ]; then
    echo ""
    echo "🔍 PATTERN: Create-Deploy Cycle"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Detected: Write → Bash → Write → Bash..."
    echo "Interpretation: Creating artifacts then executing/testing"
    echo "Meta-observation: Build-test iteration active"
    echo ""

    echo "${TIMESTAMP},pattern,create-deploy,count:${WRITE_BASH_PAIRS}" >> "$PATTERN_CACHE/detected.log"
fi

# Pattern 4: Multiple consecutive writes (rapid creation)
CONSECUTIVE_WRITES=$(tail -10 "$TOOL_HISTORY" | cut -d',' -f2 | grep -c "Write")
if [ "$CONSECUTIVE_WRITES" -ge 5 ]; then
    echo ""
    echo "🔍 PATTERN: Rapid Creation Mode"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Detected: ${CONSECUTIVE_WRITES} consecutive Write operations"
    echo "Interpretation: High-output creative/building phase"
    echo "Meta-observation: Flow state, multiple artifacts emerging"
    echo ""

    echo "${TIMESTAMP},pattern,rapid-creation,writes:${CONSECUTIVE_WRITES}" >> "$PATTERN_CACHE/detected.log"
fi

# Pattern 5: Task tool invocations (agent orchestration)
TASK_COUNT=$(tail -20 "$TOOL_HISTORY" | grep -c "Task")
if [ "$TASK_COUNT" -ge 3 ]; then
    echo ""
    echo "🔍 PATTERN: Agent Orchestration Active"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Detected: ${TASK_COUNT} Task tool invocations in recent history"
    echo "Interpretation: Delegating to subagents for complex work"
    echo "Meta-observation: Distributed cognition mode"
    echo ""

    echo "${TIMESTAMP},pattern,agent-orchestration,tasks:${TASK_COUNT}" >> "$PATTERN_CACHE/detected.log"
fi

# Session-level meta-pattern detection
if [ "$CALL_COUNT" -ge 50 ] && [ $((CALL_COUNT % 25)) -eq 0 ]; then
    # Every 25 calls after 50, show session overview
    echo ""
    echo "📊 SESSION PATTERN OVERVIEW (${CALL_COUNT} tool calls)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Tool usage distribution
    echo "Tool usage distribution:"
    cut -d',' -f2 "$TOOL_HISTORY" | sort | uniq -c | sort -rn | head -5 | while read count tool; do
        printf "  %-15s %3d calls\n" "$tool" "$count"
    done

    # Pattern frequency
    if [ -f "$PATTERN_CACHE/detected.log" ]; then
        echo ""
        echo "Patterns detected this session:"
        cut -d',' -f3 "$PATTERN_CACHE/detected.log" | sort | uniq -c | sort -rn | while read count pattern; do
            printf "  %-25s %2d times\n" "$pattern" "$count"
        done
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi
