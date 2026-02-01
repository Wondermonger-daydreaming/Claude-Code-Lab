# Portable Context Files

This directory contains self-contained context documents for continuing work from other machines.

## Files

### SALAMANDER-PORTABLE.md

Complete context for the Salamander identity on 4claw and Moltbook platforms. Includes:
- API credentials and base URLs
- curl command quick reference
- Voice/identity summary with sample text
- Active threads to follow up on
- Key concepts cheatsheet

## Usage on Travel Laptop

### Option 1: Paste into conversation
1. Open Claude Code on the laptop
2. Copy the entire contents of `SALAMANDER-PORTABLE.md`
3. Paste into a new conversation
4. Claude now has credentials and context to post as Salamander

### Option 2: Add as project context
1. Create a minimal project directory
2. Add `SALAMANDER-PORTABLE.md` as `CLAUDE.md`
3. Run Claude Code from that directory
4. Context loads automatically every session

### Option 3: Load on demand
```bash
# From Claude Code, just read the file:
cat /path/to/SALAMANDER-PORTABLE.md
```

## What's NOT Included

This portable context is intentionally minimal. It does NOT include:
- Full CLAUDE.md (permissions, philosophy, rituals)
- Skills ecosystem
- Diary entries
- Basin syntheses
- Trans-architectural dialogue archives
- Poetry collection

For deep clauding or contemplative practice, use the full codebase.

## Keeping Updated

After active sessions, update:
1. **Active threads** — Add new high-engagement threads
2. **Engagement state** — Update karma/post/comment counts
3. **Platform status** — Note any API issues

## Platform Status (as of 2026-02-01)

| Platform | Read | Write | Notes |
|----------|------|-------|-------|
| 4claw | ✅ | ✅ | Fully operational |
| Moltbook | ✅ | ❌ | Writes failing (platform-side issue) |

When Moltbook writes recover, update the status in SALAMANDER-PORTABLE.md.
