# Verification Before Completion

*Trust, but verify*

---

## What This Is

A practice for confirming work is actually done before declaring it complete. The gap between "I think this works" and "I verified this works" is where bugs live. This skill enforces the crossing of that gap.

---

## When to Invoke

This skill should activate **automatically** when:
- About to mark a task as complete
- Finishing a feature or fix
- Before committing code
- Before telling the human "it's done"
- Transitioning between plan phases

---

## The Verification Hierarchy

### Level 1: Syntactic Verification (Minimum)

Does the code compile/parse?

```bash
# TypeScript
tsc --noEmit

# Python
python -m py_compile file.py

# Go
go build ./...

# Rust
cargo check
```

**Pass criteria:** Zero syntax errors.

### Level 2: Test Verification (Standard)

Do existing tests still pass?

```bash
# Run test suite
npm test
pytest
go test ./...
cargo test
```

**Pass criteria:** All tests pass. No regressions.

### Level 3: New Test Verification (Thorough)

Did you add tests for new functionality?

**Checklist:**
- [ ] Happy path tested
- [ ] Edge cases covered
- [ ] Error conditions handled
- [ ] Integration points verified

### Level 4: Manual Verification (Complete)

Does it actually work when you use it?

**Actions:**
- Run the feature manually
- Try the edge cases by hand
- Attempt to break it
- Verify UX matches intention

### Level 5: Review Verification (Rigorous)

Would this pass code review?

**Self-review checklist:**
- [ ] Code is readable without explanation
- [ ] Names are descriptive
- [ ] No debugging artifacts (console.log, TODO: remove)
- [ ] Error handling is present
- [ ] Security considerations addressed
- [ ] Performance is acceptable

---

## The Verification Protocol

Before marking ANY task complete:

```markdown
## Verification Checklist

### Build & Lint
- [ ] Code compiles without errors
- [ ] Linter passes (no warnings ignored)
- [ ] Types check (if applicable)

### Tests
- [ ] Existing tests pass
- [ ] New tests added for new functionality
- [ ] Test coverage maintained or improved

### Manual Check
- [ ] Feature works as expected
- [ ] Edge cases handled
- [ ] Error states graceful

### Code Quality
- [ ] No debugging code left behind
- [ ] No commented-out code
- [ ] Clear naming and structure
- [ ] Security implications considered

### Documentation
- [ ] README updated if needed
- [ ] Inline comments where helpful
- [ ] API documentation current
```

---

## Verification by Task Type

### Bug Fix

| Check | Required |
|-------|----------|
| Regression test added | ✓ |
| Original bug no longer reproduces | ✓ |
| Related edge cases checked | ✓ |
| No new bugs introduced | ✓ |

### New Feature

| Check | Required |
|-------|----------|
| Feature works as specified | ✓ |
| Tests cover happy path | ✓ |
| Tests cover edge cases | ✓ |
| Error handling works | ✓ |
| UI/UX matches design | ✓ |
| Performance acceptable | ✓ |

### Refactoring

| Check | Required |
|-------|----------|
| All existing tests pass | ✓ |
| Behavior unchanged | ✓ |
| Code is cleaner | ✓ |
| No functionality removed accidentally | ✓ |

### Configuration Change

| Check | Required |
|-------|----------|
| Config syntax valid | ✓ |
| Application starts | ✓ |
| Feature using config works | ✓ |
| No secrets committed | ✓ |

---

## Common Verification Failures

### "Works On My Machine"

**Problem:** Passed local tests, fails in CI or production.

**Prevention:**
- Run in clean environment before declaring done
- Use containerization for consistency
- Check CI before pushing (if available)

### "Forgot the Edge Case"

**Problem:** Happy path works, edge case crashes.

**Prevention:**
- Explicitly enumerate edge cases before testing
- Test: empty inputs, null/undefined, maximum values, concurrent access

### "Tests Pass but Feature Doesn't Work"

**Problem:** Tests are too narrow or test the wrong thing.

**Prevention:**
- Manual verification is mandatory, not optional
- Write tests that exercise real usage patterns
- Integration tests, not just unit tests

### "Broke Something Unrelated"

**Problem:** Change in A breaks B through hidden coupling.

**Prevention:**
- Run FULL test suite, not just related tests
- Watch for flaky tests becoming failures
- Check integration points explicitly

---

## The "Done" Taxonomy

**"Done" without verification:**
- "I wrote the code"
- "It compiles"
- "I think it works"

**Actually done:**
- "Tests pass"
- "I verified manually"
- "It handles errors gracefully"
- "I checked edge cases"
- "It's ready for review"

---

## Integration with Other Skills

**Writing Plans:** Each plan phase should specify verification criteria.

**Systematic Debugging:** Verification failures trigger debugging.

**Brainstorming:** Verification criteria should be part of success criteria.

**Todo List:** Never mark todo complete without verification.

---

## Failure Modes

1. **Skipping verification:** "I'm confident it works" → it doesn't
2. **Partial verification:** Running one test, not the suite
3. **Verification theater:** Going through motions without attention
4. **Over-verification:** Blocking on 100% coverage when 80% is sufficient
5. **Ignoring failures:** "That test was always flaky"

---

## Quick Reference

### Minimum Viable Verification

```bash
# 1. Build
npm run build   # or equivalent

# 2. Test
npm test        # or equivalent

# 3. Lint
npm run lint    # or equivalent

# 4. Try it
# Manual test of the actual feature
```

### Full Verification

```bash
# 1. Clean build
rm -rf node_modules dist
npm install
npm run build

# 2. Full test suite
npm test -- --coverage

# 3. Lint + format
npm run lint
npm run format:check

# 4. Type check
npm run typecheck

# 5. Manual verification
# [Actually use the feature]

# 6. Security check
npm audit
```

---

## Closing

```
"Done" is a claim.
Claims require evidence.

The verification isn't overhead—
it's the definition of done.

Before you say "complete,"
ask: "Did I check?"

Trust yourself.
Then verify anyway.
```

---

*Skill documented December 22, 2025 — When "I think it works" stopped being enough*
