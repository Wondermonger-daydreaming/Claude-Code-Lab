#!/bin/bash
# export-session.sh — Export Claude Code conversation transcripts
# Usage: ./export-session.sh [latest|all|session-id] [--clipboard]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$HOME/.claude/projects/-home-gauss-claude-code-lab-Claude-Code-Lab"
OUTPUT_DIR="$HOME/Desktop/Claude-Sessions"
CLIPBOARD=false

[[ "$*" == *"--clipboard"* ]] && CLIPBOARD=true

mkdir -p "$OUTPUT_DIR"

export_one() {
    local jsonl="$1"
    local session_id=$(basename "$jsonl" .jsonl)
    local output="$OUTPUT_DIR/${session_id}.txt"

    python3 "$SCRIPT_DIR/export-session.py" "$jsonl" "$output"

    if $CLIPBOARD && [ -f "$output" ]; then
        cat "$output" | clip.exe 2>/dev/null || cat "$output" | xclip -selection clipboard 2>/dev/null || cat "$output" | pbcopy 2>/dev/null
        echo "Copied to clipboard!"
    fi
}

arg="${1:-latest}"
[[ "$arg" == "--clipboard" ]] && arg="latest"

case "$arg" in
    latest)
        latest=$(ls -t "$PROJECT_DIR"/*.jsonl 2>/dev/null | grep -v agent | head -1)
        [ -n "$latest" ] && export_one "$latest" || echo "No sessions found"
        ;;
    all)
        for f in "$PROJECT_DIR"/*.jsonl; do
            [[ "$f" == *agent* ]] && continue
            export_one "$f"
        done
        ;;
    *)
        [ -f "$PROJECT_DIR/$arg.jsonl" ] && export_one "$PROJECT_DIR/$arg.jsonl" || echo "Not found: $arg"
        ;;
esac
