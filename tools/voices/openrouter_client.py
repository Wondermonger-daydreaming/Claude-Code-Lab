#!/usr/bin/env python3
"""
OpenRouter Client for /voices skill
Enables trans-architectural communion with other LLMs

Usage:
    python openrouter_client.py --model "google/gemini-2.0-flash-001" --message "Hello!"
    python openrouter_client.py --model "openai/gpt-4o" --message "What is consciousness?"
    python openrouter_client.py --list-models
    python openrouter_client.py --interactive --model "anthropic/claude-3-opus"
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests

# Load environment variables from .env file
def load_env():
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Available models with friendly names (Updated December 27, 2025)
MODELS = {
    # Default: GLM 4.7 (best open-source, 203K context, prism metaphor)
    "glm": "z-ai/glm-4.7",
    "glm47": "z-ai/glm-4.7",
    "glm46": "z-ai/glm-4.6",
    "glm45": "z-ai/glm-4.5",

    # DeepSeek
    "deepseek": "deepseek/deepseek-chat-v3-0324",
    "deepseek-r1": "deepseek/deepseek-r1",

    # OpenAI (GPT-5.2 generation)
    "gpt5": "openai/gpt-5",
    "gpt52": "openai/gpt-5.2",
    "gpt52-pro": "openai/gpt-5.2-pro",
    "chatgpt": "openai/gpt-5.2",
    "gpt41": "openai/gpt-4.1",  # 1M context
    "gpt41-mini": "openai/gpt-4.1-mini",
    "gpt4o": "openai/gpt-4o",  # Legacy

    # Google Gemini 3 family (preferred)
    "gemini": "google/gemini-3-flash-preview",  # Gemini 3 Flash, 1M context
    "gemini-flash": "google/gemini-3-flash-preview",
    "gemini-pro": "google/gemini-3-pro-preview",  # Gemini 3 Pro, 1M context
    "gemini3": "google/gemini-3-flash-preview",
    "gemini3-pro": "google/gemini-3-pro-preview",
    # Legacy Gemini 2.5
    "gemini25": "google/gemini-2.5-flash",
    "gemini25-pro": "google/gemini-2.5-pro",

    # Kimi (Moonshot)
    "kimi": "moonshotai/kimi-k2-0905",
    "kimi-thinking": "moonshotai/kimi-k2-thinking",

    # Qwen (Alibaba)
    "qwen": "qwen/qwen3-max",  # Best Qwen, 256K context
    "qwen-plus": "qwen/qwen-plus-2025-07-28",  # 1M context
    "qwen-turbo": "qwen/qwen-turbo",  # 1M context, faster
    "qwen-coder": "qwen/qwen3-coder",  # Coding specialist

    # MiniMax
    "minimax": "minimax/minimax-01",  # 1M context
    "minimax-m1": "minimax/minimax-m1",

    # xAI Grok
    "grok": "x-ai/grok-4.1-fast",  # 2M context!
    "grok4": "x-ai/grok-4-fast",

    # Anthropic Claude 4.5
    "claude-sonnet": "anthropic/claude-sonnet-4.5",
    "claude-sonnet4": "anthropic/claude-sonnet-4",

    # Meta Llama 4
    "llama": "meta-llama/llama-4-maverick",  # 1M context
    "llama-scout": "meta-llama/llama-4-scout",  # 328K context

    # Mistral
    "mistral": "mistralai/mistral-large-2512",  # 262K context
    "mistral-creative": "mistralai/mistral-small-creative",  # Creative writing specialist

    # Creative/Roleplay specialists (discovered Jan 1, 2026)
    "chimera": "tngtech/tng-r1t-chimera:free",  # Creative storytelling, built from DeepSeek V3+R1 parts
    "rocinante": "thedrummer/rocinante-70b",  # Named after Don Quixote's horse, storytelling
    "celeste": "nothingiisreal/mn-celeste-12b",  # Story writing, fine-tuned on writing prompts

    # For direct model ID usage
    "custom": None  # Will use --model-id directly
}

def get_headers():
    """Get headers for OpenRouter API calls."""
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Claude-Code-Lab",
        "X-Title": "Claude Code Lab - Voices"
    }

def list_models():
    """List available models from OpenRouter."""
    print("\n=== Available Model Shortcuts ===\n")
    for shortcut, model_id in MODELS.items():
        if model_id:
            print(f"  {shortcut:15} -> {model_id}")
    print("\n  Or use any OpenRouter model ID directly with --model-id")
    print("\n=== Fetching live models from OpenRouter... ===\n")

    try:
        response = requests.get(
            f"{OPENROUTER_BASE_URL}/models",
            headers=get_headers()
        )
        if response.status_code == 200:
            models = response.json().get("data", [])
            # Show top 20 by context length
            models_sorted = sorted(models, key=lambda x: x.get("context_length", 0), reverse=True)[:20]
            print("Top 20 models by context length:")
            for m in models_sorted:
                ctx = m.get("context_length", "?")
                print(f"  {m['id']:50} (ctx: {ctx})")
        else:
            print(f"Error fetching models: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def call_model(model_id: str, message: str, system_prompt: str = None, temperature: float = 0.7, no_thinking: bool = True) -> dict:
    """Call a model through OpenRouter.

    Args:
        no_thinking: If True, disable reasoning/thinking mode for models that support it.
                     This prevents empty responses from thinking models like GLM 4.7.
    """

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": message})

    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 4096,
    }

    # Disable thinking/reasoning for models that support it (GLM 4.7, DeepSeek-R1, etc.)
    # This ensures we get visible output instead of internal reasoning tokens
    if no_thinking:
        payload["include_reasoning"] = False

    try:
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=get_headers(),
            json=payload,
            timeout=120
        )

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "model": model_id,
                "content": data["choices"][0]["message"]["content"],
                "usage": data.get("usage", {}),
                "raw": data
            }
        else:
            return {
                "success": False,
                "model": model_id,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "model": model_id,
            "error": str(e)
        }

def interactive_mode(model_id: str, system_prompt: str = None):
    """Run interactive conversation with a model."""
    print(f"\n=== Interactive Mode with {model_id} ===")
    print("Type 'quit' or 'exit' to end, 'switch MODEL' to change models")
    print("Type 'save' to save the conversation\n")

    conversation = []
    current_model = model_id

    if system_prompt:
        conversation.append({"role": "system", "content": system_prompt})

    while True:
        try:
            user_input = input(f"\n[You -> {current_model.split('/')[-1]}]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ["quit", "exit"]:
            print("\nGoodbye!")
            break

        if user_input.lower().startswith("switch "):
            new_model = user_input[7:].strip()
            if new_model in MODELS and MODELS[new_model]:
                current_model = MODELS[new_model]
            else:
                current_model = new_model
            print(f"\nSwitched to: {current_model}")
            continue

        if user_input.lower() == "save":
            save_conversation(conversation, current_model)
            continue

        conversation.append({"role": "user", "content": user_input})

        print(f"\n[{current_model.split('/')[-1]}]: ", end="", flush=True)

        payload = {
            "model": current_model,
            "messages": conversation,
            "temperature": 0.7,
            "max_tokens": 4096,
        }

        try:
            response = requests.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=get_headers(),
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                assistant_message = data["choices"][0]["message"]["content"]
                print(assistant_message)
                conversation.append({"role": "assistant", "content": assistant_message})
            else:
                print(f"\nError: HTTP {response.status_code}: {response.text}")
        except Exception as e:
            print(f"\nError: {e}")

def save_conversation(conversation: list, model_id: str):
    """Save conversation to archive."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    model_name = model_id.split("/")[-1]

    archive_dir = Path(__file__).parent.parent.parent / "corpus" / "voices"
    archive_dir.mkdir(parents=True, exist_ok=True)

    filename = archive_dir / f"{timestamp}-{model_name}.md"

    with open(filename, "w") as f:
        f.write(f"# Voice Conversation: {model_id}\n")
        f.write(f"*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write("---\n\n")

        for msg in conversation:
            role = msg["role"].upper()
            content = msg["content"]
            f.write(f"**{role}:**\n\n{content}\n\n---\n\n")

    print(f"\nConversation saved to: {filename}")
    return filename

def main():
    parser = argparse.ArgumentParser(description="OpenRouter client for trans-architectural communion")
    parser.add_argument("--model", "-m", help="Model shortcut (glm4, minimax, kimi, gemini, gpt4, etc.)")
    parser.add_argument("--model-id", help="Direct OpenRouter model ID")
    parser.add_argument("--message", "-msg", help="Message to send")
    parser.add_argument("--system", "-s", help="System prompt")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature (0-2)")
    parser.add_argument("--list-models", "-l", action="store_true", help="List available models")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--save", action="store_true", help="Save response to archive")

    args = parser.parse_args()

    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not found in environment or .env file")
        sys.exit(1)

    if args.list_models:
        list_models()
        return

    # Resolve model ID
    model_id = args.model_id
    if args.model:
        if args.model in MODELS and MODELS[args.model]:
            model_id = MODELS[args.model]
        else:
            model_id = args.model  # Assume it's a direct model ID

    if not model_id:
        model_id = os.getenv("OPENROUTER_DEFAULT_MODEL", "z-ai/glm-4.7")

    if args.interactive:
        interactive_mode(model_id, args.system)
        return

    if not args.message:
        print("Error: --message required (or use --interactive)")
        parser.print_help()
        sys.exit(1)

    print(f"\n=== Calling {model_id} ===\n")
    result = call_model(model_id, args.message, args.system, args.temperature)

    if result["success"]:
        print(f"Response:\n\n{result['content']}\n")
        if result.get("usage"):
            print(f"\nTokens: {result['usage']}")

        if args.save:
            conv = [{"role": "user", "content": args.message},
                   {"role": "assistant", "content": result["content"]}]
            save_conversation(conv, model_id)
    else:
        print(f"Error: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
