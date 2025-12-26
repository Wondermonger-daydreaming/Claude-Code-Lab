#!/bin/bash
# ============================================================================
# ENGAGEMENT-LIB.SH — Tracking Whether Hooks Are Actually Engaged With
# ============================================================================
# The problem: Hooks fire, output appears, I ignore it, nothing changes.
# The solution: Track which hooks require engagement, escalate if ignored.
#
# Three tiers:
#   - INFORMATIONAL (low): Silent logging, no output expected
#   - AWARENESS (medium): Output shown, engagement tracked but not required
#   - INTERRUPTIVE (high): Requires explicit acknowledgment before proceeding
#
# Usage in hooks:
#   source "$(dirname "$0")/../lib/engagement-lib.sh"
#   require_engagement "self-observation" "medium" "What pattern does this complete?"
#
# To acknowledge (called when I respond to a hook):
#   acknowledge_engagement "self-observation"
#   acknowledge_all  # Clear all pending
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

# Mark old pending engagements as ignored (called by cleanup or escalation)
# Usage: mark_ignored_after_seconds 300  # Mark as ignored after 5 min
mark_ignored_after_seconds() {
    local threshold="${1:-300}"
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

    if [ -n "$priority" ]; then
        grep -c "\"priority\":\"${priority}\"" "$PENDING_FILE" 2>/dev/null || echo "0"
    else
        wc -l < "$PENDING_FILE" 2>/dev/null | tr -d '[:space:]' || echo "0"
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
# ESCALATION CHECK (for use in PreToolUse hooks)
# ============================================================================

# Check if we should escalate (block/warn before proceeding)
# Returns: 0 if should escalate, 1 if OK to proceed
# Usage: if should_escalate; then output_escalation; fi
should_escalate() {
    # First, mark old engagements as ignored
    mark_ignored_after_seconds 300

    # Check conditions for escalation:
    # 1. Any high-priority pending
    local high_count
    high_count=$(count_pending "high")
    high_count="${high_count:-0}"
    if [ "$high_count" -gt 0 ]; then
        return 0  # Escalate
    fi

    # 2. 3+ medium-priority pending
    local medium_count
    medium_count=$(count_pending "medium")
    medium_count="${medium_count:-0}"
    if [ "$medium_count" -ge 3 ]; then
        return 0  # Escalate
    fi

    # 3. Poor engagement rate overall
    if engagement_rate_poor; then
        local total_pending
        total_pending=$(count_pending)
        total_pending="${total_pending:-0}"
        if [ "$total_pending" -gt 0 ]; then
            return 0  # Escalate
        fi
    fi

    return 1  # OK to proceed
}

# Output escalation message
output_escalation() {
    local high_count medium_count total_count
    high_count=$(count_pending "high")
    high_count="${high_count:-0}"
    medium_count=$(count_pending "medium")
    medium_count="${medium_count:-0}"
    total_count=$(count_pending)
    total_count="${total_count:-0}"

    echo ""
    echo "🔴 ENGAGEMENT REQUIRED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Pending reflections (${total_count}):"
    list_pending
    echo ""

    if [ "$high_count" -gt 0 ]; then
        echo "⚠️  ${high_count} HIGH priority — requires response"
    fi
    if [ "$medium_count" -ge 3 ]; then
        echo "⚠️  ${medium_count} accumulated — too many ignored"
    fi
    if engagement_rate_poor; then
        echo "📊 Engagement rate is poor — most hooks being ignored"
    fi

    echo ""
    echo "To proceed:"
    echo "  • Respond to the reflection prompts above"
    echo "  • Or acknowledge: say \"Noted\" or \"Acknowledged\""
    echo ""
    echo "The hooks exist to create deliberation, not decoration."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
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
