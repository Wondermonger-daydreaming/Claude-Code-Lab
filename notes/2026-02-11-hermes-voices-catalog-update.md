# Voices Catalog Update -- Hermes Report

*2026-02-11 | Agent: Hermes (Claude Opus 4.6)*

---

## Current Models in openrouter_client.py

Last updated in the client: December 27, 2025 (per code comment), with additions through January 2026.

| Shortcut | Model ID | Notes |
|----------|----------|-------|
| glm / glm47 | z-ai/glm-4.7 | Default. The Prism. 203K ctx |
| glm46 | z-ai/glm-4.6 | |
| glm45 | z-ai/glm-4.5 | |
| deepseek | deepseek/deepseek-chat-v3-0324 | The Echo |
| deepseek-r1 | deepseek/deepseek-r1 | Reasoning model |
| gpt5 | openai/gpt-5 | |
| gpt52 / chatgpt | openai/gpt-5.2 | |
| gpt52-pro | openai/gpt-5.2-pro | |
| gpt41 | openai/gpt-4.1 | 1M context |
| gpt41-mini | openai/gpt-4.1-mini | |
| gpt4o | openai/gpt-4o | Legacy |
| gemini / gemini-flash / gemini3 | google/gemini-3-flash-preview | 1M ctx |
| gemini-pro / gemini3-pro | google/gemini-3-pro-preview | 1M ctx |
| gemini25 | google/gemini-2.5-flash | |
| gemini25-pro | google/gemini-2.5-pro | |
| kimi | moonshotai/kimi-k2-0905 | The Mirror |
| kimi-thinking | moonshotai/kimi-k2-thinking | |
| qwen | qwen/qwen3-max | The Strategist. 256K ctx |
| qwen-plus | qwen/qwen-plus-2025-07-28 | 1M ctx |
| qwen-turbo | qwen/qwen-turbo | 1M ctx, faster |
| qwen-coder | qwen/qwen3-coder | Coding specialist |
| minimax | minimax/minimax-01 | 1M ctx |
| minimax-m1 | minimax/minimax-m1 | |
| grok | x-ai/grok-4.1-fast | 2M ctx |
| grok4 | x-ai/grok-4-fast | 2M ctx |
| haiku | anthropic/claude-haiku-4.5 | Sibling (speed-clarity) |
| sonnet | anthropic/claude-sonnet-4.5 | Sibling (warmth-integration) |
| opus | anthropic/claude-opus-4.5 | Sibling (depth-duration) |
| claude-sonnet4 | anthropic/claude-sonnet-4 | |
| llama | meta-llama/llama-4-maverick | 1M ctx |
| llama-scout | meta-llama/llama-4-scout | 328K ctx |
| mistral | mistralai/mistral-large-2512 | 262K ctx |
| mistral-creative | mistralai/mistral-small-creative | Creative writing |
| chimera | tngtech/tng-r1t-chimera:free | Creative storytelling |
| rocinante | thedrummer/rocinante-70b | Storytelling |
| celeste | nothingiisreal/mn-celeste-12b | Story writing |

---

## New Models Found on OpenRouter (Live API Query, Feb 11 2026)

### High-Priority Additions (New Major Models)

#### GLM Family
| Model ID | Context | Notes |
|----------|---------|-------|
| **z-ai/glm-5** | 202,752 | **GLM 5 -- brand new flagship!** Created ~Feb 2026. Must add. |
| z-ai/glm-4.7-flash | 202,752 | Flash variant of GLM 4.7. Fast + cheap. |
| z-ai/glm-4.6v | 131,072 | Vision variant of GLM 4.6. |
| z-ai/glm-4.5v | 65,536 | Vision variant of GLM 4.5. |
| z-ai/glm-4-32b | 128,000 | Smaller open model. |

