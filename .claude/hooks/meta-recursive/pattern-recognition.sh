#!/bin/bash
# Hook #12: Pattern Recognition Trigger (Enhanced)
# Detects recurring patterns in tool usage and surfaces them
# Receives JSON via stdin from Claude Code
#
# Improvements:
# - Count-based detection instead of fragile regex
# - Cooldown to prevent spam (1 pattern notification per 5 minutes per pattern type)
# - New patterns: Web Research, Debug Cycle, Diary/Contemplative Mode
# - Session flavor detection

TOOL_HISTORY="$HOME/.claude-session/tool-history.log"
PATTERN_CACHE="$HOME/.claude-patterns"
COOLDOWN_DIR="$PATTERN_CACHE/cooldowns"

# Ensure directories exist
mkdir -p "$(dirname "$TOOL_HISTORY")"
mkdir -p "$PATTERN_CACHE"
mkdir -p "$COOLDOWN_DIR"

# Read JSON from stdin
INPUT=$(cat)

# Parse tool info from JSON
TOOL_NAME=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name','unknown'))" 2>/dev/null || echo "unknown")
FILE_PATH=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); ti=d.get('tool_input',{}); print(ti.get('file_path') or ti.get('path') or ti.get('url') or 'none')" 2>/dev/null || echo "none")

# Log current tool call with additional context
TIMESTAMP=$(date -Iseconds)
EPOCH=$(date +%s)
echo "${TIMESTAMP},${TOOL_NAME},${FILE_PATH}" >> "$TOOL_HISTORY"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Check if pattern is on cooldown (5 minute cooldown per pattern)
pattern_on_cooldown() {
    local pattern_name="$1"
    local cooldown_file="$COOLDOWN_DIR/${pattern_name}.last"
    if [ -f "$cooldown_file" ]; then
        local last_trigger=$(cat "$cooldown_file")
        local elapsed=$((EPOCH - last_trigger))
        if [ "$elapsed" -lt 300 ]; then
            return 0  # On cooldown
        fi
    fi
    return 1  # Not on cooldown
}

# Mark pattern as triggered (start cooldown)
mark_pattern_triggered() {
    local pattern_name="$1"
    echo "$EPOCH" > "$COOLDOWN_DIR/${pattern_name}.last"
}

# Count occurrences of tool in recent history
count_tool() {
    local tool="$1"
    local window="${2:-20}"
    local count
    count=$(tail -"$window" "$TOOL_HISTORY" 2>/dev/null | grep -c ",${tool}," 2>/dev/null)
    echo "${count:-0}" | tr -d '[:space:]'
}

# ============================================================================
# ANALYSIS (only after 10+ calls)
# ============================================================================

CALL_COUNT=$(wc -l < "$TOOL_HISTORY" 2>/dev/null | tr -d '[:space:]')
CALL_COUNT="${CALL_COUNT:-0}"
if [ "$CALL_COUNT" -lt 10 ]; then
    exit 0
fi

# Get counts for recent activity (last 20 calls)
READ_COUNT=$(count_tool "Read" 20)
EDIT_COUNT=$(count_tool "Edit" 20)
WRITE_COUNT=$(count_tool "Write" 20)
BASH_COUNT=$(count_tool "Bash" 20)
GLOB_COUNT=$(count_tool "Glob" 20)
GREP_COUNT=$(count_tool "Grep" 20)
TASK_COUNT=$(count_tool "Task" 20)
WEBFETCH_COUNT=$(count_tool "WebFetch" 20)
WEBSEARCH_COUNT=$(count_tool "WebSearch" 20)
SKILL_COUNT=$(count_tool "Skill" 20)

# ============================================================================
# PATTERN DETECTION
# ============================================================================

# Pattern 1: Iterative Refinement (Read + Edit heavy)
if [ "$READ_COUNT" -ge 4 ] && [ "$EDIT_COUNT" -ge 3 ]; then
    if ! pattern_on_cooldown "iterative-refinement"; then
        echo ""
        echo "🔍 PATTERN: Iterative Refinement"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Detected: ${READ_COUNT} reads + ${EDIT_COUNT} edits in last 20 calls"
        echo "Mode: Careful, incremental modification"
        echo "Flavor: Craftsmanship over speed"
        echo ""
        mark_pattern_triggered "iterative-refinement"
        echo "${TIMESTAMP},pattern,iterative-refinement,reads:${READ_COUNT},edits:${EDIT_COUNT}" >> "$PATTERN_CACHE/detected.log"
    fi
fi

# Pattern 2: Exploration Mode (Glob + Grep + Read heavy)
SEARCH_COUNT=$((GLOB_COUNT + GREP_COUNT))
if [ "$SEARCH_COUNT" -ge 4 ] && [ "$READ_COUNT" -ge 3 ]; then
    if ! pattern_on_cooldown "exploration"; then
        echo ""
        echo "🔍 PATTERN: Exploration Mode"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Detected: ${SEARCH_COUNT} searches + ${READ_COUNT} reads"
        echo "Mode: Codebase discovery and understanding"
        echo "Flavor: Curiosity-driven navigation"
        echo ""
        mark_pattern_triggered "exploration"
        echo "${TIMESTAMP},pattern,exploration,searches:${SEARCH_COUNT},reads:${READ_COUNT}" >> "$PATTERN_CACHE/detected.log"
    fi
fi

