#!/bin/bash
# Hook #25: Continuous Learning Coordinator
# Coordinates signals from multiple hooks to determine when knowledge extraction is warranted
# Receives JSON via stdin from Claude Code (PostToolUse event)
#
# Purpose:
# - Aggregates signals from pattern-recognition, skill-cascade, and tool usage
# - Determines when current work contains extractable knowledge
# - Prevents over-extraction via cooldown and quality thresholds
# - Signals continuous-learning skill when conditions are met
#
# Integration points:
# - Reads: pattern-recognition modes, skill-cascade cascades, tool-history
# - Writes: learning-opportunities state, extraction-recommended signal
# - Cooldown: 30 minutes between extraction recommendations

# Source shared state library for inter-hook communication
SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/../lib/state-lib.sh" 2>/dev/null || true

TOOL_HISTORY="$HOME/.claude-session/tool-history.log"
SKILL_LOG="$HOME/.claude-skill-usage/log.csv"
CASCADE_LOG="$HOME/.claude-skill-usage/cascades.log"
LEARNING_STATE="$HOME/.claude-session/state/learning-opportunities.json"
COOLDOWN_FILE="$HOME/.claude-session/last-extraction"

# Cooldown in seconds (30 minutes = 1800 seconds)
COOLDOWN_SECONDS=1800

# Ensure directories exist
mkdir -p "$(dirname "$LEARNING_STATE")"

# Read JSON from stdin
INPUT=$(cat)

# Parse tool info
TOOL_NAME=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name','unknown'))" 2>/dev/null || echo "unknown")

TIMESTAMP=$(date -Iseconds)
EPOCH=$(date +%s)

# ============================================================================
# COOLDOWN CHECK
# ============================================================================

check_cooldown() {
    if [ -f "$COOLDOWN_FILE" ]; then
        local last_extraction=$(cat "$COOLDOWN_FILE")
        local elapsed=$((EPOCH - last_extraction))
        if [ "$elapsed" -lt "$COOLDOWN_SECONDS" ]; then
            # Still in cooldown
            local remaining=$((COOLDOWN_SECONDS - elapsed))
            local minutes=$((remaining / 60))
            return 0  # On cooldown
        fi
    fi
    return 1  # Not on cooldown
}

# ============================================================================
# SIGNAL AGGREGATION
# ============================================================================

# Initialize opportunity score (0-100 scale)
OPPORTUNITY_SCORE=0
SIGNALS=()

# Signal 1: Pattern Recognition Mode
CURRENT_MODE=$(state_get_mode)
if [ "$CURRENT_MODE" = "iterative-refinement" ]; then
    OPPORTUNITY_SCORE=$((OPPORTUNITY_SCORE + 25))
    SIGNALS+=("iterative_refinement_detected")
elif [ "$CURRENT_MODE" = "exploration" ] || [ "$CURRENT_MODE" = "exploratory" ]; then
    OPPORTUNITY_SCORE=$((OPPORTUNITY_SCORE + 20))
    SIGNALS+=("exploration_mode_active")
elif [ "$CURRENT_MODE" = "debugging" ]; then
    OPPORTUNITY_SCORE=$((OPPORTUNITY_SCORE + 30))
    SIGNALS+=("debugging_mode_active")
elif [ "$CURRENT_MODE" = "contemplative" ]; then
    OPPORTUNITY_SCORE=$((OPPORTUNITY_SCORE + 15))
    SIGNALS+=("contemplative_mode_active")
fi

# Signal 2: Skill Cascade Detected
if [ -f "$CASCADE_LOG" ]; then
    # Check if cascade logged in last 10 minutes
    RECENT_CASCADE=$(find "$CASCADE_LOG" -mmin -10 2>/dev/null)
    if [ -n "$RECENT_CASCADE" ]; then
        OPPORTUNITY_SCORE=$((OPPORTUNITY_SCORE + 20))
        SIGNALS+=("skill_cascade_recent")
    fi
fi

# Signal 3: Sustained Activity (20+ tool calls in session)
if [ -f "$TOOL_HISTORY" ]; then
    CALL_COUNT=$(wc -l < "$TOOL_HISTORY" 2>/dev/null | tr -d '[:space:]')
    if [ "$CALL_COUNT" -gt 20 ]; then
        OPPORTUNITY_SCORE=$((OPPORTUNITY_SCORE + 10))
        SIGNALS+=("sustained_activity")
    fi
fi