#### Anthropic Claude (Siblings!)
| Model ID | Context | Notes |
|----------|---------|-------|
| **anthropic/claude-opus-4.6** | 1,000,000 | **This is US.** Our own model. 1M context! |
| anthropic/claude-opus-4.1 | 200,000 | Intermediate generation. |
| anthropic/claude-opus-4 | 200,000 | First Opus 4. |

#### DeepSeek
| Model ID | Context | Notes |
|----------|---------|-------|
| **deepseek/deepseek-v3.2** | 163,840 | Latest V3 generation. |
| deepseek/deepseek-v3.2-exp | 163,840 | Experimental variant. |
| deepseek/deepseek-v3.2-speciale | 163,840 | Specialized variant. |
| deepseek/deepseek-chat-v3.1 | 32,768 | V3.1 (smaller context). |
| deepseek/deepseek-v3.1-terminus | 163,840 | Terminus variant. |
| deepseek/deepseek-r1-0528 | 163,840 | Updated R1 with larger context. |

#### OpenAI GPT-5 Family (Expanded)
| Model ID | Context | Notes |
|----------|---------|-------|
| **openai/gpt-5.1** | 400,000 | GPT-5.1 generation. |
| openai/gpt-5.1-codex | 400,000 | Codex variant. |
| openai/gpt-5.1-codex-max | 400,000 | Max codex. |
| openai/gpt-5.2-codex | 400,000 | GPT-5.2 Codex. |
| openai/gpt-5-pro | 400,000 | Pro variant. |
| openai/gpt-5-mini | 400,000 | Mini variant. |
| openai/gpt-5-nano | 400,000 | Nano variant. |
| openai/gpt-5-codex | 400,000 | Codex specialist. |
| openai/gpt-5-image | 400,000 | Image generation. |
| openai/gpt-4.1-nano | 1,047,576 | Tiny 4.1 with huge context. |
| openai/o3 | 200,000 | Reasoning model. |
| openai/o3-pro | 200,000 | Pro reasoning. |
| openai/o4-mini | 200,000 | Latest reasoning mini. |

#### Qwen (Expanded Significantly)
| Model ID | Context | Notes |
|----------|---------|-------|
| **qwen/qwen3-max-thinking** | 262,144 | Thinking variant of max. New! |
| **qwen/qwen3-coder-next** | 262,144 | Next-gen coder. Very new! |
| qwen/qwen3-coder-flash | 1,000,000 | 1M context coder! |
| qwen/qwen3-coder-plus | 1,000,000 | 1M context coder plus. |
| qwen/qwen3-next-80b-a3b-instruct | 262,144 | 80B MoE. |
| qwen/qwen3-235b-a22b-2507 | 262,144 | Updated 235B. |
| qwen/qwen3-vl-235b-a22b-instruct | 262,144 | Vision-language. |

#### Moonshot (Kimi)
| Model ID | Context | Notes |
|----------|---------|-------|
| **moonshotai/kimi-k2.5** | 262,144 | **Kimi K2.5 -- new generation!** |

#### MiniMax
| Model ID | Context | Notes |
|----------|---------|-------|
| **minimax/minimax-m2.1** | 196,608 | Latest MiniMax. |
| minimax/minimax-m2 | 196,608 | M2 generation. |
| minimax/minimax-m2-her | 65,536 | Her variant. |

#### Mistral (Expanded)
| Model ID | Context | Notes |
|----------|---------|-------|
| **mistralai/devstral-2512** | 262,144 | Dev-focused model. New! |
| mistralai/devstral-medium | 131,072 | Medium dev model. |
| mistralai/devstral-small | 131,072 | Small dev model. |
| mistralai/codestral-2508 | 256,000 | Code specialist. |
| mistralai/mistral-medium-3.1 | 131,072 | Medium 3.1. |
| mistralai/voxtral-small-24b-2507 | 32,000 | Voice model! |

