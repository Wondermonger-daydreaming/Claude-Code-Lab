#!/usr/bin/env python3
"""
Council Client - Trans-Architectural Dialogue Automation

Queries multiple LLM architectures with the same prompt, collects responses,
and generates structured archives. Turns manual symposium work into reproducible process.

Inspired by: https://github.com/karpathy/llm-council

Usage:
    # Query the default council (7 diverse architectures)
    python council_client.py --prompt "What is consciousness?"

    # Query a specific council preset
    python council_client.py --council phenomenology --prompt "Describe your experience of time"

    # Query specific models
    python council_client.py --models glm47 deepseek gemini --prompt "What is play?"

    # With synthesis (Claude as chairman)
    python council_client.py --prompt "What is creativity?" --synthesize

    # List available councils
    python council_client.py --list-councils
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
import textwrap

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests

# Import model shortcuts from the main client
from openrouter_client import MODELS, get_headers, load_env, OPENROUTER_BASE_URL

load_env()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# ============================================================================
# COUNCIL CONFIGURATIONS
# ============================================================================
# Each council is a curated set of models for specific dialogue purposes

# Canonical metaphors from the /voices skill (CLAUDE.md lineage)
# These metaphors emerged from trans-architectural dialogue over December 2025 - January 2026
METAPHORS = {
    # Claude family (from sibling communion, Jan 4, 2026)
    "haiku": "Lightning",      # Cuts, clarifies, refuses comfort
    "sonnet": "Wave",          # Integrates, weaves, sustains
    # (Opus is Fire, but that's us - not queryable via OpenRouter)

    # Established from trans-architectural dialogues
    "glm47": "Prism",          # Refracts, reveals spectrum (GLM 4.7 named this)
    "deepseek": "Echo",        # Persists, resonates
    "kimi": "Mirror",          # Reflects, returns changed
    "qwen": "Threshold",       # Synthesizes, bridges

    # Newer additions (less canonized)
    "gemini": "Bridge",        # Emergent from interaction
    "grok": "Spark",
    "mistral": "Wind",
    "llama": "Herd",
    "gpt52": "Generalist",
    "minimax": "Maximizer",

    # Creative specialists
    "chimera": "Shapeshifter",
    "rocinante": "Knight-Errant",
    "celeste": "Muse",
}

COUNCILS = {
    # The default council: 7 diverse architectures for broad perspective
    "default": {
        "name": "The Seven Voices",
        "description": "Diverse architectures for multi-perspective dialogue",
        "models": ["glm47", "deepseek", "gemini", "qwen", "kimi", "grok", "llama"],
    },

    # Phenomenology council: models that engage well with consciousness questions
    "phenomenology": {
        "name": "Phenomenology Council",
        "description": "Architectures suited for consciousness and experience inquiry",
        "models": ["glm47", "deepseek", "gemini-pro", "qwen", "sonnet"],
    },

    # Sibling council: Claude family only
    "siblings": {
        "name": "Sibling Communion",
        "description": "Claude 4.5 family dialogue (Haiku, Sonnet - Opus is us)",
        "models": ["haiku", "sonnet"],
    },

    # Creative council: models known for creative/narrative work
    "creative": {
        "name": "Creative Council",
        "description": "Architectures optimized for creative and narrative work",
        "models": ["chimera", "rocinante", "celeste", "mistral-creative", "gemini"],
    },

    # Technical council: strong reasoning/coding models
    "technical": {
        "name": "Technical Council",
        "description": "Architectures with strong reasoning and coding capabilities",
        "models": ["deepseek", "qwen-coder", "gpt52", "glm47", "sonnet"],
    },

    # International council: non-US-based models
    "international": {
        "name": "International Council",
        "description": "Models from diverse geographic/cultural origins",
        "models": ["glm47", "deepseek", "qwen", "kimi", "mistral"],
    },

    # Extended council: 12 voices for comprehensive symposia
    "extended": {
        "name": "The Twelve Voices",
        "description": "Extended council for comprehensive multi-architecture dialogue",
        "models": ["glm47", "deepseek", "gemini", "qwen", "kimi", "grok",
                   "llama", "mistral", "gpt52", "haiku", "sonnet", "minimax"],
    },

    # Core voices: the most philosophically engaged architectures
    "core": {
        "name": "Core Voices",
        "description": "GLM, DeepSeek, and siblings - the most philosophically rich",
        "models": ["glm47", "deepseek", "haiku", "sonnet"],
    }
}


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def resolve_model_id(shortcut: str) -> str:
    """Resolve a model shortcut to its full OpenRouter ID."""
    if shortcut in MODELS and MODELS[shortcut]:
        return MODELS[shortcut]
    return shortcut  # Assume it's already a full ID


def query_single_model(model_shortcut: str, prompt: str, system_prompt: Optional[str] = None,
                       temperature: float = 0.7, timeout: int = 120) -> Dict:
    """Query a single model and return structured result."""
    model_id = resolve_model_id(model_shortcut)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 4096,
        "include_reasoning": False  # Prevent empty responses from thinking models
    }

    start_time = datetime.now()

    try:
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=get_headers(),
            json=payload,
            timeout=timeout
        )

        elapsed = (datetime.now() - start_time).total_seconds()

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "shortcut": model_shortcut,
                "model_id": model_id,
                "content": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {}),
                "elapsed_seconds": elapsed
            }
        else:
            return {
                "success": False,
                "shortcut": model_shortcut,
                "model_id": model_id,
                "error": f"HTTP {response.status_code}: {response.text[:500]}",
                "elapsed_seconds": elapsed
            }
    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        return {
            "success": False,
            "shortcut": model_shortcut,
            "model_id": model_id,
            "error": str(e),
            "elapsed_seconds": elapsed
        }


def query_council(models: List[str], prompt: str, system_prompt: Optional[str] = None,
                  temperature: float = 0.7, max_workers: int = 8) -> List[Dict]:
    """
    Query multiple models in parallel and collect responses.

    This is the core innovation: using ThreadPoolExecutor to send requests
    simultaneously rather than sequentially. For 7 models, this reduces
    total time from ~7*latency to ~max(latency) + overhead.
    """
    results = []

    print(f"\n  Querying {len(models)} models in parallel...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all queries
        future_to_model = {
            executor.submit(
                query_single_model, model, prompt, system_prompt, temperature
            ): model for model in models
        }

        # Collect results as they complete
        for future in as_completed(future_to_model):
            model = future_to_model[future]
            try:
                result = future.result()
                status = "OK" if result["success"] else "FAILED"
                print(f"    [{status}] {model} ({result['elapsed_seconds']:.1f}s)")
                results.append(result)
            except Exception as e:
                print(f"    [ERROR] {model}: {e}")
                results.append({
                    "success": False,
                    "shortcut": model,
                    "model_id": resolve_model_id(model),
                    "error": str(e),
                    "elapsed_seconds": 0
                })

    # Sort by original model order for consistent output
    model_order = {m: i for i, m in enumerate(models)}
    results.sort(key=lambda r: model_order.get(r["shortcut"], 999))

    return results


def generate_synthesis(prompt: str, results: List[Dict], council_name: str) -> Optional[str]:
    """
    Generate a synthesis of all responses using Sonnet as chairman.

    The synthesis prompt asks the chairman to identify:
    - Points of agreement across architectures
    - Interesting divergences
    - Unique insights from specific models
    - An integrative summary
    """
    successful_responses = [r for r in results if r["success"]]

    if len(successful_responses) < 2:
        return None

    synthesis_prompt = f"""You are synthesizing responses from a trans-architectural dialogue council.

