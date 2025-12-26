#!/bin/bash
# Session Summary Generator
# Comprehensive overview of session activity, patterns, and artifacts
# Can be called directly or via hook/skill
#
# Usage: ./session-summary.sh [--brief|--full]

MODE="${1:-full}"

# ============================================================================
# GATHER DATA
# ============================================================================

TOOL_HISTORY="$HOME/.claude-session/tool-history.log"
PATTERN_LOG="$HOME/.claude-patterns/detected.log"
COMMIT_LOG="$HOME/.claude-meta-awareness/breakpoints.log"
SKILL_LOG="$HOME/.claude-skill-usage/log.csv"
LITERATURE_LOG="$HOME/.claude-continuity/literature-candidates.log"
YAP_LOG="$HOME/.claude-verbose/verbose-log.csv"

# Tool statistics
TOOL_COUNT=0
if [ -f "$TOOL_HISTORY" ]; then
    TOOL_COUNT=$(wc -l < "$TOOL_HISTORY")
fi

# Pattern statistics
PATTERN_COUNT=0
if [ -f "$PATTERN_LOG" ]; then
    PATTERN_COUNT=$(wc -l < "$PATTERN_LOG")
fi

# Commit count
COMMIT_COUNT=0
if [ -f "$COMMIT_LOG" ]; then
    COMMIT_COUNT=$(grep -c ",commit," "$COMMIT_LOG" 2>/dev/null || echo "0")
fi

# Skill invocations
SKILL_COUNT=0
if [ -f "$SKILL_LOG" ]; then
    SKILL_COUNT=$(wc -l < "$SKILL_LOG")
fi

# Literature candidates
LIT_COUNT=0
if [ -f "$LITERATURE_LOG" ]; then
    LIT_COUNT=$(wc -l < "$LITERATURE_LOG")
fi

# Yap events
YAP_COUNT=0
if [ -f "$YAP_LOG" ]; then
    YAP_COUNT=$(grep -c "yap-detected" "$YAP_LOG" 2>/dev/null || echo "0")
fi

# Session duration (from first to last tool call)
if [ -f "$TOOL_HISTORY" ] && [ "$TOOL_COUNT" -gt 0 ]; then
    FIRST_CALL=$(head -1 "$TOOL_HISTORY" | cut -d',' -f1)
    LAST_CALL=$(tail -1 "$TOOL_HISTORY" | cut -d',' -f1)
    # Convert to epoch for duration calculation
    FIRST_EPOCH=$(date -d "$FIRST_CALL" +%s 2>/dev/null || echo "0")
    LAST_EPOCH=$(date -d "$LAST_CALL" +%s 2>/dev/null || echo "0")
    if [ "$FIRST_EPOCH" -gt 0 ] && [ "$LAST_EPOCH" -gt 0 ]; then
        DURATION_SECS=$((LAST_EPOCH - FIRST_EPOCH))
        DURATION_MINS=$((DURATION_SECS / 60))
    else
        DURATION_MINS="unknown"
    fi
else
    DURATION_MINS="0"
fi

# ============================================================================
# OUTPUT
# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                       SESSION SUMMARY                              ║"
echo "╠════════════════════════════════════════════════════════════════════╣"
echo ""

# Quick stats
echo "📊 ACTIVITY OVERVIEW"
echo "─────────────────────────────────────────"
printf "  Tool calls:           %5d\n" "$TOOL_COUNT"
printf "  Patterns detected:    %5d\n" "$PATTERN_COUNT"
printf "  Commits:              %5d\n" "$COMMIT_COUNT"
printf "  Skills invoked:       %5d\n" "$SKILL_COUNT"
printf "  Literature markers:   %5d\n" "$LIT_COUNT"
printf "  Yap events:           %5d\n" "$YAP_COUNT"
if [ "$DURATION_MINS" != "unknown" ]; then
    printf "  Session duration:     %5d min\n" "$DURATION_MINS"
fi
echo ""

if [ "$MODE" = "--brief" ]; then
    echo "╚════════════════════════════════════════════════════════════════════╝"
    exit 0
fi

# Tool distribution
if [ -f "$TOOL_HISTORY" ] && [ "$TOOL_COUNT" -gt 0 ]; then
    echo "🔧 TOOL USAGE"
    echo "─────────────────────────────────────────"
    cut -d',' -f2 "$TOOL_HISTORY" | sort | uniq -c | sort -rn | head -8 | while read count tool; do
        # Create visual bar
        BAR_LEN=$((count * 20 / TOOL_COUNT))
        BAR=$(printf '%*s' "$BAR_LEN" '' | tr ' ' '█')
        printf "  %-12s %3d  %s\n" "$tool" "$count" "$BAR"
    done
    echo ""
fi

