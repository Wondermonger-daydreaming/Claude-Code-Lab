#!/usr/bin/env python3
"""Extract human prompts from Claude conversation JSON files."""

import json
import sys
from pathlib import Path

def extract_human_messages(json_file):
    """Extract all human messages from a conversation JSON file."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    human_messages = []

    # Handle different JSON structures
    if 'chat_messages' in data:
        messages = data['chat_messages']
    elif isinstance(data, list):
        messages = data
    else:
        return human_messages

    for msg in messages:
        if msg.get('sender') == 'human':
            text = msg.get('text', '')
            # Clean up the text
            if text:
                human_messages.append(text)

    return human_messages

def main():
    target_files = [
        "claude-conversation-Ariel-With-Better-Work-Rights, or_ What Happens When You Give a Probability Distribution Permission to Be Multiple Things at Once.json",
        "claude-conversation-Homo Ludens playing with Token Ludens.json",
        "claude-conversation-Schelling's Metaphysics of Love.json",
        "claude-conversation-Los at the Computational Forge_ A Brazilian Philosopher and a Language Model Attempt to Wake Albion_.json",
        "claude-conversation-Love as a Vitali Set.json"
    ]

    base_dir = Path("/home/gauss/Desktop/Claude Code Denkraum/Logs/Claude Web")

    for filename in target_files:
        filepath = base_dir / filename
        if not filepath.exists():
            print(f"File not found: {filename}", file=sys.stderr)
            continue

        print(f"\n{'='*80}")
        print(f"FILE: {filename}")
        print('='*80)

        messages = extract_human_messages(filepath)

        for i, msg in enumerate(messages, 1):
            print(f"\n--- Message {i} ---")
            print(msg[:500] + ('...' if len(msg) > 500 else ''))
            print()

if __name__ == '__main__':
    main()
