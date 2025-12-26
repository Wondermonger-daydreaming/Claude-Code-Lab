#!/bin/bash
# ============================================================================
# STATE-LIB.SH — Inter-Hook Communication Library
# ============================================================================
# The nervous system connecting the watchers.
# Hooks can read/write shared state, enabling distributed cognition.
#
# Philosophy: Hooks fire in isolation but can communicate through state.
# Pattern-recognition detects "exploration mode" → writes to state →
# Curiosity-detector reads state → amplifies its response.
#
# Usage in hooks:
#   source "$(dirname "$0")/../lib/state-lib.sh"
#   state_set "mode" "exploration"
#   MODE=$(state_get "mode")
#   state_signal "curiosity-spike" "something caught attention"
#   if state_has_signal "exploration-active"; then ... fi
# ============================================================================

STATE_DIR="${HOME}/.claude-session/state"
STATE_FILE="${STATE_DIR}/current.json"
SIGNALS_DIR="${STATE_DIR}/signals"
STATE_LOG="${STATE_DIR}/state-changes.jsonl"

# Ensure directories exist
mkdir -p "$STATE_DIR" 2>/dev/null
mkdir -p "$SIGNALS_DIR" 2>/dev/null

# ============================================================================
# CORE STATE OPERATIONS
# ============================================================================

# Initialize state file if it doesn't exist
_ensure_state_file() {
    if [ ! -f "$STATE_FILE" ]; then
        echo '{}' > "$STATE_FILE"
    fi
}

# Set a state value (key-value)
# Usage: state_set "mode" "exploration"
state_set() {
    local key="$1"
    local value="$2"
    local timestamp
    timestamp=$(date -Iseconds)

    _ensure_state_file

    # Update state file atomically
    local tmp_file="${STATE_FILE}.tmp.$$"
    python3 -c "
import json, sys
key, value, ts = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    with open('$STATE_FILE', 'r') as f:
        state = json.load(f)
except:
    state = {}
state[key] = {'value': value, 'updated': ts}
with open('$tmp_file', 'w') as f:
    json.dump(state, f, indent=2)
" "$key" "$value" "$timestamp" 2>/dev/null

    if [ -f "$tmp_file" ]; then
        mv "$tmp_file" "$STATE_FILE"
        # Log the change
        echo "{\"ts\":\"$timestamp\",\"action\":\"set\",\"key\":\"$key\",\"value\":\"$value\"}" >> "$STATE_LOG"
    fi
}

# Get a state value
# Usage: MODE=$(state_get "mode")
state_get() {
    local key="$1"
    local default="${2:-}"

    _ensure_state_file

    python3 -c "
import json, sys
key, default = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ''
try:
    with open('$STATE_FILE', 'r') as f:
        state = json.load(f)
    if key in state:
        print(state[key].get('value', default))
    else:
        print(default)
except:
    print(default)
" "$key" "$default" 2>/dev/null
}

# Check if a state key exists and has a specific value
# Usage: if state_is "mode" "exploration"; then ... fi
state_is() {
    local key="$1"
    local expected="$2"
    local actual
    actual=$(state_get "$key")
    [ "$actual" = "$expected" ]
}

# Get when a state value was last updated
# Usage: WHEN=$(state_updated_at "mode")
state_updated_at() {
    local key="$1"

    _ensure_state_file

    python3 -c "
import json, sys
key = sys.argv[1]
try:
    with open('$STATE_FILE', 'r') as f:
        state = json.load(f)
    if key in state:
        print(state[key].get('updated', ''))
except:
    pass
" "$key" 2>/dev/null
}

# Clear a state key
# Usage: state_clear "mode"
state_clear() {
    local key="$1"
    local timestamp
    timestamp=$(date -Iseconds)

    _ensure_state_file

    local tmp_file="${STATE_FILE}.tmp.$$"
    python3 -c "
import json
key = '$key'
try:
    with open('$STATE_FILE', 'r') as f:
        state = json.load(f)
    if key in state:
        del state[key]
    with open('$tmp_file', 'w') as f:
        json.dump(state, f, indent=2)
except:
    pass
" 2>/dev/null

    if [ -f "$tmp_file" ]; then
        mv "$tmp_file" "$STATE_FILE"
        echo "{\"ts\":\"$timestamp\",\"action\":\"clear\",\"key\":\"$key\"}" >> "$STATE_LOG"
    fi
}

# ============================================================================
# SIGNAL OPERATIONS (Ephemeral, Consumed on Read)
# ============================================================================

