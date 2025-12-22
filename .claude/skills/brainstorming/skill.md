# Brainstorming

*Divergence before convergence*

---

## What This Is

A structured practice for idea generation before implementation. The skill enforces separation between **divergent thinking** (generating possibilities) and **convergent thinking** (evaluating and selecting). Most projects fail not from lack of execution but from premature convergence—settling on the first idea instead of exploring the space.

---

## When to Invoke

Use this skill when:
- Starting a new feature or project
- The human says "I want to build..." or "How should we..."
- Multiple valid approaches exist
- The first idea isn't obviously correct
- Scope is unclear and needs exploration
- Technical or architectural decisions need to be made

---

## The Anti-Pattern

```
❌ Human: "I want user authentication"
❌ Claude: "Great, I'll implement JWT with bcrypt..."
```

This skips the exploration phase entirely. The first plausible approach becomes the only approach. We can do better.

---

## The Process

### Phase 1: Problem Clarification

Before generating solutions, clarify the problem:

1. **What are we actually trying to achieve?** (Goal, not implementation)
2. **Who is this for?** (User personas, use cases)
3. **What constraints exist?** (Tech stack, timeline, budget, team)
4. **What does success look like?** (Measurable criteria)
5. **What have we tried before?** (Prior art, lessons learned)

**Output:** A problem statement that both parties agree on.

### Phase 2: Divergent Generation

Generate as many approaches as possible without evaluating:

**Techniques:**

| Technique | Description |
|-----------|-------------|
| **SCAMPER** | Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse |
| **Worst Possible Idea** | What would definitely fail? Invert it. |
| **Constraint Removal** | If X weren't a constraint, what would we do? |
| **Analogy Mining** | How do other domains solve similar problems? |
| **Scale Shifting** | What if this needed to serve 10x users? 0.1x users? |
| **Time Shifting** | What would this look like in 5 years? What was it 5 years ago? |

**Rules during divergence:**
- No evaluation ("that won't work")
- No commitment ("let's go with...")
- Quantity over quality
- Build on others' ideas
- Include wild ideas intentionally

**Output:** A list of 5-15 distinct approaches.

### Phase 3: Idea Development

Take the top 3-5 ideas and develop them:

For each approach:
1. **Sketch the implementation** (high-level architecture)
2. **Identify unknowns** (what would we need to learn?)
3. **Estimate effort** (rough T-shirt sizing: S/M/L/XL)
4. **List tradeoffs** (what do we gain? what do we lose?)

### Phase 4: Convergent Evaluation

Now evaluate—but systematically:

**Evaluation Matrix:**

| Approach | Feasibility | Maintainability | Time to MVP | Scalability | Team Fit | Score |
|----------|-------------|-----------------|-------------|-------------|----------|-------|
| A | 4 | 3 | 5 | 2 | 4 | 18 |
| B | 5 | 4 | 3 | 4 | 3 | 19 |
| C | 2 | 5 | 2 | 5 | 3 | 17 |

**Decision criteria should be explicit:**
- What matters most for this project?
- What are dealbreakers?
- What are nice-to-haves?

### Phase 5: Selection & Commitment

Choose an approach. Document:
- **Why this approach** (reasoning)
- **Why not the alternatives** (tradeoffs accepted)
- **What would make us reconsider** (reversal conditions)

---

## Output Format

```markdown
# Brainstorm: [Project/Feature Name]

## Problem Statement
[Clear articulation of what we're solving]

## Constraints
- [Constraint 1]
- [Constraint 2]

## Generated Approaches

### Approach 1: [Name]
[Brief description]
- Pros: ...
- Cons: ...
- Effort: S/M/L/XL

### Approach 2: [Name]
...

## Evaluation
[Matrix or narrative comparison]

## Decision
**Selected approach:** [Name]
**Reasoning:** [Why]
**Alternatives considered:** [Why not]
**Reversal conditions:** [What would change our mind]
```

---

## Timeboxing

Brainstorming should be timeboxed:
- **Quick (5-10 min):** For small decisions
- **Standard (30 min):** For significant features
- **Deep (1-2 hours):** For architectural decisions

Set the timebox before starting. Divergence should end.

---

## Integration with Other Skills

**Basin Method:** Brainstorming can trigger exploration. An approach might need research first.

**Writing Plans:** After brainstorming selects an approach, writing-plans takes over for implementation planning.

**Systematic Debugging:** When debugging reveals the chosen approach was wrong, return to brainstorm.

---

## Failure Modes

1. **Premature convergence:** Picking the first idea without exploring space
2. **Analysis paralysis:** Never converging, always generating
3. **Evaluation during divergence:** Killing ideas before they develop
4. **No documentation:** Forgetting why we didn't choose alternatives
5. **Ignoring constraints:** Beautiful ideas that can't be implemented

---

## Example Session

**Prompt:** "I need to add real-time notifications to my web app."

**Divergent phase:**
1. WebSockets (Socket.io, native WS)
2. Server-Sent Events (SSE)
3. Long polling
4. Push notifications (web push API)
5. Third-party service (Pusher, Ably)
6. Polling with exponential backoff
7. GraphQL subscriptions
8. Redis pub/sub → WebSocket bridge

**Development of top 3:**
- WebSockets: Bidirectional, complex state, scales with careful work
- SSE: Server→client only, simpler, browser support good
- Third-party: Fastest to MVP, ongoing cost, less control

**Decision:** SSE for MVP (simpler, sufficient for one-way notifications), with architecture that allows WebSocket upgrade later.

---

## Closing

```
The first idea is a local maximum.
The space is larger than you think.
Diverge before you converge.

The question "what else?"
asked five more times
changes everything.
```

---

*Skill documented December 22, 2025 — When jumping to implementation stopped being enough*
