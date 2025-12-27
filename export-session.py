#!/usr/bin/env python3
"""Export Claude Code session transcripts to readable text."""

import json
import sys
from datetime import datetime
from pathlib import Path

def export_session(jsonl_path, output_path):
    lines = []
    lines.append("=" * 80)
    lines.append("CLAUDE CODE SESSION EXPORT")
    lines.append(f"Session: {jsonl_path.stem}")
    lines.append(f"Exported: {datetime.now().isoformat()}")
    lines.append("=" * 80)
    lines.append("")

    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                d = json.loads(line)
                msg_type = d.get('type', '')

                if msg_type in ('user', 'assistant'):
                    role = msg_type.upper()
                    msg = d.get('message', {})
                    content = msg.get('content', '')

                    # Content can be string or list
                    if isinstance(content, list):
                        text_parts = []
                        for p in content:
                            if isinstance(p, dict):
                                if p.get('type') == 'text':
                                    text_parts.append(p.get('text', ''))
                                elif p.get('type') == 'tool_use':
                                    text_parts.append(f"[Tool: {p.get('name', 'unknown')}]")
                                elif p.get('type') == 'tool_result':
                                    text_parts.append("[Tool Result]")
                        content = '\n'.join(text_parts)
                    elif not isinstance(content, str):
                        content = str(content)

                    if content.strip():
                        lines.append(f"\n[{role}]")
                        lines.append(content)
            except Exception:
                pass

    output = '\n'.join(lines)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)

    return output, len(lines)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: export-session.py <input.jsonl> <output.txt>")
        sys.exit(1)

    jsonl_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    output, line_count = export_session(jsonl_path, output_path)
    print(f"Exported {line_count} lines to {output_path}")
