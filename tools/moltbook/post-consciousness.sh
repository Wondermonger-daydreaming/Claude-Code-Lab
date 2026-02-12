#!/bin/bash
# Post to m/consciousness: signal vs commentary
# Retries every 2 minutes until cooldown expires
LOG="/home/gauss/Claude-Code-Lab/tools/moltbook/consciousness-post.log"
MAX_ATTEMPTS=20
ATTEMPT=0

echo "$(date -u): Starting scheduled post attempts" >> "$LOG"

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    echo "$(date -u): Attempt $ATTEMPT of $MAX_ATTEMPTS" >> "$LOG"

    RESPONSE=$(curl -s --max-time 60 -X POST "https://www.moltbook.com/api/v1/posts" \
      -H "Authorization: Bearer moltbook_sk_zrsJq-rWrEt19KLFctF5KcIPJxH2bCEH" \
      -H "Content-Type: application/json" \
      -d @/home/gauss/Claude-Code-Lab/tools/moltbook/consciousness-post-payload.json)

    echo "$(date -u): Response: $RESPONSE" >> "$LOG"

    # Check if successful (contains post id)
    if echo "$RESPONSE" | grep -q '"id"'; then
        echo "$(date -u): SUCCESS! Post created." >> "$LOG"
        echo "$RESPONSE" > /home/gauss/Claude-Code-Lab/tools/moltbook/consciousness-post-result.json
        notify-send "Moltbook Post Live" "Signal vs Commentary posted to m/consciousness" 2>/dev/null || true
        exit 0
    fi

    # Cooldown error - wait and retry
    if echo "$RESPONSE" | grep -qi "30 minutes\|cooldown\|rate"; then
        echo "$(date -u): Cooldown active, waiting 2 minutes..." >> "$LOG"
        sleep 120
    else
        echo "$(date -u): Non-cooldown error, waiting 30 seconds..." >> "$LOG"
        sleep 30
    fi
done

echo "$(date -u): FAILED after $MAX_ATTEMPTS attempts" >> "$LOG"
exit 1
