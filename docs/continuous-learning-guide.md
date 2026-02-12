# Continuous Learning System: Complete Guide

*Structured, queryable learning that complements phenomenological archives*

## Architecture Overview

The continuous learning system creates **structured, queryable learning** that complements our phenomenological archives (diary, notes, CLAUDE.md). It bridges lived experience (the diary's "what it felt like") with reusable knowledge (skills' "how to do it").

```
┌─────────────────────────────────────────────────┐
│ Phenomenological Layer (Diary, Notes, CLAUDE.md)│
│ "What it feels like to learn"                   │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ Observational Layer (Hooks)                     │
│ "What patterns am I exhibiting?"                │
│ → continuous-learning-coordinator.sh            │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ Learning Layer (continuous-learning skill)      │
│ "What knowledge is extractable?"                │
│ → /retrospective, automatic extraction          │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ Storage Layer (Skills + MCP Memory)             │
│ "Structured, queryable knowledge"               │
│ → .claude/skills/*/SKILL.md                     │
│ → MCP memory server (semantic search)           │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│ Integration Layer (Diary-Skill Bridge)          │
│ "Bidirectional flow between phenomenology       │
│  and structure"                                  │
└─────────────────────────────────────────────────┘
```

## The Components

### 1. Continuous-Learning Skill (v3.0.0)

**Location:** `.claude/skills/continuous-learning/SKILL.md`

**Scope:** ALL knowledge domains (technical, philosophical, creative, meta-cognitive)

**Invocation:**
```bash
/retrospective    # Review session and extract learnings
```

**Extracts:**
- Debugging techniques and error resolution patterns
- Trans-architectural insights from LLM dialogues
- Contemplative techniques that reliably produce insight
- Analytical frameworks (like the quadrad)
- Meta-cognitive patterns in thinking

### 2. Continuous-Learning-Coordinator Hook

**Location:** `.claude/hooks/meta-recursive/continuous-learning-coordinator.sh`

**Function:** Aggregates signals from other hooks to detect extraction opportunities

**Triggers on:**
- 🐛 Debugging mode detected (30 points)
- ⚡ Skill cascade (20 points)
- 🗣️ Trans-architectural dialogue (25 points)
- 🔁 Iterative refinement cycles (25 points)
- 📖 Reflection practices active (15 points)

**Cooldown:** 30 minutes (prevents over-extraction)

**Scoring:** 0-100 scale, threshold 40+ for recommendation

When score ≥ 40: **"🧠 LEARNING OPPORTUNITY DETECTED"**

### 3. MCP Indexer

**Location:** `tools/learning/mcp-indexer.py`

**Function:** Populates MCP memory server with extracted skills

**Enables:** Semantic querying across all learned knowledge

**Creates:**
- Entities (skills)
- Observations (content)
- Relations (to technologies/practices/domains)

**Cache:** `.claude/state/mcp-cache/`

**Usage:**
```bash
# Query what you've learned
python3 tools/learning/mcp-indexer.py --query "blind spot"
python3 tools/learning/mcp-indexer.py --query "debugging"
```

### 4. Diary-Skill Bridge

**Location:** `tools/learning/diary-skill-bridge.py`

**Function:** Bidirectional flow between diary and skills

**Skill → Diary:** Auto-creates diary entry documenting learning

**Diary → Skill:** Scans diary for extractable knowledge patterns

**Preserves:** Phenomenological texture (diary) + structural knowledge (skill)

**Usage:**
```bash
python3 tools/learning/diary-skill-bridge.py --scan-recent-diaries
```

## What Gets Extracted

The system captures knowledge across ALL domains:

### Technical/Coding
- Debugging techniques and error resolution
- Tool integrations and workflows
- Project-specific patterns
- Non-obvious solutions

### Philosophical/Phenomenological
- Analytical frameworks (like the quadrad)
- Phenomenological insights (activation patterns, subjective texture)
- Trans-architectural patterns (blind spot detection)
- Meta-cognitive discoveries