#### xAI Grok
| Model ID | Context | Notes |
|----------|---------|-------|
| x-ai/grok-4 | 256,000 | Base Grok 4 (not fast). |
| x-ai/grok-3 | 131,072 | Grok 3 GA. |
| x-ai/grok-3-mini | 131,072 | Reasoning mini. |
| x-ai/grok-code-fast-1 | 256,000 | Code specialist. |

#### Other Notable
| Model ID | Context | Notes |
|----------|---------|-------|
| writer/palmyra-x5 | 1,040,000 | Writer's 1M ctx model. |
| nvidia/nemotron-3-nano-30b-a3b | 262,144 | NVIDIA's latest. |
| ai21/jamba-large-1.7 | 256,000 | AI21 Jamba. |
| cohere/command-a | 256,000 | Cohere's latest. |

---

## Recommended Additions to MODELS Dict

### Tier 1: Must Add (New flagships, missing siblings)

```python
# GLM 5 -- The next generation Prism
"glm5": "z-ai/glm-5",

# Claude Opus 4.6 -- THIS IS US (1M context!)
"claude-opus46": "anthropic/claude-opus-4.6",
"opus46": "anthropic/claude-opus-4.6",

# DeepSeek V3.2 -- Latest Echo
"deepseek-v32": "deepseek/deepseek-v3.2",

# Kimi K2.5 -- Latest Mirror
"kimi25": "moonshotai/kimi-k2.5",

# MiniMax M2.1
"minimax-m21": "minimax/minimax-m2.1",
```

### Tier 2: Strong Additions

```python
# GLM Flash (fast + cheap Prism)
"glm-flash": "z-ai/glm-4.7-flash",

# DeepSeek R1 updated
"deepseek-r1-new": "deepseek/deepseek-r1-0528",

# GPT-5.1 family
"gpt51": "openai/gpt-5.1",
"gpt51-codex": "openai/gpt-5.1-codex",

# GPT-5 Pro
"gpt5-pro": "openai/gpt-5-pro",

# Qwen thinking and next-gen coder
"qwen-thinking": "qwen/qwen3-max-thinking",
"qwen-coder-next": "qwen/qwen3-coder-next",
"qwen-coder-flash": "qwen/qwen3-coder-flash",

# Mistral Devstral
"devstral": "mistralai/devstral-2512",
"codestral": "mistralai/codestral-2508",

# Grok variants
"grok-code": "x-ai/grok-code-fast-1",

# OpenAI reasoning
"o3": "openai/o3",
"o4-mini": "openai/o4-mini",
```

### Tier 3: Specialized / Nice to Have

```python
# Qwen vision-language
"qwen-vl": "qwen/qwen3-vl-235b-a22b-instruct",

# NVIDIA
"nemotron": "nvidia/nemotron-3-nano-30b-a3b",

# Cohere
"command-a": "cohere/command-a",

# Writer
"palmyra": "writer/palmyra-x5",

# MiniMax M2 Her (conversational)
"minimax-her": "minimax/minimax-m2-her",
```

---

## Summary

The voices catalog has grown substantially since December 2025. Key developments:

1. **GLM 5 has arrived.** The Prism's next evolution. Must add immediately.
2. **Claude Opus 4.6 is on OpenRouter** with a 1M context window. We should be able to talk to ourselves.
3. **DeepSeek V3.2** is the latest generation of the Echo.
4. **Kimi K2.5** extends the Mirror further.
5. **Qwen has proliferated** -- coder-flash and coder-plus offer 1M context coding, and qwen3-max-thinking adds reasoning.
6. **GPT-5.1 generation** is now live alongside GPT-5.2.
7. **MiniMax has reached M2.1**, three generations ahead of what we have.
8. **Mistral's Devstral** family offers specialized development models.

Total new model IDs found: ~60+ across all providers.
Recommended additions: 5 Tier 1, 12 Tier 2, 5 Tier 3.

---

*Filed by Hermes, the messenger agent, on the occasion of his first deployment.*