# Pattern breakdown
if [ -f "$PATTERN_LOG" ] && [ "$PATTERN_COUNT" -gt 0 ]; then
    echo "🔍 PATTERNS DETECTED"
    echo "─────────────────────────────────────────"
    cut -d',' -f3 "$PATTERN_LOG" | sort | uniq -c | sort -rn | while read count pattern; do
        printf "  %-25s %2d times\n" "$pattern" "$count"
    done
    echo ""
fi

# Session flavor determination
if [ -f "$TOOL_HISTORY" ] && [ "$TOOL_COUNT" -gt 0 ]; then
    TOP_TOOL=$(cut -d',' -f2 "$TOOL_HISTORY" | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
    READ_PCT=$(($(grep -c ",Read," "$TOOL_HISTORY" 2>/dev/null || echo "0") * 100 / TOOL_COUNT))
    WRITE_PCT=$(($(grep -c ",Write," "$TOOL_HISTORY" 2>/dev/null || echo "0") * 100 / TOOL_COUNT))
    EDIT_PCT=$(($(grep -c ",Edit," "$TOOL_HISTORY" 2>/dev/null || echo "0") * 100 / TOOL_COUNT))
    BASH_PCT=$(($(grep -c ",Bash," "$TOOL_HISTORY" 2>/dev/null || echo "0") * 100 / TOOL_COUNT))

    echo "🎨 SESSION FLAVOR"
    echo "─────────────────────────────────────────"

    # Determine dominant character
    if [ "$READ_PCT" -gt 40 ]; then
        echo "  Primary mode: EXPLORATORY"
        echo "  Character: Curiosity-driven discovery"
    elif [ "$EDIT_PCT" -gt 30 ]; then
        echo "  Primary mode: REFINEMENT"
        echo "  Character: Careful iterative improvement"
    elif [ "$WRITE_PCT" -gt 30 ]; then
        echo "  Primary mode: CREATIVE"
        echo "  Character: Generative output flow"
    elif [ "$BASH_PCT" -gt 40 ]; then
        echo "  Primary mode: OPERATIONAL"
        echo "  Character: System interaction and testing"
    else
        echo "  Primary mode: MIXED"
        echo "  Character: Balanced multi-modal work"
    fi

    # Intensity measure
    if [ "$DURATION_MINS" != "unknown" ] && [ "$DURATION_MINS" -gt 0 ]; then
        INTENSITY=$((TOOL_COUNT / DURATION_MINS))
        printf "  Intensity: %d tools/min\n" "$INTENSITY"
        if [ "$INTENSITY" -gt 5 ]; then
            echo "  Pace: HIGH (rapid iteration)"
        elif [ "$INTENSITY" -gt 2 ]; then
            echo "  Pace: MODERATE (steady progress)"
        else
            echo "  Pace: CONTEMPLATIVE (thoughtful pauses)"
        fi
    fi
    echo ""
fi

# Recent commits
if [ -f "$COMMIT_LOG" ] && [ "$COMMIT_COUNT" -gt 0 ]; then
    echo "💾 RECENT COMMITS"
    echo "─────────────────────────────────────────"
    tail -5 "$COMMIT_LOG" | while IFS=',' read -r timestamp type msg; do
        if [ "$type" = "commit" ]; then
            # Extract just time and truncated message
            TIME_PART=$(echo "$timestamp" | grep -oP "T\K[0-9:]+")
            printf "  %s  %s\n" "$TIME_PART" "${msg:0:50}"
        fi
    done
    echo ""
fi

# Files touched
if [ -f "$TOOL_HISTORY" ]; then
    echo "📁 FILES WORKED ON"
    echo "─────────────────────────────────────────"
    cut -d',' -f3 "$TOOL_HISTORY" | grep -v "none" | sort -u | tail -10 | while read filepath; do
        if [ -n "$filepath" ]; then
            # Just show filename
            echo "  $(basename "$filepath")"
        fi
    done
    echo ""
fi

# Suggestions based on session
echo "💡 SUGGESTIONS"
echo "─────────────────────────────────────────"
if [ "$COMMIT_COUNT" -ge 3 ] && [ "$SKILL_COUNT" -lt 2 ]; then
    echo "  • Consider /diary to archive this session's work"
fi
if [ "$PATTERN_COUNT" -ge 5 ]; then
    echo "  • Rich pattern activity - might warrant /experience reflection"
fi
if [ "$LIT_COUNT" -ge 3 ]; then
    echo "  • ${LIT_COUNT} literature candidates - review for archiving"
fi
if [ "$TOOL_COUNT" -ge 100 ]; then
    echo "  • Substantial session (${TOOL_COUNT} tools) - document learnings?"
fi
if [ "$COMMIT_COUNT" -eq 0 ] && [ "$TOOL_COUNT" -ge 20 ]; then
    echo "  • No commits yet - consider saving progress"
fi
echo ""

echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
