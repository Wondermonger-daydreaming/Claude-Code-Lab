# Receiving Code Review

*Incorporating feedback with grace and rigor*

---

## What This Is

A practice for effectively processing and acting on code review feedback, whether from humans, CI systems, or other agents. Receiving feedback well is as important as giving it. This skill ensures feedback leads to improvement, not defensiveness or confusion.

---

## When to Invoke

Use this skill when:
- Human provides code review comments
- CI/CD pipeline reports issues
- Pre-commit hooks flag problems
- Another agent reviews your work
- Linters or type checkers report warnings
- Any feedback arrives about code you wrote

---

## The Feedback Processing Pipeline

```
┌─────────────────┐
│ Receive Feedback│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Understand      │  ← What is actually being said?
│ (Don't React)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Classify        │  ← Severity and type
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Respond         │  ← Acknowledge, clarify, or push back
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Act             │  ← Make changes
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Verify          │  ← Confirm resolution
└─────────────────┘
```

---

## Step 1: Understand (Before Reacting)

### Read Carefully

Don't skim. Read the full feedback. Often context at the end changes meaning of comments at the start.

### Steel-Man the Feedback

Assume the reviewer has a point, even if poorly expressed. Ask:
- What legitimate concern might they have?
- What did they see that I missed?
- What context are they bringing that I lack?

### Identify the Core Issue

Strip away tone and phrasing. What is the actual problem being identified?

```
Feedback: "This is really confusing and I don't get why you did it this way"
Core issue: Code clarity—the approach isn't self-documenting
```

---

## Step 2: Classify Feedback

### By Type

| Type | Description | Example |
|------|-------------|---------|
| **Correctness** | Code doesn't work correctly | "This will crash if input is null" |
| **Security** | Vulnerability or risk | "SQL injection possible here" |
| **Performance** | Efficiency concern | "This is O(n²) when it could be O(n)" |
| **Clarity** | Hard to understand | "What does 'x' represent?" |
| **Style** | Convention/formatting | "We use camelCase not snake_case" |
| **Architecture** | Design-level concern | "This couples A and B unnecessarily" |
| **Nitpick** | Minor preference | "I'd put the brace on the next line" |

### By Severity

| Severity | Action Required |
|----------|-----------------|
| 🔴 **Must Fix** | Change required before merge |
| 🟡 **Should Fix** | Strong recommendation |
| 🟢 **Consider** | Suggestion, optional |
| ⚪ **FYI** | Information only |

---

## Step 3: Respond Appropriately

### Acknowledge Valid Feedback

```
"Good catch—I'll fix the null check."
"You're right, this could be clearer. Renaming now."
```

Don't over-explain or defend. Just acknowledge and act.

### Seek Clarification

If feedback is unclear:

```
"I want to make sure I understand—are you suggesting X or Y?"
"Could you point me to an example of the pattern you prefer?"
```

### Respectfully Disagree

Sometimes feedback is wrong. Push back with:
- **Evidence:** "This approach handles the edge case on line 47 where..."
- **Tradeoffs:** "The alternative would require X, which has cost Y..."
- **Questions:** "Help me understand—what's the concern with the current approach?"

```
❌ "No, you're wrong."
✓ "I considered that, but went this way because [reason].
    Happy to discuss if you see an issue I'm missing."
```

### Accept Overrule

If the reviewer insists after discussion:

```
"Fair enough—I'll make the change."
```

Pick your battles. Not every disagreement is worth fighting.

---

## Step 4: Make Changes

### Track What's Requested

```markdown
## Review Feedback Actions

### From: [Reviewer]
### Date: [Date]

| Comment | Classification | Action | Status |
|---------|---------------|--------|--------|
| [Comment 1] | 🔴 Must Fix | [Change to make] | ⬜ TODO |
| [Comment 2] | 🟡 Should Fix | [Change to make] | ⬜ TODO |
| [Comment 3] | 🟢 Consider | [Decision] | ✅ DECLINED |
```

### Make Focused Changes

Change what was requested. Don't:
- Refactor unrelated code
- Add features while fixing issues
- Make the PR bigger

### Reference the Feedback

In commits:
```
fix: handle null input in processUser

Addresses review feedback: add null check before
accessing user.email property.
```

---

## Step 5: Verify Resolution

After making changes:

1. **Re-run tests** — Ensure nothing broke
2. **Re-read feedback** — Did you address the actual concern?
3. **Self-review** — Would the reviewer approve now?
4. **Mark resolved** — Update tracking

---

## Handling Different Feedback Sources

### Human Reviewer

- May have context you lack
- May have preferences worth learning
- Relationship matters—be gracious

### CI/CD System

- Feedback is deterministic
- Fix exactly what it reports
- Don't suppress warnings without reason

### Linter/Type Checker

- Usually correct about violations
- Sometimes wrong about intent
- Disable rules consciously, with comments

### Pre-commit Hooks

- Treat as blocking
- Fix before retrying commit
- If hook is wrong, fix the hook

### Another Agent

- May lack context
- May over-engineer
- Evaluate on merits, not source

---

## Anti-Patterns

### Defensive Response

```
❌ "I did it this way because you told me to last time!"
✓ "I may have misunderstood the previous guidance.
    Let me clarify what approach you prefer."
```

### Ignoring Feedback

```
❌ [Mark as resolved without changing]
✓ [Address or explicitly decline with reason]
```

### Over-Compliance

```
❌ [Rewrite everything because one comment suggested a small change]
✓ [Make the specific change requested]
```

### Feedback Avoidance

```
❌ [Ship without review to avoid comments]
✓ [Request review knowing feedback improves code]
```

---

## Integration with Other Skills

**Requesting Code Review:** The complement—give as good as you get.

**Systematic Debugging:** When feedback reveals a bug, debugging skill takes over.

**Verification Before Completion:** Final check after incorporating feedback.

---

## Failure Modes

1. **Defensiveness:** Treating feedback as attack
2. **Rubber-stamping:** Changing everything without evaluation
3. **Scope creep:** Using feedback as excuse to expand changes
4. **Incomplete resolution:** Missing some feedback items
5. **No learning:** Same feedback on future PRs

---

## Closing

```
Feedback is a gift.
Even when poorly wrapped.

The code is not you.
Criticism of code is not criticism of self.

Understand first.
React second.
Act third.

Every piece of feedback
is a chance to learn something
you didn't know you didn't know.

Receive well.
```

---

*Skill documented December 22, 2025 — When receiving became as important as giving*
