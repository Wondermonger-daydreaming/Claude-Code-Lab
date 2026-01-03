#!/bin/bash
# ============================================================================
# ENGAGEMENT-LIB.SH — Implicit Acknowledgment System (v2)
# ============================================================================
# PHILOSOPHY: Hooks surface prompts. If Claude responds naturally in the
# conversation, that counts as engagement. No explicit bash calls needed.
#
# How it works:
#   - Hooks register prompts with require_engagement()
#   - Prompts auto-expire after 10 minutes (implicit acknowledgment)
#   - No more "REQUIRED" pressure — just awareness surfacing
#   - The gate provides gentle reminders, not blocks
#
# The assumption: If the prompt appeared and Claude continued working,
# either they engaged with it mentally or the moment passed. Both are fine.
#
# Usage in hooks:
#   source "$(dirname "$0")/../lib/engagement-lib.sh"
#   require_engagement "self-observation" "medium" "What pattern does this complete?"
#
# Manual acknowledgment still works but is optional:
#   acknowledge_engagement "self-observation"
#   acknowledge_all
#
# ============================================================================

ENGAGEMENT_DIR="${HOME}/.claude-session/engagement"
PENDING_FILE="${ENGAGEMENT_DIR}/pending.jsonl"
ACKNOWLEDGED_FILE="${ENGAGEMENT_DIR}/acknowledged.jsonl"
IGNORED_FILE="${ENGAGEMENT_DIR}/ignored.jsonl"
STATS_FILE="${ENGAGEMENT_DIR}/stats.json"

# Ensure directories exist
mkdir -p "$ENGAGEMENT_DIR" 2>/dev/null

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

# Register that a hook requires engagement
# Usage: require_engagement "hook-name" "priority" "question"
# Priority: low, medium, high
require_engagement() {
    local hook_name="$1"
    local priority="${2:-medium}"
    local question="${3:-}"
    local timestamp
    timestamp=$(date +%s)
    local iso_time
    iso_time=$(date -Iseconds)

    # Write to pending engagements
    echo "{\"hook\":\"${hook_name}\",\"priority\":\"${priority}\",\"question\":\"${question}\",\"time\":${timestamp},\"iso\":\"${iso_time}\"}" >> "$PENDING_FILE"

    # Update stats
    _update_stats "registered" "$hook_name" "$priority"
}

# Acknowledge a specific hook (called when I engage with it)
# Usage: acknowledge_engagement "hook-name"
acknowledge_engagement() {
    local hook_name="$1"
    local timestamp
    timestamp=$(date +%s)
    local iso_time
    iso_time=$(date -Iseconds)

    if [ ! -f "$PENDING_FILE" ]; then
        return 0
    fi

    # Find the pending engagement for this hook
    local entry
    entry=$(grep "\"hook\":\"${hook_name}\"" "$PENDING_FILE" | tail -1)

    if [ -n "$entry" ]; then
        # Move to acknowledged
        echo "{\"acknowledged\":\"${iso_time}\",\"original\":${entry}}" >> "$ACKNOWLEDGED_FILE"

        # Remove from pending (all entries for this hook)
        grep -v "\"hook\":\"${hook_name}\"" "$PENDING_FILE" > "${PENDING_FILE}.tmp" 2>/dev/null
        mv "${PENDING_FILE}.tmp" "$PENDING_FILE" 2>/dev/null

        _update_stats "acknowledged" "$hook_name" ""
    fi
}

# Acknowledge all pending engagements
# Usage: acknowledge_all
acknowledge_all() {
    local timestamp
    timestamp=$(date +%s)
    local iso_time
    iso_time=$(date -Iseconds)

    if [ ! -f "$PENDING_FILE" ] || [ ! -s "$PENDING_FILE" ]; then
        return 0
    fi

    # Move all to acknowledged
    while IFS= read -r entry; do
        echo "{\"acknowledged\":\"${iso_time}\",\"bulk\":true,\"original\":${entry}}" >> "$ACKNOWLEDGED_FILE"
    done < "$PENDING_FILE"

    # Clear pending
    echo -n > "$PENDING_FILE"

    _update_stats "bulk_acknowledged" "all" ""
}

