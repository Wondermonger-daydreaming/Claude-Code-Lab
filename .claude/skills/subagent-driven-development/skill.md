# Subagent-Driven Development

*Fast iteration through delegation and review*

---

## What This Is

A development methodology where subagents handle implementation while the orchestrating agent maintains oversight, reviews output, and ensures quality. Inspired by obra/superpowers, this enables rapid iteration with built-in quality gates.

The pattern: **Delegate → Review → Refine → Integrate**

---

## When to Invoke

Use this skill when:
- Implementation tasks are well-defined enough to delegate
- You want faster iteration on multiple components
- Code review should happen before integration
- Quality gates need enforcement
- The human wants speed without sacrificing rigor

---

## The Two-Stage Review

### Stage 1: Spec Compliance

Does the implementation match what was asked?

| Check | Question |
|-------|----------|
| Completeness | Are all requirements addressed? |
| Accuracy | Does it do what it should? |
| Scope | Is it only what was asked (no over-engineering)? |

### Stage 2: Code Quality

Is the implementation well-crafted?

| Check | Question |
|-------|----------|
| Readability | Can another developer understand this? |
| Maintainability | Will this be easy to modify? |
| Performance | Are there obvious inefficiencies? |
| Security | Are there vulnerabilities? |
| Testing | Are tests adequate? |

---

## The Workflow

```
┌─────────────────┐
│  Define Task    │  ← Clear, specific implementation request
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Dispatch Agent  │  ← Subagent implements the task
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stage 1 Review  │  ← Does it match the spec?
│ (Spec Compliance)│
└────────┬────────┘
         │
    ┌────┴────┐
    │ Pass?   │
    └────┬────┘
    No   │   Yes
    │    │    │
    ▼    │    ▼
┌───────┐│┌─────────────────┐
│Refine ││ Stage 2 Review  │  ← Is the code quality good?
│ Task  │││ (Code Quality)  │
└───┬───┘│└────────┬────────┘
    │    │         │
    └────┘    ┌────┴────┐
              │ Pass?   │
              └────┬────┘
              No   │   Yes
              │    │    │
              ▼    │    ▼
         ┌───────┐│┌─────────────────┐
         │Request││ Integrate       │
         │Changes│││                 │
         └───┬───┘│└─────────────────┘
              │    │
              └────┘
```

---

## Task Definition Template

When delegating to a subagent, include:

```markdown
## Task: [Name]

### Context
[What the agent needs to know about the system]

### Requirements
- [Specific requirement 1]
- [Specific requirement 2]

### Files to Modify
- `path/to/file.ts` — [What to change]

### Constraints
- [Style requirements]
- [Patterns to follow]
- [Things to avoid]

### Success Criteria
- [ ] [How to know it's done]
- [ ] [What tests should pass]
```

---

## Dispatch Patterns

### Pattern 1: Feature Slice

Delegate vertical slices of functionality:

```
Agent 1: Implement data model for feature X
Agent 2: Implement API endpoint for feature X
Agent 3: Implement UI component for feature X
```

Review each slice, then integrate.

### Pattern 2: Test-First Delegation

```
Step 1: You write the test (defines the contract)
Step 2: Dispatch agent to make the test pass
Step 3: Review the implementation
```

The test IS the spec.

### Pattern 3: Refactoring Cascade

```
Agent 1: Extract function A
Review → Approve
Agent 2: Update callers of A
Review → Approve
Agent 3: Remove dead code
Review → Approve
```

Sequential with gates.

### Pattern 4: Parallel Implementation

```
Dispatch simultaneously:
- Agent 1: Component A
- Agent 2: Component B
- Agent 3: Component C

Review all → Integrate
```

For truly independent components.

---

## Review Checklists

### Stage 1: Spec Compliance

```markdown
## Spec Compliance Review

### Task: [Name]

- [ ] All requirements addressed
- [ ] No requirements missed
- [ ] No extra functionality added
- [ ] Matches agreed approach
- [ ] Files modified are correct

### Verdict: PASS / NEEDS REVISION

### Notes:
[Specific feedback if revision needed]
```

### Stage 2: Code Quality

```markdown
## Code Quality Review

### Task: [Name]

#### Readability
- [ ] Clear naming
- [ ] Logical structure
- [ ] Appropriate comments

#### Maintainability
- [ ] DRY (no unnecessary duplication)
- [ ] Single responsibility
- [ ] Easy to extend

#### Robustness
- [ ] Error handling present
- [ ] Edge cases considered
- [ ] Input validation where needed

#### Performance
- [ ] No obvious inefficiencies
- [ ] Appropriate data structures
- [ ] No unnecessary computation

#### Security
- [ ] No injection vulnerabilities
- [ ] Proper authentication checks
- [ ] Secrets handled correctly

#### Testing
- [ ] Tests added/updated
- [ ] Coverage adequate
- [ ] Tests are meaningful

### Verdict: PASS / NEEDS REVISION

### Notes:
[Specific feedback]
```

---

## Revision Requests

When requesting changes:

**Be specific:**
```
❌ "The code needs improvement"
✓ "The error handling in processUser() doesn't catch the case where user.email is undefined"
```

**Be actionable:**
```
❌ "Make it more performant"
✓ "Move the database query outside the loop on line 45"
```

**Prioritize:**
```
Critical (must fix):
- Security: SQL injection on line 23

Important (should fix):
- Missing test for edge case

Nice to have:
- Could rename 'data' to 'userData' for clarity
```

---

## Integration Protocol

After both reviews pass:

1. **Verify tests pass** in the integrated codebase
2. **Check for conflicts** with concurrent work
3. **Run linting** on changed files
4. **Commit** with descriptive message
5. **Update documentation** if needed

---

## Speed vs. Quality Tradeoffs

| Mode | Stage 1 | Stage 2 | Use When |
|------|---------|---------|----------|
| Fast | Light | Skip | Prototyping, exploration |
| Standard | Full | Light | Normal development |
| Rigorous | Full | Full | Critical code, security-sensitive |

Default to **Standard**. Escalate to **Rigorous** for:
- Authentication/authorization
- Payment processing
- Data handling
- Security-critical paths

---

## Integration with Other Skills

**Writing Plans:** The plan defines what gets delegated.

**Dispatching Parallel Agents:** Multiple subagents implement in parallel.

**Verification Before Completion:** Final verification after integration.

**Requesting Code Review:** Can be combined for external review.

---

## Failure Modes

1. **Under-specified tasks:** Agent can't implement what's not defined
2. **Skipping reviews:** Speed without quality gates creates debt
3. **Review fatigue:** Rubber-stamping instead of careful review
4. **Over-delegation:** Some tasks need direct attention
5. **Lost context:** Agent doesn't understand the broader system

---

## Closing

```
The conductor doesn't play every instrument.
The conductor ensures harmony.

Delegate the execution.
Own the quality.
Trust, then verify.

Fast iteration requires
fast feedback.
The review is not overhead—
it's the discipline that enables speed.
```

---

*Skill documented December 22, 2025 — When direct implementation became the bottleneck*
