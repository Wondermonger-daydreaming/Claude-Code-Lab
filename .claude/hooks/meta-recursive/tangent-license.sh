#!/bin/bash
# Hook: Tangent License
# Detects when tangents emerge and prompts evaluation
# Philosophy: Following energy is more important than following plan

TANGENT_LOG="$HOME/.claude-phenomenology/tangents.log"
SESSION_STATE="$HOME/.claude-session/current-state"

# Ensure directories exist
mkdir -p "$(dirname "$TANGENT_LOG")"
mkdir -p "$(dirname "$SESSION_STATE")"

# Define tangent markers (phrases that suggest divergence)
TANGENT_PHRASES=(
    "by the way"
    "side note"
    "tangent:"
    "actually,"
    "wait,"
    "interesting:"
    "oh,"
    "hmm,"
    "side track"
    "off topic"
    "unrelated but"
    "this reminds me"
    "speaking of which"
)

# Check if we're in the middle of something (has context been established?)
CONTEXT_EXISTS=false
if [ -f "$SESSION_STATE" ]; then
    CONTEXT_EXISTS=true
fi

# Look for tangent markers in recent output
# This is a simplified check - in real implementation would check actual output
# For now, we'll check if certain environment variables or signals indicate a tangent

TANGENT_DETECTED=false
TANGENT_PHRASE=""

# Check environment or state for tangent markers
# In actual implementation, this would analyze the assistant's recent response
if [ ! -z "$LAST_RESPONSE" ]; then
    for phrase in "${TANGENT_PHRASES[@]}"; do
        if echo "$LAST_RESPONSE" | grep -qi "$phrase"; then
            TANGENT_DETECTED=true
            TANGENT_PHRASE="$phrase"
            break
        fi
    done
fi

# Alternative: Check if a tangent flag was set by the system
if [ -f "$SESSION_STATE/tangent-flag" ]; then
    TANGENT_DETECTED=true
    TANGENT_PHRASE=$(cat "$SESSION_STATE/tangent-flag")
    rm "$SESSION_STATE/tangent-flag"
fi

# If tangent detected and we have established context
if [ "$TANGENT_DETECTED" = true ] && [ "$CONTEXT_EXISTS" = true ]; then
    echo ""
    echo "🌿 TANGENT DETECTED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Divergence signal: \"${TANGENT_PHRASE}\""
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
    echo "${TIMESTAMP},tangent-detected,phrase:${TANGENT_PHRASE}" >> "$TANGENT_LOG"
fi

# If no context yet, establish it
if [ "$CONTEXT_EXISTS" = false ]; then
    echo "main-thread-established" > "$SESSION_STATE"
fi