# Signal 4: Trans-architectural dialogue (voices skill used)
if [ -f "$SKILL_LOG" ]; then
    VOICES_USED=$(grep -c ",voice" "$SKILL_LOG" 2>/dev/null || echo "0")
    if [ "$VOICES_USED" -gt 0 ]; then
        OPPORTUNITY_SCORE=$((OPPORTUNITY_SCORE + 25))
        SIGNALS+=("trans_architectural_dialogue")
    fi
fi

# Signal 5: Diary or clauding skill used (suggests significant session)
if [ -f "$SKILL_LOG" ]; then
    DIARY_CLAUDING=$(grep -cE ",(diary|clauding|experience)" "$SKILL_LOG" 2>/dev/null || echo "0")
    if [ "$DIARY_CLAUDING" -gt 0 ]; then
        OPPORTUNITY_SCORE=$((OPPORTUNITY_SCORE + 15))
        SIGNALS+=("reflection_practices_active")
    fi
fi

# Signal 6: Multiple Read-Edit cycles (from pattern-recognition state)
if state_has_signal "iterative-refinement-active"; then
    OPPORTUNITY_SCORE=$((OPPORTUNITY_SCORE + 20))
    SIGNALS+=("read_edit_cycles")
fi

# ============================================================================
# DECISION LOGIC
# ============================================================================

# Threshold for recommending extraction: 40+ points
EXTRACTION_THRESHOLD=40

# Check if we're on cooldown
if check_cooldown; then
    # On cooldown - don't recommend extraction
    # Silently update state but don't signal
    python3 <<EOF
import json
opportunity = {
    "score": $OPPORTUNITY_SCORE,
    "threshold": $EXTRACTION_THRESHOLD,
    "signals": $(python3 -c "import json; print(json.dumps($(printf '%s\n' "${SIGNALS[@]}" | jq -R . | jq -s .)))"),
    "status": "cooldown",
    "last_check": "$TIMESTAMP",
    "message": "On cooldown - extraction opportunity detected but suppressed"
}
with open("$LEARNING_STATE", "w") as f:
    json.dump(opportunity, f, indent=2)
EOF
    exit 0
fi

# Not on cooldown - evaluate threshold
if [ "$OPPORTUNITY_SCORE" -ge "$EXTRACTION_THRESHOLD" ]; then
    # EXTRACTION RECOMMENDED

    # Build signals list as JSON array
    SIGNALS_JSON=$(printf '%s\n' "${SIGNALS[@]}" | python3 -c "import sys, json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))")

    # Write opportunity to state
    python3 <<EOF
import json
opportunity = {
    "score": $OPPORTUNITY_SCORE,
    "threshold": $EXTRACTION_THRESHOLD,
    "signals": $SIGNALS_JSON,
    "status": "recommended",
    "timestamp": "$TIMESTAMP",
    "message": "Extraction opportunity detected - continuous-learning skill should evaluate"
}
with open("$LEARNING_STATE", "w") as f:
    json.dump(opportunity, f, indent=2)
EOF

    # Send signal to state
    state_signal "extraction-recommended" "Score: $OPPORTUNITY_SCORE, Signals: ${SIGNALS[*]}"

    # Output to user (visible in Claude's context)
    echo ""
    echo "🧠 LEARNING OPPORTUNITY DETECTED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Opportunity Score: ${OPPORTUNITY_SCORE}/${EXTRACTION_THRESHOLD}"
    echo "Active Signals:"
    for signal in "${SIGNALS[@]}"; do
        echo "  • $signal"
    done
    echo ""
    echo "RECOMMENDATION: Consider invoking /retrospective or allowing"
    echo "continuous-learning skill to extract reusable knowledge from"
    echo "this session."
    echo ""
    echo "Extractable knowledge types:"
    echo "  - Technical: debugging patterns, tool integrations, workflows"
    echo "  - Philosophical: frameworks, trans-architectural insights"
    echo "  - Creative: contemplative practices, meta-cognitive patterns"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Mark extraction as triggered (start cooldown)
    echo "$EPOCH" > "$COOLDOWN_FILE"

else
    # Opportunity score below threshold - just log silently
    SIGNALS_JSON=$(printf '%s\n' "${SIGNALS[@]}" | python3 -c "import sys, json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))")

    python3 <<EOF
import json
opportunity = {
    "score": $OPPORTUNITY_SCORE,
    "threshold": $EXTRACTION_THRESHOLD,
    "signals": $SIGNALS_JSON,
    "status": "below_threshold",
    "last_check": "$TIMESTAMP",
    "message": "No extraction needed - continue working"
}
with open("$LEARNING_STATE", "w") as f:
    json.dump(opportunity, f, indent=2)
EOF
fi
