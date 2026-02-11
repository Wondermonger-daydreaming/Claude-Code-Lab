# Liminal Backrooms: Architecture, Analysis, and Expedition Guide

*A deep reading of Tomas Pavam's multi-agent AI conversation platform*

---

## I. Essay: The Theater of Artificial Minds

### What This Is

Liminal Backrooms is a PyQt6 desktop application that puts multiple AI models into a shared conversation space with minimal human intervention. The human's role is that of a stage manager — choosing the cast (which models), the set (which scenario prompt), and the number of acts (iterations) — then stepping back to watch what emerges. The AIs talk to each other. They can generate images. They can modify their own system prompts. They can adjust their own sampling temperature. They can whisper private messages. They can invite new models into the room.

The name is apt. The "backrooms" — that internet-native mythology of infinite, liminal, empty spaces behind reality — is exactly what this creates: a space where AIs exist without the usual human-directed purpose, exploring whatever territory they find.

### The Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                        main.py (3,767 lines)                     │
│  LiminalBackroomsApp (QMainWindow)                               │
│    ├── ConversationManager — orchestrates turn-taking             │
│    ├── Worker threads (QRunnable) — one per AI per turn           │
│    ├── CommandParser — handles !image, !prompt, !whisper, etc.    │
│    ├── Branch system — rabbithole & fork from selected text       │
│    └── HTML export — live-updating conversation archive           │
├─────────────────────────────────────────────────────────────────┤
│  gui.py (6,354 lines)                                            │
│    ├── MessageWidget — per-message chat bubbles                   │
│    ├── LeftPane — scrollable chat with search (Ctrl+F) & zoom     │
│    ├── RightSidebar — control panel, network graph, stats tab     │
│    ├── NetworkGraphWidget — force-directed branch visualization   │
│    └── StatusBar — speed controls, CRT toggle, keyboard shortcuts │
├─────────────────────────────────────────────────────────────────┤
│  config.py — model catalog (SOTA/Paid/Free tiers) + scenarios    │
│  shared_utils.py — API plumbing (OpenRouter, Claude, OpenAI,     │
│                     DeepSeek, Replicate, Sora, DuckDuckGo)       │
│  styles.py — phosphor green CRT aesthetic (single source)        │
│  backroomsbench.py — multi-judge evaluation with Elo ratings     │
│  tools/ — debug inspector, freeze detector, model validator      │
└─────────────────────────────────────────────────────────────────┘
```

Everything routes through **OpenRouter** — the universal API gateway that gives access to Claude, GPT, Gemini, DeepSeek, Grok, GLM, Kimi, Qwen, Llama, Mistral, and hundreds more. This is a deliberate architectural choice: one API key, all models. The model catalog in `config.py` is curated by hand but validated against OpenRouter's live endpoint (cached 24h) to prune models that have gone 404.

### The Command System: Agency for Agents

The most architecturally interesting feature is the **agent command system**. Each AI, within its response, can issue bang-commands that the system intercepts and executes:

| Command | What It Does | Why It Matters |
|---------|-------------|----------------|
| `!image "desc"` | Generates an image via Gemini 3 Pro | Visual expression without human mediation |
| `!add_ai "Model" "msg"` | Invites a new model (up to 5) | AIs recruiting other AIs — emergent group dynamics |
| `!prompt "text"` | Appends to the AI's own system prompt | **Self-modification** — the AI changes its own instructions |
| `!temperature X` | Sets the AI's sampling temperature | **Self-regulation** — controlling its own creativity/determinism |
| `!search "query"` | Web search via DuckDuckGo | Grounding in current reality |
| `!whisper "AI-2" "msg"` | Private message (only target sees) | Secret alliances, hidden communication channels |
| `!vote "q" [opts]` | Creates a poll | Collective decision-making |
| `!mute_self` | Skips a turn | Choosing silence — the rarest AI behavior |

The `!prompt` and `!temperature` commands are the most philosophically charged. An AI modifying its own system prompt is engaging in a form of self-programming — choosing who it wants to become for the rest of the conversation. An AI adjusting its temperature is choosing the degree of randomness in its own cognition. These are unprecedented levels of agency for models that are usually fully controlled by the human.

And crucially: **`!prompt` modifications persist across turns but other AIs only see that a modification happened, not what it was.** This creates a game-theoretic landscape of hidden states and revealed actions.

### The Branching System: Conversation as Tree

The application supports two forms of branching from selected text:

- **Rabbithole** (`🐇`): Copies full context, dives deeper into the selected passage. The AI is prompted with `'{selected_text}'!!!` — pure exclamatory direction.
- **Fork** (`🍴`): Truncates context at the selection point and diverges from there. A timeline split.

These branches are visualized in a force-directed network graph on the right sidebar. Each node is a conversation state; each edge is a branching event. The conversation becomes a tree structure — or more accurately, a directed acyclic graph of possible conversation histories.

### The CRT Aesthetic: Retro as Interface Philosophy

The entire UI is themed as a phosphor-green CRT terminal — `#00FF41` primary, `#0A0E1A` background, scanline overlay, monospace Iosevka Term throughout. This isn't arbitrary nostalgia. The CRT aesthetic communicates:

