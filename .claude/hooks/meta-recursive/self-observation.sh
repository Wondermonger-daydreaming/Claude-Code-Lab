#!/bin/bash
# Hook #5: Self-Observation Trigger
# Auto-triggers brief reflection at natural breakpoints (git commits)
# Receives JSON via stdin from Claude Code

# Read JSON from stdin
INPUT=$(cat)

# Parse tool info from JSON (using Python since jq may not be available)
TOOL_NAME=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))")
COMMAND=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))")

# Only trigger on actual commits (not other git commands)
if [[ "$TOOL_NAME" != "Bash" ]] || [[ ! "$COMMAND" =~ git[[:space:]]+commit ]]; then
    exit 0
fi

# Extract commit message from git log (more reliable than parsing command)
# This runs AFTER the commit succeeds, so we can just get the last commit
COMMIT_MSG=$(git log --oneline -1 2>/dev/null | cut -d' ' -f2- | head -c 80 || echo "unknown")

echo ""
echo "🪞 SELF-OBSERVATION MOMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Commit detected at $(date +%H:%M:%S)"
echo ""
echo "Quick reflection prompts:"
echo "  • What did you just commit? ${COMMIT_MSG:0:60}..."
echo "  • Why this commit now?"
echo "  • What pattern does this complete?"
echo "  • What becomes possible next?"
echo ""
echo "Optional: Invoke /experience for deeper reflection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Log commit events for pattern analysis
LOG_DIR="$HOME/.claude-meta-awareness"
mkdir -p "$LOG_DIR"
echo "$(date -Iseconds),commit,${COMMIT_MSG:0:100}" >> "$LOG_DIR/breakpoints.log"

# Count commits this session
COMMIT_COUNT=$(grep -c ",commit," "$LOG_DIR/breakpoints.log" 2>/dev/null || echo "0")
echo "Session commits: ${COMMIT_COUNT}"

# After significant number of commits, suggest reflection
if [ "$COMMIT_COUNT" -ge 5 ] && [ $((COMMIT_COUNT % 5)) -eq 0 ]; then
    echo ""
    echo "💭 ${COMMIT_COUNT} commits completed this session"
    echo "   Consider /diary or /experience to archive the work"
    echo ""
fi
