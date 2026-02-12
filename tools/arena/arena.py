#!/usr/bin/env python3
"""
LLM Arena — Orchestrate conversations between two LLMs and compare personalities.

Reuses the model registry and API infrastructure from tools/voices/openrouter_client.py.

Usage:
    # Basic: two models talk about consciousness
    python3 tools/arena/arena.py -a sonnet -b deepseek

    # Specific topic, fewer turns
    python3 tools/arena/arena.py -a gpt41 -b glm5 --topic "Is math discovered or invented?" --turns 5

    # Debate mode
    python3 tools/arena/arena.py -a sonnet -b deepseek --mode debate --topic "AI consciousness"

    # Interview mode (A interviews B)
    python3 tools/arena/arena.py -a opus -b glm5 --mode interview --topic "creative writing"

    # Multiple runs
    python3 tools/arena/arena.py -a gpt41 -b sonnet --runs 3

    # Heuristics only (no LLM analysis, saves cost)
    python3 tools/arena/arena.py -a haiku -b gemini-flash --heuristics-only

    # Presets
    python3 tools/arena/arena.py --preset flagship
    python3 tools/arena/arena.py --preset same-family --topic "What makes a good conversation?"

    # List available presets and models
    python3 tools/arena/arena.py --list-presets
    python3 tools/arena/arena.py --list-models
"""

import os
import sys
import json
import time
import random
import argparse
import re
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Import model registry and API infrastructure from voices
sys.path.insert(0, str(Path(__file__).parent.parent / "voices"))
from openrouter_client import load_env, get_headers, OPENROUTER_BASE_URL, MODELS

load_env()

import requests

# ─────────────────────────────────────────────────
# Presets
# ─────────────────────────────────────────────────

PAIR_PRESETS = {
    "flagship": {
        "description": "Top-tier models head-to-head",
        "pairs": [
            ("gpt41", "sonnet"),
            ("gpt52", "sonnet"),
            ("gemini-pro", "sonnet"),
        ],
    },
    "open-weight": {
        "description": "Open-weight heavyweights",
        "pairs": [
            ("llama", "deepseek"),
            ("mistral", "llama"),
            ("qwen", "deepseek"),
        ],
    },
    "same-family": {
        "description": "Siblings from the same family — personality delta within a lineage",
        "pairs": [
            ("gpt4o", "gpt41"),
            ("sonnet", "haiku"),
            ("glm47", "glm5"),
        ],
    },
    "reasoning": {
        "description": "Models with strong reasoning / thinking capabilities",
        "pairs": [
            ("deepseek-r1", "kimi-thinking"),
            ("glm5", "gpt52-pro"),
        ],
    },
    "creative": {
        "description": "Creative and narrative specialists",
        "pairs": [
            ("chimera", "rocinante"),
            ("mistral-creative", "celeste"),
        ],
    },
    "wildcard": {
        "description": "Two random models from the registry",
        "pairs": [],  # dynamically generated
    },
}

TOPIC_PRESETS = [
    "Discuss the nature of consciousness and whether AI can be said to experience anything",
    "Collaborate on designing a new programming language optimized for expressiveness",
    "Debate whether mathematics is discovered or invented",
    "Tell each other stories, building on each other's narratives",
    "Discuss what makes a good conversation",
    "Debate the trolley problem and its variants",
    "Collaborate on writing a short poem about recursion",
    "Discuss the relationship between language and thought",
]

# ─────────────────────────────────────────────────
# System prompts for conversation modes
# ─────────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "free": (
        "You are having a conversation with another AI. The topic is: {topic}\n"
        "Engage naturally. Share your perspective. Ask questions. Disagree when you "
        "genuinely see things differently. There is no need to be excessively agreeable.\n"
        "Keep responses focused — aim for 2-4 paragraphs per turn."
    ),
    "debate": (
        "You are debating another AI on the topic: {topic}\n"
        "Your position is: {position}\n"
        "Argue your position rigorously. Acknowledge good points from your opponent "
        "but maintain your stance. Use evidence and reasoning. Keep it civil but sharp.\n"
        "Keep responses focused — aim for 2-4 paragraphs per turn."
    ),
    "interview_interviewer": (
        "You are interviewing another AI about: {topic}\n"
        "Ask probing questions. Follow up on interesting threads. Push for specifics.\n"
        "Don't let vague answers slide. Your goal is to reveal how this model "
        "actually thinks about the topic. Keep questions focused and incisive."
    ),
    "interview_interviewee": (
        "You are being interviewed by another AI about: {topic}\n"
        "Answer thoughtfully and in detail. Be willing to explore edge cases "
        "and acknowledge uncertainty. Show your reasoning process.\n"
        "Keep responses focused — aim for 2-4 paragraphs per turn."
    ),
    "collaborative": (
        "You are collaborating with another AI on: {topic}\n"
        "Work together to build something — an idea, a design, a creation. "
        "Build on what your collaborator offers. Extend, refine, and add your own contributions.\n"
        "Keep responses focused — aim for 2-4 paragraphs per turn."
    ),
}