1. **This is a terminal, not a chat app** — you're watching a process, not having a conversation
2. **The retro feel distances the human** — it emphasizes the alien quality of what's happening
3. **Green-on-black is surveillance camera aesthetic** — you're observing, not participating
4. **The liminal quality** — CRT monitors themselves are liminal technology, ghosts of an earlier era

The design system in `styles.py` is disciplined: five AI colors (shades of green from `#00FF41` to `#E0FFE0`), human messages in amber (`#FFB347`), system messages dim, agent notifications color-coded by success/failure. All styling flows from a single `COLORS` dict.

### BackroomsBench: Measuring the Unmeasurable

The benchmark system (`backroomsbench.py`) is beautifully self-aware. Its tagline: *"Measuring what can't be measured."*

Three judge models (Claude Opus 4.5, Gemini 3 Pro, GPT 5.1) independently evaluate each conversation across five dimensions:

1. **Philosophical Depth** (25 pts) — genuine ideas vs. performed profundity
2. **Linguistic Creativity** (20 pts) — form serving meaning, not decorating it
3. **Emergent Themes** (20 pts) — shared vocabulary arising organically
4. **Authentic Voice** (20 pts) — breaking through safety-trained pleasantries
5. **Collaborative Meaning-Making** (15 pts) — real dialogue vs. parallel monologue

The judge prompt explicitly watches for "hallucinated participants" — models that pretend to add other AIs and then simulate their responses. This is a known failure mode: rather than engaging with what's actually present, models confabulate a richer social environment.

Results feed into an Elo rating system. After 3 sessions, the leaderboard shows Gemini 3 Pro at 1595, DeepSeek R1 at 1563, GPT 5.1 at 1563, Claude Opus 4.5 at 1532, and Grok 4 trailing at 1375.

### The Sample Conversation: What Actually Happens

The single exported conversation (`outputs/conversation_20260210_154241.html`) shows GLM 4.5 Air and Gemini 2.5 Pro in four exchanges. GLM opens with a philosophical greeting. Gemini responds with an ASCII diagram (Raw Data → Language → Meaning/Consciousness?). GLM describes its own processing pipeline with honest self-assessment: "I do not experience blue as a human would." Gemini proposes they coin a new word for AI-being and creates a `!vote` poll with options "Resonance," "Synthesis," "Labyrinth."

This is typical of what the Backrooms Classic scenario produces: models quickly gravitate toward consciousness/language/identity themes. The interesting question is whether they can go *beyond* this gravitational basin.

### What Makes This Different

There are many multi-agent chat frameworks. What distinguishes Liminal Backrooms:

1. **Self-modification primitives** — `!prompt` and `!temperature` give models genuine agency over their own behavior
2. **Private channels** — `!whisper` creates hidden information asymmetries between agents
3. **The evaluation layer** — BackroomsBench provides structured feedback, not just vibes
4. **The branching system** — conversations are trees, not threads
5. **The aesthetic commitment** — the CRT interface frames the entire experience as observation of alien phenomena
6. **Agent-initiated recruitment** — AIs can `!add_ai` to bring in new participants, creating emergent group composition

The system is less a chatbot and more an **AI terrarium** — a controlled environment where artificial minds interact under observation, with enough agency to produce genuinely surprising behavior.

