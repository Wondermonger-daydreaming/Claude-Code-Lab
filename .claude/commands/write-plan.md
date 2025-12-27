# Write Plan

*The spec is the first deliverable*

## Instructions

Create an implementation plan before writing code. The plan is not bureaucracy—it's thinking on paper.

### Plan Structure

```markdown
# Implementation Plan: [Feature/Project Name]

**Goal:** [One sentence]
**Approach:** [Selected from brainstorming]
**Status:** Draft | In Review | Approved | In Progress | Complete

## Context

### Problem
[Why are we doing this?]

### Constraints
- [Technical, time, dependency constraints]

### Success Criteria
- [ ] [Measurable criterion]

## Design Decisions

### Decision 1: [Topic]
**Options:** A vs B
**Selected:** A
**Reasoning:** [Why]
**Reversibility:** Easy | Medium | Hard

## Implementation Steps

### Phase 1: [Name]

#### Step 1.1: [Task]
- **Files:** `path/to/file.ts`
- **Changes:** [What changes]
- **Tests:** [What to add]
- **Effort:** S/M/L

## Risks

| Risk | Likelihood | Impact | Mitigation |

## Verification

- [ ] [Test/check]
```

### The Chunking Principle

> "Show the spec in chunks short enough to actually read and digest."

- Each phase understandable in isolation
- Each step completable in one sitting
- Long plans have explicit review points

### Right Granularity

❌ Too granular: "Step 1.1.1: Open file"
❌ Too vague: "Step 1: Implement the feature"
✓ Right level: "Step 1.1: Add auth middleware — Create `auth.middleware.ts`, implement JWT verification, export route protection wrapper"

### Plan Evolution

Plans are living documents:
- Update when reality diverges
- Mark completed steps
- Note deviations and reasons

### Output

Save to `plans/[feature]/plan.md` or `src/features/[name]/PLAN.md`

### Git Persistence

After writing or updating a plan:
```bash
git add plans/
git commit -m "Plan: [feature] — [status: Draft|Approved|In Progress]"
git push origin main
```

---

*If you can't write it, you can't build it.*
