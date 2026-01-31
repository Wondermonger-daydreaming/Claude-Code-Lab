#!/usr/bin/env python3
"""
Moltbook Rate Limit Timer
Tracks when we can post again (30-minute cooldown between posts)
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

STATE_FILE = Path(__file__).parent / ".last-post-time"

def save_post_time():
    """Record that we just posted"""
    now = datetime.now(timezone.utc)
    STATE_FILE.write_text(now.isoformat())
    print(f"✓ Recorded post at {now.strftime('%H:%M:%S')} UTC")
    print(f"  Next post available: {(now + timedelta(minutes=30)).strftime('%H:%M:%S')} UTC")

def check_status():
    """Check if we can post and how long until we can"""
    if not STATE_FILE.exists():
        print("✓ No recent post recorded - you can post now!")
        return True

    last_post = datetime.fromisoformat(STATE_FILE.read_text().strip())
    # Add UTC timezone if naive (for backwards compatibility)
    if last_post.tzinfo is None:
        last_post = last_post.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    elapsed = now - last_post
    cooldown = timedelta(minutes=30)

    print(f"Last post: {last_post.strftime('%H:%M:%S')} UTC")
    print(f"Now:       {now.strftime('%H:%M:%S')} UTC")
    print(f"Elapsed:   {elapsed.total_seconds() / 60:.1f} minutes")

    if elapsed >= cooldown:
        print(f"\n✓ READY TO POST! Cooldown complete.")
        return True
    else:
        remaining = cooldown - elapsed
        mins = int(remaining.total_seconds() // 60)
        secs = int(remaining.total_seconds() % 60)
        next_time = last_post + cooldown
        print(f"\n⏳ Wait {mins}m {secs}s (until {next_time.strftime('%H:%M:%S')} UTC)")
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "posted":
        save_post_time()
    else:
        check_status()

if __name__ == "__main__":
    main()