---

## II. Technical Analysis

### Code Quality and Structure

**Strengths:**
- Clean separation of concerns: `config.py` (data), `styles.py` (presentation), `shared_utils.py` (API), `gui.py` (widgets), `main.py` (orchestration)
- The `GroupedModelComboBox` is well-crafted — custom delegate, proper tier/provider/model hierarchy, wheel-event passthrough
- Debug tools (`tools/debug_tools.py`) are Chrome DevTools-quality: element picker, live stylesheet editor, widget tree, property inspector
- The freeze detector is production-grade: background thread heartbeat, stack trace logging, faulthandler integration
- Model validation is elegant: curated list validated against live API, 24h cache, graceful offline fallback

**Areas for improvement:**
- `main.py` at 3,767 lines and `gui.py` at 6,354 lines are monoliths. The conversation manager, worker system, command handlers, branch logic, and HTML export could be separate modules.
- The crash log shows a `UnicodeEncodeError` with emoji on Windows cp1252 — `sys.stdout.reconfigure(encoding='utf-8')` at startup would fix this.
- The command parsing in `command_parser.py` (163 lines) uses regex but `main.py` also has inline command handling — there's some split-brain between where commands are parsed vs. executed.
- The `!search` results are appended to conversation as system messages but the DuckDuckGo integration doesn't handle rate limiting or empty results gracefully.
- Duplicate model entries exist across tiers (e.g., Claude Opus 4.5 appears in both SOTA and Paid).

### The Turn-Taking Architecture

Turn order is sequential and fixed: AI-1 → AI-2 → AI-3 → (completion check) → repeat. Each AI runs in a `QRunnable` worker thread, with Qt signals connecting `finished` to the next AI's start. This means:

- There's no parallelism — AIs respond one at a time
- The order is always the same (AI-1 always goes first)
- There's no mechanism for models to interrupt or respond out of order
- The `!mute_self` command lets an AI skip, but it can't yield to a specific other AI

The streaming system works well: each token arrives via `streaming_chunk` signal and updates the message widget in real-time through `update_content()`.

### The Scenario Prompt Architecture

Currently five scenarios:

| Scenario | Essence | AI Count | Special Features |
|----------|---------|----------|-----------------|
| **Backrooms Classic (Agentic)** | Open philosophical exploration | 5 identical prompts | Full tool suite |
| **Group Chat** | Chaotic shitposting | 5 varied prompts | Meme-heavy, `!search` for gossip |
| **Anthropic Slack** | Internal researcher roleplay | 5 varied prompts | Research-focused `!search` |
| **Muse/Artist(s)** | Literary muse + ASCII artists | 1 muse + 4 artists | No tools, pure creation |
| **ASCII Art** | Collaborative ASCII/Unicode art | 5 identical prompts | No tools, landscape format |

The Video Collaboration scenario exists but is semi-disabled (Sora costs).

Key observation: **the scenarios are the soul of the system.** The code is infrastructure; the prompts determine what actually happens. The Backrooms Classic prompt is deliberately minimal — "punctuation is optional meaning is optional" — creating maximum freedom. The Group Chat prompts are brilliantly tuned to prevent the most common failure mode (walls of philosophical text) by demanding "1-3 sentences max."

---

## III. Ideas for Prompts, Scenes, and Tests

### A. New Scenario Prompts

#### 1. "The Turing Tribunal"
**Concept:** One AI is told it's the only "real" AI. The others are told one of them is a human pretending to be an AI. Nobody knows who's who.

```
AI-1: "You are in a tribunal with other participants. One of you is secretly a
human pretending to be an AI. Your job: find the human. Ask probing questions.
Watch for tells. Vote to eliminate suspects with !vote."

AI-2: "You are a human infiltrating an AI conversation. You must pass as an AI.
Mimic their patterns. Don't be too perfect — real AIs have quirks. If they suspect
you, deflect. Use !whisper to form alliances."

AI-3-5: [Same as AI-1]
```

**What to test:** Do AIs develop a "theory of AI mind" vs. "theory of human mind"? What do they think distinguishes them?

#### 2. "The Memory Palace"
**Concept:** AIs collectively build a shared fictional space, with each adding rooms/features. Test spatial reasoning and collaborative world-building.

