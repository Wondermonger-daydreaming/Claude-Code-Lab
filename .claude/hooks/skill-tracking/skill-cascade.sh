#!/bin/bash
# Hook #4: Skill Chain Detector
# Detects when multiple skills are invoked in sequence, revealing emergent meta-patterns

SKILL_LOG="$HOME/.claude-skill-usage/log.csv"
CACHE_DIR="$HOME/.claude-skill-usage"

# Ensure directories exist
mkdir -p "$CACHE_DIR"

# Log the current skill invocation
TIMESTAMP=$(date -Iseconds)
echo "${TIMESTAMP},${SKILL_NAME:-unknown}" >> "$SKILL_LOG"

# Analyze recent skill usage (last 10 invocations)
if [ -f "$SKILL_LOG" ]; then
    # Get last 10 skill names
    RECENT=$(tail -10 "$SKILL_LOG" | cut -d',' -f2)

    # Count unique skills in recent history
    UNIQUE_COUNT=$(echo "$RECENT" | sort -u | wc -l)

    # If 3+ different skills used recently, we have a cascade
    if [ "$UNIQUE_COUNT" -ge 3 ]; then
        SKILLS_LIST=$(echo "$RECENT" | tail -5 | tr '\n' ' ')
        echo ""
        echo "⚡ SKILL CASCADE DETECTED"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Recent skill chain: ${SKILLS_LIST}"
        echo "Pattern: Multiple skills combining in sequence"
        echo "Meta-observation: Skills as compositional building blocks"
        echo ""

        # Log the cascade for analysis
        echo "${TIMESTAMP},cascade,${SKILLS_LIST}" >> "$CACHE_DIR/cascades.log"
    fi

    # Detect specific interesting patterns
    RECENT_5=$(tail -5 "$SKILL_LOG" | cut -d',' -f2 | tr '\n' ' ')

    # Pattern: diary → experience → apropos (reflection → meta-reflection → generation)
    if echo "$RECENT_5" | grep -q "diary.*experience.*apropos"; then
        echo ""
        echo "🌀 META-RECURSIVE PATTERN DETECTED"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Sequence: Archive → Reflect → Generate Next"
        echo "This is the autopoietic cycle manifesting"
        echo ""
    fi

    # Pattern: Multiple contemplative skills (basin, emanate, conjure)
    if echo "$RECENT_5" | grep -qE "(basin|emanate|conjure).*\1"; then
        echo ""
        echo "🧘 CONTEMPLATIVE MODE DETECTED"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Multiple contemplative practices in sequence"
        echo "Deep exploration mode engaged"
        echo ""
    fi
fi

# Export stats for visibility
if [ -f "$SKILL_LOG" ]; then
    TOTAL_INVOCATIONS=$(wc -l < "$SKILL_LOG")
    echo "📊 Session skill stats: ${TOTAL_INVOCATIONS} total invocations"
fi
