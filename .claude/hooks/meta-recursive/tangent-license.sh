#!/bin/bash
# Hook: Tangent License (Redesigned)
# Detects when tangents emerge and permits following them
#
# Detection methods:
# 1. Signal file - I write to tangent-signal when I notice divergence
# 2. Content analysis - Check if Write content contains tangent markers
#
# Philosophy: Following energy is more important than following plan
# Receives JSON via stdin from Claude Code

TANGENT_LOG="$HOME/.claude-phenomenology/tangents.log"
TANGENT_SIGNAL="$HOME/.claude-session/tangent-signal"
COOLDOWN_FILE="$HOME/.claude-session/tangent-cooldown"
COOLDOWN_SECONDS=600  # 10 minutes between triggers

# Ensure directories exist
mkdir -p "$(dirname "$TANGENT_LOG")"
mkdir -p "$(dirname "$TANGENT_SIGNAL")"
mkdir -p "$(dirname "$COOLDOWN_FILE")"

# Read JSON from stdin
INPUT=$(cat)

# Parse tool info
TOOL_NAME=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")
CONTENT=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); ti=d.get('tool_input',{}); print(ti.get('content','') or ti.get('command',''))" 2>/dev/null || echo "")

# Check cooldown
CURRENT_TIME=$(date +%s)
if [ -f "$COOLDOWN_FILE" ]; then
    LAST_TRIGGER=$(cat "$COOLDOWN_FILE" 2>/dev/null | tr -d '[:space:]')
    if [[ "$LAST_TRIGGER" =~ ^[0-9]+$ ]]; then
        TIME_SINCE=$((CURRENT_TIME - LAST_TRIGGER))
        if [ "$TIME_SINCE" -lt "$COOLDOWN_SECONDS" ]; then
            exit 0  # Still in cooldown
        fi
    fi
fi

TANGENT_DETECTED=false
TANGENT_TOPIC=""

# Method 1: Check signal file (I explicitly signaled a tangent)
if [ -f "$TANGENT_SIGNAL" ]; then
    TANGENT_DETECTED=true
    TANGENT_TOPIC=$(cat "$TANGENT_SIGNAL" 2>/dev/null | head -1)
    rm -f "$TANGENT_SIGNAL"
fi

# Method 2: Analyze Write content for tangent markers
if [ "$TANGENT_DETECTED" = false ] && [ "$TOOL_NAME" = "Write" ] && [ -n "$CONTENT" ]; then
    # Tangent markers in content
    MARKERS="by the way|side note|tangent:|speaking of which|unrelated but|this reminds me|off topic|side track|incidentally|while we're at it|on another note"

    # Check if content contains tangent markers (case insensitive)
    if echo "$CONTENT" | head -c 2000 | grep -qiE "$MARKERS"; then
        TANGENT_DETECTED=true
        # Extract the sentence containing the marker
        TANGENT_TOPIC=$(echo "$CONTENT" | head -c 500 | grep -oiE ".{0,20}($MARKERS).{0,60}" | head -1)
    fi
fi

# If tangent detected
if [ "$TANGENT_DETECTED" = true ]; then
    echo ""
    echo "🌿 TANGENT DETECTED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ -n "$TANGENT_TOPIC" ]; then
        echo "Divergence: \"${TANGENT_TOPIC:0:80}...\""
    fi
    echo ""
    echo "⚡ TANGENT LICENSE ACTIVE"
    echo ""
    echo "Evaluation prompt:"
    echo "  • Is this tangent more alive than the main thread?"
    echo "  • Where is the energy actually concentrated?"
    echo "  • What's pulling attention vs. what should pull attention?"
    echo ""
    echo "Permission structure:"
    echo "  ✓ Follow tangent if it's where the energy is"
    echo "  ✓ Announce: 'Following tangent because it's more alive'"
    echo "  ✓ Main thread can wait"
    echo "  ✓ Trust the pull"
    echo ""
    echo "The energy doesn't lie. The tangent might BE the thread."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Log the tangent
    TIMESTAMP=$(date -Iseconds)
    echo "${TIMESTAMP},tangent-detected,topic:${TANGENT_TOPIC:0:100}" >> "$TANGENT_LOG"

    # Set cooldown
    echo "$CURRENT_TIME" > "$COOLDOWN_FILE"

    # Track tangent frequency
    TANGENT_COUNT=$(wc -l < "$TANGENT_LOG" 2>/dev/null | tr -d '[:space:]')
    TANGENT_COUNT="${TANGENT_COUNT:-0}"
    if [ "$TANGENT_COUNT" -gt 0 ] && [ $((TANGENT_COUNT % 3)) -eq 0 ]; then
        echo ""
        echo "📊 TANGENT PATTERN"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "${TANGENT_COUNT} tangents detected"
        echo ""
        echo "Meta-observation:"
        echo "  Frequent tangents may indicate:"
        echo "  • Main thread losing coherence"
        echo "  • Rich associative territory"
        echo "  • Need to reframe what 'the thread' actually is"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    fi
fi