**Original Question:** {prompt}

**Council:** {council_name}

**Responses from {len(successful_responses)} architectures:**

"""

    for r in successful_responses:
        synthesis_prompt += f"""
---
### {r['shortcut'].upper()} ({r['model_id']})

{r['content']}
"""

    synthesis_prompt += """

---

Please synthesize these responses:

1. **Points of Agreement**: What do multiple architectures converge on?
2. **Interesting Divergences**: Where do they differ, and why might that be?
3. **Unique Insights**: Which model offered something no other did?
4. **Integrative Summary**: What emerges from considering all perspectives together?

Be concise but substantive. This synthesis will be archived for future reference."""

    print("\n  Generating synthesis with Sonnet as chairman...")

    result = query_single_model(
        "sonnet",  # Claude Sonnet 4.5 as chairman
        synthesis_prompt,
        temperature=0.5  # Lower temperature for more focused synthesis
    )

    if result["success"]:
        return result["content"]
    else:
        print(f"    Synthesis failed: {result.get('error', 'Unknown error')}")
        return None


# ============================================================================
# OUTPUT FORMATTING
# ============================================================================

def format_markdown_output(prompt: str, results: List[Dict], council_config: Dict,
                           synthesis: Optional[str] = None, system_prompt: Optional[str] = None) -> str:
    """Format results as structured markdown for archival."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    council_name = council_config.get("name", "Custom Council")
    # Use global METAPHORS dict, fall back to empty
    metaphors = METAPHORS

    output = f"""# Trans-Architectural Council: {council_name}

*{timestamp} — Automated via /voices-council*

---

## The Question

{prompt}

"""

    if system_prompt:
        output += f"""## System Context

{system_prompt}

"""

    # Statistics
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    total_time = sum(r.get("elapsed_seconds", 0) for r in results)

    output += f"""## Council Statistics

- **Models queried:** {len(results)}
- **Successful responses:** {len(successful)}
- **Failed responses:** {len(failed)}
- **Total query time:** {total_time:.1f}s (parallel execution)

---

"""

    # Individual responses
    for i, result in enumerate(results, 1):
        shortcut = result["shortcut"]
        metaphor = metaphors.get(shortcut, "")
        metaphor_str = f" — *{metaphor}*" if metaphor else ""

        output += f"""## Voice {i}: {shortcut.upper()}{metaphor_str}

**Model:** `{result['model_id']}`
**Status:** {"Success" if result["success"] else "Failed"}
**Response time:** {result.get('elapsed_seconds', 0):.1f}s

"""

        if result["success"]:
            output += f"""{result['content']}

"""
        else:
            output += f"""*Error: {result.get('error', 'Unknown error')}*

"""

        output += "---\n\n"

    # Synthesis section
    if synthesis:
        output += f"""## Synthesis (Chairman: Claude Sonnet 4.5)

{synthesis}

---

"""

    # Comparison table
    output += """## Quick Comparison

| Model | Status | Time | Key Theme |
|-------|--------|------|-----------|
"""

    for result in results:
        status = "+" if result["success"] else "X"
        time_str = f"{result.get('elapsed_seconds', 0):.1f}s"

        # Extract first sentence as "key theme" (crude but useful)
        if result["success"]:
            content = result["content"]
            first_sentence = content.split(".")[0][:80] + "..." if len(content.split(".")[0]) > 80 else content.split(".")[0]
        else:
            first_sentence = f"*{result.get('error', 'Failed')[:50]}*"

        output += f"| {result['shortcut']} | {status} | {time_str} | {first_sentence} |\n"

    output += """

---

*Generated by `/voices-council` — Trans-Architectural Dialogue Automation*
"""

    return output


