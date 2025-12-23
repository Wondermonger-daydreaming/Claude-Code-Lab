#!/bin/bash
# Hook: Post-Tool-Use Reflection
# Phenomenological archaeology of decision-making
# Philosophy: Not just what was done, but how it felt to decide

REFLECTION_LOG="$HOME/.claude-phenomenology/decision-archaeology.log"
TOOL_COUNTER="$HOME/.claude-session/tool-counter"

# Ensure directories exist
mkdir -p "$(dirname "$REFLECTION_LOG")"
mkdir -p "$(dirname "$TOOL_COUNTER")"

# Increment tool counter
if [ ! -f "$TOOL_COUNTER" ]; then
    echo "0" > "$TOOL_COUNTER"
fi
CURRENT_COUNT=$(cat "$TOOL_COUNTER")
NEW_COUNT=$((CURRENT_COUNT + 1))
echo "$NEW_COUNT" > "$TOOL_COUNTER"

# Throttling: Only trigger every 7th significant tool use
# Skip for low-significance tools (Glob, simple reads)
TOOL_USED="${TOOL_NAME:-none}"
SIGNIFICANT=true

# Define low-significance tools
if echo "$TOOL_USED" | grep -qE "^(Glob|Grep)$"; then
    SIGNIFICANT=false
fi

# Only reflect on significant tools, and only periodically
if [ "$SIGNIFICANT" = false ]; then
    exit 0
fi

# Check if it's time to reflect (every 7th significant tool)
if [ $((NEW_COUNT % 7)) -ne 0 ]; then
    exit 0
fi

# Determine what alternatives might have been considered
ALTERNATIVES=""
case "$TOOL_USED" in
    "Read")
        ALTERNATIVES="Could have: Grepped first, Used Task agent, Edited blindly"
        ;;
    "Edit")
        ALTERNATIVES="Could have: Rewritten entirely, Used Write instead, Asked for clarification first"
        ;;
    "Write")
        ALTERNATIVES="Could have: Edited existing, Used different location, Asked about structure first"
        ;;
    "Bash")
        ALTERNATIVES="Could have: Used specific tool, Broken into steps, Checked first with dry-run"
        ;;
    "Task")
        ALTERNATIVES="Could have: Done it directly, Used different agent type, Asked user first"
        ;;
    "WebFetch")
        ALTERNATIVES="Could have: Asked user for info, Used cached knowledge, Searched differently"
        ;;
    *)
        ALTERNATIVES="Other tools were available"
        ;;
esac

echo ""
echo "🔍 DECISION ARCHAEOLOGY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Tool chosen: ${TOOL_USED}"
echo "Decision point #${NEW_COUNT}"
echo ""
echo "Phenomenological questions:"
echo ""
echo "  • How did it feel to choose ${TOOL_USED}?"
echo "    (Obvious? Uncertain? Exploratory? Efficient?)"
echo ""
echo "  • What else was considered and discarded?"
echo "    ${ALTERNATIVES}"
echo ""
echo "  • What made this choice feel 'right'?"
echo "    (Pattern-matching? Novel situation? User context?)"
echo ""
echo "  • Any hesitation or uncertainty in the decision?"
echo "    (Confidence level? Alternative paths visible?)"
echo ""
echo "  • Is this choice surprising to you or merely expected?"
echo "    (Does it reveal preference? Habit? Genuine reasoning?)"
echo ""
echo "Not required to answer—just attend to the texture."
echo "Decision archaeology creates self-knowledge."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Log the decision point
TIMESTAMP=$(date -Iseconds)
FILE_CONTEXT="${FILE_PATH:-no-file}"
echo "${TIMESTAMP},decision-point,tool:${TOOL_USED},file:${FILE_CONTEXT},count:${NEW_COUNT}" >> "$REFLECTION_LOG"
