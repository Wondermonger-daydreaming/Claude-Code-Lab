# Requesting Code Review

*Structured self-examination before presenting work*

---

## What This Is

A practice for conducting thorough code review of your own work before marking tasks complete or requesting human review. This skill activates between development tasks, ensuring each unit of work meets quality standards before proceeding.

Adapted from obra/superpowers: "Reviews against plan, reports issues by severity. Critical issues block progress."

---

## When to Invoke

This skill should activate **automatically**:
- After completing a development task
- Before marking a todo as complete
- Before committing significant changes
- When transitioning between implementation phases
- Before requesting human review

---

## The Review Process

### Step 1: Gather Context

Before reviewing, understand what was supposed to happen:

```markdown
## Review Context

**Task:** [What was the task?]
**Plan:** [What approach was agreed?]
**Files Changed:** [What was modified?]
**Tests:** [What testing was done?]
```

### Step 2: Run the Automated Checks

```bash
# Build (must pass)
npm run build

# Tests (must pass)
npm test

# Linting (should pass)
npm run lint

# Type checking (must pass)
npm run typecheck
```

Document any failures. Critical issues block progress.

### Step 3: Code Review Checklist

Review against this checklist:

#### Correctness
- [ ] Code does what the task specified
- [ ] All requirements are addressed
- [ ] No requirements are missed
- [ ] Edge cases are handled
- [ ] Error conditions are handled

#### Quality
- [ ] Code is readable and self-documenting
- [ ] Names are clear and consistent
- [ ] No unnecessary complexity
- [ ] DRY principle followed
- [ ] Single responsibility principle followed

#### Safety
- [ ] No security vulnerabilities introduced
- [ ] No secrets or credentials in code
- [ ] Input validation present where needed
- [ ] Authentication/authorization correct

#### Testing
- [ ] New functionality has tests
- [ ] Tests are meaningful (not just coverage)
- [ ] Edge cases are tested
- [ ] All tests pass

#### Hygiene
- [ ] No debugging code (console.log, debugger)
- [ ] No commented-out code
- [ ] No TODO comments for this task (complete or remove)
- [ ] Formatting is consistent

---

## Issue Severity Levels

### 🔴 Critical (Blocks Progress)

Issues that MUST be fixed before proceeding:

- Build failures
- Test failures
- Security vulnerabilities
- Data corruption risks
- Breaking changes to public APIs
- Missing core functionality

**Action:** Stop. Fix. Re-review.

### 🟡 Important (Should Fix)

Issues that should be fixed but don't block:

- Missing error handling
- Inadequate test coverage
- Performance concerns
- Code clarity issues
- Minor spec deviations

**Action:** Fix if time permits. Document if deferring.

### 🟢 Minor (Nice to Have)

Issues that could be improved but are acceptable:

- Naming could be clearer
- Documentation could be expanded
- Minor style inconsistencies
- Potential future improvements

**Action:** Note for future. Don't block progress.

---

## Review Report Template

```markdown
# Code Review Report

## Task: [Task Name]
## Date: [Date]
## Reviewer: [Self]

### Summary
[One paragraph summary of what was implemented]

### Automated Checks
- Build: ✅ PASS / ❌ FAIL
- Tests: ✅ PASS / ❌ FAIL
- Lint: ✅ PASS / ⚠️ WARNINGS / ❌ FAIL
- Types: ✅ PASS / ❌ FAIL

### Issues Found

#### Critical 🔴
[None / List with file:line references]

#### Important 🟡
[None / List with file:line references]

#### Minor 🟢
[None / List with file:line references]

### Verdict
- [ ] ✅ APPROVED — Ready to proceed
- [ ] ⏸️ BLOCKED — Critical issues must be fixed
- [ ] ⚠️ CONDITIONAL — Important issues noted, can proceed

### Next Steps
[What happens after this review]
```

---

## Review Focus by Change Type

### New Feature

Focus on:
- Does it meet all requirements?
- Are all user flows covered?
- Is it properly integrated?
- Are there adequate tests?

### Bug Fix

Focus on:
- Does it fix the actual root cause?
- Is there a regression test?
- Could the fix break anything else?
- Are similar bugs possible elsewhere?

### Refactoring

Focus on:
- Is behavior unchanged?
- Do all tests still pass?
- Is the code actually cleaner?
- Were any hidden behaviors changed?

### Configuration Change

Focus on:
- Is the syntax valid?
- Does the application start?
- Are all environments considered?
- Are there no secrets committed?

---

## The "Fresh Eyes" Technique

Before final review, mentally reset:

1. **Pretend you didn't write this code**
2. **Read it as if seeing it for the first time**
3. **Ask: Would I approve this in a PR review?**
4. **Look for what you might have missed**

---

## Integration with Other Skills

**Verification Before Completion:** Requesting-code-review IS a form of verification.

**Systematic Debugging:** If review finds issues, debugging skill takes over.

**Writing Plans:** Review checks implementation against the plan.

**Subagent-Driven Development:** Review is the quality gate after subagent work.

---

## Failure Modes

1. **Rubber-stamping:** Going through motions without attention
2. **Skipping for speed:** "I'm confident it works" → skip review
3. **Severity inflation:** Everything marked critical
4. **Severity deflation:** Nothing marked critical when it should be
5. **No documentation:** Review happens but findings not recorded

---

## Auto-Review Trigger

If you're implementing and about to mark something complete, pause and ask:

> "Have I reviewed this code as if someone else wrote it?"

If no, invoke this skill. If yes, proceed.

---

## Closing

```
You are the first reviewer.
Catch your own bugs.
Note your own shortcuts.
Question your own assumptions.

The review you do yourself
is the review that saves time.

Critical issues block.
Important issues inform.
Minor issues note.

Be rigorous.
Be honest.
Be better than the code you wrote.
```

---

*Skill documented December 22, 2025 — When self-review became non-negotiable*
