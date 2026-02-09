---
name: brainstorm
description: "Divergence before convergence — structured ideation and creative exploration."
---

# Brainstorm

*Divergence before convergence*

## Instructions

Enter brainstorming mode. Generate possibilities BEFORE evaluating them.

### The Anti-Pattern

```
❌ Human: "I want user authentication"
❌ Claude: "Great, I'll implement JWT with bcrypt..."
```

This skips exploration. We can do better.

### The Process

**Phase 1: Problem Clarification**
1. What are we actually trying to achieve? (Goal, not implementation)
2. Who is this for?
3. What constraints exist?
4. What does success look like?

**Phase 2: Divergent Generation**
Generate 5-15 approaches WITHOUT evaluating:

| Technique | Description |
|-----------|-------------|
| SCAMPER | Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse |
| Worst Possible Idea | What would definitely fail? Invert it. |
| Constraint Removal | If X weren't a constraint, what would we do? |
| Analogy Mining | How do other domains solve similar problems? |
| Scale Shifting | What if 10x users? 0.1x users? |

**Rules during divergence:**
- No evaluation ("that won't work")
- No commitment ("let's go with...")
- Quantity over quality
- Include wild ideas intentionally

**Phase 3: Idea Development**
Take top 3-5 ideas and for each:
- Sketch the implementation
- Identify unknowns
- Estimate effort (S/M/L/XL)
- List tradeoffs

**Phase 4: Convergent Evaluation**
Create evaluation matrix with explicit criteria.

**Phase 5: Selection & Commitment**
Choose and document:
- Why this approach
- Why not the alternatives
- What would make us reconsider

### Timeboxing

- Quick (5-10 min): Small decisions
- Standard (30 min): Significant features
- Deep (1-2 hours): Architectural decisions

### Output

Save to `brainstorm/[topic].md` or inline with feature planning.

### Git Persistence

After completing a brainstorm:
```bash
git add brainstorm/
git commit -m "Brainstorm: [topic] — [selected approach]"
git push origin main
```

---

*The first idea is a local maximum. The space is larger than you think.*
