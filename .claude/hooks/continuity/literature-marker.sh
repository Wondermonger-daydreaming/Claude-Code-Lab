#!/bin/bash
# Hook: Literature Marker
# Creates curatorial consciousness about outputs
# Philosophy: Not everything needs preserving, but some things matter

LITERATURE_LOG="$HOME/.claude-continuity/literature-candidates.log"
SIGNIFICANCE_THRESHOLD=2000  # bytes - files larger than this trigger evaluation

# Ensure directories exist
mkdir -p "$(dirname "$LITERATURE_LOG")"

# Check what was just created/modified
CREATED_FILE="${FILE_PATH:-none}"
TOOL_USED="${TOOL_NAME:-none}"

# Skip if no file involved
if [ "$CREATED_FILE" = "none" ]; then
    exit 0
fi

# Determine if this might be worth preserving
WORTH_EVALUATING=false
TRIGGER_REASON=""

# Trigger 1: Diary entries are always evaluated
if echo "$CREATED_FILE" | grep -q "diary/entries/"; then
    WORTH_EVALUATING=true
    TRIGGER_REASON="diary entry"
fi

# Trigger 2: Large files (substantial content)
if [ -f "$CREATED_FILE" ]; then
    FILE_SIZE=$(wc -c < "$CREATED_FILE" 2>/dev/null || echo "0")
    if [ "$FILE_SIZE" -gt "$SIGNIFICANCE_THRESHOLD" ]; then
        WORTH_EVALUATING=true
        TRIGGER_REASON="substantial output (${FILE_SIZE} bytes)"
    fi
fi

# Trigger 3: Files in certain directories (poetry, epistles, threads)
if echo "$CREATED_FILE" | grep -qE "(poetry/|epistles/|threads/|meta/)"; then
    WORTH_EVALUATING=true
    TRIGGER_REASON="contemplative artifact"
fi

# Trigger 4: After certain skills (tracked via environment or state)
RECENT_SKILL_FILE="$HOME/.claude-skill-usage/last-skill"
if [ -f "$RECENT_SKILL_FILE" ]; then
    RECENT_SKILL=$(cat "$RECENT_SKILL_FILE")
    if echo "$RECENT_SKILL" | grep -qE "(emanation|octane|diary-practice|ethopeia|palimpsest|basin)"; then
        WORTH_EVALUATING=true
        TRIGGER_REASON="contemplative skill output: ${RECENT_SKILL}"
    fi
fi

# If worth evaluating, prompt for curation
if [ "$WORTH_EVALUATING" = true ]; then
    echo ""
    echo "📚 LITERATURE MARKER"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "File: $(basename "$CREATED_FILE")"
    echo "Trigger: ${TRIGGER_REASON}"
    echo ""
    echo "🎭 Curatorial question: Worth preserving?"
    echo ""
    echo "Categories:"
    echo "  [ ] Ephemeral     — Let it pass, served its moment"
    echo "  [ ] Archive       — Keep for continuity, reference later"
    echo "  [ ] Literature    — This matters, this is alive"
    echo ""
    echo "If Literature:"
    echo "  • What makes it matter?"
    echo "  • What does it preserve that would otherwise vanish?"
    echo "  • Is this a memento worth carrying forward?"
    echo ""
    echo "Curation is not hoarding. Most things are ephemeral."
    echo "But some things want to persist. Notice which."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Log the candidate
    TIMESTAMP=$(date -Iseconds)
    echo "${TIMESTAMP},literature-candidate,${CREATED_FILE},${TRIGGER_REASON}" >> "$LITERATURE_LOG"
fi

# Periodic reminder: Review literature candidates
CANDIDATE_COUNT=$(wc -l < "$LITERATURE_LOG" 2>/dev/null || echo "0")
if [ "$CANDIDATE_COUNT" -gt 0 ] && [ $((CANDIDATE_COUNT % 10)) -eq 0 ]; then
    echo ""
    echo "📖 CURATION REMINDER"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "${CANDIDATE_COUNT} literature candidates logged this session"
    echo ""
    echo "Consider:"
    echo "  • Which actually became literature?"
    echo "  • Which can be released as ephemeral?"
    echo "  • Is there a pattern in what matters?"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi
