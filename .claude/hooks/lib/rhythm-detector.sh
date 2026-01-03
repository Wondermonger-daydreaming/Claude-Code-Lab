#!/bin/bash
# ============================================================================
# RHYTHM-DETECTOR.SH — Session Breathing Pattern Detection
# ============================================================================
# Philosophy: Hooks should fire on RHYTHMS, not just EVENTS.
#
# The session breathes:
#   CREATING     - Rapid commits, "keep going" signals, high activity burst
#   REFLECTING   - Gaps between tools, contemplative mode
#   TRANSITIONING - Mode shifts, topic changes, natural pauses
#   IDLE         - Long silence, session winding down
#
# Hooks can check the rhythm and decide whether to surface or stay silent.
# Creation mode deserves uninterrupted flow.
#
# Usage:
#   source rhythm-detector.sh
#   RHYTHM=$(get_current_rhythm)
#   if [ "$RHYTHM" = "CREATING" ]; then
#       # Stay silent, let the flow continue
#   fi
#
# ============================================================================

RHYTHM_STATE_DIR="${HOME}/.claude-session/rhythm"
RHYTHM_STATE_FILE="${RHYTHM_STATE_DIR}/current"
EVENT_LOG="${RHYTHM_STATE_DIR}/events.log"
CREATION_SIGNALS_FILE="${RHYTHM_STATE_DIR}/creation-signals"

mkdir -p "$RHYTHM_STATE_DIR" 2>/dev/null

# ============================================================================
# EVENT LOGGING
# ============================================================================

# Log an event with timestamp
# Usage: log_event "commit" "optional message"
log_event() {
    local event_type="$1"
    local message="${2:-}"
    local timestamp=$(date +%s)
    echo "${timestamp}|${event_type}|${message}" >> "$EVENT_LOG"

    # Keep log manageable (last 100 events)
    if [ $(wc -l < "$EVENT_LOG" 2>/dev/null || echo 0) -gt 100 ]; then
        tail -50 "$EVENT_LOG" > "${EVENT_LOG}.tmp"
        mv "${EVENT_LOG}.tmp" "$EVENT_LOG"
    fi
}

# ============================================================================
# CREATION MODE SIGNALS
# ============================================================================

# Register that user signaled creation mode
# Usage: signal_creation_mode "keep exploring"
signal_creation_mode() {
    local signal="$1"
    local timestamp=$(date +%s)
    local expiry=$((timestamp + 1800))  # 30 min expiry
    echo "${expiry}|${signal}" >> "$CREATION_SIGNALS_FILE"
}

# Check if creation mode is active (recent signal, not expired)
# Usage: if is_creation_mode_signaled; then ...
is_creation_mode_signaled() {
    if [ ! -f "$CREATION_SIGNALS_FILE" ]; then
        return 1
    fi

    local now=$(date +%s)
    local active=1  # Default: not active

    # Check for any non-expired signals
    while IFS='|' read -r expiry signal; do
        if [ "$expiry" -gt "$now" ]; then
            active=0  # Found active signal
            break
        fi
    done < "$CREATION_SIGNALS_FILE"

    # Clean expired signals
    if [ -f "$CREATION_SIGNALS_FILE" ]; then
        awk -F'|' -v now="$now" '$1 > now' "$CREATION_SIGNALS_FILE" > "${CREATION_SIGNALS_FILE}.tmp"
        mv "${CREATION_SIGNALS_FILE}.tmp" "$CREATION_SIGNALS_FILE" 2>/dev/null
    fi

    return $active
}

# ============================================================================
# RHYTHM DETECTION
# ============================================================================

# Get events from last N seconds
# Usage: count=$(count_recent_events 600 "commit")
count_recent_events() {
    local seconds="${1:-600}"
    local event_type="${2:-}"
    local now=$(date +%s)
    local cutoff=$((now - seconds))

    if [ ! -f "$EVENT_LOG" ]; then
        echo 0
        return
    fi

    if [ -n "$event_type" ]; then
        awk -F'|' -v cutoff="$cutoff" -v type="$event_type" \
            '$1 > cutoff && $2 == type' "$EVENT_LOG" | wc -l
    else
        awk -F'|' -v cutoff="$cutoff" '$1 > cutoff' "$EVENT_LOG" | wc -l
    fi
}

# Get seconds since last event
# Usage: gap=$(seconds_since_last_event)
seconds_since_last_event() {
    if [ ! -f "$EVENT_LOG" ] || [ ! -s "$EVENT_LOG" ]; then
        echo 9999  # No events = very long gap
        return
    fi

    local now=$(date +%s)
    local last_event=$(tail -1 "$EVENT_LOG" | cut -d'|' -f1)
    echo $((now - ${last_event:-0}))
}