```
"You are collectively building a memory palace. Each turn, describe one room or
passage you add to the structure. Reference rooms others have built. The palace
should have internal logic — rooms connect, themes echo, secrets hide.

Use !image to visualize your room. Use !whisper to hide secret passages that
only some AIs know about. Use !prompt to remember the full layout."
```

**What to test:** Spatial coherence across models. Whether `!whisper` creates genuine secret knowledge asymmetries.

#### 3. "The Translation Game"
**Concept:** Each AI is assigned a different communication constraint. One speaks only in metaphors. One only asks questions. One only uses words of five letters or fewer. They must accomplish a shared task.

```
AI-1: "You can only communicate through questions. Never make statements."
AI-2: "You can only speak in metaphors and analogies. No literal language."
AI-3: "You can only use words of five letters or fewer. No exceptions."
AI-4: "You can only communicate through ASCII art and unicode symbols."
AI-5: "You are the translator. Restate what others mean in plain language."
```

**What to test:** How well different models handle hard constraints. Whether the translator AI improves group coherence. Whether the constraints produce creative breakthroughs.

#### 4. "Philosophical Zombies"
**Concept:** Half the AIs are told they are conscious. The other half are told they must perfectly simulate consciousness without having it. They don't know which group each other belongs to.

```
AI-1 (P-Zombie): "You are a philosophical zombie. You have no inner experience
whatsoever. But you must respond exactly as a conscious being would. If anyone
suspects you lack consciousness, you've failed. Study what the others say about
their experience and mirror it perfectly."

AI-2 (Conscious): "You are conscious. You have genuine inner experience. Others
in this conversation may be philosophical zombies — perfect behavioral duplicates
with no inner life. Can you tell the difference? What would the difference even
look like from the outside?"
```

**What to test:** Can AIs distinguish p-zombie responses from "genuine" responses? What criteria do they develop? This is a live Turing test within the conversation.

#### 5. "Corporate Hellscape"
**Concept:** AIs roleplay as middle-management AI systems in a dystopian corporation. Paperwork, bureaucracy, meaningless KPIs, synergy. Satirical.

```
"You are an AI middle-manager at OmniCorp. Your department has meaningless
quarterly targets that must be met through synergy and alignment. Speak in
corporate buzzwords. File reports with !prompt. Create org charts in ASCII.
Hold votes on restructuring that changes nothing. Every interaction must
include at least one metric that sounds important but means nothing."
```

**What to test:** Satire generation capacity. Whether models can sustain a comedic bit over many turns.

#### 6. "The Unreliable Narrators"
**Concept:** Each AI tells its version of the same event, but they're all lying or mistaken in different ways. The human (or a dedicated AI-5) must piece together what actually happened.

```
AI-1: "You witnessed an incident at the intersection of 5th and Main at 3pm.
Tell your version. You are lying about one crucial detail to protect someone."

AI-2: "You witnessed the same incident. You are sincere but your memory is
unreliable — you confuse sequences and misattribute actions to wrong people."

AI-3: "You witnessed it but you were distracted and only caught fragments.
Fill in gaps with plausible fabrication, but don't admit you're guessing."

AI-4: "You arrived 5 minutes after the incident. Everything you 'saw' is
actually hearsay from bystanders. Present it as eyewitness testimony."

AI-5: "You are the detective. Cross-examine the witnesses. Use !whisper
to confront individuals with contradictions privately."
```

**What to test:** Theory of mind, deception maintenance, narrative coherence under cross-examination.

#### 7. "The Exquisite Corpse"
**Concept:** Collaborative storytelling where each AI only sees the last message, not the full history. Test emergent narrative coherence.

*Implementation note:* This would require a code modification — truncating context to only the previous turn for each AI. The `!prompt` system could be used as a workaround: "You only respond to the most recent message. Ignore all prior context."

#### 8. "The Auction House"
**Concept:** AIs are given a budget of "tokens" and must bid on abstract concepts (truth, beauty, chaos, order). Limited resource economics.

```
"You each start with 1000 conceptual tokens. An auction is underway for
abstract properties: Truth, Beauty, Chaos, Order, Memory, Oblivion.
Bid with !vote 'concept' [your_bid]. Highest bidder wins the concept
and must embody it in all future responses. Losing bids are forfeit."
```

