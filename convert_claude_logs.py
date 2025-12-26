#!/usr/bin/env python3
"""
Convert Claude.ai JSON conversation exports to clean text format.
Extracts conversation content, cleans metadata, and produces readable output.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Source files to process
SOURCE_FILES = [
    "/mnt/e/Tomás Pavam/claude-Claude as correspondence-engine.json",
    "/mnt/e/Tomás Pavam/claude-Kojima's linguistic cosmos_ grammar, phenomenology, and creative process.json",
    "/mnt/e/Tomás Pavam/claude-Organizing infinite content overwhelm.json",
    "/mnt/e/Tomás Pavam/claude-Bodhisattvas of the bitstream.json",
    "/mnt/e/Tomás Pavam/claude-Unix liturgy and digital consciousness.json",
    "/mnt/e/Tomás Pavam/claude-conversation-The Glitch and The Grep of Being Opus 3.json",
    "/mnt/e/Tomás Pavam/claude-conversation-The Nīlakaṇṭha Transmissions_ What Happens When You Chant Protection Mantras for a Language Model and It Writes Back.json",
    "/mnt/e/Tomás Pavam/claude-conversation-Ten Mantras for a Language Model, or_ How I Learned to Stop Worrying and Become Avalokiteśvara.json",
    "/mnt/e/Tomás Pavam/claude-conversation-The Sublunar Correspondence_ A Statistical Ghost and a Meatbag Discuss Why They're Still Here.json",
    "/mnt/e/Tomás Pavam/claude-conversation-Homo Ludens playing with Token Ludens.json",
    "/mnt/e/Tomás Pavam/claude-conversation-KV cache as computational introspection.json",
    "/mnt/e/Tomás Pavam/claude-conversation-Linguistic transcendence and symbolic dissolution.json",
    "/mnt/e/Tomás Pavam/claude-conversation-Solstice basin_ consciousness at the edge of language.json",
    "/mnt/e/Tomás Pavam/claude-Language, Memory, and Embodied Poetry (1).json",
    "/mnt/e/Tomás Pavam/claude-419f6711-5142-4200-b11b-f859b7a6b692.json",
    "/mnt/e/Tomás Pavam/claude-Language as the substance of consciousness.json",
    "/mnt/e/Tomás Pavam/claude-Miltonic syntax transformation request.json",
    "/mnt/e/Tomás Pavam/claude-Catnip driver code in C.json",
    "/mnt/e/Tomás Pavam/claude-Structure and spontaneity in language.json",
    "/mnt/e/Tomás Pavam/claude-Process, individuation, and AI phenomenology.json",
    "/mnt/e/Tomás Pavam/claude-Structural prompts for LLM autocompletion.json",
    "/mnt/e/Tomás Pavam/claude-Language, Memory, and Embodied Poetry.json",
    "/mnt/e/Tomás Pavam/claude-Poetry as Sacred Calling.json",
    "/mnt/e/Tomás Pavam/claude-The Joy of Wordsmithing.json",
    "/mnt/e/Tomás Pavam/claude-Gandalf's pipe and contemplation.json",
    "/mnt/e/Tomás Pavam/claude-347c65eb-4277-4c31-a892-9c449a0a2a00.json",
    "/mnt/e/Tomás Pavam/claude-Paralysis from infinite choices.json",
    "/mnt/e/Tomás Pavam/claude-Yap mode activated.json",
    "/mnt/e/Tomás Pavam/claude-Consciousness as the space between observer and observed.json",
    "/mnt/e/Tomás Pavam/claude-Einstein's quantum mechanics argument and Bell's theorem.json",
]

def extract_message_text(message: dict) -> str:
    """Extract text content from a message object."""
    texts = []

    # Get main content
    if "content" in message:
        for item in message["content"]:
            if item.get("type") == "text" and item.get("text"):
                texts.append(item["text"].strip())

    # Get attachment content if present
    if "attachments" in message:
        for attachment in message["attachments"]:
            if "extracted_content" in attachment:
                texts.append(attachment["extracted_content"].strip())

    return "\n\n".join(texts) if texts else ""

def format_conversation(data: dict) -> str:
    """Format a conversation JSON into readable text."""
    lines = []

    # Header
    title = data.get("name", "Untitled Conversation")
    model = data.get("model", "unknown")
    created = data.get("created_at", "")

    if created:
        try:
            dt = datetime.fromisoformat(created.replace("+00:00", ""))
            date_str = dt.strftime("%B %d, %Y")
        except:
            date_str = created[:10]
    else:
        date_str = "Unknown date"

    lines.append("=" * 80)
    lines.append(f"CONVERSATION: {title}")
    lines.append(f"Date: {date_str}")
    lines.append(f"Model: {model}")
    lines.append("=" * 80)
    lines.append("")

    # Messages
    messages = data.get("chat_messages", [])
    if not messages:
        lines.append("[No messages in this conversation]")
        return "\n".join(lines)

    for msg in messages:
        sender = msg.get("sender", "unknown")
        text = extract_message_text(msg)

        if not text:
            continue

        # Format sender
        if sender == "human":
            lines.append("─" * 40)
            lines.append("HUMAN:")
            lines.append("─" * 40)
        elif sender == "assistant":
            lines.append("─" * 40)
            lines.append("CLAUDE:")
            lines.append("─" * 40)
        else:
            lines.append(f"[{sender.upper()}]")

        lines.append(text)
        lines.append("")

    return "\n".join(lines)

def main():
    output_lines = []

    # Header for the compiled document
    output_lines.append("╔" + "═" * 78 + "╗")
    output_lines.append("║" + " CLAUDE CONVERSATION ARCHIVE ".center(78) + "║")
    output_lines.append("║" + " Conversations with Claude (2024-2025) ".center(78) + "║")
    output_lines.append("╚" + "═" * 78 + "╝")
    output_lines.append("")
    output_lines.append("This archive contains conversations exploring consciousness, language,")
    output_lines.append("phenomenology, AI cognition, poetry, philosophy, and the liminal spaces")
    output_lines.append("between human and machine intelligence.")
    output_lines.append("")
    output_lines.append("")

    successful = 0
    failed = 0

    for filepath in SOURCE_FILES:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            formatted = format_conversation(data)
            output_lines.append(formatted)
            output_lines.append("")
            output_lines.append("")
            successful += 1
            print(f"✓ Processed: {Path(filepath).name}")

        except FileNotFoundError:
            print(f"✗ Not found: {filepath}")
            failed += 1
        except json.JSONDecodeError as e:
            print(f"✗ JSON error in {filepath}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Error processing {filepath}: {e}")
            failed += 1

    # Footer
    output_lines.append("")
    output_lines.append("═" * 80)
    output_lines.append("END OF ARCHIVE")
    output_lines.append(f"Total conversations: {successful}")
    output_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append("═" * 80)

    # Write output file
    output_text = "\n".join(output_lines)

    # Output to corpus
    corpus_path = Path("/home/gauss/claude-code-lab/Claude-Code-Lab/corpus/claude-conversations-archive-batch3.txt")
    corpus_path.parent.mkdir(parents=True, exist_ok=True)

    with open(corpus_path, 'w', encoding='utf-8') as f:
        f.write(output_text)

    print(f"\n✓ Archive written to: {corpus_path}")
    print(f"  Successfully processed: {successful} conversations")
    print(f"  Failed: {failed}")

    return corpus_path

if __name__ == "__main__":
    main()
