#!/bin/bash
# ============================================================================
# ENGAGEMENT-CONTROL.SH — User Commands for Hook Control
# ============================================================================
# Source this file to get convenient commands for controlling hook behavior.
#
# Usage:
#   source ~/.claude/hooks/lib/engagement-control.sh
#   # Or:
#   source /path/to/project/.claude/hooks/lib/engagement-control.sh
#
# Commands:
#   hooks-quiet [minutes]  — Silence hooks for N minutes (default: 30)
#   hooks-loud             — Resume normal hook behavior
#   hooks-clear            — Acknowledge all pending items
#   hooks-status           — Show current state
#
# ============================================================================

# Get the directory where this script lives
ENGAGEMENT_CONTROL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the main engagement library
source "${ENGAGEMENT_CONTROL_DIR}/engagement-lib.sh"

# ============================================================================
# USER COMMANDS
# ============================================================================

# Silence hooks for N minutes
# Usage: hooks-quiet       # 30 minutes (default)
#        hooks-quiet 60    # 60 minutes
hooks-quiet() {
    local minutes="${1:-30}"
    set_quiet_mode "$minutes"
}

# Resume normal hook behavior
# Usage: hooks-loud
hooks-loud() {
    clear_quiet_mode
}

# Acknowledge all pending items
# Usage: hooks-clear
hooks-clear() {
    local count
    count=$(count_pending)
    acknowledge_all
    echo "✓ Cleared ${count:-0} pending reflection(s)"
}

# Show current status
# Usage: hooks-status
hooks-status() {
    echo "═══════════════════════════════════════════════════"
    echo "  Hook Engagement Status"
    echo "═══════════════════════════════════════════════════"
    echo ""

    # Quiet mode status
    if is_quiet_mode; then
        local quiet_until
        quiet_until=$(cat "$QUIET_MODE_FILE" 2>/dev/null || echo "0")
        echo "  🔇 Quiet mode: ON (until $(date -d "@${quiet_until}" +%H:%M 2>/dev/null || echo 'unknown'))"
    else
        echo "  🔊 Quiet mode: OFF"
    fi

    # Throttle status
    if [ -f "$THROTTLE_FILE" ]; then
        local last_escalation elapsed remaining
        last_escalation=$(cat "$THROTTLE_FILE" 2>/dev/null || echo "0")
        elapsed=$(($(date +%s) - last_escalation))
        remaining=$((THROTTLE_INTERVAL - elapsed))
        if [ "$remaining" -gt 0 ]; then
            echo "  ⏱️  Throttle: ${remaining}s until next escalation"
        else
            echo "  ⏱️  Throttle: Ready"
        fi
    else
        echo "  ⏱️  Throttle: Ready"
    fi

    echo ""

    # Engagement summary
    echo "  $(engagement_summary)"
    echo ""

    # List pending if any
    local pending_count
    pending_count=$(count_pending)
    if [ "${pending_count:-0}" -gt 0 ]; then
        echo "  Pending:"
        list_pending | sed 's/^/  /'
    fi

    echo ""
    echo "═══════════════════════════════════════════════════"
}

# Short aliases
alias hq='hooks-quiet'
alias hl='hooks-loud'
alias hc='hooks-clear'
alias hs='hooks-status'

# ============================================================================
# LOADED MESSAGE
# ============================================================================

echo "Hook controls loaded. Commands: hooks-quiet, hooks-loud, hooks-clear, hooks-status"
echo "  (aliases: hq, hl, hc, hs)"