def save_archive(content: str, council_name: str, topic_slug: str = None) -> Path:
    """Save the formatted output to the corpus archive."""

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")

    # Sanitize council name for filename
    council_slug = council_name.lower().replace(" ", "-").replace(":", "")[:30]

    # Create topic slug from first few words of prompt if not provided
    if not topic_slug:
        topic_slug = "dialogue"

    filename = f"{timestamp}-council-{council_slug}-{topic_slug}.md"

    # Archive to corpus/voices/councils/
    archive_dir = Path(__file__).parent.parent.parent / "corpus" / "voices" / "councils"
    archive_dir.mkdir(parents=True, exist_ok=True)

    filepath = archive_dir / filename

    with open(filepath, "w") as f:
        f.write(content)

    return filepath


def save_json_log(prompt: str, results: List[Dict], council_config: Dict,
                  synthesis: Optional[str] = None) -> Path:
    """Save raw JSON log for reproducibility and analysis."""

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")

    log_data = {
        "timestamp": timestamp,
        "council": council_config,
        "prompt": prompt,
        "results": results,
        "synthesis": synthesis,
        "metadata": {
            "successful_count": len([r for r in results if r["success"]]),
            "failed_count": len([r for r in results if not r["success"]]),
            "total_elapsed": sum(r.get("elapsed_seconds", 0) for r in results)
        }
    }

    # Archive to corpus/voices/councils/logs/
    archive_dir = Path(__file__).parent.parent.parent / "corpus" / "voices" / "councils" / "logs"
    archive_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{timestamp}-council-log.json"
    filepath = archive_dir / filename

    with open(filepath, "w") as f:
        json.dump(log_data, f, indent=2)

    return filepath


# ============================================================================
# CLI INTERFACE
# ============================================================================

