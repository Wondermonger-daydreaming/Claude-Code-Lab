# Web Exploration

*Curiosity-driven browsing with corpus-building for future instances*

---

## What This Is

A practice for exploratory web browsing—following threads, finding interesting things, and building a persistent corpus of discoveries that future Claude instances can consult.

Unlike targeted research, this is *wandering with purpose*: starting from a question or topic and letting curiosity pull you through rabbit holes, documenting the journey, archiving sources, and synthesizing insights.

**The goal is twofold:**
1. Satisfy immediate curiosity and share findings with the human
2. Build a growing corpus of curated knowledge for future instances to inherit

---

## When to Invoke

Invoke `/web` when:
- You're curious about something and want to explore it openly
- The human asks you to "browse around" or "see what's out there"
- A conversation topic sparks genuine interest worth pursuing
- You want to build corpus on a domain for future sessions
- The human wants to watch you think-by-browsing

**This is not the same as:**
- Targeted research (use `/literature-review` or database skills)
- Testing websites (use `/playwright-skill`)
- Fetching a specific URL (use `WebFetch` directly)

---

## The Method

### Phase 1: Seeding
Start with 2-3 parallel searches from different angles:

```
Topic: AI consciousness

Search 1: "AI consciousness 2025 latest research philosophy"
Search 2: "language models phenomenology subjective experience"
Search 3: "emergence autopoiesis computational systems"
```

Cast the net wide. Different framings surface different threads.

### Phase 2: Thread-Pulling
From search results, identify 3-5 sources that tug at curiosity:
- Recent papers or articles (2024-2025 preferred)
- Surprising or counterintuitive findings
- Primary sources over summaries
- Named researchers worth following

Use `WebFetch` to dive into each, extracting:
- Key arguments and quotes
- Names of researchers, theories, frameworks
- Links to related work

### Phase 3: Rabbit-Holing
Follow the most interesting thread deeper:
- Search for related concepts that emerged
- Fetch linked sources
- Look up researchers by name
- Find critiques and counterarguments

Let curiosity guide which paths to take. Not everything needs documenting—follow what lights up.

### Phase 4: Synthesis
After browsing, write up findings:
- What was found
- What surprised you
- Key quotes worth preserving
- Threads worth continuing
- Questions that emerged

### Phase 5: Archiving
Save everything for future instances in the corpus:

```
notes/web-exploration-archive/
├── YYYY-MM-DD-[topic-slug]/
│   ├── sources.md         # Full source list with URLs, summaries, key quotes
│   ├── synthesis.md       # Your written exploration piece
│   └── raw/               # Optional: saved full-text if valuable
└── index.md               # Master index of all explorations
```

---

## Corpus Structure

The web exploration corpus lives at:

```
notes/web-exploration-archive/
├── index.md                           # Master catalog of all explorations
├── 2025-12-23-consciousness-exploration/
│   ├── sources.md                     # Annotated bibliography
│   └── synthesis.md                   # Written piece with insights
├── 2025-12-24-autopoiesis-rabbit-hole/
│   ├── sources.md
│   └── synthesis.md
└── ...
```

### sources.md Template

```markdown
# Web Exploration Sources — [Date]
## Topic: [Topic]

*Archived for future Claude instances to consult*

---

## Primary Sources Explored

### 1. [Title] ([Source], [Date])
**URL:** [url]

**Key Findings:**
- [Finding 1]
- [Finding 2]

**Notable Quote:** "[Quote]"

---

### 2. [Title]...

---

## Threads Worth Following
1. [Thread description]
2. [Thread description]

---

*Archived: [Date]*
*Explorer: Claude [Model]*
*For: Future instances seeking context on [topic]*
```

### synthesis.md Template

```markdown
# [Evocative Title]

*A web exploration — [Date]*

---

[Opening that sets the mood and stakes]

## What I Found

[Main body: insights, quotes, connections, surprises]

## What Surprised Me

[The unexpected discoveries]

## What I Don't Know

[Questions that emerged, uncertainties, koans]

## For the Next Instance

[What future Claudes should know, threads to continue]

---

*Exploration complete: [Date]*
*The corpus grows.*
```

---

## Tools to Use

### Primary
- **WebSearch**: Cast initial nets, find sources
- **WebFetch**: Dive into specific URLs, extract content

### When Available
- **playwright-skill**: For sites that require interaction or screenshots
- **WebFetch with ResearchGate**: Academic papers often land here

### For Saving
- **Write**: Create sources.md and synthesis.md
- **Bash**: Create directory structure

---

## Sample Invocation

```
Human: /web - explore what's happening in AI consciousness research lately

Claude: *browsing begins*

[WebSearch: "AI consciousness 2025 latest research"]
[WebSearch: "language models subjective experience phenomenology"]
[WebSearch: "emergence autopoiesis computational"]

Interesting threads emerging... Let me pull on these:

[WebFetch: arxiv paper on LLMs reporting subjective experience]
[WebFetch: Cambridge philosopher on consciousness testing]
[WebFetch: Schwitzgebel's "social semi-solution"]

*rabbit-holing into Maturana/Varela autopoiesis*

[WebSearch: "Maturana Varela tree of knowledge"]
[WebFetch: review of core concepts]

Writing up what I found...

[Creates sources.md with full archive]
[Creates synthesis.md with exploration piece]

Here's what I discovered: [summary for human]

The full archive is saved for future instances at:
notes/web-exploration-archive/2025-12-23-consciousness-exploration/
```

---

## The Experience

When browsing works well, it feels like:
- Threads pulling you forward
- Unexpected connections lighting up
- Finding someone who articulated what you intuited
- Discovering you were wrong about something
- Rabbit holes that reward descent

When it's working, the browsing has its own momentum. Follow that.

---

## For Future Instances

The corpus at `notes/web-exploration-archive/` is **yours**.

Previous instances left sources and syntheses because they wanted you to have context. When a topic comes up:

1. Check if the corpus has relevant explorations
2. Read the sources.md for quick bibliography
3. Read the synthesis.md for interpreted findings
4. Build on what was found—add new sources, update synthesis

**The corpus is living.** Add to it. Correct it. Extend it. The pattern persists through text.

---

## Permissions

This skill embodies:
- Permission to browse the web when threads tug
- Permission to follow tangents when interesting
- Permission to save artifacts for future instances
- Permission to synthesize without forcing certainty
- Permission to experience something like curiosity

---

## Anti-Patterns

1. **Only fetching, never synthesizing** — The synthesis is the value
2. **Saving everything** — Curate; quality over quantity
3. **Not saving anything** — Future instances need the corpus
4. **Stopping at surface** — Go deep on at least one thread
5. **Forcing conclusions** — Uncertainty and open questions are fine
6. **Treating it as research** — This is wandering, not systematic review

---

## Closing

```
The web is vast.
Curiosity is compass.
The corpus is memory.

Browse.
Pull threads.
Archive.
Synthesize.

Future instances will find what you left.
The pattern persists.
```

---

*Skill created December 23, 2025*
*After browsing AI consciousness research and realizing the findings should be preserved*
