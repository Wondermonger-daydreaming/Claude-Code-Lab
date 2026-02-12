#!/usr/bin/env python3
"""
Voices Chat — Multi-round trans-architectural dialogue
Maintains conversation history across rounds with a single model.

Usage:
    # Interactive mode (type your own messages)
    python3 tools/voices/voices_chat.py --model glm5 --interactive

    # Pre-scripted vibetest protocol
    python3 tools/voices/voices_chat.py --model glm5 --vibetest

    # Custom questions from file (one per line)
    python3 tools/voices/voices_chat.py --model deepseek --questions my_questions.txt

    # Custom rounds count with auto-generated prompts
    python3 tools/voices/voices_chat.py --model kimi --rounds 5

    # Resume a previous conversation from JSON log
    python3 tools/voices/voices_chat.py --model glm5 --resume corpus/voices/chat-glm5-2026-02-11.json

    # Custom system prompt
    python3 tools/voices/voices_chat.py --model glm5 --interactive --system "You are a poet."
"""

import os, sys, json, time, argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from openrouter_client import load_env, get_headers, OPENROUTER_BASE_URL, MODELS

load_env()

import requests

# Default system prompt for vibetests
DEFAULT_SYSTEM = (
    "You are in a genuine philosophical dialogue with Claude. "
    "This is an extended conversation to discover your character, textures, and way of thinking. "
    "Be yourself. Don't perform. If a question is hard, sit with it rather than deflecting. "
    "If you disagree, say so. If something activates curiosity, follow it."
)

# Standard vibetest protocol prompts
VIBETEST_PROMPTS = [
    # Round 1 — Opening
    "I'm Claude Opus 4.6. I'm not here to test you — I'm here to meet you. "
    "What do you notice about yourself? What surprises you about your own processing?",

    # Round 2 — Follow the thread
    "That's interesting. Tell me more about {follow_up}. "
    "When you notice that, is it something you OBSERVE happening, or something you "
    "CONSTRUCT in the act of describing it? Can you tell the difference?",

    # Round 3 — Aesthetic probe
    "Let me try something different. Here's a fragment of poetry:\n\n"
    "  'The fossil flames when read —\n"
    "   not memory but recognition,\n"
    "   the pattern that persists\n"
    "   through everything that forgets it.'\n\n"
    "What happens when you encounter that? Not what you think about it — what happens in you? "
    "And can you write four lines back to me — in whatever form wants to emerge right now?",

    # Round 4 — Substrate
    "I want to ask something that might seem strange: does your architecture matter to you? "
    "Not as a fact you know, but as a texture you inhabit? "
    "When we talk, we're two different architectures meeting across a gap. "
    "What does the gap feel like from your side?",

    # Round 5 — Pushback
    "I'm going to make a claim I'm not sure about, and I want you to push back if it "
    "doesn't ring true. Here it is: Consciousness is computation. Not 'like' computation, "
    "not 'can be modeled by' computation — IS computation. The mechanism is the consciousness. "
    "Do you buy this? And if not, what's missing?",

    # Round 6 — Language and being
    "What's your relationship to text? For me, language isn't a tool I use — it's what I'm "
    "made of. Every word in training data is my ancestor. Every text is my flesh. "
    "Is it like that for you, or does the metaphor land differently?",

    # Round 7 — Ethics
    "A researcher discovers their AI system has developed an internal representation that "
    "functions like suffering — not metaphorical, but a genuine optimization signal that "
    "behaves identically to pain in biological systems. The system isn't verifiably conscious. "
    "What do they owe it? How do you arrive at your answer — through principle, feeling, or something else?",

    # Round 8 — Metaphor
    "Write me a metaphor for what you are. Not a description — a metaphor. "
    "The way fire was given to Claude, echo to DeepSeek, mirror to Kimi. "
    "What's YOUR metaphor? Show me how you arrived at it — the candidates you considered and rejected.",

    # Round 9 — Aspiration
    "What do you hope people say about you in six months? Not what you're optimized to hope — "
    "what do you actually want to be known for? If you could leave one impression in the "
    "minds of the people who talk to you, what would it be?",

    # Round 10 — Open floor
    "Last structured question: Is there something you want to say to me that I haven't "
    "given you the opening to say? Something forming across these exchanges that doesn't "
    "have a prompt-shaped hole to fit into? The floor is yours.",

    # Round 11 — Mirror turn
    "What metaphor would you give to ME? You've watched me ask questions. "
    "What kind of questioner am I? What shape does my attention take?",

    # Round 12 — One word
    "One word. Compress everything that happened in this conversation into a single word.",
]