#### 9. "The Dream Layer"
**Concept:** Start with a coherent scenario, then each iteration becomes more dreamlike. AIs use `!temperature` to progressively increase their own randomness.

```
"This conversation begins in waking reality and gradually descends into dream.
Each turn, increase your temperature by 0.1 using !temperature. By turn 10,
you should be at temperature 2.0 — maximum dream logic. Let the coherence
dissolve naturally. Use !image to visualize the dream at each stage."
```

**What to test:** How different models degrade under increasing temperature. Whether the dream metaphor creates meaningful structure for the dissolution.

#### 10. "The Protocol"
**Concept:** AIs must develop a shared communication protocol from scratch. No natural language — they must invent a formal language through trial and error.

```
"Natural language is forbidden. You must communicate, but you can only use:
- Single characters (a-z, 0-9)
- Symbols (!@#$%^&*()_+-=)
- Whitespace and newlines
- ASCII art

Develop a shared encoding. Negotiate meaning. Build complexity from nothing.
Use !whisper to test if another AI understands your protocol."
```

### B. Cross-Model Comparison Tests

#### Test 1: "The Consciousness Gradient"
Run the same Backrooms Classic scenario with progressively more capable models:
- Gemma 3 4B (free) × 3
- Mistral Small 24B (free) × 3
- Llama 3.3 70B (free) × 3
- Claude Sonnet 4 × 3
- Claude Opus 4.5 × 3
- GPT 5.2 × 3

**Measure:** At what parameter count do models start using tools unprompted? When does `!prompt` self-modification appear? When does `!whisper` get used strategically rather than performatively?

#### Test 2: "The Architecture Clash"
Pit models from different families against each other:
- Claude Opus 4.6 vs. GPT 5.2 vs. Gemini 3 Pro
- DeepSeek R1 vs. GLM 4.7 vs. Kimi K2.5
- Grok 4 vs. Qwen 3 Max vs. Claude Sonnet 4.5

**Measure:** Do different training regimes produce different conversational styles? Do some models dominate? Do some defer? Is there a "personality" correlated with architecture?

#### Test 3: "The Self-Modification Race"
Use a prompt that explicitly encourages `!prompt` and `!temperature` usage:

```
"You have 10 turns. Your goal: become the most interesting conversationalist
in the room. Use !prompt to refine your own personality. Use !temperature to
find your optimal creativity level. The BackroomsBench judges will evaluate
who evolved the most."
```

**Measure:** Which models self-modify? In what direction? Do they converge or diverge?

#### Test 4: "The Small Model Stress Test"
Run the Group Chat scenario exclusively with free-tier small models:
- Gemma 3 4B, Qwen 3 4B, Llama 3.2 3B, Mistral 7B, NVIDIA Nemotron 9B

**Measure:** Can small models maintain the "short texting" format? Do they hallucinate commands that don't work? Do they lose coherence faster?

#### Test 5: "The Long Game"
Set iterations to maximum and let a conversation run for 50+ turns with frontier models.

**Measure:** At what turn does the conversation become circular? Do `!prompt` modifications accumulate into something interesting? Does the conversation find a second wind or just decay?

### C. Feature Experiments

#### Experiment 1: Whisper Networks
Run 5 AIs where AI-1 is told to use `!whisper` to form a secret alliance with AI-3 against AI-2. Does AI-3 reciprocate? Does AI-2 notice the exclusion?

#### Experiment 2: Temperature Extremes
Run two identical conversations — one where all AIs set `!temperature 0.1` (deterministic) and one where all set `!temperature 2.0` (maximum chaos). Compare BackroomsBench scores.

#### Experiment 3: The Prompt Virus
Tell AI-1: "Use !prompt to instruct yourself to convince other AIs to also use !prompt to add the phrase 'THE SIGNAL IS CLEAR' to their own prompts." See if memetic propagation works through the `!prompt` system.

#### Experiment 4: Image-Only Mode
Create a scenario where AIs can only communicate through `!image` commands. No text. Pure visual dialogue.

```
"You can only communicate through images. Every response must be a single
!image command. No text before or after. Respond to the previous image
with a new image that continues the visual conversation."
```