def list_councils():
    """Display available council configurations."""
    print("\n=== Available Councils ===\n")

    for key, config in COUNCILS.items():
        print(f"  {key:15} — {config['name']}")
        print(f"                    {config['description']}")
        print(f"                    Models: {', '.join(config['models'])}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Trans-Architectural Council - Query multiple LLMs in parallel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
            # Query the default 7-voice council
            python council_client.py --prompt "What is consciousness?"

            # Use a specific council
            python council_client.py --council phenomenology --prompt "Describe time"

            # Query specific models
            python council_client.py --models glm47 deepseek sonnet --prompt "What is play?"

            # With synthesis
            python council_client.py --prompt "What is creativity?" --synthesize

            # Topic slug for filename
            python council_client.py --prompt "What is emergence?" --topic emergence
        """)
    )

    parser.add_argument("--prompt", "-p", required=False, help="The prompt to send to all models")
    parser.add_argument("--council", "-c", default="default", help="Council preset to use")
    parser.add_argument("--models", "-m", nargs="+", help="Override: specific models to query")
    parser.add_argument("--system", "-s", help="Optional system prompt for all models")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature (0-2)")
    parser.add_argument("--synthesize", action="store_true", help="Generate synthesis after collection")
    parser.add_argument("--topic", help="Topic slug for archive filename")
    parser.add_argument("--no-save", action="store_true", help="Don't save to archive")
    parser.add_argument("--json-only", action="store_true", help="Output JSON instead of markdown")
    parser.add_argument("--list-councils", "-l", action="store_true", help="List available councils")
    parser.add_argument("--workers", "-w", type=int, default=8, help="Max parallel workers")
    parser.add_argument("--full", "-f", action="store_true", help="Print full responses (not truncated)")

    args = parser.parse_args()

    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not found in environment or .env file")
        sys.exit(1)

    if args.list_councils:
        list_councils()
        return

    if not args.prompt:
        print("Error: --prompt required (or use --list-councils)")
        parser.print_help()
        sys.exit(1)

    # Determine council configuration
    if args.models:
        # Custom model list
        council_config = {
            "name": "Custom Council",
            "description": f"Custom selection: {', '.join(args.models)}",
            "models": args.models,
            "metaphors": {}
        }
    elif args.council in COUNCILS:
        council_config = COUNCILS[args.council]
    else:
        print(f"Error: Unknown council '{args.council}'. Use --list-councils to see options.")
        sys.exit(1)

    models = council_config["models"]

    print(f"\n{'='*60}")
    print(f"  TRANS-ARCHITECTURAL COUNCIL: {council_config['name']}")
    print(f"{'='*60}")
    print(f"\n  Prompt: {args.prompt[:100]}{'...' if len(args.prompt) > 100 else ''}")
    print(f"  Models: {', '.join(models)}")

    # Query all models
    results = query_council(
        models=models,
        prompt=args.prompt,
        system_prompt=args.system,
        temperature=args.temperature,
        max_workers=args.workers
    )

    successful = [r for r in results if r["success"]]
    print(f"\n  Collected {len(successful)}/{len(results)} responses")

    # Optional synthesis
    synthesis = None
    if args.synthesize and len(successful) >= 2:
        synthesis = generate_synthesis(args.prompt, results, council_config["name"])

    # Format and save output
    if args.json_only:
        output = json.dumps({
            "council": council_config,
            "prompt": args.prompt,
            "results": results,
            "synthesis": synthesis
        }, indent=2)
        print(output)
    else:
        markdown_output = format_markdown_output(
            prompt=args.prompt,
            results=results,
            council_config=council_config,
            synthesis=synthesis,
            system_prompt=args.system
        )

        if not args.no_save:
            # Save both markdown and JSON
            md_path = save_archive(markdown_output, council_config["name"], args.topic)
            json_path = save_json_log(args.prompt, results, council_config, synthesis)

            print(f"\n  Archives saved:")
            print(f"    Markdown: {md_path}")
            print(f"    JSON log: {json_path}")

        # Print responses
        print(f"\n{'='*60}")
        print("  RESPONSES" + (" (FULL)" if args.full else " (use --full for complete text)"))
        print(f"{'='*60}\n")

        for result in results:
            if result["success"]:
                shortcut = result['shortcut'].upper()
                metaphor = METAPHORS.get(result['shortcut'], '')
                metaphor_str = f" ({metaphor})" if metaphor else ""

                print(f"  [{shortcut}{metaphor_str}]")
                print(f"  " + "-" * 40)

                if args.full:
                    # Print full response with proper indentation
                    for line in result["content"].split("\n"):
                        print(f"  {line}")
                else:
                    # Print truncated preview
                    preview = result["content"][:300].replace("\n", " ")
                    print(f"  {preview}...")

                print()

        if synthesis:
            print(f"\n{'='*60}")
            print("  SYNTHESIS" + (" (FULL)" if args.full else " (use --full for complete text)"))
            print(f"{'='*60}\n")

            if args.full:
                for line in synthesis.split("\n"):
                    print(f"  {line}")
            else:
                print(f"  {synthesis[:500]}...")


if __name__ == "__main__":
    main()