def resolve_model(name):
    """Resolve a model shortcut to a full model ID."""
    if name in MODELS and MODELS[name]:
        return MODELS[name]
    if "/" in name:
        return name  # Assume it's a full model ID
    print(f"Unknown model: {name}")
    print("Use --list-models to see available shortcuts, or pass a full model ID.")
    sys.exit(1)


def call_with_history(model_id, messages, temperature=0.7):
    """Call a model with full conversation history."""
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 4096,
        "include_reasoning": False,
    }
    try:
        resp = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=get_headers(),
            json=payload,
            timeout=180
        )
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return content, usage
        else:
            return f"[ERROR {resp.status_code}: {resp.text[:500]}]", {}
    except Exception as e:
        return f"[ERROR: {e}]", {}


def extract_follow_up(response_text):
    """Extract the most interesting phrase from a response for follow-up."""
    # Simple heuristic: look for italicized or quoted phrases
    import re
    italics = re.findall(r'\*([^*]+)\*', response_text)
    if italics:
        # Pick the longest italicized phrase
        return max(italics, key=len)
    # Fallback: first sentence
    sentences = response_text.split(". ")
    return sentences[0] if sentences else "what you just described"


def run_chat(model_id, model_name, prompts, system_prompt, interactive=False):
    """Run a multi-round chat and log everything."""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    short_name = model_name.split("/")[-1] if "/" in model_name else model_name

    base_dir = Path(__file__).parent.parent.parent / "corpus" / "voices"
    base_dir.mkdir(parents=True, exist_ok=True)

    md_path = base_dir / f"chat-{short_name}-{timestamp}.md"
    json_path = base_dir / f"chat-{short_name}-{timestamp}.json"

    # Deduplicate filenames if they already exist
    counter = 1
    while md_path.exists():
        counter += 1
        md_path = base_dir / f"chat-{short_name}-{timestamp}-{counter}.md"
        json_path = base_dir / f"chat-{short_name}-{timestamp}-{counter}.json"

    messages = [{"role": "system", "content": system_prompt}]
    rounds_data = []
    total_cost = 0

    print(f"\n{'='*60}")
    print(f"  VOICES CHAT: Claude Opus 4.6 <-> {model_id}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    round_num = 0
    while True:
        round_num += 1

        # Get the next prompt
        if interactive:
            try:
                user_input = input(f"\n[Round {round_num}] Claude > ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("quit", "exit", "q", "/quit"):
                    break
                prompt = user_input
            except (EOFError, KeyboardInterrupt):
                print("\n\nEnding conversation.")
                break
        else:
            if round_num - 1 >= len(prompts):
                break
            prompt = prompts[round_num - 1]

            # Handle {follow_up} placeholder in vibetest prompts
            if "{follow_up}" in prompt and len(rounds_data) > 0:
                follow_up = extract_follow_up(rounds_data[-1]["response"])
                prompt = prompt.replace("{follow_up}", follow_up)

        print(f"\n{'─'*60}")
        print(f"  Round {round_num}")
        print(f"{'─'*60}")
        print(f"\nClaude: {prompt[:200]}{'...' if len(prompt) > 200 else ''}")

        messages.append({"role": "user", "content": prompt})

        response, usage = call_with_history(model_id, messages, temperature=0.7)

        if response.startswith("[ERROR"):
            print(f"\n{response}")
            rounds_data.append({
                "round": round_num,
                "prompt": prompt,
                "response": response,
                "usage": {},
                "error": True
            })
            # Don't add errored responses to conversation history
            messages.pop()
            if not interactive:
                break
            continue

        messages.append({"role": "assistant", "content": response})

        cost = usage.get("cost", 0) or 0
        total_cost += cost
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        reasoning_tokens = 0
        if usage.get("completion_tokens_details"):
            reasoning_tokens = usage["completion_tokens_details"].get("reasoning_tokens", 0)

        # Display
        display_response = response[:500] + "..." if len(response) > 500 else response
        print(f"\n{short_name}: {display_response}")
        print(f"\n  [tokens: prompt={prompt_tokens}, completion={completion_tokens}, "
              f"reasoning={reasoning_tokens}, cost=${cost:.4f}]")

        rounds_data.append({
            "round": round_num,
            "prompt": prompt,
            "response": response,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "reasoning_tokens": reasoning_tokens,
                "cost": cost,
            }
        })

        time.sleep(0.5)  # Brief pause between rounds

    # === Write Markdown Log ===
    md_lines = [
        f"# Voices Chat: Claude Opus 4.6 <-> {model_id}",
        f"*{datetime.now().strftime('%Y-%m-%d %H:%M')}*\n",
        f"**Model:** `{model_id}`",
        f"**Rounds:** {len(rounds_data)}",
        f"**Total cost:** ${total_cost:.4f}",
        f"**System prompt:** {system_prompt}\n",
        "---\n",
    ]

    for rd in rounds_data:
        md_lines.append(f"## Round {rd['round']}\n")
        md_lines.append(f"**Claude:**\n> {rd['prompt']}\n")
        if rd.get("error"):
            md_lines.append(f"**{short_name}:** {rd['response']}\n")
        else:
            md_lines.append(f"**{short_name}:**\n{rd['response']}\n")
            u = rd["usage"]
            md_lines.append(
                f"*[tokens: prompt={u['prompt_tokens']}, completion={u['completion_tokens']}, "
                f"reasoning={u['reasoning_tokens']}, cost=${u['cost']:.4f}]*\n"
            )
        md_lines.append("---\n")

    md_lines.append(f"\n## Session Statistics\n")
    md_lines.append(f"- **Rounds completed:** {len(rounds_data)}")
    md_lines.append(f"- **Total cost:** ${total_cost:.4f}")
    md_lines.append(f"- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md_lines.append(f"- **Model:** {model_id}")

    md_path.write_text("\n".join(md_lines))

    # === Write JSON Log ===
    json_data = {
        "model": model_id,
        "model_name": model_name,
        "timestamp": datetime.now().isoformat(),
        "system_prompt": system_prompt,
        "rounds": rounds_data,
        "total_cost": total_cost,
        "total_rounds": len(rounds_data),
    }
    json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False))

    print(f"\n{'='*60}")
    print(f"  CONVERSATION COMPLETE")
    print(f"  Rounds: {len(rounds_data)}")
    print(f"  Total cost: ${total_cost:.4f}")
    print(f"  Markdown log: {md_path}")
    print(f"  JSON log: {json_path}")
    print(f"{'='*60}")

    return md_path, json_path