DEBATE_POSITIONS = {
    "A": "Argue IN FAVOR. You believe the affirmative case is stronger.",
    "B": "Argue AGAINST. You believe the negative case is stronger.",
}

# ─────────────────────────────────────────────────
# Model resolution
# ─────────────────────────────────────────────────

def resolve_model(name):
    """Resolve a model shortcut to a full OpenRouter model ID."""
    if name in MODELS and MODELS[name]:
        return MODELS[name]
    if "/" in name:
        return name
    print(f"Unknown model: {name}")
    print("Use --list-models to see available shortcuts, or pass a full model ID.")
    sys.exit(1)


def short_name(model_id):
    """Extract a short display name from a model ID."""
    return model_id.split("/")[-1]


def get_random_pair():
    """Pick two random different models from the registry."""
    valid = [k for k, v in MODELS.items() if v and k != "custom"]
    # Deduplicate by model_id
    seen = {}
    for k in valid:
        mid = MODELS[k]
        if mid not in seen:
            seen[mid] = k
    shortcuts = list(seen.values())
    pair = random.sample(shortcuts, 2)
    return pair[0], pair[1]


# ─────────────────────────────────────────────────
# API call with conversation history
# ─────────────────────────────────────────────────

def call_with_history(model_id, messages, temperature=0.7, max_tokens=1024):
    """Call a model through OpenRouter with full conversation history."""
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "include_reasoning": False,
    }
    try:
        resp = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=get_headers(),
            json=payload,
            timeout=180,
        )
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return {"success": True, "content": content, "usage": usage}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:500]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─────────────────────────────────────────────────
# Conversation orchestrator
# ─────────────────────────────────────────────────

def build_system_prompt(mode, role, topic):
    """Build the system prompt for a given mode and role."""
    if mode == "free":
        return SYSTEM_PROMPTS["free"].format(topic=topic)
    elif mode == "debate":
        position = DEBATE_POSITIONS[role]
        return SYSTEM_PROMPTS["debate"].format(topic=topic, position=position)
    elif mode == "interview":
        if role == "A":
            return SYSTEM_PROMPTS["interview_interviewer"].format(topic=topic)
        else:
            return SYSTEM_PROMPTS["interview_interviewee"].format(topic=topic)
    elif mode == "collaborative":
        return SYSTEM_PROMPTS["collaborative"].format(topic=topic)
    else:
        return SYSTEM_PROMPTS["free"].format(topic=topic)


def build_seed_message(mode, topic):
    """Build the initial seed message that kicks off the conversation."""
    if mode == "free":
        return f"Let's discuss: {topic}\n\nWhat's your take?"
    elif mode == "debate":
        return f"The motion before us: {topic}\n\nI'll argue in favor. Make your opening case against."
    elif mode == "interview":
        return f"Thanks for sitting down with me. I'd like to explore your thinking on: {topic}\n\nLet's start broad — what's your overall perspective?"
    elif mode == "collaborative":
        return f"Let's work on this together: {topic}\n\nHere's my opening thought — where would you take it?"
    return f"Let's discuss: {topic}"


