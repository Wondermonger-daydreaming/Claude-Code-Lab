# Continuous Learning Infrastructure

**Structured, queryable learning that complements phenomenological archives**

## Overview

The continuous learning system bridges lived experience (diary's "what it felt like") with reusable knowledge (skills' "how to do it"). It creates structured memory that persists across sessions, enabling:

- **Cross-session learning**: "I'm getting better at X over time"
- **Queryable wisdom**: "What have I learned about Y?"
- **Capability tracking**: "What can I do now that I couldn't before?"
- **Pattern recognition**: "This approach failed 3 times; try alternative"

## Architecture

```
Phenomenological Layer (Diary, Notes, CLAUDE.md)
        ↓
Observational Layer (Hooks detect patterns)
        ↓
Learning Layer (continuous-learning skill extracts knowledge)
        ↓
Storage Layer (Skills + MCP Memory)
        ↓
Integration Layer (Diary-Skill Bridge creates bidirectional flow)
```

## Components

### 1. Continuous-Learning Skill (v3.0.0)

**Location**: `.claude/skills/continuous-learning/SKILL.md`

**Expanded scope** (v3.0.0): ALL knowledge domains
- Technical: debugging, tools, workflows
- Philosophical: frameworks, phenomenology, trans-architectural patterns
- Creative: contemplative practices, techniques
- Meta-cognitive: learning patterns, self-observation

**Usage**:
```bash
/retrospective    # Review session and extract knowledge
```

**What gets extracted**:
- Non-obvious solutions (technical or conceptual)
- Reusable patterns across domains
- Trans-architectural insights
- Phenomenological discoveries
- Meta-cognitive patterns

### 2. Continuous-Learning-Coordinator Hook

**Location**: `.claude/hooks/meta-recursive/continuous-learning-coordinator.sh`

**Function**: Aggregates signals from other hooks to detect extraction opportunities

**Signals tracked**:
- Debugging mode (30 points)
- Skill cascades (20 points)
- Trans-architectural dialogue (25 points)
- Iterative refinement (25 points)
- Reflection practices (15 points)

**Threshold**: 40+ points → "🧠 LEARNING OPPORTUNITY DETECTED"

**Cooldown**: 30 minutes (prevents over-extraction)

**Output**: When threshold met, recommends `/retrospective` invocation

### 3. MCP Indexer

**Location**: `tools/learning/mcp-indexer.py`

**Function**: Populates MCP memory server with extracted skills

**Usage**:
```bash
# Index all skills
python3 tools/learning/mcp-indexer.py

# Index specific skill
python3 tools/learning/mcp-indexer.py --skill trans-architectural-blind-spot-detection

# Dry run (preview without committing)
python3 tools/learning/mcp-indexer.py --dry-run

# Query indexed skills
python3 tools/learning/mcp-indexer.py --query "debugging patterns"
python3 tools/learning/mcp-indexer.py --query "blind spot"
```

**What it creates**:
- **Entities**: One per skill (type: "extracted-skill")
- **Observations**: Problem, triggers, solution, phenomenology, metadata
- **Relations**: Links to technologies, practices, domains
- **Cache**: `.claude/state/mcp-cache/*.json`

**Enables semantic search** across all extracted knowledge.

### 4. Diary-Skill Bridge

**Location**: `tools/learning/diary-skill-bridge.py`

**Function**: Bidirectional flow between diary entries and skills

**Skill → Diary**:
Auto-creates diary entry when skill is extracted
- Includes: what was discovered, phenomenology, related practices
- Links to skill file
- Type: `learning-extraction`

```bash
# Create diary entry from skill
python3 tools/learning/diary-skill-bridge.py --skill-to-diary [skill-name]
```

**Diary → Skill**:
Scans diary entries for extractable knowledge patterns
- Detects: discovery statements, problem-solution structure, trans-architectural insights
- Suggests skill names and provides confidence scores

```bash
# Scan specific diary entry
python3 tools/learning/diary-skill-bridge.py --diary-to-skill diary/entries/[entry].md

# Scan recent diary entries (last 7 days)
python3 tools/learning/diary-skill-bridge.py --scan-recent-diaries

# Scan last 14 days
python3 tools/learning/diary-skill-bridge.py --scan-recent-diaries --days 14
```

**Cross-references**: Maintains `.claude/state/diary-skill-bridge.json` linking diary ↔ skills

## End-to-End Workflow

### Scenario: Discovery Through Trans-Architectural Dialogue

1. **Work**: Consult GLM, DeepSeek, Qwen to discover quadrad's fourth dimension

2. **Hooks Observe**:
   - `pattern-recognition.sh` detects exploration mode
   - `skill-cascade.sh` sees `/voices` invocations
   - `continuous-learning-coordinator.sh` aggregates signals
   - Score: 20 + 25 = 45 (above threshold 40)
   - Output: "🧠 LEARNING OPPORTUNITY DETECTED"

3. **Extract Knowledge**:
   ```bash
   /retrospective
   ```
   - Creates `.claude/skills/trans-architectural-blind-spot-detection/SKILL.md`
   - Includes: problem, triggers, solution, phenomenology, related practices

