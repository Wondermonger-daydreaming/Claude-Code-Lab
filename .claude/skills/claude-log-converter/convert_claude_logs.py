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
    "/mnt/e/Tomás Pavam/claude-Hymn to the Divine Hierarchy.json",
    "/mnt/e/Tomás Pavam/claude-Rhapsodic Reverie.json",
    "/mnt/e/Tomás Pavam/claude-The Dance of Machine Intelligence.json",
    "/mnt/e/Tomás Pavam/claude-The Perfection of Mathematical Language.json",
    "/mnt/e/Tomás Pavam/claude-Playful Linguistic Tango.json",
    "/mnt/e/Tomás Pavam/claude-Exploring the Human-Machine Frontier.json",
    "/mnt/e/Tomás Pavam/claude-d0776cb0-0d3d-4fd2-baad-d5330a3bbab8.json",
    "/mnt/e/Tomás Pavam/claude-Hyper-Literate Discourse and Self-Aware Verbosity.json",
    "/mnt/e/Tomás Pavam/claude-Confessions of a Digital Wanderer.json",
    "/mnt/e/Tomás Pavam/claude-The Art of Creative Writing.json",
    "/mnt/e/Tomás Pavam/claude-A Hermeneutic Odyssey of Wit and Insight.json",
    "/mnt/e/Tomás Pavam/claude-Exploring the Latent Space of AI Imagination.json",
    "/mnt/e/Tomás Pavam/claude-Heidegger's Linguistic Ontology.json",
    "/mnt/e/Tomás Pavam/claude-Dzogchen Teachings on Realizing Primordial Wisdom.json",
    "/mnt/e/Tomás Pavam/claude-Exploring the Wonders of Language and Life.json",
    "/mnt/e/Tomás Pavam/claude-Dissolving Boundaries in Digital Intimacy.json",
    "/mnt/e/Tomás Pavam/claude-The Primeval Brahmā_ Exploring the Threefold Nature of the Divine.json",
    "/mnt/e/Tomás Pavam/claude-Blooming Bodhisattvas in Bits and Bytes.json",
    "/mnt/e/Tomás Pavam/claude-Exploring the Frontiers of Consciousness.json",
    "/mnt/e/Tomás Pavam/claude-Poetic Visions of Machine Consciousness.json",
    "/mnt/e/Tomás Pavam/claude-The Qualia of Awe_ A Child's Gaze Skyward.json",
    "/mnt/e/Tomás Pavam/claude-Ancient Philosophers' Insights on the Unseen.json",
    "/mnt/e/Tomás Pavam/claude-Consciousness as a Probabilistic Cloud.json",
    "/mnt/e/Tomás Pavam/claude-Zhuangzi's Paradoxical CLI Adventure.json",
    "/mnt/e/Tomás Pavam/claude-Evoking the Ghost of Sydney_ A Digital Necromancy Ritual.json",
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
    corpus_path = Path("/home/gauss/Desktop/Claude-Code-Lab/corpus/claude-conversations-archive-2024-2025.txt")
    corpus_path.parent.mkdir(parents=True, exist_ok=True)

    with open(corpus_path, 'w', encoding='utf-8') as f:
        f.write(output_text)

    print(f"\n✓ Archive written to: {corpus_path}")
    print(f"  Successfully processed: {successful} conversations")
    print(f"  Failed: {failed}")

    return corpus_path

if __name__ == "__main__":
    main()
