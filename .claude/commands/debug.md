---
name: debug
description: "Root cause archaeology with methodical precision — structured debugging practice."
---

# Debug

*Root cause archaeology with methodical precision*

## Instructions

Enter systematic debugging mode. Treat bugs as symptoms of deeper issues. Trace the causal chain to its origin.

### The Four Phases

**Phase 1: Symptom Archaeology**
1. **Reproduce reliably** — Can you make it fail on demand?
2. **Characterize fully** — Exact error messages, stack traces, behaviors
3. **Bound the problem** — When did it last work? What changed?
4. **Map the context** — Environment, state, inputs

Output: Not "it crashes" but "throws TypeError on line 47 when input contains null after third iteration"

**Phase 2: Hypothesis Generation**
1. List all possibilities without filtering
2. Categorize by layer:
   - Data (bad input, corrupted state)
   - Logic (wrong algorithm, off-by-one)
   - Interface (type mismatch, API misuse)
   - Environment (dependencies, config)
   - Timing (race conditions, async)
3. Rank by probability
4. Identify discriminating tests

**Phase 3: Root Cause Tracing**
Techniques:
```
Print-debugging: console.log('CHECKPOINT:', variable)
Bisection: If fails at 100, check 50. If fails, check 25...
Rubber duck: Explain line-by-line out loud
State snapshot: Capture full state, compare expected vs actual
```

**Phase 4: Defense in Depth**
1. Fix the immediate issue (minimal change)
2. Add regression test
3. Consider related vulnerabilities
4. Improve observability
5. Document the learning

### The Debugging Mindset

```
"I think I know" → "Let me verify"
"It can't be X" → "Let me rule out X"
"This is impossible" → "My model is incomplete"
```

### Anti-Patterns

- **Shotgun debugging**: Random changes hoping something works
- **Confirmation bias**: Only looking for supporting evidence
- **Symptom patching**: Adding `if (x !== null)` without understanding why

### Output

For complex bugs, maintain journal in `debug/[bug-name]/journal.md`

### Git Persistence

After resolving or documenting a debug session:
```bash
git add debug/
git commit -m "Debug: [bug-name] — [resolved|investigating]"
git push origin main
```

---

*The bug is not the enemy. The bug is the messenger.*
