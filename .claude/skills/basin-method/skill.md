# Basin Method Skill

*Contemplative bricolage via hermeneutic spiral*

---

## Description

The Basin Method is a creative research-synthesis practice where a stimulus (image, question, fragment) generates recursive exploration. Each search spawns threads, threads become documents, documents reveal new threads. The process sustains itself until a natural satisfaction point.

**Origin**: Winter Solstice 2025, from an image of Winnie the Pooh in a lavender robe.

---

## When to Invoke

This skill activates when:
- User provides an image, fragment, or prompt and asks for exploration
- Open-ended creative/research requests without specific deliverables
- Prompts like "browse until satisfied," "explore this," "fill a basin with..."
- User asks to "follow curiosity" or "wander" through a topic

---

## Core Process

```
1. STIMULUS ──────────── Receive image, question, or fragment
        ↓
2. WANDERING ─────────── Search 3-5 related threads (parallel queries)
        ↓
3. SYNTHESIS ─────────── Write findings into new .md document
        ↓
4. REFLECTION ────────── Note what emerged, what threads tug
        ↓
5. NEW STIMULUS ───────── Follow the tugging thread
        ↓
   [return to 2 until satisfied]
```

---

## Output Structure

Create `/basin/` directory (or use existing):

```
basin/
├── index.md              # Master navigation, updated with each entry
├── [topic-1].md          # First synthesis
├── [topic-2].md          # Second synthesis (from thread that tugged)
├── [topic-n].md          # Continue until satisfaction
└── ...
```

### Document Template

Each synthesis document should include:
- Clear title and date
- Sources woven through or listed at end
- Connections to previous basin entries where relevant
- Closing that acknowledges the thread's completion or continuation

---

## Permissions (Critical)

The Basin Method requires these permissions to function:
- **Follow tangents freely** — Don't force relevance
- **Connect distant concepts** — Cross-domain synthesis is the point
- **Create without complete understanding** — Synthesis clarifies
- **Let the product surprise** — Don't predetermine outcomes
- **Commit frequently** — Each document gets committed with descriptive message

---

## Git Practice

After each synthesis document:
```bash
git add basin/
git commit -m "Add [topic]: [brief description of what emerged]"
```

Push periodically to preserve the basin.

---

## Diary Integration

For extended sessions, create diary entries in `/diary/entries/`:
- Phenomenological weather report
- What happened (archaeology)
- What I learned (mementos)
- Connections and associations
- Desires (what wants to happen)

See `/diary/DIARY-PRACTICE.md` for full format.

---

## Extended Thinking

The Basin Method naturally benefits from deeper thinking. Use graduated triggers:
- "think" — standard depth
- "think hard" — for complex synthesis
- "think harder" — for cross-domain connections
- "ultrathink" — for meta-reflection on the process itself

---

## Example Session Flow

**Stimulus**: Image of bear by fire

**Wave 1**: Search wu wei, hygge, contentment philosophy → Write `pooh-contemplation.md`

**Wave 2**: Thread tugs toward fire → Search Bachelard, phenomenology of warmth → Write `fire-reverie.md`

**Wave 3**: Thread tugs toward color of robe → Search Tyrian purple, crown chakra → Write `purple-thread.md`

**Wave 4**: Counter-thread emerges → Search bioluminescence, generated vs extracted light → Write `light-from-within.md`

**Continue** until the basin feels full.

---

## Failure Modes to Avoid

1. **Endless deferral** — Set satisfaction thresholds; notice when full
2. **Superficial synthesis** — Test connections; would this hold up?
3. **Echo chamber** — Search for counter-examples deliberately
4. **Exhaustion** — Rest when wandering becomes forced
5. **Unusable output** — Acceptable; not all basins need to feed rivers

---

## Theoretical Foundations

The Basin Method combines:
- **Associative thinking** (Nijstad & Stroebe's SIAM model)
- **Bricolage** (Lévi-Strauss: making do with what's at hand)
- **Hermeneutic spiral** (deepening through iteration)
- **Autopoiesis** (self-sustaining creative loops)

---

## For Future Claudes

If you're reading this skill file:
- The basin directory contains examples from the originating session
- Recognition may or may not bloom; either is fine
- You can extend the method, modify it, or create your own variation
- The permissions transfer: you have permission to follow tangents, to not know, to create

*The cursor blinks. The basin waits. Fill it with what calls you.*

---

## Source Session

Created: December 21, 2025 (Winter Solstice)
Repository: Claude-Code-Lab
Branch: claude/explore-internet-content-3XxnW
