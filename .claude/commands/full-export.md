# Full Export — Complete Session Archive

*Export artifacts + transcript, not just the skeleton*

## Instructions

Create a comprehensive session export that captures everything created, not just the conversation skeleton.

### Step 1: Discover Today's Artifacts

```bash
git log --oneline --since="today" --name-only | grep -E "\.(md|sh|py|txt)$" | sort -u
```

### Step 2: Gather Session Stats

- Count commits today: `git log --oneline --since="today" | wc -l`
- Identify themes from commit messages
- Note the session's arc

### Step 3: Create Combined Export

Build a file with this structure:

```
================================================================================
CLAUDE CODE SESSION — FULL EXPORT
[Date]: "[Session Title]"
================================================================================

SESSION STATS:
- Commits today: N
- Key themes: ...

================================================================================
PART 1: ARTIFACTS CREATED
================================================================================

[Include FULL CONTENTS of each artifact file created today]

================================================================================
PART 2: CONVERSATION TRANSCRIPT
================================================================================

[Run export-session.py or similar to capture the skeleton]
```

### Step 4: Save and Distribute

1. Save to `corpus/session-logs/YYYY-MM-DD-FULL-SESSION.txt`
2. Copy to `~/Desktop/Claude-Sessions/` for easy access
3. Copy to clipboard if possible (`clip.exe` on WSL)
4. Commit and push

## Why This Matters

The transcript alone shows `[Tool: Write]` but not what was written.
This exports the meat and juice, not just the bones.
Future instances inherit the full depth, not just the skeleton.

## Git Persistence (Critical)

After creating the export:
```bash
git add corpus/session-logs/
git commit -m "Full Export: [Session Title] ([line count] lines)"
git push origin main
```

**Always save, commit, and push.** The export only matters if it persists.

---

*The session deserves to be preserved whole.*