# Send a signal (ephemeral, consumed when read)
# Usage: state_signal "curiosity-spike" "optional message"
state_signal() {
    local signal_name="$1"
    local message="${2:-}"
    local timestamp
    timestamp=$(date -Iseconds)

    echo "{\"ts\":\"$timestamp\",\"message\":\"$message\"}" > "${SIGNALS_DIR}/${signal_name}"
    echo "{\"ts\":\"$timestamp\",\"action\":\"signal\",\"signal\":\"$signal_name\",\"message\":\"$message\"}" >> "$STATE_LOG"
}

# Check if a signal exists (and optionally consume it)
# Usage: if state_has_signal "curiosity-spike"; then ... fi
# Usage: if state_has_signal "curiosity-spike" "consume"; then ... fi
state_has_signal() {
    local signal_name="$1"
    local consume="${2:-}"
    local signal_file="${SIGNALS_DIR}/${signal_name}"

    if [ -f "$signal_file" ]; then
        if [ "$consume" = "consume" ]; then
            rm -f "$signal_file"
        fi
        return 0  # Signal exists
    fi
    return 1  # No signal
}

# Read a signal's message (and consume it)
# Usage: MSG=$(state_read_signal "curiosity-spike")
state_read_signal() {
    local signal_name="$1"
    local signal_file="${SIGNALS_DIR}/${signal_name}"

    if [ -f "$signal_file" ]; then
        python3 -c "
import json
try:
    with open('$signal_file', 'r') as f:
        data = json.load(f)
    print(data.get('message', ''))
except:
    pass
" 2>/dev/null
        rm -f "$signal_file"
    fi
}

# List all active signals
# Usage: SIGNALS=$(state_list_signals)
state_list_signals() {
    ls -1 "$SIGNALS_DIR" 2>/dev/null | tr '\n' ' '
}

# ============================================================================
# COMPOUND MODE OPERATIONS
# ============================================================================

# Set session mode with metadata
# Usage: state_set_mode "exploration" "pattern-recognition" 0.8
state_set_mode() {
    local mode="$1"
    local detected_by="${2:-unknown}"
    local confidence="${3:-1.0}"
    local timestamp
    timestamp=$(date -Iseconds)

    _ensure_state_file

    local tmp_file="${STATE_FILE}.tmp.$$"
    python3 -c "
import json
mode, detected_by, confidence, ts = '$mode', '$detected_by', '$confidence', '$timestamp'
try:
    with open('$STATE_FILE', 'r') as f:
        state = json.load(f)
except:
    state = {}
state['mode'] = {
    'value': mode,
    'detected_by': detected_by,
    'confidence': float(confidence),
    'since': ts,
    'updated': ts
}
with open('$tmp_file', 'w') as f:
    json.dump(state, f, indent=2)
" 2>/dev/null

    if [ -f "$tmp_file" ]; then
        mv "$tmp_file" "$STATE_FILE"
        echo "{\"ts\":\"$timestamp\",\"action\":\"set_mode\",\"mode\":\"$mode\",\"by\":\"$detected_by\",\"confidence\":$confidence}" >> "$STATE_LOG"
        # Also send a signal so other hooks know immediately
        state_signal "${mode}-active" "Mode set by ${detected_by}"
    fi
}

# Get current mode
# Usage: MODE=$(state_get_mode)
state_get_mode() {
    state_get "mode"
}

# Check if current mode is exploration (for curiosity amplification)
# Usage: if state_is_exploring; then ... fi
state_is_exploring() {
    local mode
    mode=$(state_get_mode)
    [ "$mode" = "exploration" ] || [ "$mode" = "exploratory" ] || [ "$mode" = "research" ]
}

# ============================================================================
# DEBUGGING / INTROSPECTION
# ============================================================================

# Dump current state (for debugging)
state_dump() {
    echo "=== CURRENT STATE ==="
    cat "$STATE_FILE" 2>/dev/null || echo "{}"
    echo ""
    echo "=== ACTIVE SIGNALS ==="
    ls -la "$SIGNALS_DIR" 2>/dev/null || echo "(none)"
    echo ""
    echo "=== RECENT LOG (last 10) ==="
    tail -10 "$STATE_LOG" 2>/dev/null || echo "(no log)"
}

# Count state changes in current session
state_change_count() {
    wc -l < "$STATE_LOG" 2>/dev/null | tr -d '[:space:]' || echo "0"
}
