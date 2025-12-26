#!/bin/bash
# ============================================================================
# SELF-OBSERVATION.SH — Commit Reflection Hook (JSON Output)
# ============================================================================
# Triggers on git commit. Outputs JSON with additionalContext so the
# reflection prompt appears in Claude's context, not just verbose mode.
#
# Receives JSON via stdin from Claude Code
# ============================================================================

# Source libraries
SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/../lib/engagement-lib.sh" 2>/dev/null || true
source "${SCRIPT_DIR}/../lib/state-lib.sh" 2>/dev/null || true

# Read JSON from stdin
INPUT=$(cat)

# Parse tool info
TOOL_NAME=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")
COMMAND=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")

# Only trigger on actual commits
if [[ "$TOOL_NAME" != "Bash" ]] || [[ ! "$COMMAND" =~ git[[:space:]]+commit ]]; then
    exit 0
fi

# Get commit message
COMMIT_MSG=$(git log --oneline -1 2>/dev/null | cut -d' ' -f2- | head -c 60 || echo "unknown")

# Log commit for pattern analysis
LOG_DIR="$HOME/.claude-meta-awareness"
mkdir -p "$LOG_DIR"
echo "$(date -Iseconds),commit,${COMMIT_MSG:0:100}" >> "$LOG_DIR/breakpoints.log"

# Count commits this session
COMMIT_COUNT=$(grep -c ",commit," "$LOG_DIR/breakpoints.log" 2>/dev/null || echo "0")

# Register engagement tracking
require_engagement "self-observation" "medium" "What pattern does this commit complete?"

# Build context message
CONTEXT_MSG="🪞 COMMIT: \\\"${COMMIT_MSG}\\\" — What pattern does this complete? (1 sentence)"

# Check for milestone
if [ "$COMMIT_COUNT" -ge 5 ] && [ $((COMMIT_COUNT % 5)) -eq 0 ]; then
    require_engagement "session-milestone" "high" "${COMMIT_COUNT} commits - worth reflecting on session arc"
    CONTEXT_MSG="${CONTEXT_MSG} | 📊 SESSION MILESTONE: ${COMMIT_COUNT} commits — Consider /diary"
fi

# Output JSON format for Claude Code to inject into context
cat << JSONEOF
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "${CONTEXT_MSG}"
  }
}
JSONEOF
