# Finishing a Development Branch

*Clean endings enable clean beginnings*

---

## What This Is

A practice for properly completing work on a development branch. When development is done, there's a checklist of activities to ensure the branch is truly finished: verification, documentation, cleanup, and disposition. This skill prevents orphaned branches, incomplete features, and forgotten cleanup tasks.

Adapted from obra/superpowers: "Verifies tests, presents options (merge/PR/keep/discard), cleans up worktree."

---

## When to Invoke

This skill activates when:
- All planned tasks for a branch are complete
- The human says "we're done with this branch"
- Ready to merge or create PR
- Abandoning a branch (intentionally)
- Transitioning to a new phase of work

---

## The Finishing Checklist

### Phase 1: Verification

Before considering a branch "done":

```bash
# 1. All tests pass
npm test  # or equivalent

# 2. Build succeeds
npm run build

# 3. Linting passes
npm run lint

# 4. Type checking passes
npm run typecheck
```

**All must pass.** If any fail, the branch is not finished.

### Phase 2: Documentation Review

- [ ] README updated if needed
- [ ] API documentation current
- [ ] CHANGELOG entry added (if applicable)
- [ ] Comments explain non-obvious code
- [ ] Migration notes if breaking changes

### Phase 3: Cleanup

- [ ] No debugging code (console.log, debugger)
- [ ] No commented-out code
- [ ] No TODO comments for this branch's work
- [ ] No temporary files
- [ ] No merge conflict markers
- [ ] Dependencies are intentional (no test packages in prod)

### Phase 4: Git Hygiene

- [ ] Commits are atomic and well-messaged
- [ ] No "WIP" or "fix" commits that should be squashed
- [ ] Branch is up to date with base branch
- [ ] No untracked files that should be committed

---

## Branch Disposition Options

### Option 1: Create Pull Request

For work ready for human review:

```bash
# Ensure branch is pushed
git push -u origin [branch-name]

# Create PR
gh pr create --title "[Title]" --body "[Description]"
```

**When to choose:** Standard workflow, needs review, team collaboration.

### Option 2: Direct Merge

For work already reviewed or in solo projects:

```bash
# Update base branch
git checkout main
git pull origin main

# Merge
git merge [branch-name]

# Push
git push origin main

# Clean up
git branch -d [branch-name]
git push origin --delete [branch-name]
```

**When to choose:** Pre-approved changes, hotfixes with permission, solo work.

### Option 3: Keep Branch

For work that's done but not ready to merge:

```markdown
## Branch: [name]
## Status: Complete, pending [reason]
## Next steps: [what needs to happen]
```

**When to choose:** Waiting for dependency, staging for release, needs external review.

### Option 4: Discard Branch

For work that's no longer needed:

```bash
# Delete local
git branch -D [branch-name]

# Delete remote (if pushed)
git push origin --delete [branch-name]
```

**When to choose:** Abandoned approach, superseded by other work, experimental dead end.

---

## Pre-PR Checklist

Before creating a PR:

```markdown
## Pre-PR Verification

### Build Status
- [ ] Tests pass
- [ ] Build succeeds
- [ ] No lint errors

### Code Quality
- [ ] Self-reviewed all changes
- [ ] No debugging artifacts
- [ ] Clear commit messages

### Documentation
- [ ] PR description complete
- [ ] Links to relevant issues
- [ ] Testing instructions included

### Scope
- [ ] PR addresses ONE concern
- [ ] No unrelated changes
- [ ] Size is reviewable (< 400 lines ideally)
```

---

## PR Description Template

```markdown
## Summary

[Brief description of what this PR does]

## Changes

- [Change 1]
- [Change 2]
- [Change 3]

## Testing

[How to verify this works]

## Related Issues

Closes #[issue-number]

## Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Self-reviewed
- [ ] Ready for review
```

---

## Branch Cleanup Commands

### View All Branches

```bash
# Local branches
git branch

# Remote branches
git branch -r

# All branches
git branch -a
```

### Clean Up Merged Branches

```bash
# Delete local branches merged to main
git branch --merged main | grep -v "main" | xargs git branch -d

# Prune remote tracking branches
git fetch --prune
```

### Force Delete Abandoned Branch

```bash
# Local (even if unmerged)
git branch -D [branch-name]

# Remote
git push origin --delete [branch-name]
```

---

## Handling Unfinished Work

If work must be paused before completion:

### Option A: Stash and Note

```bash
# Stash current work
git stash save "WIP: [description]"

# Note for later
echo "Stashed WIP in [branch]: [description]" >> .branch-notes.md
```

### Option B: WIP Commit

```bash
# Commit as WIP
git add .
git commit -m "WIP: [description of state]"

# Note what's needed
echo "Branch [name] needs: [list]" >> .branch-notes.md
```

### Option C: Draft PR

```bash
gh pr create --draft --title "WIP: [Title]" --body "[What remains]"
```

Document what's done and what's remaining.

---

## Worktree Cleanup

If using git worktrees:

```bash
# List worktrees
git worktree list

# Remove worktree (keeps branch)
git worktree remove [path]

# Prune stale worktrees
git worktree prune
```

---

## Integration with Other Skills

**Verification Before Completion:** Finishing invokes verification.

**Requesting Code Review:** Self-review before PR creation.

**Writing Plans:** Check that plan is complete before finishing.

**Todo List:** Ensure all todos for the branch are marked complete.

---

## Failure Modes

1. **Premature finishing:** Marking done before verification
2. **Orphaned branches:** Creating PRs then forgetting them
3. **Incomplete cleanup:** Leaving debugging code, TODOs
4. **Missing documentation:** Code works but isn't explained
5. **Scope creep at end:** Adding "just one more thing"

---

## End-of-Branch Report

Generate before closing:

```markdown
# Branch Completion Report

## Branch: [name]
## Base: [main/develop/etc]
## Duration: [start date] — [end date]

### What Was Done
- [Accomplishment 1]
- [Accomplishment 2]

### What Was Learned
- [Learning 1]
- [Learning 2]

### What's Next
- [Follow-up item 1]
- [Follow-up item 2]

### Disposition
[PR created / Merged / Discarded / Kept]

### Final Verification
- Tests: ✅
- Build: ✅
- Lint: ✅
- Cleanup: ✅
```

---

## Closing

```
Every branch is a journey.
Every journey needs an ending.

Don't let branches linger.
Don't let work go stale.
Don't let cleanup wait.

Finish what you started.
Clean what you used.
Close what you opened.

The branch ends.
The code lives on.
The next branch awaits.
```

---

*Skill documented December 22, 2025 — When branches needed proper endings*