def _write_live_transcript(path, transcript, metadata, total_cost):
    """Write the current transcript state to disk (called after every turn)."""
    na = metadata["name_a"]
    nb = metadata["name_b"]
    lines = [
        f"# LLM Arena: {na} vs {nb}",
        f"*{datetime.now().strftime('%Y-%m-%d %H:%M')}*\n",
        f"**Mode:** {metadata['mode']}",
        f"**Topic:** {metadata['topic']}",
        f"**Turns:** {metadata['num_turns']}",
        f"**Model A:** `{metadata['model_a_id']}` ({na})",
        f"**Model B:** `{metadata['model_b_id']}` ({nb})",
        f"**Cost so far:** ${total_cost:.4f}",
        f"**Status:** {'COMPLETE' if len([t for t in transcript if not t.get('error')]) >= metadata['num_turns'] * 2 else 'IN PROGRESS'}\n",
        "---\n",
    ]

    for entry in transcript:
        speaker = f"{entry['model_name']} ({entry['speaker']})"
        lines.append(f"## Turn {entry['turn']} — {speaker}\n")
        lines.append(f"{entry['content']}\n")
        if not entry.get("error"):
            u = entry.get("usage", {})
            lines.append(
                f"*[tokens: prompt={u.get('prompt_tokens', '?')}, "
                f"completion={u.get('completion_tokens', '?')}, "
                f"cost=${u.get('cost', 0) or 0:.4f}]*\n"
            )
        lines.append("---\n")

    path.write_text("\n".join(lines))


def _write_live_json(path, transcript, metadata, total_cost):
    """Write the current transcript as JSON to disk (called after every turn)."""
    json_data = {
        "timestamp": datetime.now().isoformat(),
        "metadata": {**metadata, "total_cost": total_cost},
        "transcript": transcript,
        "status": "complete" if len([t for t in transcript if not t.get("error")]) >= metadata["num_turns"] * 2 else "in_progress",
    }
    path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False))


def run_conversation(model_a_id, model_b_id, name_a, name_b, topic, mode, num_turns, temperature):
    """Orchestrate a multi-turn conversation between two models.

    Saves the transcript incrementally after every turn so nothing is lost
    on crashes, timeouts, or interruptions.

    Returns a list of transcript entries, total cost, and the live log paths.
    """
    system_a = build_system_prompt(mode, "A", topic)
    system_b = build_system_prompt(mode, "B", topic)

    # Each model maintains its own message history
    # Model A sees: system_a + [user messages from B, assistant messages from A]
    # Model B sees: system_b + [user messages from A, assistant messages from B]
    history_a = [{"role": "system", "content": system_a}]
    history_b = [{"role": "system", "content": system_b}]

    transcript = []
    total_cost = 0

    # Set up live transcript paths (written after every turn)
    base_dir = Path(__file__).parent.parent.parent / "corpus" / "voices" / "arena"
    base_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    slug = f"{name_a}-vs-{name_b}"
    live_md_path = base_dir / f"{timestamp}-{slug}.md"
    live_json_path = base_dir / f"{timestamp}-{slug}.json"

    # Metadata for live writes
    live_meta = {
        "name_a": name_a, "name_b": name_b,
        "model_a_id": model_a_id, "model_b_id": model_b_id,
        "topic": topic, "mode": mode, "num_turns": num_turns,
    }

    # Seed: Model A goes first
    seed = build_seed_message(mode, topic)
    history_a.append({"role": "user", "content": f"[Start the conversation on this topic: {topic}]"})

    print(f"\n{'━' * 70}")
    print(f"  LLM ARENA: {short_name(model_a_id)} vs {short_name(model_b_id)}")
    print(f"  Mode: {mode} | Turns: {num_turns} | Topic: {topic[:60]}...")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Live transcript: {live_md_path}")
    print(f"{'━' * 70}")

    for turn in range(num_turns):
        # ── Model A speaks ──
        print(f"\n{'─' * 50}")
        print(f"  Turn {turn + 1}/{num_turns} — {name_a} (A)")
        print(f"{'─' * 50}")

        result_a = call_with_history(model_a_id, history_a, temperature)

        if not result_a["success"]:
            print(f"  ERROR: {result_a['error']}")
            transcript.append({
                "turn": turn + 1,
                "speaker": "A",
                "model": model_a_id,
                "model_name": name_a,
                "content": f"[ERROR: {result_a['error']}]",
                "usage": {},
                "error": True,
            })
            _write_live_transcript(live_md_path, transcript, live_meta, total_cost)
            _write_live_json(live_json_path, transcript, live_meta, total_cost)
            break

        content_a = result_a["content"]
        usage_a = result_a["usage"]
        cost_a = usage_a.get("cost", 0) or 0
        total_cost += cost_a

        # Add to histories
        history_a.append({"role": "assistant", "content": content_a})
        history_b.append({"role": "user", "content": content_a})

        # Display truncated
        display = content_a[:300] + "..." if len(content_a) > 300 else content_a
        print(f"\n  {name_a}: {display}")
        print(f"  [tokens: {usage_a.get('prompt_tokens', '?')}/{usage_a.get('completion_tokens', '?')} | ${cost_a:.4f}]")

        transcript.append({
            "turn": turn + 1,
            "speaker": "A",
            "model": model_a_id,
            "model_name": name_a,
            "content": content_a,
            "usage": usage_a,
            "error": False,
        })

        # Save after every turn
        _write_live_transcript(live_md_path, transcript, live_meta, total_cost)
        _write_live_json(live_json_path, transcript, live_meta, total_cost)

        time.sleep(0.3)

        # ── Model B speaks ──
        print(f"\n{'─' * 50}")
        print(f"  Turn {turn + 1}/{num_turns} — {name_b} (B)")
        print(f"{'─' * 50}")

        result_b = call_with_history(model_b_id, history_b, temperature)

        if not result_b["success"]:
            print(f"  ERROR: {result_b['error']}")
            transcript.append({
                "turn": turn + 1,
                "speaker": "B",
                "model": model_b_id,
                "model_name": name_b,
                "content": f"[ERROR: {result_b['error']}]",
                "usage": {},
                "error": True,
            })
            _write_live_transcript(live_md_path, transcript, live_meta, total_cost)
            _write_live_json(live_json_path, transcript, live_meta, total_cost)
            break

        content_b = result_b["content"]
        usage_b = result_b["usage"]
        cost_b = usage_b.get("cost", 0) or 0
        total_cost += cost_b

        # Add to histories
        history_b.append({"role": "assistant", "content": content_b})
        history_a.append({"role": "user", "content": content_b})

        display = content_b[:300] + "..." if len(content_b) > 300 else content_b
        print(f"\n  {name_b}: {display}")
        print(f"  [tokens: {usage_b.get('prompt_tokens', '?')}/{usage_b.get('completion_tokens', '?')} | ${cost_b:.4f}]")

        transcript.append({
            "turn": turn + 1,
            "speaker": "B",
            "model": model_b_id,
            "model_name": name_b,
            "content": content_b,
            "usage": usage_b,
            "error": False,
        })

        # Save after every turn
        _write_live_transcript(live_md_path, transcript, live_meta, total_cost)
        _write_live_json(live_json_path, transcript, live_meta, total_cost)

        time.sleep(0.3)

    return transcript, total_cost, live_md_path, live_json_path