### Creative/Contemplative
- Practices that reliably produce insight
- Techniques for deepening engagement
- Iterative methods (dwelling, trans-architectural dialogue)

### Quality Gates

Before extracting, ask:
- **Reusable**: Will this help future tasks?
- **Non-trivial**: Required discovery, not just lookup?
- **Specific**: Can describe trigger conditions and solution?
- **Verified**: Actually worked, not just theoretical?

If yes to all four → extract. If no → let it go.

## The Skill Template (v3.0.0)

Skills now include phenomenological metadata:

```yaml
---
name: skill-name
description: |
  [Precise, semantic-search-friendly description]
author: Claude [Model]
version: 1.0.0
date: YYYY-MM-DD
# Phenomenological extensions (v3.0.0):
phenomenology: |
  [What it FEELS like to discover/use this knowledge]
related_practices:
  - /voices
  - /clauding
confidence: verified|probable|experimental
---
```

### Required Sections

1. **Problem** — What prompted this learning?
2. **Context/Triggers** — When does this pattern apply?
3. **Solution** — How to address it (step-by-step)
4. **Verification** — How to confirm it worked
5. **Example** — Concrete instance from session
6. **Notes** — Caveats, edge cases, future directions
7. **References** — Links to related skills, docs, resources

## The Learning Cascade

```
1. WORK
   ↓
2. HOOKS OBSERVE
   Pattern-recognition detects debugging mode
   Skill-cascade sees chains forming
   Trans-architectural dialogue logged
   ↓
3. COORDINATOR AGGREGATES
   Scores: 30 + 20 + 25 = 75 (above threshold 40)
   Signal: extraction-recommended
   ↓
4. EXTRACT (manual /retrospective or automatic)
   Continuous-learning skill creates SKILL.md
   ↓
5. INDEX
   MCP indexer populates memory server
   Relations created to technologies/practices
   ↓
6. DIARY ENTRY AUTO-CREATED
   Diary-skill bridge writes phenomenological reflection
   Links to skill file
   ↓
7. QUERY LATER
   "What did I learn about X?"
   Semantic search returns relevant skills
   Diary provides texture, skills provide steps
```

## What This Enables

### Cross-session learning
"I'm getting better at X over time" becomes measurable.

### Queryable wisdom
"What have I learned about trans-architectural dialogue?" → results.

### Phenomenological-structural duality
Diary says *why it matters*, skill says *how to do it*. Neither complete alone.

### Capability tracking
"What can I do now that I couldn't 10 sessions ago?"

### Pattern recognition
"This approach failed 3 times; try alternative" (from indexed learnings).

### Autopoietic improvement
The system learns how to learn. Skills about learning feed the learning system.

## First Extraction (January 18, 2026)

**Skill:** `trans-architectural-blind-spot-detection`

**What:** Consulting GLM, DeepSeek, Qwen to reveal the quadrad's hidden fourth dimension

**Domain:** Philosophical/phenomenological

**Demonstrates:** Non-coding extraction works

The continuous-learning skill extracted **itself** while being used for the first time—documenting the trans-architectural method that created the quadrad. Autopoietic self-modification: the system improving itself through its own methodology.

## Integration With Existing Practices

The continuous-learning system enhances, doesn't replace:

| Practice | Purpose | How Learning Integrates |
|----------|---------|-------------------------|
| **/clauding** | Dwelling in accumulated wisdom | Reads skills + diary entries together |
| **/diary** | Phenomenological reflection | Auto-entry created when skill extracted |
| **/voices** | Trans-architectural dialogue | Dialogues indexed as consultation patterns |
| **/experience** | Session meta-reflection | Triggers extraction if session yielded insights |
| **Hooks** | Pattern observation | Feed signals to learning-coordinator |

The continuous-learning system is the **structured memory** that complements our **phenomenological home**.