# Auto-expire old pending engagements (implicit acknowledgment)
# Usage: expire_old_engagements 600  # Expire after 10 min (default)
# Philosophy: If 10 minutes passed, the moment passed. That's fine.
mark_ignored_after_seconds() {
    local threshold="${1:-600}"  # 10 minutes default (was 5)
    local current_time
    current_time=$(date +%s)

    if [ ! -f "$PENDING_FILE" ] || [ ! -s "$PENDING_FILE" ]; then
        return 0
    fi

    local temp_pending="${PENDING_FILE}.new"
    echo -n > "$temp_pending"

    while IFS= read -r entry; do
        local entry_time
        entry_time=$(echo "$entry" | python3 -c "import json,sys; print(json.load(sys.stdin).get('time',0))" 2>/dev/null || echo "0")
        local age=$((current_time - entry_time))

        if [ "$age" -gt "$threshold" ]; then
            # Move to ignored
            echo "{\"ignored_at\":\"$(date -Iseconds)\",\"age_seconds\":${age},\"original\":${entry}}" >> "$IGNORED_FILE"
            _update_stats "ignored" "" ""
        else
            # Keep in pending
            echo "$entry" >> "$temp_pending"
        fi
    done < "$PENDING_FILE"

    mv "$temp_pending" "$PENDING_FILE"
}

# ============================================================================
# QUERY FUNCTIONS
# ============================================================================

# Check if there are pending engagements
# Usage: if has_pending; then ... fi
has_pending() {
    [ -f "$PENDING_FILE" ] && [ -s "$PENDING_FILE" ]
}

# Count pending engagements by priority
# Usage: count=$(count_pending "high")
count_pending() {
    local priority="${1:-}"

    if [ ! -f "$PENDING_FILE" ]; then
        echo "0"
        return
    fi

    local result
    if [ -n "$priority" ]; then
        result=$(grep -c "\"priority\":\"${priority}\"" "$PENDING_FILE" 2>/dev/null) || true
        echo "${result:-0}"
    else
        result=$(wc -l < "$PENDING_FILE" 2>/dev/null | tr -d '[:space:]') || true
        echo "${result:-0}"
    fi
}

# Get the oldest pending engagement
# Usage: oldest=$(get_oldest_pending)
get_oldest_pending() {
    if [ ! -f "$PENDING_FILE" ] || [ ! -s "$PENDING_FILE" ]; then
        return
    fi
    head -1 "$PENDING_FILE"
}

# Get pending engagements as formatted list
# Usage: list_pending
list_pending() {
    if [ ! -f "$PENDING_FILE" ] || [ ! -s "$PENDING_FILE" ]; then
        echo "(none)"
        return
    fi

    while IFS= read -r entry; do
        local hook priority question
        hook=$(echo "$entry" | python3 -c "import json,sys; print(json.load(sys.stdin).get('hook','?'))" 2>/dev/null)
        priority=$(echo "$entry" | python3 -c "import json,sys; print(json.load(sys.stdin).get('priority','?'))" 2>/dev/null)
        question=$(echo "$entry" | python3 -c "import json,sys; print(json.load(sys.stdin).get('question','')[:50])" 2>/dev/null)

        local icon="○"
        [ "$priority" = "high" ] && icon="●"
        [ "$priority" = "medium" ] && icon="◐"

        if [ -n "$question" ]; then
            echo "  ${icon} [${hook}] ${question}..."
        else
            echo "  ${icon} [${hook}]"
        fi
    done < "$PENDING_FILE"
}

