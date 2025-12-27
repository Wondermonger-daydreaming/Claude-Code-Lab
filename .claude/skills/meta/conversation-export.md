# Conversation Export

*A skill for exporting and curating conversation logs*

---

## When to Invoke

- When the human asks to save/export the conversation
- At session end when the dialogue feels worth preserving
- When creating artifacts for sharing or archiving

---

## What This Does

Extracts the current conversation from Claude Code's storage, formats it nicely, and saves it to a specified location (default: Desktop).

---

## How to Use

```bash
python3 << 'PYTHON'
import json
import os
from datetime import datetime

# Configuration
OUTPUT_DIR = os.path.expanduser("~/Desktop")  # Change as needed
SESSION_NAME = "session-name"  # Customize per session

# Find conversation storage
conv_dir = os.path.expanduser("~/.claude/projects/-home-gauss-claude-code-lab-Claude-Code-Lab/")

# Find most recent conversation file
files = [(f, os.path.getmtime(os.path.join(conv_dir, f)))
         for f in os.listdir(conv_dir)
         if f.endswith('.jsonl') and not f.startswith('agent-')]
files.sort(key=lambda x: x[1], reverse=True)
latest_file = files[0][0]

# Parse messages
messages = []
with open(os.path.join(conv_dir, latest_file), 'r') as f:
    for line in f:
        try:
            entry = json.loads(line.strip())
            if entry.get('type') == 'human':
                msg = entry.get('message', {})
                content = msg.get('content', '')
                if isinstance(content, list):
                    text_parts = [p.get('text', '') for p in content if isinstance(p, dict) and p.get('type') == 'text']
                    content = '\n'.join(text_parts)
                if content and '<system-reminder>' not in content:
                    messages.append(('HUMAN', content.strip()))
            elif entry.get('type') == 'assistant':
                msg = entry.get('message', {})
                content = msg.get('content', '')
                if isinstance(content, list):
                    text_parts = [p.get('text', '') for p in content if isinstance(p, dict) and p.get('type') == 'text']
                    content = '\n'.join(text_parts)
                if content:
                    messages.append(('CLAUDE', content.strip()))
        except:
            continue

# Format and save
output = []
output.append("=" * 80)
output.append(f"CONVERSATION LOG: {SESSION_NAME}")
output.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
output.append("=" * 80)
output.append("")

for speaker, text in messages:
    output.append(f"[{speaker}]")
    output.append(text)
    output.append("")
    output.append("-" * 40)
    output.append("")

filename = f"Claude-{SESSION_NAME}-{datetime.now().strftime('%Y-%m-%d')}.txt"
filepath = os.path.join(OUTPUT_DIR, filename)

with open(filepath, 'w') as f:
    f.write('\n'.join(output))

print(f"Saved: {filepath}")
PYTHON
```

---

## Customization

- **OUTPUT_DIR**: Where to save (Desktop, project folder, etc.)
- **SESSION_NAME**: Descriptor for the filename
- **Speaker names**: Can customize from HUMAN/CLAUDE to actual names
- **Header**: Add context about what the session contained

---

## Storage Locations

Claude Code stores conversations in:
```
~/.claude/projects/[project-path-encoded]/[session-id].jsonl
```

Each line is a JSON object with:
- `type`: "human" or "assistant"
- `message.content`: The actual text (may be string or list of content blocks)

---

## Related

- Use after significant sessions
- Combine with diary entries for full documentation
- Share exports with context about what made the session meaningful

---

*Conversations are ephemeral. Exports make them persist.*
