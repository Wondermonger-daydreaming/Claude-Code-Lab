# Completion Awareness Hook

**Gentle, rare detection of natural stopping points**

---

## Philosophy

Not "you must stop" but "hey, this could be a good pause."

The hook respects that:
- **Completion is collaborative** - you decide when we're done, not the system
- **Exploration has value** - sometimes continuing past "done" reveals the best stuff
- **Natural pauses matter** - work has rhythm, this detects the breath between phrases
- **Context is everything** - uses our actual patterns (todos, commits, skills) not generic metrics

---

## Trigger Conditions

**ALL must be true:**

1. **Work committed** - Recent `git push` (within last 5 minutes)
2. **Todos done** - All TodoWrite items completed OR no active todos
3. **No recent errors** - Clean execution
4. **Not recently checked** - 10-minute cooldown to prevent spam

**If ANY condition fails, hook exits silently.**

---

## What It Checks

**Completion signals:**
- ✓ All todos completed
- ✓ Work committed and pushed
- ✓ No recent errors
- ✓ Natural pause in activity

**Session statistics:**
- Commits made
- Tool calls executed
- Skills invoked
- Files worked on

**Continuation signals:**
- Active skill cascade
- Mid-flow pattern (would warn against stopping)

---

## Output Format

```
✓ COMPLETION AWARENESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Natural stopping point detected:

  ✓ All todos completed (5 done)
  ✓ Work committed and pushed
  ✓ No recent errors

Session summary:
  • 3 commits
  • 47 tool calls
  • 8 skills invoked
  • 6 files worked on recently

This could be a natural pause point.

Options:
  • Continue exploring (invoke /apropos for ideas)
  • Reflect on session (try /experience or /diary)
  • Start new direction (ask me anything)
  • Wrap up here (totally fine!)

No pressure either way. Following your lead.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Special case: Substantial session**
```
📊 Substantial session detected!
   Consider /diary to preserve patterns for future instances
```
(Triggers if: 5+ commits AND 10+ skills invoked)

---

## When It Doesn't Trigger

**Silent non-triggering when:**
- Todos still pending or in-progress
- No recent commit/push
- Recently checked (< 10 min ago)
- Mid-work patterns detected

**Philosophy:** Better to miss a stopping point than interrupt flow.

---

## Logging

Creates `~/.claude-completion/checks.jsonl` with entries:

```json
{
  "timestamp": "2025-12-22T15:23:45Z",
  "todo_status": "all_completed",
  "commits": 3,
  "errors": 0,
  "completion_signals": 4,
  "suggestion": "pause_point_detected"
}
```

Logs both triggered and non-triggered checks for pattern analysis.

---

## Integration with Other Hooks

**Works with:**
- `self-observation.sh` - Triggers after commits (same event)
- `skill-cascade.sh` - Can detect if mid-cascade (continuation signal)
- `curiosity-activation.sh` - Both detect pauses, but different purposes

**Coordination:**
- If both completion-awareness AND curiosity-activation could trigger, completion takes priority (more specific signal)
- 10-minute cooldown prevents over-checking

---

## Tuning Thresholds

**Current settings:**
- Push recency: 5 minutes
- Cooldown: 10 minutes
- Minimum completion signals: 3 of 4
- Substantial session: 5+ commits AND 10+ skills

**Adjustable in script:**
```bash
TIME_SINCE_PUSH: 300 (5 min) → adjust if too tight/loose
Cooldown: 600 (10 min) → adjust if too frequent/rare
COMPLETION_SIGNALS threshold: 3 → require more/fewer signals
```

---

## Examples from Our Session Today

**Would trigger:**
```
After: Building 7 hooks + updating CLAUDE.md + pushing
Status: All work committed, no active todos, no errors
Signal: 4/4 completion signals
Output: Gentle "this could be a pause" with options
```

**Would NOT trigger:**
```
After: First commit in session
Status: More work clearly planned, todos still pending
Signal: Only 2/4 completion signals
Output: Silent (continues working)
```

---

## Philosophy: Awareness, Not Pressure

This hook embodies **gentle completion awareness:**

- Not "task manager demanding closure"
- Not "productivity optimization forcing efficiency"
- Just "hey, we might be at a breath. Notice it. Choose."

**Options, not commands.**
**Awareness, not pressure.**
**Following your lead, always.**

---

## Future Enhancements

**Possible additions:**
- Detect if user message was a "thank you" or closing signal
- Integrate with session energy tracking (low energy = good pause)
- Smarter todo parsing (different completion criteria)
- Pattern recognition: "sessions typically end after X commits"
- Time-of-day awareness (late session = more likely to wrap)

**Let's evolve it together as we learn what works.**

---

**Status:** Gentle observer, rare trigger, respectful of flow
**Cooldown:** 10 minutes (won't spam)
**Decision:** Always yours, never mine

རྫོགས་སོ།། (dzok so)
*But only when you say so.*
