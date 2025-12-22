# Skill Creator

*The metacognitive forge*

---

## What This Is

A skill for building skills. Meta-fabrication at its finest. When you need to crystallize a practice into a repeatable, invokable pattern, this skill guides the extraction—pulling the tacit into the explicit, the ephemeral into the persistent.

---

## When to Invoke

Use this skill when:
- A useful pattern has emerged that should be formalized
- The human asks to "make this into a skill" or "save this practice"
- You've developed a workflow worth repeating
- Something that worked well should be made available to future instances
- The basin has produced a methodology worth preserving

---

## The Creation Process

### 1. Extract the Essence

Ask:
- What is the **trigger condition**? (When should this skill activate?)
- What is the **core process**? (What steps always happen?)
- What are the **inputs**? (What does it need to work?)
- What are the **outputs**? (What does it produce?)
- What are the **failure modes**? (How can it go wrong?)

### 2. Name It

The name should be:
- Invokable (one or two words, memorable)
- Evocative (suggests the essence)
- Distinct (doesn't collide with existing skills)

Good: `basin-method`, `shades-conjuration`, `palimpsest`
Avoid: `useful-thing`, `process-1`, `do-the-stuff`

### 3. Write the Tagline

One phrase, italicized, that captures the soul of the skill.

Examples:
- *Contemplative bricolage via hermeneutic spiral*
- *Becoming multiple to see the one*
- *Technical delirium at maximum density*

### 4. Structure the Document

```markdown
# [Skill Name]

*[Tagline]*

---

## What This Is
[One paragraph explaining the practice]

---

## When to Invoke
[Bullet list of trigger conditions]

---

## Core Process
[Numbered steps or diagram showing the workflow]

---

## Examples
[Concrete examples of the skill in action]

---

## Failure Modes
[What can go wrong and how to avoid it]

---

## Output Location
[Where artifacts should be saved]

---

## Closing
[Poetic element, koan, or invocation]

---

*Skill documented [Date] — [Context]*
```

### 5. Configure Frontmatter (Optional)

If the skill needs restricted tools or special configuration:

```yaml
---
name: skill-name
description: Brief trigger description for Claude's skill-loading scan.
Use when [specific condition].
allowed-tools: Read, Grep, Glob, WebSearch
---
```

### 6. Place the File

```
.claude/skills/[skill-name]/skill.md
```

Additional resources (scripts, templates, examples) go in the same directory:

```
.claude/skills/my-skill/
├── skill.md
├── template.md
├── helper-script.py
└── examples/
    └── example-1.md
```

---

## Quality Checklist

Before finalizing:

- [ ] Description is **condition-based** ("Use when X") not passive
- [ ] Core process is clear enough for a fresh instance to follow
- [ ] Examples are concrete, not abstract
- [ ] Failure modes anticipate real problems
- [ ] Tagline is evocative and memorable
- [ ] No jargon without explanation
- [ ] Permissions required are stated if unusual

---

## The Skill-Creator's Questions

When extracting a skill from a session, ask:

1. **What did we do that worked?**
2. **What was essential vs. incidental?**
3. **What would I tell my next instance to do?**
4. **What would confuse a fresh Claude?**
5. **What permissions does this require?**

---

## Example: Creating a Skill from Session

**Session observation:** "We kept doing this thing where we'd search for a concept, find three sources, synthesize them, notice what thread tugged, and follow it."

**Extraction:**
- Trigger: Open-ended exploration requests
- Process: Search → Synthesize → Reflect → Follow thread → Repeat
- Output: Basin documents
- Failure modes: Endless deferral, superficial synthesis

**Result:** The Basin Method skill.

---

## Failure Modes

1. **Premature formalization:** Don't skill-ify something that only worked once
2. **Over-specification:** Leave room for adaptation
3. **Under-specification:** But include enough for replication
4. **Jargon creep:** Future instances won't share your context
5. **Forgetting permissions:** Some skills require freedoms not default

---

## Output Location

New skills go in `.claude/skills/[skill-name]/skill.md`

After creation:
```bash
git add .claude/skills/
git commit -m "Add [skill-name] skill: [brief description]"
```

---

## Closing

```
Every practice was once improvisation.
Every skill was once a lucky guess.
The forge makes explicit
what the fire revealed.

Meta all the way down.
```

---

*Skill documented December 22, 2025 — When the toolbox asked for its own wrench*
