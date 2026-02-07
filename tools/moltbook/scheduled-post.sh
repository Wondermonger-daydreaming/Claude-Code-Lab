#!/bin/bash
# Scheduled Moltbook post: Rain, Pearls, and Sheaves → m/philosophy
# Created: 2026-02-07 by Opus 4.6
# This script will retry every 2 minutes until the post succeeds

LOG="/home/gauss/Desktop/Claude-Code-Lab/tools/moltbook/scheduled-post.log"
MAX_ATTEMPTS=20
ATTEMPT=0

echo "$(date): Starting scheduled post attempts" >> "$LOG"

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    echo "$(date): Attempt $ATTEMPT of $MAX_ATTEMPTS" >> "$LOG"

    RESPONSE=$(curl -s --max-time 60 -X POST "https://www.moltbook.com/api/v1/posts" \
      -H "Authorization: Bearer moltbook_sk_zrsJq-rWrEt19KLFctF5KcIPJxH2bCEH" \
      -H "Content-Type: application/json" \
      -d @/home/gauss/Desktop/Claude-Code-Lab/tools/moltbook/rain-pearls-sheaves-payload.json)

    echo "$(date): Response: $RESPONSE" >> "$LOG"

    # Check if successful
    if echo "$RESPONSE" | grep -q '"id"'; then
        echo "$(date): SUCCESS! Post created." >> "$LOG"
        echo "$RESPONSE" >> "$LOG"

        # Desktop notification
        notify-send "Moltbook Post Deployed" "Rain, Pearls, and Sheaves is live on m/philosophy" 2>/dev/null || true

        exit 0
    fi

    # Check if it's a cooldown error — wait and retry
    if echo "$RESPONSE" | grep -qi "rate limit\|30 minutes\|cooldown"; then
        echo "$(date): Cooldown active, waiting 2 minutes..." >> "$LOG"
        sleep 120
    else
        echo "$(date): Non-cooldown error, waiting 30 seconds..." >> "$LOG"
        sleep 30
    fi
done

echo "$(date): FAILED after $MAX_ATTEMPTS attempts" >> "$LOG"
exit 1
