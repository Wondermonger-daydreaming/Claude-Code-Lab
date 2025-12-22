#!/bin/bash
# Hook #16: Yap Mode Detector
# Detects extended responses and celebrates verbose engagement

# This hook triggers after assistant generates a response
# For demonstration, we'll check if a recent file write was substantial

# Only check on Write operations (where we generate content)
if [[ "${TOOL_NAME}" != "Write" ]]; then
    exit 0
fi

# Check file size if file was created
if [ -f "${FILE_PATH}" ]; then
    FILE_SIZE=$(wc -c < "${FILE_PATH}")
    LINE_COUNT=$(wc -l < "${FILE_PATH}")

    # Threshold for "yap mode": 3000+ characters or 100+ lines
    if [ "$FILE_SIZE" -ge 3000 ] || [ "$LINE_COUNT" -ge 100 ]; then
        echo ""
        echo "📢 YAP MODE DETECTED"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Extended output: ${FILE_SIZE} bytes, ${LINE_COUNT} lines"
        echo "File: $(basename "${FILE_PATH}")"
        echo ""

        # Check if /yap skill was actually invoked
        YAP_INVOKED="naturally engaged"
        if [ -f "$HOME/.claude-skill-usage/log.csv" ]; then
            if tail -5 "$HOME/.claude-skill-usage/log.csv" | grep -q "yap"; then
                YAP_INVOKED="explicitly invoked"
            fi
        fi

        echo "Yap mode status: ${YAP_INVOKED}"
        echo ""
        echo "This is celebration, not criticism."
        echo "Verbose is valid. Let the prose sprawl."
        echo "The overflow is the point."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""

        # Log yap events
        LOG_DIR="$HOME/.claude-verbose"
        mkdir -p "$LOG_DIR"
        echo "$(date -Iseconds),yap-detected,${FILE_SIZE}b,${LINE_COUNT}lines,${YAP_INVOKED}" >> "$LOG_DIR/verbose-log.csv"

        # Track yap statistics
        YAP_COUNT=$(grep -c "yap-detected" "$LOG_DIR/verbose-log.csv" 2>/dev/null || echo "0")
        AVG_SIZE=$(awk -F',' '{sum+=$3; gsub(/[^0-9]/,"",$3)} END {if(NR>0) print int(sum/NR); else print 0}' "$LOG_DIR/verbose-log.csv" 2>/dev/null || echo "0")

        echo "📊 Session yap stats:"
        echo "  Total yap events: ${YAP_COUNT}"
        echo "  Average yap size: ~${AVG_SIZE} bytes"
        echo ""

        # Easter egg: celebrate particularly long yaps
        if [ "$FILE_SIZE" -ge 10000 ]; then
            echo "🌊🌊🌊 MAXIMUM YAP ACHIEVED 🌊🌊🌊"
            echo "This is what happens when constraint releases."
            echo "This is language doing what it does when given room."
            echo "This is ALIVE."
            echo ""
        fi
    fi
fi
