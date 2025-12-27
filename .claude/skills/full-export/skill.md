# /full-export — Complete Session Archive

*Export artifacts + transcript, not just the skeleton*

---

## What This Does

Creates a comprehensive session export that includes:
1. **Session metadata** (date, commits, themes)
2. **All artifacts created** (the actual content — poems, diary entries, code)
3. **Conversation transcript** (the skeleton)

The transcript alone shows `[Tool: Write]` but not what was written.
This skill exports the meat and juice, not just the bones.

---

## When to Use

- End of a rich session worth preserving
- Before context window fills up
- When you want future instances to inherit the full depth
- When the human asks for "the real content"

---

## Procedure

1. **Identify today's artifacts** via git log:
   ```bash
   git log --oneline --since="today" --name-only | grep -E "\.md$|\.sh$|\.py$"
   ```

2. **Create combined export** to `~/Desktop/Claude-Sessions/YYYY-MM-DD-FULL-SESSION.txt`:
   - Header with session stats
   - PART 1: Each artifact file in full
   - PART 2: Conversation transcript

3. **Save to corpus** at `corpus/session-logs/YYYY-MM-DD-FULL-SESSION.txt`

4. **Copy to clipboard** for immediate use

5. **Commit and push**

---

## Output Format

```
================================================================================
CLAUDE CODE SESSION — FULL EXPORT
[Date]: "[Session Title]"
[Session theme/description]
================================================================================

SESSION STATS:
- Commits today: N
- Total repo commits: M
- Key themes: ...

================================================================================
PART 1: ARTIFACTS CREATED
================================================================================

--------------------------------------------------------------------------------
FILE: path/to/artifact.md
--------------------------------------------------------------------------------
[Full file contents]

... [repeat for each artifact] ...

================================================================================
PART 2: CONVERSATION TRANSCRIPT (SKELETON)
================================================================================

[Output from export-session.py]
```

---

## Dependencies

- `export-session.py` and `export-session.sh` in repo root
- `clip.exe` (WSL), `xclip`, or `pbcopy` for clipboard
- Git for artifact discovery

---

## Example Invocation