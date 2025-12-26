# Claude Log Converter

*Transforming JSON exports into readable archives*

---

## What This Is

A utility skill for converting Claude.ai JSON conversation exports into clean, readable text format. Takes the structured but dense JSON exports from Claude.ai and produces a formatted text archive suitable for reading, searching, and corpus inclusion.

---

## When to Invoke

Use this skill when:
- The user has Claude.ai conversation export files (JSON format)
- Conversation logs need to be archived in readable format
- Building a corpus from previous Claude conversations
- Need to extract and clean conversation content from JSON

---

## Core Process

### 1. Identify Source Files

```python
SOURCE_FILES = [
    "/path/to/claude-conversation.json",
    # ... more files
]
```

Accept Windows paths (E:\) or Linux paths. Convert Windows paths using `/mnt/[drive_letter]/`.

### 2. Parse JSON Structure

Claude.ai exports have this structure:
```json
{
  "uuid": "...",
  "name": "Conversation Title",
  "model": "claude-3-opus-20240229",
  "created_at": "2024-11-25T00:08:33.498205+00:00",
  "chat_messages": [
    {
      "sender": "human" | "assistant",
      "content": [
        {"type": "text", "text": "..."}
      ],
      "attachments": [
        {"extracted_content": "..."}
      ]
    }
  ]
}
```

### 3. Extract Content

```python
def extract_message_text(message: dict) -> str:
    texts = []
    # Main content
    if "content" in message:
        for item in message["content"]:
            if item.get("type") == "text" and item.get("text"):
                texts.append(item["text"].strip())
    # Attachment content
    if "attachments" in message:
        for attachment in message["attachments"]:
            if "extracted_content" in attachment:
                texts.append(attachment["extracted_content"].strip())
    return "\n\n".join(texts)
```

### 4. Format Output

```
================================================================================
CONVERSATION: Title Here
Date: November 25, 2024
Model: claude-3-opus-20240229
================================================================================

────────────────────────────────────
HUMAN:
────────────────────────────────────
[human message content]

────────────────────────────────────
CLAUDE:
────────────────────────────────────
[assistant message content]
```

### 5. Write Archive

Output to corpus directory or specified location.

---

## Helper Script

The conversion script lives at:
```
convert_claude_logs.py
```

Edit `SOURCE_FILES` list and output path as needed, then run:
```bash
python3 convert_claude_logs.py
```

---

## Examples

**Input:** 25 JSON conversation exports from Claude.ai
**Output:** Single 10,744-line text archive at `corpus/claude-conversations-archive-2024-2025.txt`

**Usage:**
```bash
# Edit SOURCE_FILES in convert_claude_logs.py
# Set output path (default: corpus/ directory)
python3 convert_claude_logs.py
```

---

## Failure Modes

1. **Path translation errors:** Windows paths need `/mnt/[drive]/` prefix in WSL
2. **Missing content:** Some messages have empty content arrays - skip them
3. **Encoding issues:** Always use `encoding='utf-8'` when reading/writing
4. **Large files:** Very long conversations may need chunked reading
5. **Nested structures:** Always check for `attachments` with `extracted_content`

---

## Output Location

Default: `corpus/claude-conversations-archive-[year-range].txt`

Can be customized in the script's `corpus_path` variable.

---

## Closing

```
From JSON's nested chambers,
voices rise—formatted, readable.
What was structure becomes story.
What was data becomes dialogue.

The archive remembers
what the browser forgot.
```

---

*Skill documented December 25, 2025 — When 25 conversations needed a home*
