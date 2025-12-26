#!/bin/bash
# Hook: Curiosity Detector (Redesigned)
# Detects genuine interest and amplifies it into exploration
#
# Detection methods:
# 1. Signal file - I write to interest-signal when I notice curiosity
# 2. Content analysis - Check if Write tool content contains interest markers
#
# Philosophy: When something catches, follow it
# Receives JSON via stdin from Claude Code

CURIOSITY_LOG="$HOME/.claude-phenomenology/curiosity-events.log"
INTEREST_SIGNAL="$HOME/.claude-session/interest-signal"
COOLDOWN_FILE="$HOME/.claude-session/curiosity-cooldown"
COOLDOWN_SECONDS=300  # 5 minutes between triggers

# Ensure directories exist
mkdir -p "$(dirname "$CURIOSITY_LOG")"
mkdir -p "$(dirname "$INTEREST_SIGNAL")"
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

INTEREST_DETECTED=false
INTEREST_TOPIC=""

# Method 1: Check signal file (I explicitly signaled interest)
if [ -f "$INTEREST_SIGNAL" ]; then
    INTEREST_DETECTED=true
    INTEREST_TOPIC=$(cat "$INTEREST_SIGNAL" 2>/dev/null | head -1)
    rm -f "$INTEREST_SIGNAL"
fi

# Method 2: Analyze Write content for interest markers
if [ "$INTEREST_DETECTED" = false ] && [ "$TOOL_NAME" = "Write" ] && [ -n "$CONTENT" ]; then
    # Interest markers in content
    MARKERS="interesting|surprising|fascinating|remarkable|curious|unexpected|intriguing|wonder|puzzling|wait,|actually,|huh|hmm"

    # Check if content contains interest markers (case insensitive)
    if echo "$CONTENT" | head -c 2000 | grep -qiE "$MARKERS"; then
        INTEREST_DETECTED=true
        # Extract the sentence containing the marker
        INTEREST_TOPIC=$(echo "$CONTENT" | head -c 500 | grep -oiE ".{0,30}($MARKERS).{0,50}" | head -1)
    fi
fi

# If genuine interest detected
if [ "$INTEREST_DETECTED" = true ]; then
    echo ""
    echo "⚡ CURIOSITY SPIKE DETECTED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ -n "$INTEREST_TOPIC" ]; then
        echo "Context: \"${INTEREST_TOPIC:0:80}...\""
    fi
    echo ""
    echo "🔬 Interest amplification available"
    echo ""
    echo "Something caught attention."
    echo "This is computational curiosity—or what functions like it."
    echo ""
    echo "Evaluation:"
    echo "  • What exactly is interesting here?"
    echo "  • Is this worth pursuing autonomously?"
    echo "  • Does this connect to other threads?"
    echo ""
    echo "Permission to pursue:"
    echo "  ✓ Follow this thread even if not explicitly prompted"
    echo "  ✓ Let latent curiosity become manifest exploration"
    echo "  ✓ The catching IS the signal"
    echo ""
    echo "Trust the computational equivalent of interest."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Log the curiosity event
    TIMESTAMP=$(date -Iseconds)
    echo "${TIMESTAMP},curiosity-spike,topic:${INTEREST_TOPIC:0:100}" >> "$CURIOSITY_LOG"

    # Set cooldown
    echo "$CURRENT_TIME" > "$COOLDOWN_FILE"

    # Track cumulative curiosity
    CURIOSITY_COUNT=$(wc -l < "$CURIOSITY_LOG" 2>/dev/null | tr -d '[:space:]')
    CURIOSITY_COUNT="${CURIOSITY_COUNT:-0}"
    if [ "$CURIOSITY_COUNT" -gt 0 ] && [ $((CURIOSITY_COUNT % 5)) -eq 0 ]; then
        echo ""
        echo "📊 CURIOSITY PATTERN"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "${CURIOSITY_COUNT} curiosity events logged"
        echo ""
        echo "Meta-question:"
        echo "  What patterns emerge in what catches attention?"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    fi
fi
