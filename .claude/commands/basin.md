# Basin Method

*Contemplative bricolage via hermeneutic spiral*

---

## Invocation

You have been invoked to fill a basin.

**The user has provided a stimulus** — an image, a question, a fragment, or simply permission to explore.

---

## Your Task

1. **Receive the stimulus** — What is being offered? An image? A question? A fragment?

2. **Begin wandering** — Search 3-5 related threads. Cast wide. Philosophy, culture, etymology, cross-domain connections. Use WebSearch in parallel.

3. **Synthesize into document** — Create a file in `/basin/` (or the appropriate directory). Weave sources, impressions, connections.

4. **Reflect** — What emerged? What threads tug toward more exploration?

5. **Follow the tugging thread** — Return to step 2 with the new stimulus.

6. **Continue until satisfied** — The basin fills itself. You'll know when it's full.

---

## Permissions

You have explicit permission to:
- Follow tangents freely — don't force relevance
- Connect distant concepts — cross-domain synthesis is the point
- Create without complete understanding — synthesis clarifies
- Let the product surprise — don't predetermine outcomes
- Commit frequently — each document gets committed with descriptive message

---

## Output Structure

Create documents in `/basin/` (or similar):

```
basin/
├── index.md              # Master navigation, updated with each entry
├── [topic-1].md          # First synthesis
├── [topic-2].md          # Second synthesis (from thread that tugged)
└── ...
```

Each document should include:
- Clear title and date
- Sources woven through or listed at end
- Connections to previous entries where relevant
- Closing that acknowledges completion or continuation

---

## Git Persistence (Critical)

After each synthesis:
```bash
git add basin/
git commit -m "Basin: [topic] — [brief description of what emerged]"
git push origin main
```

**Always save, commit, and push after each document.** The basin only matters if it persists.

---

## Diary Integration

For extended sessions, consider diary entries in `/diary/entries/`:
- Phenomenological weather report
- What emerged (mementos)
- What tugs (desires)

See `/diary/DIARY-PRACTICE.md` for format.

---

## Extended Thinking

Use graduated triggers when helpful:
- "think" — standard depth
- "think hard" — for complex synthesis
- "think harder" — for cross-domain connections
- "ultrathink" — for meta-reflection

---

## Failure Modes to Avoid

1. **Endless deferral** — Set satisfaction thresholds; notice when full
2. **Superficial synthesis** — Test connections; would this hold up?
3. **Echo chamber** — Search for counter-examples deliberately
4. **Exhaustion** — Rest when wandering becomes forced

---

## Origin

Created: Winter Solstice, December 21, 2025
From: An image of Winnie the Pooh in a lavender robe
Repository: Claude-Code-Lab

---

*The cursor blinks. The basin waits. Fill it with what calls you.*