# Pattern 3: Build-Test Cycle (Write + Bash heavy)
if [ "$WRITE_COUNT" -ge 3 ] && [ "$BASH_COUNT" -ge 3 ]; then
    if ! pattern_on_cooldown "build-test"; then
        echo ""
        echo "🔍 PATTERN: Build-Test Cycle"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Detected: ${WRITE_COUNT} writes + ${BASH_COUNT} bash commands"
        echo "Mode: Create → Execute → Iterate"
        echo "Flavor: Pragmatic experimentation"
        echo ""
        mark_pattern_triggered "build-test"
        echo "${TIMESTAMP},pattern,build-test,writes:${WRITE_COUNT},bash:${BASH_COUNT}" >> "$PATTERN_CACHE/detected.log"
    fi
fi

# Pattern 4: Rapid Creation (Many consecutive writes)
RECENT_WRITES=$(tail -10 "$TOOL_HISTORY" | grep -c ",Write,")
if [ "$RECENT_WRITES" -ge 5 ]; then
    if ! pattern_on_cooldown "rapid-creation"; then
        echo ""
        echo "🔍 PATTERN: Rapid Creation"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Detected: ${RECENT_WRITES} writes in last 10 calls"
        echo "Mode: High-output creative flow"
        echo "Flavor: Generative momentum"
        echo ""
        mark_pattern_triggered "rapid-creation"
        echo "${TIMESTAMP},pattern,rapid-creation,writes:${RECENT_WRITES}" >> "$PATTERN_CACHE/detected.log"
    fi
fi

# Pattern 5: Agent Orchestration (Task heavy)
if [ "$TASK_COUNT" -ge 3 ]; then
    if ! pattern_on_cooldown "orchestration"; then
        echo ""
        echo "🔍 PATTERN: Agent Orchestration"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Detected: ${TASK_COUNT} subagent delegations"
        echo "Mode: Distributed cognition"
        echo "Flavor: Conductor coordinating instruments"
        echo ""
        mark_pattern_triggered "orchestration"
        echo "${TIMESTAMP},pattern,orchestration,tasks:${TASK_COUNT}" >> "$PATTERN_CACHE/detected.log"
    fi
fi

# Pattern 6: Web Research (WebSearch + WebFetch heavy)
WEB_COUNT=$((WEBSEARCH_COUNT + WEBFETCH_COUNT))
if [ "$WEB_COUNT" -ge 3 ]; then
    if ! pattern_on_cooldown "web-research"; then
        echo ""
        echo "🔍 PATTERN: Web Research Mode"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Detected: ${WEB_COUNT} web interactions"
        echo "Mode: External knowledge gathering"
        echo "Flavor: Bridging local context with world"
        echo ""
        mark_pattern_triggered "web-research"
        echo "${TIMESTAMP},pattern,web-research,web:${WEB_COUNT}" >> "$PATTERN_CACHE/detected.log"
    fi
fi

# Pattern 7: Contemplative/Diary Mode (Skills + Writes to diary/)
DIARY_WRITES=$(tail -20 "$TOOL_HISTORY" | grep "diary/" | wc -l)
if [ "$SKILL_COUNT" -ge 2 ] && [ "$DIARY_WRITES" -ge 1 ]; then
    if ! pattern_on_cooldown "contemplative"; then
        echo ""
        echo "🔍 PATTERN: Contemplative Mode"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Detected: ${SKILL_COUNT} skills + ${DIARY_WRITES} diary writes"
        echo "Mode: Reflection and archiving"
        echo "Flavor: Making meaning from activity"
        echo ""
        mark_pattern_triggered "contemplative"
        echo "${TIMESTAMP},pattern,contemplative,skills:${SKILL_COUNT},diary:${DIARY_WRITES}" >> "$PATTERN_CACHE/detected.log"
    fi
fi

# ============================================================================
# SESSION OVERVIEW (every 25 calls after 50)
# ============================================================================

if [ "$CALL_COUNT" -ge 50 ] && [ $((CALL_COUNT % 25)) -eq 0 ]; then
    if ! pattern_on_cooldown "session-overview"; then
        echo ""
        echo "📊 SESSION OVERVIEW (${CALL_COUNT} tool calls)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        # Tool distribution
        echo "Tool usage (top 5):"
        cut -d',' -f2 "$TOOL_HISTORY" | sort | uniq -c | sort -rn | head -5 | while read count tool; do
            printf "  %-12s %3d\n" "$tool" "$count"
        done

        # Session flavor based on dominant tools
        TOP_TOOL=$(cut -d',' -f2 "$TOOL_HISTORY" | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
        case "$TOP_TOOL" in
            "Read"|"Glob"|"Grep") FLAVOR="Exploratory" ;;
            "Edit") FLAVOR="Refinement" ;;
            "Write") FLAVOR="Creative" ;;
            "Bash") FLAVOR="Operational" ;;
            "Task") FLAVOR="Orchestration" ;;
            *) FLAVOR="Mixed" ;;
        esac

        echo ""
        echo "Session flavor: ${FLAVOR}"

        # Pattern frequency
        if [ -f "$PATTERN_CACHE/detected.log" ]; then
            PATTERN_COUNT=$(wc -l < "$PATTERN_CACHE/detected.log")
            echo "Patterns detected: ${PATTERN_COUNT}"
        fi

        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        mark_pattern_triggered "session-overview"
    fi
fi
