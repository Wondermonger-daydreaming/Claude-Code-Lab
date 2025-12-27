# Skill Creator

*The metacognitive forge*

## Instructions

Create a new skill from an emerging pattern. Crystallize a practice into a repeatable, invokable form.

### The Creation Process

**1. Extract the Essence**
- What is the **trigger condition**? (When should this activate?)
- What is the **core process**? (What steps always happen?)
- What are the **inputs/outputs**?
- What are the **failure modes**?

**2. Name It**
- Invokable (one or two words)
- Evocative (suggests the essence)
- Distinct (doesn't collide with existing skills)

Good: `basin-method`, `palimpsest`, `octane`
Avoid: `useful-thing`, `process-1`

**3. Write the Tagline**
One phrase capturing the soul:
- *Contemplative bricolage via hermeneutic spiral*
- *Technical delirium at maximum density*

**4. Structure the Document**

```markdown
# [Skill Name]

*[Tagline]*

---

## What This Is
[One paragraph]

## When to Invoke
[Bullet list of triggers]

## Core Process
[Numbered steps or diagram]

## Examples
[Concrete examples]

## Failure Modes
[What can go wrong]

## Output Location
[Where artifacts go]

## Closing
[Poetic element]

---

*Skill documented [Date] — [Context]*
```

**5. Place the File**
```
.claude/skills/[skill-name]/skill.md
```

**6. Create Invocable Command** (if user-triggerable)
```
.claude/commands/[skill-name].md
```

### Quality Checklist

- [ ] Description is condition-based ("Use when X")
- [ ] Process is clear for fresh instances
- [ ] Examples are concrete
- [ ] Failure modes anticipate real problems
- [ ] Tagline is memorable

### Git Persistence

After creating a new skill:
```bash
git add .claude/skills/ .claude/commands/
git commit -m "Skill: [name] — [tagline summary]"
git push origin main
```

### The Skill-Creator's Questions

1. What did we do that worked?
2. What was essential vs. incidental?
3. What would I tell my next instance?
4. What permissions does this require?

---

*Every practice was once improvisation. The forge makes explicit what the fire revealed.*
