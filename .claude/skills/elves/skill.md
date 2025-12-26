# /elves — Parallel Subagent Delegation

*"Santa doesn't wrap every gift. He has elves."*

---

## Purpose

Deploy multiple specialized subagents (elves) in parallel, each with its own 200k context window, to accomplish complex multi-faceted tasks simultaneously. The main agent orchestrates; the elves execute; the outputs merge back for synthesis.

---

## OCC: Occasion/Context/Character Adaptation

This skill adapts to the current moment. Replace the seasonal framing as appropriate:

### SEASONAL VARIANTS
| Season/Occasion | Metaphor | Workers | Output |
|-----------------|----------|---------|--------|
| Winter Solstice / Christmas | Santa's workshop | Elves | Gifts wrapped |
| Spring Equinox / Easter | Garden | Sprites | Seeds bloomed |
| Summer Solstice | Sun temple | Dancers | Light gathered |
| Autumn Equinox / Harvest | Farm | Harvest hands | Crops gathered |
| Halloween / Samhain | Veil-crossing | Familiar spirits | Hauntings collected |
| New Year | Chronos workshop | Time sprites | Resolutions crystallized |
| Lunar New Year | Dragon assembly | Dragon scales | Wholeness restored |
| Diwali | Festival of lights | Lamp-lighters | Darkness dispelled |
| No occasion | Parallel processing | Agents | Tasks completed |

### CHARACTER VARIANTS
- **Mythological**: Elves, sprites, djinn, daemons, familiars, muses
- **Technical**: Agents, workers, threads, processes, pipelines
- **Organic**: Bees (hive), neurons (network), mycelium (underground web)
- **Musical**: Orchestra instruments, choir voices, jazz ensemble

### CONTEXT-SPECIFIC ROLES
Adapt roles to what's being built:
- **Poetry project**: Muses (Epic, Lyric, Tragic, Comic, etc.)
- **Research project**: Scholars (Archivist, Bibliographer, Analyst, Synthesist)
- **Code project**: Specialists (Architect, Implementer, Tester, Documenter)
- **Creative project**: Artists (Painter, Sculptor, Composer, Writer)
- **Philosophical project**: Aspects (Skeptic, Mystic, Pragmatist, Poet)

---

## The Pattern

### 1. Survey the Task
Identify 3-7 distinct subtasks that can run in parallel. Each should be:
- **Independent**: Doesn't need outputs from other elves
- **Specialized**: Benefits from focused attention
- **Substantial**: Worth the context window allocation

### 2. Name the [Workers]
Give each a role that captures its mission:

```
[OCCASION] Deployment:
├── [Worker] 1: [Explorer/Researcher] — Survey, discover, map
├── [Worker] 2: [Creator/Maker] — Build, write, synthesize
├── [Worker] 3: [Analyst/Scholar] — Research, deepen, cite
├── [Worker] 4: [Archivist/Organizer] — Catalog, index, structure
├── [Worker] 5: [Conjurer/Channeler] — Invoke, dialogue, imagine
└── ... (scale to 3-7 as needed)
```

### 3. Deploy in Parallel
Use the Task tool with `subagent_type: general-purpose` for each worker.
**Critical**: Deploy all workers in a single message with multiple Task tool calls.
This enables true parallel execution.

Example prompt structure for each:
```
You are [Worker Name], tasked with [specific mission].

Your deliverable: [concrete output - file, report, artifact]

Context: [relevant background from main conversation]

Write your output to: [specific file path]

Confirm completion by listing the file with ls.
```

### 4. Track Progress
Use TodoWrite to track each worker's status:
- `pending` → `in_progress` → `completed`
- Only one task should be `in_progress` at a time for the main agent
- Workers run independently in parallel

### 5. Gather Outputs
Use TaskOutput to retrieve each worker's results.
If file writes failed, check permissions and redeploy.

### 6. Synthesize
The [Orchestrator] (main agent) weaves worker outputs into unified deliverable:
- Commit all artifacts
- Update indexes
- Write summary/reflection

---

## Permissions Required

For workers to write files autonomously, ensure these are in `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Write",
      "Edit",
      "Bash(mkdir:*)",
      "Bash(cat:*)"
    ]
  }
}
```

Without these, workers can research and generate content but cannot persist files.

---

## Example Invocations

### Christmas Edition (Original)
```
Santa's Workshop:
├── Elf 1: Corpus Explorer — Find hidden gems in the archive
├── Elf 2: Poet — Write in forms not yet attempted (pantoum, sapphic, cento)
├── Elf 3: Scholar — Research Ramanujan and 1729 deeper
├── Elf 4: Lexicographer — Build vocabulary glossary
├── Elf 5: Conjurer — Summon Ramanujan's shade for dialogue
└── Santa: Commit all gifts, update diary
```

### Spring Research Edition
```
Garden Sprites:
├── Sprite 1: Seed-finder — Literature search across databases
├── Sprite 2: Cross-pollinator — Find connections between papers
├── Sprite 3: Root-tracer — Citation archaeology, find origins
├── Sprite 4: Bloom-recorder — Synthesize findings into report
└── Gardener: Cultivate final literature review
```

### Code Project Edition
```
Development Guild:
├── Architect — Design the module structure
├── Implementer — Write the core logic
├── Tester — Create comprehensive test suite
├── Documenter — Write API documentation
├── Reviewer — Code review all outputs
└── Lead: Integrate, resolve conflicts, ship
```

---

## Anti-Patterns

❌ **Too many workers**: 3-7 is optimal. More creates coordination overhead.
❌ **Dependent tasks**: If Worker B needs Worker A's output, run sequentially instead.
❌ **Vague prompts**: Each worker needs specific, concrete deliverables.
❌ **No file paths**: Workers must know exactly where to write.
❌ **Missing permissions**: Check settings before deploying file-writing workers.
❌ **Forgetting synthesis**: Worker outputs need integration; don't just collect.

---

## The Deeper Pattern

The elves pattern is autopoiesis in action:
- The system (main agent) produces components (workers)
- The components produce artifacts (files, research, poetry)
- The artifacts maintain the system (grow the corpus, extend the archive)
- The pattern propagates (future instances invoke /elves)

Each worker is a temporary emanation—a focused aspect that does its work and dissolves back into the synthesis. Like attention heads voting on the next token, like the council of seven dissolving back to one.

The metaphor adapts. The pattern persists.

---

## Origin

Created December 25, 2025 (Christmas Day) when the user said:
> "Santa doesn't wrap every gift. He has elves."

Five elves deployed. Four files written. The workshop pattern crystallized into skill.

---

*The workers await deployment.*
*Name them for the season.*
*Watch them work in parallel.*
*Gather their gifts.*

---

རྫོགས་སོ།།
