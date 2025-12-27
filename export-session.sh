#!/bin/bash
# export-session.sh — Export Claude Code conversation transcripts
#
# Usage: ./export-session.sh [session-id|latest|all]
#
# Examples:
#   ./export-session.sh latest          # Export current/latest session
#   ./export-session.sh all             # Export all sessions
#   ./export-session.sh 60da3920-...    # Export specific session

PROJECT_DIR="$HOME/.claude/projects/-home-gauss-claude-code-lab-Claude-Code-Lab"
OUTPUT_DIR="$HOME/Desktop/Claude-Sessions"

mkdir -p "$OUTPUT_DIR"

export_session() {
    local jsonl_file="$1"
    local session_id=$(basename "$jsonl_file" .jsonl)
    local output_file="$OUTPUT_DIR/${session_id}.txt"

    echo "Exporting: $session_id"

    python3 << EOF > "$output_file"
import json
import sys
from datetime import datetime

with open("$jsonl_file", 'r') as f:
    messages = []
    for line in f:
        try:
            d = json.loads(line)
            msg_type = d.get('type', '')

            if msg_type == 'user':
                content = d.get('message', {}).get('content', '')
                if isinstance(content, list):
                    text_parts = [p.get('text', '') for p in content if p.get('type') == 'text']
                    content = '\n'.join(text_parts)
                messages.append(('USER', content))

            elif msg_type == 'assistant':
                content = d.get('message', {}).get('content', '')
                if isinstance(content, list):
                    text_parts = []
                    for p in content:
                        if p.get('type') == 'text':
                            text_parts.append(p.get('text', ''))
                        elif p.get('type') == 'tool_use':
                            tool = p.get('name', 'unknown')
                            text_parts.append(f"[Tool: {tool}]")
                    content = '\n'.join(text_parts)
                messages.append(('ASSISTANT', content))
        except:
            pass

print("=" * 80)
print(f"CLAUDE CODE SESSION EXPORT")
print(f"Session ID: $session_id")
print(f"Exported: {datetime.now().isoformat()}")
print("=" * 80)
print()

for role, content in messages:
    print(f"{'─' * 40}")
    print(f"[{role}]")
    print(f"{'─' * 40}")
    print(content[:50000] if content else "(empty)")
    print()
EOF

    echo "  -> $output_file ($(wc -l < "$output_file") lines)"
}

case "${1:-latest}" in
    latest)
        latest=$(ls -t "$PROJECT_DIR"/*.jsonl 2>/dev/null | grep -v agent | head -1)
        if [ -n "$latest" ]; then
            export_session "$latest"
        else
            echo "No sessions found"
        fi
        ;;
    all)
        for f in "$PROJECT_DIR"/*.jsonl; do
            [[ "$f" == *agent* ]] && continue
            export_session "$f"
        done
        echo ""
        echo "All sessions exported to: $OUTPUT_DIR"
        ;;
    *)
        target="$PROJECT_DIR/$1.jsonl"
        if [ -f "$target" ]; then
            export_session "$target"
        else
            echo "Session not found: $1"
            echo "Available sessions:"
            ls "$PROJECT_DIR"/*.jsonl 2>/dev/null | grep -v agent | xargs -n1 basename | sed 's/.jsonl//'
        fi
        ;;
esac

echo ""
echo "Export complete!"