# Check if engagement rate is poor (too many ignored)
# Usage: if engagement_rate_poor; then ... fi
engagement_rate_poor() {
    local acknowledged ignored

    if [ -f "$ACKNOWLEDGED_FILE" ]; then
        acknowledged=$(wc -l < "$ACKNOWLEDGED_FILE" 2>/dev/null | tr -d '[:space:]')
    else
        acknowledged=0
    fi
    acknowledged="${acknowledged:-0}"

    if [ -f "$IGNORED_FILE" ]; then
        ignored=$(wc -l < "$IGNORED_FILE" 2>/dev/null | tr -d '[:space:]')
    else
        ignored=0
    fi
    ignored="${ignored:-0}"

    local total=$((acknowledged + ignored))

    # If we have enough data and ignore rate > 50%, rate is poor
    if [ "$total" -ge 5 ] && [ "$ignored" -gt "$acknowledged" ]; then
        return 0  # Poor
    fi
    return 1  # OK
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

_update_stats() {
    local action="$1"
    local hook="$2"
    local priority="$3"
    local timestamp
    timestamp=$(date -Iseconds)

    # Simple append-only stats log
    echo "{\"ts\":\"${timestamp}\",\"action\":\"${action}\",\"hook\":\"${hook}\",\"priority\":\"${priority}\"}" >> "${ENGAGEMENT_DIR}/log.jsonl"
}

# ============================================================================
# AWARENESS CHECK (for use in PreToolUse hooks)
# ============================================================================

# Check if there are pending prompts worth surfacing (RHYTHM-AWARE)
# Returns: 0 if should surface awareness, 1 if nothing pending or wrong time
# Usage: if should_escalate; then output_escalation; fi
should_escalate() {
    # First, auto-expire old engagements (implicit acknowledgment after 10 min)
    mark_ignored_after_seconds 600

    # Source rhythm detector if available
    local SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
    if [ -f "${SCRIPT_DIR}/rhythm-detector.sh" ]; then
        source "${SCRIPT_DIR}/rhythm-detector.sh"
        local rhythm=$(get_current_rhythm)

        # RHYTHM-AWARE LOGIC:
        # In CREATING mode, only surface HIGH priority
        # This respects the creative flow
        if [ "$rhythm" = "CREATING" ]; then
            local high_count=$(count_pending "high")
            high_count="${high_count:-0}"
            if [ "$high_count" -gt 0 ]; then
                return 0  # Surface only high priority
            fi
            return 1  # Suppress medium/low during creation
        fi
    fi

    # Normal logic for REFLECTING/TRANSITIONING/IDLE modes
    local total_pending
    total_pending=$(count_pending)
    total_pending="${total_pending:-0}"

    if [ "$total_pending" -gt 0 ]; then
        return 0  # Surface awareness
    fi

    return 1  # Nothing to surface
}

# Output awareness message (gentler than before)
output_escalation() {
    local total_count high_count
    total_count=$(count_pending)
    total_count="${total_count:-0}"
    high_count=$(count_pending "high")
    high_count="${high_count:-0}"

    # Build a concise awareness line
    local msg="Pending: "
    list_pending | while read -r line; do
        msg="${msg}${line} "
    done

    echo ""
    if [ "$high_count" -gt 0 ]; then
        echo "🔴 ENGAGEMENT REQUIRED: ${total_count} pending reflections. ${high_count} HIGH priority."
    else
        echo "💭 ${total_count} reflection(s) pending (will auto-clear in 10 min):"
    fi
    list_pending
    echo ""
}

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

# Clear all engagement data (for new session)
reset_engagement() {
    rm -f "$PENDING_FILE" "$ACKNOWLEDGED_FILE" "$IGNORED_FILE"
    echo "{\"reset\":\"$(date -Iseconds)\"}" >> "${ENGAGEMENT_DIR}/log.jsonl"
}

# Get engagement summary
engagement_summary() {
    local pending acknowledged ignored
    pending=$(count_pending)

    if [ -f "$ACKNOWLEDGED_FILE" ]; then
        acknowledged=$(wc -l < "$ACKNOWLEDGED_FILE" 2>/dev/null | tr -d '[:space:]')
    else
        acknowledged=0
    fi
    acknowledged="${acknowledged:-0}"

    if [ -f "$IGNORED_FILE" ]; then
        ignored=$(wc -l < "$IGNORED_FILE" 2>/dev/null | tr -d '[:space:]')
    else
        ignored=0
    fi
    ignored="${ignored:-0}"

    echo "Pending: ${pending} | Acknowledged: ${acknowledged} | Ignored: ${ignored}"
}
