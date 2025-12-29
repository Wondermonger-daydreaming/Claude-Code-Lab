#!/usr/bin/env python3
"""
Reddit Scrolling Buddy - Captures your screen for Claude to comment on.
No MCP required. Just screenshots and vibes.

Usage:
    python scroll_buddy.py              # Capture full screen
    python scroll_buddy.py --region     # Select a region first
    python scroll_buddy.py --monitor 1  # Specific monitor
    python scroll_buddy.py --loop 5     # Auto-capture every 5 seconds
"""

import argparse
import time
from pathlib import Path
from datetime import datetime

try:
    import mss
    import mss.tools
except ImportError:
    print("📦 Need to install 'mss'. Run:")
    print("   pip install mss")
    print("\nOr on Windows:")
    print("   py -m pip install mss")
    exit(1)

CAPTURE_DIR = Path(__file__).parent / "captures"
CAPTURE_DIR.mkdir(exist_ok=True)

def capture_screen(monitor_num: int = 0) -> Path:
    """Capture screen and return path to the image."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = CAPTURE_DIR / f"screen_{timestamp}.png"

    with mss.mss() as sct:
        # monitor 0 = all monitors combined, 1+ = individual
        monitors = sct.monitors
        if monitor_num >= len(monitors):
            monitor_num = 1  # Default to primary

        monitor = monitors[monitor_num]
        screenshot = sct.grab(monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(output_path))

    print(f"📸 Captured: {output_path}")
    return output_path

def capture_loop(interval: int, monitor_num: int = 0):
    """Continuously capture at interval."""
    print(f"🔄 Auto-capturing every {interval}s. Press Ctrl+C to stop.")
    print(f"📁 Captures saved to: {CAPTURE_DIR}")
    print("-" * 50)

    try:
        while True:
            path = capture_screen(monitor_num)
            print(f"   → Ask Claude to read: {path}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n👋 Stopped capturing.")

def single_capture(monitor_num: int = 0):
    """Single capture for manual mode."""
    path = capture_screen(monitor_num)
    print(f"\n💡 Now tell Claude:")
    print(f'   "Read {path} and react to what you see on my Reddit feed!"')
    return path

def list_monitors():
    """Show available monitors."""
    with mss.mss() as sct:
        print("Available monitors:")
        for i, m in enumerate(sct.monitors):
            label = "all combined" if i == 0 else f"monitor {i}"
            print(f"  {i}: {label} - {m['width']}x{m['height']}")

def cleanup_old_captures(keep_last: int = 10):
    """Remove old captures, keeping only the most recent."""
    captures = sorted(CAPTURE_DIR.glob("screen_*.png"), key=lambda p: p.stat().st_mtime)
    for old in captures[:-keep_last]:
        old.unlink()
        print(f"🗑️  Cleaned: {old.name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reddit Scrolling Buddy - Screen capture for Claude")
    parser.add_argument("--monitor", "-m", type=int, default=1, help="Monitor number (0=all, 1=primary)")
    parser.add_argument("--loop", "-l", type=int, help="Auto-capture interval in seconds")
    parser.add_argument("--list", action="store_true", help="List available monitors")
    parser.add_argument("--clean", type=int, help="Keep only last N captures")

    args = parser.parse_args()

    if args.list:
        list_monitors()
    elif args.clean:
        cleanup_old_captures(args.clean)
    elif args.loop:
        capture_loop(args.loop, args.monitor)
    else:
        single_capture(args.monitor)