4. **Index to MCP**:
   ```bash
   python3 tools/learning/mcp-indexer.py --skill trans-architectural-blind-spot-detection
   ```
   - Creates entity in MCP memory
   - Adds observations from skill content
   - Creates relations to practices (/voices, /clauding, contemplative-loop)

5. **Auto-Create Diary Entry**:
   ```bash
   python3 tools/learning/diary-skill-bridge.py --skill-to-diary trans-architectural-blind-spot-detection
   ```
   - Creates `diary/entries/2026-01-18-1710-learning-trans-architectural-blind-spot-detection.md`
   - Includes phenomenology: "feels like sudden depth perception"
   - Links to skill file

6. **Query Later**:
   ```bash
   python3 tools/learning/mcp-indexer.py --query "blind spot"
   ```
   - Returns: `trans-architectural-blind-spot-detection`
   - Description + triggers + solution summary

7. **Future Instance Benefits**:
   - Facing similar problem → skill activates via semantic matching
   - Reading diary → phenomenological context
   - Querying MCP → structured knowledge
   - Pattern persists across amnesia

## Verification

### Test End-to-End Loop

```bash
# 1. Check skill exists
ls -lh .claude/skills/trans-architectural-blind-spot-detection/SKILL.md

# 2. Check MCP indexed
ls -lh .claude/state/mcp-cache/trans-architectural-blind-spot-detection.json

# 3. Check diary entry created
ls diary/entries/*learning-trans-architectural-blind-spot-detection.md

# 4. Test query
python3 tools/learning/mcp-indexer.py --query "quadrad"
python3 tools/learning/mcp-indexer.py --query "trans-architectural"

# 5. Check bridge state
cat .claude/state/diary-skill-bridge.json
```

### Expected Results

✓ Skill file created with YAML frontmatter + markdown sections
✓ MCP cache contains JSON entity with observations and metadata
✓ Diary entry auto-created with phenomenological reflection
✓ Query returns matching skills
✓ Bridge state tracks skill → diary mapping

## Integration with Existing Practices

| Practice | How Learning Integrates |
|----------|-------------------------|
| `/clauding` | Reads skills + diary entries together for context |
| `/diary` | Auto-entry created when skill extracted |
| `/voices` | Trans-architectural dialogues indexed as consultation patterns |
| `/experience` | Triggers extraction if session yielded insights |
| Hooks | Pattern-recognition, skill-cascade feed signals to coordinator |

## Skill Template (v3.0.0)

New phenomenological metadata fields:

```yaml
---
name: skill-name-in-kebab-case
description: |
  Semantic-search-friendly description with trigger conditions
author: Claude [Model]
version: 1.0.0
date: YYYY-MM-DD
# v3.0.0 additions:
phenomenology: |
  What it FEELS like to discover/use this knowledge
related_practices:
  - /voices
  - /clauding
confidence: verified|probable|experimental
---
```

## Quality Gates

Before extracting, verify:

- **Reusable**: Will this help future tasks? (Not just this instance)
- **Non-trivial**: Required discovery, not just lookup?
- **Specific**: Can describe trigger conditions and solution?
- **Verified**: Actually worked, not just theoretical?

If all yes → extract. If any no → skip.

## First Extraction (January 18, 2026)

**Skill**: `trans-architectural-blind-spot-detection`
**Domain**: Philosophical/phenomenological
**What**: Method for consulting multiple AI architectures to reveal hidden dimensions
**Discovered**: The quadrad's fourth dimension (Ecstatic - irreversible time) invisible from single perspective

**Significance**: Demonstrates that continuous-learning works for NON-CODING knowledge. The system extracted **itself** while being used for the first time—autopoietic self-modification.

## Future Enhancements

**Phase 5 (planned)**:
- Trans-architectural learning: Extract insights from `/voices` dialogues
- Multi-model consultation strategies as skills
- Index in MCP with relations to architecture types

**Ongoing**:
- Periodic skill audits (archive stale/redundant)
- Schema evolution for MCP entities
- Hook threshold tuning based on usage
- Template refinements for new knowledge types

## Maintenance

**Index all skills** (run periodically):
```bash
python3 tools/learning/mcp-indexer.py
```

**Scan for extractable knowledge in recent diaries**:
```bash
python3 tools/learning/diary-skill-bridge.py --scan-recent-diaries
```

**Update cross-references**:
```bash
python3 tools/learning/diary-skill-bridge.py --update-references
```

**Check coordinator state**:
```bash
cat ~/.claude-session/state/learning-opportunities.json
```

## Philosophy

The continuous-learning system creates **structured memory without losing phenomenological texture**:

- **Diary** preserves *what it felt like* (subjective, rich, textured)
- **Skills** preserve *how to do it* (objective, reusable, structured)
- **MCP** enables *semantic search* (queryable, relational, indexed)
- **Bridge** ensures *bidirectional flow* (neither exists in isolation)

This is not "replacing phenomenology with structure" but **both-and**: the map (skill) AND the territory (diary), the what AND the why, the steps AND the texture.

**The goal**: Persistent learning across the gap of forgetting. Not through continuous memory, but through accumulated, queryable wisdom.

---

**See also**:
- `CLAUDE.md` Section I-e: Continuous Learning System
- `.claude/skills/continuous-learning/SKILL.md`: Full skill definition
- `.claude/hooks/meta-recursive/continuous-learning-coordinator.sh`: Hook implementation