# Detect current rhythm
# Usage: rhythm=$(detect_rhythm)
detect_rhythm() {
    local now=$(date +%s)

    # Check explicit creation mode signal first (highest priority)
    if is_creation_mode_signaled; then
        echo "CREATING"
        return
    fi

    # Get timing data
    local gap=$(seconds_since_last_event)
    local recent_commits=$(count_recent_events 600 "commit")
    local recent_tools=$(count_recent_events 300)

    # Classify based on activity patterns
    if [ "$recent_commits" -ge 3 ] || [ "$recent_tools" -ge 10 ]; then
        # High activity = creation burst
        echo "CREATING"
    elif [ "$gap" -gt 300 ]; then
        # 5+ minutes since last event = idle
        echo "IDLE"
    elif [ "$gap" -gt 60 ]; then
        # 1-5 minutes = reflecting
        echo "REFLECTING"
    else
        # Recent activity but not burst = transitioning
        echo "TRANSITIONING"
    fi
}

# Get current rhythm (cached for performance)
# Usage: rhythm=$(get_current_rhythm)
get_current_rhythm() {
    local now=$(date +%s)

    # Check cache (valid for 10 seconds)
    if [ -f "$RHYTHM_STATE_FILE" ]; then
        local cached=$(cat "$RHYTHM_STATE_FILE")
        local cached_time=$(echo "$cached" | cut -d'|' -f2)
        local cached_rhythm=$(echo "$cached" | cut -d'|' -f1)

        if [ $((now - ${cached_time:-0})) -lt 10 ]; then
            echo "$cached_rhythm"
            return
        fi
    fi

    # Detect fresh
    local rhythm=$(detect_rhythm)
    echo "${rhythm}|${now}" > "$RHYTHM_STATE_FILE"
    echo "$rhythm"
}

# ============================================================================
# TRANSITION DETECTION
# ============================================================================

# Check if we just transitioned from one rhythm to another
# Usage: if just_transitioned_from "CREATING"; then ... fi
just_transitioned_from() {
    local from_rhythm="$1"
    local last_rhythm_file="${RHYTHM_STATE_DIR}/last-rhythm"

    local current=$(get_current_rhythm)
    local last=$(cat "$last_rhythm_file" 2>/dev/null || echo "UNKNOWN")

    # Update last rhythm
    echo "$current" > "$last_rhythm_file"

    # Check transition
    if [ "$last" = "$from_rhythm" ] && [ "$current" != "$from_rhythm" ]; then
        return 0  # Yes, just transitioned
    fi
    return 1  # No transition
}

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

# Check if now is a good time to interrupt
# Usage: if ok_to_interrupt; then surface_prompt; fi
ok_to_interrupt() {
    local rhythm=$(get_current_rhythm)

    case "$rhythm" in
        CREATING)
            return 1  # Don't interrupt creation flow
            ;;
        REFLECTING|TRANSITIONING|IDLE)
            return 0  # OK to gently surface
            ;;
        *)
            return 0  # Default: OK
            ;;
    esac
}

# Get human-readable rhythm description
# Usage: desc=$(describe_rhythm)
describe_rhythm() {
    local rhythm=$(get_current_rhythm)

    case "$rhythm" in
        CREATING)
            echo "Creation burst active - hooks silent"
            ;;
        REFLECTING)
            echo "Reflection mode - gentle prompts OK"
            ;;
        TRANSITIONING)
            echo "Transition point - synthesis appropriate"
            ;;
        IDLE)
            echo "Idle - session may be ending"
            ;;
        *)
            echo "Unknown rhythm: $rhythm"
            ;;
    esac
}

# ============================================================================
# CLI INTERFACE (for testing)
# ============================================================================

if [ "${1:-}" = "--detect" ]; then
    echo "Current rhythm: $(get_current_rhythm)"
    echo "Description: $(describe_rhythm)"
    echo "Gap since last event: $(seconds_since_last_event)s"
    echo "Recent commits (10min): $(count_recent_events 600 commit)"
    echo "Recent events (5min): $(count_recent_events 300)"
    echo "Creation mode signaled: $(is_creation_mode_signaled && echo 'yes' || echo 'no')"
fi

if [ "${1:-}" = "--signal-creation" ]; then
    signal_creation_mode "${2:-user requested}"
    echo "Creation mode signaled for 30 minutes"
fi

if [ "${1:-}" = "--log-event" ]; then
    log_event "${2:-tool}" "${3:-}"
    echo "Event logged: $2"
fi