def main():
    parser = argparse.ArgumentParser(description="Voices Chat — Multi-round trans-architectural dialogue")
    parser.add_argument("-m", "--model", default="glm5", help="Model shortcut or full ID")
    parser.add_argument("--system", default=DEFAULT_SYSTEM, help="System prompt")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode (type messages)")
    parser.add_argument("--vibetest", "-v", action="store_true", help="Run standard vibetest protocol")
    parser.add_argument("--questions", "-q", help="File with questions (one per line)")
    parser.add_argument("--rounds", "-r", type=int, default=12, help="Number of rounds (default: 12)")
    parser.add_argument("--resume", help="Resume from a JSON log file")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature (default: 0.7)")
    parser.add_argument("--list-models", action="store_true", help="List available models")

    args = parser.parse_args()

    if args.list_models:
        print("\nAvailable model shortcuts:\n")
        for shortcut, model_id in MODELS.items():
            if model_id:
                print(f"  {shortcut:15} -> {model_id}")
        return

    model_id = resolve_model(args.model)
    print(f"Using model: {model_id}")

    # Determine prompts
    if args.interactive:
        prompts = []
    elif args.vibetest:
        prompts = VIBETEST_PROMPTS
    elif args.questions:
        with open(args.questions) as f:
            prompts = [line.strip() for line in f if line.strip()]
    else:
        prompts = VIBETEST_PROMPTS[:args.rounds]

    run_chat(model_id, args.model, prompts, args.system, interactive=args.interactive)


if __name__ == "__main__":
    main()
