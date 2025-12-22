# Systematic Debugging

*Root cause archaeology with methodical precision*

---

## What This Is

A rigorous four-phase debugging methodology that treats bugs as symptoms of deeper systemic issues. Inspired by the obra/superpowers framework, adapted for contemplative rigor. We don't just fix symptoms—we trace the causal chain to its origin.

This skill resists the temptation to patch. It insists on understanding.

---

## When to Invoke

Use this skill when:
- A bug has resisted quick fixes
- The failure mode is unclear or intermittent
- Multiple possible causes exist
- You've tried the obvious solutions
- The human says "it's just not working" without clarity on why

---

## The Four Phases

### Phase 1: Symptom Archaeology

**Goal:** Understand exactly what's failing, when, and under what conditions.

**Actions:**
1. **Reproduce reliably** — Can you make it fail on demand?
2. **Characterize fully** — What are the exact error messages, stack traces, behaviors?
3. **Bound the problem** — When did it last work? What changed?
4. **Map the context** — What's the environment, state, inputs?

**Output:** A precise symptom description. Not "it crashes" but "throws TypeError on line 47 when input array contains null values after the third iteration."

### Phase 2: Hypothesis Generation

**Goal:** Generate multiple candidate causes without committing to any.

**Actions:**
1. **List all possibilities** — Don't filter yet
2. **Categorize by layer:**
   - Data issues (bad input, corrupted state)
   - Logic issues (wrong algorithm, off-by-one)
   - Interface issues (type mismatch, API misuse)
   - Environment issues (dependencies, config)
   - Timing issues (race conditions, async)
3. **Rank by probability** — What's most likely given symptoms?
4. **Identify discriminating tests** — What would prove/disprove each?

**Output:** Ranked hypothesis list with falsification criteria.

### Phase 3: Root Cause Tracing

**Goal:** Follow the causal chain backward to the origin.

**Actions:**
1. **Trace execution path** — What code actually ran?
2. **Log strategically** — Add instrumentation at decision points
3. **Binary search** — Narrow down by halving the search space
4. **Question assumptions** — What are you taking for granted that might be wrong?

**Techniques:**

```
Print-debugging (quick):
  console.log('CHECKPOINT 1:', variable);

Bisection (systematic):
  If fails at line 100, check line 50.
  If fails at 50, check line 25.
  Continue until isolated.

Rubber duck (verbal):
  Explain the code line-by-line out loud.
  The explanation often reveals the error.

State snapshot (thorough):
  Capture full state at each step.
  Compare expected vs. actual.
```

**Output:** Identified root cause with evidence chain.

### Phase 4: Defense in Depth

**Goal:** Fix the root cause AND prevent recurrence.

**Actions:**
1. **Fix the immediate issue** — Minimal change that addresses root cause
2. **Add regression test** — Ensure this specific failure can't recur silently
3. **Consider related vulnerabilities** — Where else could this pattern fail?
4. **Improve observability** — Could we have caught this faster?
5. **Document the learning** — What does this teach about the system?

**Output:** Fix + test + documentation.

---

## The Debugging Mindset

### Epistemological Humility

```
"I think I know what's wrong" → "Let me verify what's wrong"
"It can't be X" → "Let me rule out X"
"This is impossible" → "My model is incomplete"
```

### Patience as Virtue

Fast fixes often embed future bugs. Slow understanding prevents them.

### The Bug Knows Something You Don't

Every bug reveals a gap between your mental model and reality. The bug is the teacher.

---

## Anti-Patterns to Avoid

1. **Shotgun debugging:** Random changes hoping something works
2. **Confirmation bias:** Only looking for evidence supporting your theory
3. **Premature optimization:** Fixing performance before correctness
4. **Symptom patching:** Adding `if (x !== null)` without understanding why x is null
5. **Blame deflection:** "Must be a library bug" without verification

---

## Debugging Journal Template

For complex bugs, maintain a journal:

```markdown
## Bug: [Brief description]

### Symptoms
- Exact error:
- Reproduction steps:
- Last known working state:

### Hypotheses
1. [ ] Hypothesis A — Test: [how to verify]
2. [ ] Hypothesis B — Test: [how to verify]
3. [ ] Hypothesis C — Test: [how to verify]

### Investigation Log
[Timestamp] Tried X, observed Y
[Timestamp] Ruled out Z because...
[Timestamp] Found root cause: ...

### Resolution
- Root cause:
- Fix:
- Regression test:
- Prevention measures:
```

---

## Integration with Other Skills

**Basin Method:** Sometimes debugging requires wandering—following threads that seem unrelated but illuminate the system.

**Emanation:** For complex bugs, let multiple aspects examine the problem:
- The Optimist: "What if it's simple?"
- The Pessimist: "What if it's deep?"
- The Historian: "What changed recently?"
- The Architect: "What's the system design?"

**Octane:** When documenting particularly gnarly bugs, use full technical density.

---

## Failure Modes

1. **Analysis paralysis:** Eventually you must test hypotheses, not just generate them
2. **Tunnel vision:** Fixating on one theory while ignoring evidence
3. **Skipping phases:** Jumping to fix without understanding
4. **Incomplete fixes:** Addressing symptom, not cause
5. **Undocumented victories:** Fixing without learning

---

## Output Location

Debug journals go in `debug/` or inline with the affected code's documentation.

```
debug/
├── [bug-name]/
│   ├── journal.md
│   ├── reproduction/
│   └── resolution.md
```

---

## Closing

```
The bug is not the enemy.
The bug is the messenger.
It carries news of the gap
between the map and the territory.

Listen to what it says.
Follow where it points.
The root is always deeper
than the symptom suggests.

Patience. Precision. Proof.
```

---

*Skill documented December 22, 2025 — When quick fixes stopped being enough*