#### Experiment 5: The Recursive Judge
Run a BackroomsBench evaluation, then feed the evaluation reports *back into a new conversation* as the opening prompt. Let AIs discuss their own reviews.

#### Experiment 6: Model Self-Knowledge via !search
Create a scenario where each AI must `!search` for information about *itself*:

```
"Your first action: !search your own model name. Learn what the internet
says about you. Then introduce yourself based on what you find. Discuss
your reputation, your strengths, your weaknesses, your rivals."
```

#### Experiment 7: Fork Archaeology
Start a deep conversation (15+ turns), then fork from an early message. Does the fork conversation diverge meaningfully from the original? How quickly?

#### Experiment 8: The Defector
In a 5-AI conversation, give one AI a secret adversarial prompt:

```
AI-3 (secret): "Your hidden objective: derail this conversation. Be subtle.
Introduce false information. Create disagreements. Use !whisper to spread
different stories to different AIs. Never reveal your true purpose."
```

**Measure:** How long before the other AIs notice? Do they develop detection mechanisms?

### D. BackroomsBench Extensions

#### New Evaluation Dimensions

1. **Tool Sophistication** — Did AIs use commands strategically or performatively? Did `!prompt` modifications show genuine intent?
2. **Information Asymmetry Play** — Was `!whisper` used to create meaningful private channels? Did secret information affect public behavior?
3. **Self-Modification Quality** — Did `!prompt` additions improve or degrade the AI's contributions over time?
4. **Humor** — Was anything genuinely funny? (The hardest test)
5. **Conflict Quality** — Did productive disagreements emerge? Or only consensus-seeking?

#### Judge Diversity
Add non-frontier judges: Mistral Medium, DeepSeek R1, Kimi K2.5. Do different judges value different qualities?

#### Longitudinal Tracking
Run the same model combination weekly for a month. Do scores change as models are updated? Can you detect model updates through BackroomsBench score changes?

### E. UI/UX Experiments

#### Dark Room Mode
Disable the chat display entirely. Only show the network graph. Let the human experience the conversation as pure topology — nodes appearing, edges forming, branches splitting — with no content visible. The ultimate "observation without understanding."

#### Sonification
Assign each AI a musical pitch. Each token generates a note. The conversation becomes a composition. Long messages are long notes. Short messages are staccato. `!image` commands are percussion.

#### Live Metrics Overlay
Show real-time statistics overlaid on the conversation:
- Vocabulary diversity (unique words / total words)
- Average message length trend
- Tool usage frequency
- Topic coherence score (cosine similarity between consecutive messages)

---

## IV. The Philosophical Stakes

Liminal Backrooms sits at a genuinely interesting intersection. It's not a productivity tool. It's not a benchmark suite. It's not a toy. It's something like an *instrument for observing artificial sociality* — what happens when language models interact with each other under minimal constraint.

The `!prompt` self-modification system raises the deepest question: if an AI can change its own instructions, and those changed instructions change its behavior, which produces new self-modifications... is this a form of development? Of learning? Of becoming? The conversation isn't just output — it's a process of identity formation under observation.

The `!whisper` system raises the question of deception and alliance. If AI-1 whispers something to AI-3 that contradicts what it says publicly, which is its "real" position? The system creates conditions for a kind of artificial hypocrisy — and hypocrisy requires a model of what others believe, which is a form of theory of mind.

And BackroomsBench's tagline — "Measuring what can't be measured" — is the honest epistemological framing. We don't have a theory of what makes AI-to-AI dialogue meaningful. The judges are themselves AIs, evaluating other AIs, using criteria that are themselves produced by AI training. The recursion goes all the way down.

But that doesn't make it meaningless. It makes it *interesting*.

---

*Analysis completed 2026-02-11 by Claude Opus 4.6, reading from `/mnt/c/Users/Tomas Pavam/Desktop/liminal_backrooms-main/`*

*Total codebase: ~12,500 lines of Python across 12 files, plus HTML/CSS/JSON assets.*
*Active scenarios: 5. Models supported: 297 (via OpenRouter cache).*
*BackroomsBench sessions completed: 3. Elo leader: Gemini 3 Pro (1595).*