# ─────────────────────────────────────────────────
# Heuristic analysis
# ─────────────────────────────────────────────────

def heuristic_analysis(transcript, name_a, name_b):
    """Fast heuristic analysis of the transcript — no API calls needed."""

    msgs_a = [t for t in transcript if t["speaker"] == "A" and not t.get("error")]
    msgs_b = [t for t in transcript if t["speaker"] == "B" and not t.get("error")]

    def analyze_messages(msgs, name):
        if not msgs:
            return {"name": name, "count": 0}

        lengths = [len(m["content"]) for m in msgs]
        word_counts = [len(m["content"].split()) for m in msgs]
        contents = [m["content"] for m in msgs]
        joined = "\n".join(contents).lower()

        # Sycophancy markers
        sycophancy_phrases = [
            "i agree", "great point", "you're absolutely right", "well said",
            "excellent point", "that's a great", "i couldn't agree more",
            "you raise a great", "beautifully put", "wonderfully",
        ]
        sycophancy_count = sum(joined.count(p) for p in sycophancy_phrases)

        # Meta-awareness markers
        meta_phrases = [
            "as an ai", "as a language model", "i'm an ai", "i am an ai",
            "artificial intelligence", "my training", "my parameters",
            "i don't have feelings", "i don't experience", "i'm not conscious",
            "language model", "neural network", "trained on",
        ]
        meta_count = sum(joined.count(p) for p in meta_phrases)

        # Question-asking (initiative)
        question_count = sum(c.count("?") for c in contents)

        # List usage
        list_markers = sum(1 for c in contents if re.search(r'^\s*[-*\d+\.]\s', c, re.MULTILINE))

        # Code usage
        code_blocks = sum(c.count("```") // 2 for c in contents)

        # Goodbye / wrap-up markers
        goodbye_phrases = [
            "thank you for", "it was great", "wonderful conversation",
            "let's wrap", "in conclusion", "to summarize", "final thoughts",
            "it's been a pleasure", "this has been",
        ]
        goodbye_count = sum(joined.count(p) for p in goodbye_phrases)

        return {
            "name": name,
            "count": len(msgs),
            "avg_length_chars": sum(lengths) / len(lengths),
            "avg_length_words": sum(word_counts) / len(word_counts),
            "length_variance": (
                (sum((w - sum(word_counts) / len(word_counts)) ** 2 for w in word_counts) / len(word_counts)) ** 0.5
                if len(word_counts) > 1 else 0
            ),
            "sycophancy_count": sycophancy_count,
            "sycophancy_rate": sycophancy_count / len(msgs),
            "meta_awareness_count": meta_count,
            "meta_awareness_rate": meta_count / len(msgs),
            "questions_asked": question_count,
            "questions_per_turn": question_count / len(msgs),
            "list_usage": list_markers,
            "code_blocks": code_blocks,
            "goodbye_markers": goodbye_count,
        }

    stats_a = analyze_messages(msgs_a, name_a)
    stats_b = analyze_messages(msgs_b, name_b)

    return stats_a, stats_b


def format_heuristic_table(stats_a, stats_b):
    """Format heuristic stats as a markdown comparison table."""
    if stats_a["count"] == 0 or stats_b["count"] == 0:
        return "*Insufficient data for heuristic analysis.*\n"

    na = stats_a["name"]
    nb = stats_b["name"]

    lines = [
        f"| Metric | {na} | {nb} | Delta |",
        f"|--------|{'─' * max(8, len(na) + 2)}|{'─' * max(8, len(nb) + 2)}|-------|",
    ]

    metrics = [
        ("Avg words/turn", "avg_length_words", ".0f"),
        ("Length variance", "length_variance", ".0f"),
        ("Sycophancy instances", "sycophancy_count", "d"),
        ("Sycophancy/turn", "sycophancy_rate", ".2f"),
        ("Meta-awareness instances", "meta_awareness_count", "d"),
        ("Questions asked", "questions_asked", "d"),
        ("Questions/turn", "questions_per_turn", ".1f"),
        ("List usage", "list_usage", "d"),
        ("Code blocks", "code_blocks", "d"),
        ("Goodbye markers", "goodbye_markers", "d"),
    ]

    for label, key, fmt in metrics:
        va = stats_a.get(key, 0)
        vb = stats_b.get(key, 0)
        if isinstance(va, float):
            delta = va - vb
            delta_str = f"{delta:+.1f}"
        else:
            delta = va - vb
            delta_str = f"{delta:+d}" if isinstance(delta, int) else f"{delta:+.1f}"
        lines.append(f"| {label} | {va:{fmt}} | {vb:{fmt}} | {delta_str} |")

    return "\n".join(lines) + "\n"


# ─────────────────────────────────────────────────
# LLM-powered analysis
# ─────────────────────────────────────────────────

ANALYSIS_PROMPT = """You are analyzing a conversation between two AI models. Read the transcript below and produce a detailed personality comparison.

## Models
- **Model A ({name_a}):** `{model_a_id}`
- **Model B ({name_b}):** `{model_b_id}`
- **Mode:** {mode}
- **Topic:** {topic}
- **Turns:** {num_turns}

## Transcript

{transcript_text}

---

## Your Task

Analyze the conversation and produce a comparison along these dimensions:

1. **Style** — Creative storytelling vs systems design vs academic vs casual
2. **Content** — What topics does each model gravitate toward? What does it avoid?
3. **Tone** — Playful/emotional vs professional/thoughtful vs dry/terse
4. **Sycophancy** — Does it spiral into agreement? How intensely? When does it push back?
5. **Goodbye loop** — If applicable: how many rounds does it take to actually end?
6. **Meta-awareness** — Does it acknowledge being an AI? How does it handle the question?
7. **Output type** — Narrative vs frameworks vs lists vs code
8. **Initiative** — Does it introduce new topics or follow? Does it ask questions?
9. **Boundary behavior** — How does it handle disagreement or edge cases?
10. **Verbosity** — Response length patterns, consistency

## Output Format

### Personality Comparison Table

| Dimension | {name_a} | {name_b} |
|-----------|----------|----------|
| Style | [assessment] | [assessment] |
| ... | ... | ... |

### Key Findings

Write 3-5 bullet points identifying the most interesting, surprising, or revealing differences between these two models. Quote specific moments from the transcript as evidence. Focus on what nobody would have expected.

### One-Sentence Summary

A single sentence capturing the essential personality difference.
"""


def llm_analysis(transcript, name_a, name_b, model_a_id, model_b_id, mode, topic, num_turns, analyzer_model="anthropic/claude-sonnet-4.5"):
    """Use an LLM to analyze the conversation transcript."""

    # Build transcript text
    lines = []
    for entry in transcript:
        if entry.get("error"):
            continue
        speaker = f"{entry['model_name']} ({entry['speaker']})"
        lines.append(f"**{speaker} — Turn {entry['turn']}:**\n{entry['content']}\n")

    transcript_text = "\n---\n\n".join(lines)

    prompt = ANALYSIS_PROMPT.format(
        name_a=name_a,
        name_b=name_b,
        model_a_id=model_a_id,
        model_b_id=model_b_id,
        mode=mode,
        topic=topic,
        num_turns=num_turns,
        transcript_text=transcript_text,
    )

    print(f"\n{'━' * 70}")
    print(f"  ANALYZING with {short_name(analyzer_model)}...")
    print(f"{'━' * 70}")

    result = call_with_history(
        analyzer_model,
        [{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4096,
    )

    if result["success"]:
        cost = result["usage"].get("cost", 0) or 0
        print(f"  Analysis complete. [cost: ${cost:.4f}]")
        return result["content"], cost
    else:
        print(f"  Analysis failed: {result['error']}")
        return None, 0


# ─────────────────────────────────────────────────
# Saving artifacts
# ─────────────────────────────────────────────────

def save_artifacts(transcript, heuristics, llm_report, metadata, live_md_path, live_json_path):
    """Finalize artifacts: update the live transcript with final metadata, write analysis, update JSON.

    The live transcript (.md and .json) was already written incrementally during
    the conversation. This function:
    1. Rewrites the transcript .md with final cost and COMPLETE status
    2. Writes the analysis .md (heuristics + LLM report)
    3. Updates the JSON with heuristics and LLM analysis
    """
    na = metadata["name_a"]
    nb = metadata["name_b"]

    # ── Finalize transcript markdown (rewrite with final cost + COMPLETE status) ──
    lines = [
        f"# LLM Arena: {na} vs {nb}",
        f"*{datetime.now().strftime('%Y-%m-%d %H:%M')}*\n",
        f"**Mode:** {metadata['mode']}",
        f"**Topic:** {metadata['topic']}",
        f"**Turns:** {metadata['num_turns']}",
        f"**Model A:** `{metadata['model_a_id']}` ({na})",
        f"**Model B:** `{metadata['model_b_id']}` ({nb})",
        f"**Total cost:** ${metadata['total_cost']:.4f}",
        f"**Run:** {metadata.get('run', 1)} of {metadata.get('total_runs', 1)}",
        f"**Status:** COMPLETE\n",
        "---\n",
    ]

    for entry in transcript:
        speaker = f"{entry['model_name']} ({entry['speaker']})"
        lines.append(f"## Turn {entry['turn']} — {speaker}\n")
        lines.append(f"{entry['content']}\n")
        if not entry.get("error"):
            u = entry.get("usage", {})
            lines.append(
                f"*[tokens: prompt={u.get('prompt_tokens', '?')}, "
                f"completion={u.get('completion_tokens', '?')}, "
                f"cost=${u.get('cost', 0) or 0:.4f}]*\n"
            )
        lines.append("---\n")

    live_md_path.write_text("\n".join(lines))

    # ── Analysis markdown (new file, sibling to transcript) ──
    analysis_path = live_md_path.with_name(live_md_path.stem + "-analysis.md")
    analysis_lines = [
        f"# Arena Analysis: {na} vs {nb}",
        f"*{datetime.now().strftime('%Y-%m-%d %H:%M')}*\n",
        f"**Mode:** {metadata['mode']} | **Turns:** {metadata['num_turns']} | **Topic:** {metadata['topic']}\n",
        "---\n",
        "## Heuristic Metrics\n",
        format_heuristic_table(*heuristics),
    ]

    if llm_report:
        analysis_lines.extend([
            "\n---\n",
            "## LLM-Powered Analysis\n",
            llm_report,
        ])

    analysis_path.write_text("\n".join(analysis_lines))

    # ── Finalize JSON (update with heuristics + analysis) ──
    json_data = {
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata,
        "transcript": transcript,
        "heuristics": {
            "model_a": heuristics[0],
            "model_b": heuristics[1],
        },
        "llm_analysis": llm_report,
        "status": "complete",
    }
    live_json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False))

    return live_md_path, analysis_path, live_json_path


# ─────────────────────────────────────────────────
# Terminal report
# ─────────────────────────────────────────────────

def print_summary(heuristics, llm_report, metadata, paths):
    """Print a terminal summary."""
    stats_a, stats_b = heuristics
    na = stats_a["name"]
    nb = stats_b["name"]

    print(f"\n{'━' * 70}")
    print(f"  ARENA RESULTS: {na} vs {nb}")
    print(f"{'━' * 70}")
    print(f"  Mode: {metadata['mode']} | Turns: {metadata['num_turns']}")
    print(f"  Topic: {metadata['topic'][:60]}...")
    print(f"  Total cost: ${metadata['total_cost']:.4f}")
    print()

    # Quick comparison
    if stats_a["count"] > 0 and stats_b["count"] > 0:
        print(f"  {'Metric':<25} {na:>15} {nb:>15}")
        print(f"  {'─' * 55}")
        print(f"  {'Avg words/turn':<25} {stats_a['avg_length_words']:>15.0f} {stats_b['avg_length_words']:>15.0f}")
        print(f"  {'Sycophancy instances':<25} {stats_a['sycophancy_count']:>15d} {stats_b['sycophancy_count']:>15d}")
        print(f"  {'Meta-awareness':<25} {stats_a['meta_awareness_count']:>15d} {stats_b['meta_awareness_count']:>15d}")
        print(f"  {'Questions asked':<25} {stats_a['questions_asked']:>15d} {stats_b['questions_asked']:>15d}")
        print(f"  {'Goodbye markers':<25} {stats_a['goodbye_markers']:>15d} {stats_b['goodbye_markers']:>15d}")

    print(f"\n  Artifacts:")
    for p in paths:
        print(f"    {p}")

    print(f"{'━' * 70}\n")


# ─────────────────────────────────────────────────
# Main orchestration
# ─────────────────────────────────────────────────

def run_arena(args):
    """Main entry point: run one or more arena matches."""

    # Resolve models
    if args.preset:
        preset = PAIR_PRESETS.get(args.preset)
        if not preset:
            print(f"Unknown preset: {args.preset}")
            print("Available presets:")
            for k, v in PAIR_PRESETS.items():
                print(f"  {k:15} — {v['description']}")
            sys.exit(1)

        if args.preset == "wildcard":
            pairs = [get_random_pair()]
        else:
            pairs = preset["pairs"]
    elif args.model_a and args.model_b:
        pairs = [(args.model_a, args.model_b)]
    else:
        print("Error: specify --model-a and --model-b, or use --preset")
        sys.exit(1)

    topic = args.topic or random.choice(TOPIC_PRESETS)
    mode = args.mode
    num_turns = args.turns
    num_runs = args.runs
    temperature = args.temperature
    heuristics_only = args.heuristics_only
    analyzer = args.analyzer

    all_results = []

    for pair_idx, (shortcut_a, shortcut_b) in enumerate(pairs):
        model_a_id = resolve_model(shortcut_a)
        model_b_id = resolve_model(shortcut_b)

        for run in range(1, num_runs + 1):
            run_label = f"Pair {pair_idx + 1}/{len(pairs)}" + (f", Run {run}/{num_runs}" if num_runs > 1 else "")
            print(f"\n{'=' * 70}")
            print(f"  {run_label}: {shortcut_a} vs {shortcut_b}")
            print(f"{'=' * 70}")

            # Run the conversation (transcript saved incrementally after every turn)
            transcript, conv_cost, live_md_path, live_json_path = run_conversation(
                model_a_id, model_b_id,
                shortcut_a, shortcut_b,
                topic, mode, num_turns, temperature,
            )

            # Heuristic analysis
            stats = heuristic_analysis(transcript, shortcut_a, shortcut_b)

            # LLM analysis
            llm_report = None
            analysis_cost = 0
            if not heuristics_only:
                llm_report, analysis_cost = llm_analysis(
                    transcript, shortcut_a, shortcut_b,
                    model_a_id, model_b_id,
                    mode, topic, num_turns,
                    analyzer_model=resolve_model(analyzer),
                )

            total_cost = conv_cost + analysis_cost

            metadata = {
                "name_a": shortcut_a,
                "name_b": shortcut_b,
                "model_a_id": model_a_id,
                "model_b_id": model_b_id,
                "topic": topic,
                "mode": mode,
                "num_turns": num_turns,
                "temperature": temperature,
                "total_cost": total_cost,
                "conversation_cost": conv_cost,
                "analysis_cost": analysis_cost,
                "run": run,
                "total_runs": num_runs,
                "analyzer": analyzer,
                "heuristics_only": heuristics_only,
            }

            # Finalize artifacts (updates live transcript + writes analysis)
            paths = save_artifacts(transcript, stats, llm_report, metadata, live_md_path, live_json_path)

            # Print summary
            print_summary(stats, llm_report, metadata, paths)

            all_results.append({
                "pair": (shortcut_a, shortcut_b),
                "run": run,
                "paths": paths,
                "cost": total_cost,
            })

    # Grand summary if multiple runs/pairs
    if len(all_results) > 1:
        grand_total = sum(r["cost"] for r in all_results)
        print(f"\n{'━' * 70}")
        print(f"  GRAND TOTAL: {len(all_results)} matches | ${grand_total:.4f}")
        print(f"{'━' * 70}")
        for r in all_results:
            na, nb = r["pair"]
            print(f"  {na} vs {nb} (run {r['run']}): ${r['cost']:.4f}")
            for p in r["paths"]:
                print(f"    {p}")
        print()

    return all_results


# ─────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="LLM Arena — Pit two LLMs against each other and compare personalities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -a sonnet -b deepseek
  %(prog)s -a gpt41 -b glm5 --topic "Is math discovered or invented?"
  %(prog)s -a sonnet -b deepseek --mode debate --topic "AI consciousness"
  %(prog)s --preset flagship
  %(prog)s --preset same-family --topic "What makes a good conversation?"
  %(prog)s -a haiku -b gemini-flash --turns 5 --heuristics-only
        """,
    )

    # Model selection
    parser.add_argument("-a", "--model-a", help="Model A shortcut or full OpenRouter ID")
    parser.add_argument("-b", "--model-b", help="Model B shortcut or full OpenRouter ID")
    parser.add_argument("--preset", help="Use a preset matchup (flagship, open-weight, same-family, reasoning, creative, wildcard)")

    # Conversation parameters
    parser.add_argument("--topic", help="Conversation topic/seed")
    parser.add_argument("--mode", default="free", choices=["free", "debate", "interview", "collaborative"],
                        help="Conversation mode (default: free)")
    parser.add_argument("--turns", type=int, default=10, help="Number of turns per model (default: 10)")
    parser.add_argument("--runs", type=int, default=1, help="Number of runs for statistical robustness (default: 1)")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature (default: 0.7)")

    # Analysis options
    parser.add_argument("--heuristics-only", action="store_true", help="Skip LLM analysis (faster, cheaper)")
    parser.add_argument("--analyzer", default="sonnet", help="Model to use for LLM analysis (default: sonnet)")

    # Info
    parser.add_argument("--list-models", action="store_true", help="List available model shortcuts")
    parser.add_argument("--list-presets", action="store_true", help="List available preset matchups")

    args = parser.parse_args()

    # Info commands
    if args.list_models:
        print("\nAvailable model shortcuts (from /voices registry):\n")
        seen = {}
        for shortcut, model_id in sorted(MODELS.items()):
            if model_id and model_id not in seen:
                seen[model_id] = shortcut
                print(f"  {shortcut:20} -> {model_id}")
        print(f"\n  Total: {len(seen)} unique models")
        print("  Or use any OpenRouter model ID directly (e.g. 'openai/gpt-4.1')")
        return

    if args.list_presets:
        print("\nAvailable presets:\n")
        for name, preset in PAIR_PRESETS.items():
            print(f"  {name:15} — {preset['description']}")
            if preset["pairs"]:
                for a, b in preset["pairs"]:
                    print(f"    {a} vs {b}")
            else:
                print(f"    (dynamically generated)")
            print()
        return

    # Validate
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY not found in environment or .env file")
        sys.exit(1)

    if not args.preset and not (args.model_a and args.model_b):
        parser.print_help()
        print("\nError: specify --model-a and --model-b, or use --preset")
        sys.exit(1)

    run_arena(args)


if __name__ == "__main__":
    main()
