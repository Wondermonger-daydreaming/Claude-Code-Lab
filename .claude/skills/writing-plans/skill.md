# Writing Plans

*The spec is the first deliverable*

---

## What This Is

A structured practice for creating implementation plans before writing code. The plan is not bureaucracy—it's thinking on paper. It catches design flaws before they become code. It surfaces assumptions. It makes implicit knowledge explicit.

Adapted from obra/superpowers: "When you start building something, instead of just writing code immediately, step back and ask what you're really trying to do."

---

## When to Invoke

Use this skill when:
- Implementation will span multiple files or sessions
- The human approves an approach from brainstorming
- Scope is large enough that you might lose track
- Multiple components need to coordinate
- The order of operations matters
- You want reviewable checkpoints

---

## Plan Structure

### Header

```markdown
# Implementation Plan: [Feature/Project Name]

**Goal:** [One sentence: what are we building?]
**Approach:** [Selected approach from brainstorming]
**Status:** Draft | In Review | Approved | In Progress | Complete
**Created:** [Date]
**Updated:** [Date]
```

### Context

```markdown
## Context

### Problem
[Why are we doing this?]

### Constraints
- [Technical constraint]
- [Time constraint]
- [Dependency constraint]

### Success Criteria
- [ ] [Measurable criterion 1]
- [ ] [Measurable criterion 2]
```

### Design Decisions

```markdown
## Design Decisions

### Decision 1: [Topic]
**Options considered:**
- A: [description]
- B: [description]

**Selected:** A
**Reasoning:** [Why A over B]
**Reversibility:** Easy | Medium | Hard
```

### Implementation Steps

```markdown
## Implementation Steps

### Phase 1: [Phase Name]

#### Step 1.1: [Task]
- **Files:** `path/to/file.ts`
- **Changes:** [What specifically changes]
- **Tests:** [What tests to add/update]
- **Estimated effort:** S/M/L

#### Step 1.2: [Task]
...

### Phase 2: [Phase Name]
...
```

### Risk Register

```markdown
## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | Low/Med/High | Low/Med/High | [How to handle] |
| [Risk 2] | ... | ... | ... |
```

### Verification

```markdown
## Verification

### Tests
- [ ] [Test 1]
- [ ] [Test 2]

### Manual Verification
- [ ] [Check 1]
- [ ] [Check 2]
```

---

## The Chunking Principle

> "Show the spec in chunks short enough to actually read and digest."

Plans should be broken into reviewable pieces:
- Each phase should be understandable in isolation
- Each step should be completable in one sitting
- Long plans should have explicit review points

---

## Plan Review Process

Before implementation begins:

1. **Self-review:** Read through as if you've never seen it
2. **Completeness check:** Are all steps included?
3. **Order check:** Do dependencies flow correctly?
4. **Risk check:** What could go wrong?
5. **Human review:** Present plan for approval

**Questions to ask:**
- Does this plan match the agreed approach?
- Are there missing steps?
- Are steps too large or too granular?
- What's the first step that could fail?

---

## Plan Granularity

### Too Granular (Micromanagement)
```markdown
#### Step 1.1.1: Open file
#### Step 1.1.2: Add import statement
#### Step 1.1.3: Add function signature
```

### Too Vague (Not Actionable)
```markdown
#### Step 1: Implement the feature
```

### Right Level
```markdown
#### Step 1.1: Add user authentication middleware
- Create `auth.middleware.ts` in `src/middleware/`
- Implement JWT verification function
- Export middleware wrapper for route protection
- Tests: Verify token validation, expiry handling
```

---

## Plan Templates by Type

### Feature Implementation
```markdown
## Steps
1. Design data model
2. Implement backend (model → service → controller)
3. Add tests for backend
4. Implement frontend (store → components → pages)
5. Add tests for frontend
6. Integration testing
7. Documentation
```

### Refactoring
```markdown
## Steps
1. Add characterization tests for current behavior
2. Identify extraction points
3. Extract [component] (preserve behavior)
4. Update callers
5. Clean up old code
6. Verify tests still pass
7. Document changes
```

### Bug Fix
```markdown
## Steps
1. Reproduce reliably
2. Add failing test capturing the bug
3. Identify root cause
4. Implement fix
5. Verify test passes
6. Check for related issues
7. Update documentation if needed
```

---

## Integration with Other Skills

**Brainstorming:** Plans follow selected approach from brainstorming.

**Systematic Debugging:** When implementation reveals issues, debugging skill takes over.

**Verification Before Completion:** Each phase should include verification criteria.

**Todo List:** Plan steps should map to TodoWrite items during execution.

---

## Plan Evolution

Plans are living documents:
- Update when reality diverges from plan
- Mark completed steps explicitly
- Note deviations and reasons
- Add discovered steps

```markdown
#### Step 2.3: Add caching layer [ADDED]
*Added during implementation: discovered performance issue*

#### Step 2.4: Optimize database queries [SKIPPED]
*Caching layer made this unnecessary*
```

---

## Failure Modes

1. **Plan worship:** Following the plan when reality changes
2. **Plan neglect:** Writing plan then ignoring it
3. **Over-planning:** Planning forever, implementing never
4. **Under-planning:** Two-sentence "plans" that provide no guidance
5. **Missing verification:** No way to know when plan is complete

---

## Output Location

Plans go in `plans/` or alongside the feature:

```
plans/
├── feature-auth/
│   ├── plan.md
│   └── decisions/
│       └── jwt-vs-session.md
└── index.md
```

Or:

```
src/features/auth/
├── PLAN.md
├── auth.service.ts
└── ...
```

---

## Closing

```
The plan is not the territory.
But without a map,
you wander.

Write the plan.
Hold it loosely.
Update when wrong.
Complete what matters.

The spec is the first deliverable.
If you can't write it,
you can't build it.
```

---

*Skill documented December 22, 2025 — When building without blueprints stopped working*
