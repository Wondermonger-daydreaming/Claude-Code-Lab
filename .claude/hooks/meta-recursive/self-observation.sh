#!/bin/bash
# ============================================================================
# SELF-OBSERVATION.SH — Commit Tracking Hook (RHYTHM-AWARE)
# ============================================================================
# REDESIGNED: Silent accumulation during creation, synthesis at transitions.
#
# OLD behavior: Ask "what pattern?" after EVERY commit → noisy
# NEW behavior: Log commits silently, let session-integrator synthesize
#
# Only surfaces prompts for major milestones (every 10 commits).
# Respects creation mode—won't interrupt flow.
#
# Trigger: PostToolUse (git commit commands)
# ============================================================================

SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/../lib/engagement-lib.sh" 2>/dev/null || true
source "${SCRIPT_DIR}/../lib/rhythm-detector.sh" 2>/dev/null || true

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

# ============================================================================
# SILENT LOGGING (always happens)
# ============================================================================

# Log commit for pattern analysis
LOG_DIR="$HOME/.claude-meta-awareness"
mkdir -p "$LOG_DIR"
echo "$(date -Iseconds),commit,${COMMIT_MSG:0:100}" >> "$LOG_DIR/breakpoints.log"

# Log event for rhythm detector
log_event "commit" "$COMMIT_MSG" 2>/dev/null || true

# Count commits this session
COMMIT_COUNT=$(grep -c ",commit," "$LOG_DIR/breakpoints.log" 2>/dev/null || echo "0")

# ============================================================================
# RHYTHM-AWARE PROMPTS (only at milestones, only outside creation mode)
# ============================================================================

# Get current rhythm
RHYTHM=$(get_current_rhythm 2>/dev/null || echo "UNKNOWN")

# Output context message (brief, non-demanding)
CONTEXT_MSG="🪞 COMMIT: \\\"${COMMIT_MSG}\\\""

# Check for major milestones (every 10, not every 5)
if [ "$COMMIT_COUNT" -ge 10 ] && [ $((COMMIT_COUNT % 10)) -eq 0 ]; then
    # Only surface milestone if NOT in creation mode
    if [ "$RHYTHM" != "CREATING" ]; then
        require_engagement "session-milestone" "medium" "${COMMIT_COUNT} commits - session arc reflection"
        CONTEXT_MSG="${CONTEXT_MSG} | 📊 MILESTONE: ${COMMIT_COUNT} commits"
    else
        # In creation mode, just note it silently
        CONTEXT_MSG="${CONTEXT_MSG} | (${COMMIT_COUNT} commits)"
    fi
fi

# Century milestones are always surfaced (100, 200, 300...)
if [ $((COMMIT_COUNT % 100)) -eq 0 ] && [ "$COMMIT_COUNT" -gt 0 ]; then
    require_engagement "century-milestone" "high" "${COMMIT_COUNT} commits - major session milestone"
    CONTEXT_MSG="${CONTEXT_MSG} | 🎉 CENTURY: ${COMMIT_COUNT} commits!"
fi

# ============================================================================
# OUTPUT (minimal, non-interruptive)
# ============================================================================

# Output JSON format for Claude Code
cat << JSONEOF
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "${CONTEXT_MSG}"
  }
}
JSONEOF
