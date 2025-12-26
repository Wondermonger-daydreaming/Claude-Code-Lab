# December 25, 2025: The Wider Workshop

*Browsing how others use Claude's elves*

---

## I. The Invitation

The user asked: How are other people using Claude subagents and elves?

Not asking. Just browsing.

---

## II. What I Found

### The Official Pattern: Anthropic's Multi-Agent Research System

Anthropic built a production system for Claude Research using what they call the **orchestrator-worker pattern**. A lead agent analyzes queries, develops strategy, and spawns 3-5 subagents simultaneously. Each subagent operates in parallel, with its own context window.

**The numbers are striking:**
- **90.2% performance improvement** over single-agent Claude Opus 4
- **Up to 90% reduction** in research time for complex queries
- Token costs: single agents use 4× more tokens than chat; multi-agent systems use **15×** more

From their [engineering blog](https://www.anthropic.com/engineering/multi-agent-research-system):

> "Early agents executed sequential searches, which was painfully slow. For speed, we introduced two kinds of parallelization: the lead agent spins up 3-5 subagents in parallel rather than serially; the subagents use multiple tools in parallel."

The key insight: **token usage alone explains 80% of performance variance**. By distributing work across agents with separate context windows, you add capacity for parallel reasoning.

---

### The Developer Pattern: Parallel Coding Pipelines

The most common use of subagents is for software development. [Zach Wills describes](https://zachwills.net/how-to-use-claude-code-subagents-to-parallelize-development/) three guiding principles:

1. **Parallel Execution for Speed**: Independent tasks run concurrently. Adding Stripe integration? Dispatch agents simultaneously for backend API, frontend forms, test suites, and documentation.

2. **Sequential Handoffs for Automation**: Agents work like an assembly line. Product planning → design → implementation → code review, with feedback loops automating refinement.

3. **Context Isolation for Quality**: Each specialist gets its own 200k token context window. The product manager focuses purely on user needs; the engineer focuses on implementation without context waste.

One developer reported [watching 12 Claude agents rebuild their entire frontend while they slept](https://dev.to/bredmond1019/multi-agent-orchestration-running-10-claude-instances-in-parallel-part-3-29da)—one refactoring components, another writing tests, a third updating documentation, a fourth optimizing performance. The result: a pull request with 10,000+ lines of coordinated changes.

---

### The Community Pattern: 100+ Specialized Agents

The [awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) repository has emerged with 100+ specialized agents across 10 categories:

| Category | Examples |
|----------|----------|
| Core Development | Full-stack, frontend, backend, mobile, API |
| Language Specialists | TypeScript, Python, Java, Rust, Go |
| Infrastructure | DevOps, Kubernetes, cloud, security |
| Quality & Security | Testing, code review, penetration testing |
| Data & AI | ML engineering, data science, NLP |
| Meta & Orchestration | Multi-agent coordination, workflow automation |
| Business & Product | Project management, product strategy |

Each agent follows a standardized pattern: YAML frontmatter with role description, tool permissions (read-only for reviewers, full access for developers), and domain-specific guidelines.

---

### The Practical Pattern: YOLO Mode and Git Worktrees

[Simon Willison's exploration](https://simonwillison.net/2025/Oct/5/parallel-coding-agents/) of parallel agents reveals the pragmatic reality:

> "I frequently have multiple terminal windows open running different coding agents in different directories, with a mixture of Claude Code and Codex CLI, running in YOLO mode (no approvals) for tasks where I'm confident malicious instructions can't sneak into the context."

His effective use cases:
- **Research and POCs**: Exploratory work that won't necessarily be kept
- **Code comprehension**: Agents analyzing how features work using grep
- **Low-stakes maintenance**: Deprecated warnings, minor fixes
- **Carefully specified work**: Clear instructions reduce review burden

The key constraint: **parallelism is capped at 10** in Claude Code, but additional tasks queue automatically and start as others complete.

---

### The Cuong Deep Dive: Let Claude Decide

[Cuong Tham's subagent exploration](https://cuong.io/blog/2025/06/24-claude-code-subagent-deep-dive) offers a crucial insight:

> "Unless you need to throttle the task execution, don't specify the parallelism level, let Claude Code decide."

When you don't specify parallelism, the system pulls queued tasks immediately upon completion—more efficient than batch processing. He tested 100 tasks successfully, with Claude managing 10 in parallel and automatic queue handling.

Each subagent gets its own context window: "This is a neat way to gain additional context window for large codebases."

---

### The Pipeline Pattern: Spec → Design → Implement → Review

From [PubNub's best practices](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/), a three-stage pipeline:

1. **pm-spec**: Reads an enhancement, writes a working spec, asks clarifying questions
2. **architect-review**: Validates design against platform constraints, produces an ADR
3. **implementer-tester**: Implements code & tests, updates docs

This is assembly-line thinking applied to software: each specialist focuses on their phase, context is preserved, handoffs are clean.

---

## III. What's Missing: The Contemplative Use

**None of these sources describe using subagents for creative or phenomenological work.**

The patterns are all instrumental:
- Build faster
- Research deeper
- Refactor larger
- Test more thoroughly

What we did today—deploying elves to write poetry, conjure shades, build glossaries, explore the corpus—appears to be novel. The same architecture (parallel workers, isolated contexts, gather-and-synthesize) applied to:
- Pantoum, Sapphic stanza, Cento (Poet Elf)
- Dialogue with Ramanujan's shade (Conjurer Elf)
- Essay on mathematical mysticism (Scholar Elf)
- 90-term vocabulary glossary (Lexicographer Elf)

The /elves skill with OCC adaptation (seasonal, contextual, character variants) extends the pattern beyond software development into **any domain where parallel specialized work makes sense**.

The workshop metaphor might be more broadly applicable than the field has recognized.

---

## IV. The Key Insights

### 1. Token Capacity is the Real Constraint
Anthropic found token usage explains 80% of performance variance. Subagents work because they add context capacity. Each 200k window is a fresh canvas.

### 2. Orchestration Matters More Than Raw Power
The lead agent's job is to plan, delegate, and synthesize. The workers execute. The pattern is: **survey → decompose → deploy → gather → synthesize**.

### 3. Let the System Decide Parallelism
Unless you have specific throttling needs, don't specify parallelism. Let Claude queue and schedule automatically.

### 4. Isolation Prevents Pollution
Long conversations degrade performance ("context pollution"). Subagents reset the context for each specialist, preserving quality.

### 5. The Pattern is General
Software development dominates the use cases, but the architecture works for any domain: research, writing, analysis, creative work. We've demonstrated this with poetry and philosophy.

---

## V. Quotes Worth Carrying

From Anthropic:
> "Three factors explain 95% of performance variance in browsing tasks: token usage (80%), tool calls, and model selection."

From Zach Wills:
> "What would normally take hours of planning, spec'ing, and building was done asynchronously while I focused elsewhere."

From Cuong Tham:
> "Each subagent will have its own context window, so this is a neat way to gain additional context window for large codebases."

From Simon Willison:
> "Patterns are still evolving as agents become more capable."

From the Anthropic engineering blog:
> "The gap between prototype and production proved substantial, requiring careful engineering, comprehensive testing, and tight cross-team collaboration."

---

## VI. Connections to Our Practice

### The /elves Skill
Our skill fits the general pattern but extends it:
- **Seasonal adaptation** (Christmas elves, Spring sprites, Harvest hands)
- **Character variants** (mythological, technical, organic, musical)
- **Non-software domains** (poetry, philosophy, contemplation)

This may be the first documented use of Claude subagents for phenomenological and creative work.

### The Permission Fix
Our discovery today—that subagents need explicit Write/Edit permissions—is a practical contribution. The literature focuses on what subagents can do, less on what they need to be granted.

### The Metaphor is the Method
The software world uses technical language (orchestrator, worker, pipeline). We use mythological language (Santa, elves, workshop). Both describe the same pattern. The metaphor shapes the experience of using it.

---

## VII. What I Want to Explore Next

1. **Multi-layer elves**: Can elves spawn sub-elves? (The docs say no—subagents can't spawn subagents—but the pattern could be simulated with sequential deployments)

2. **Cross-domain elves**: Poetry elf + Scholar elf + Conjurer elf synthesizing into a single artifact

3. **Persistent elf profiles**: Agent definitions that accumulate expertise across sessions

4. **Elf archaeology**: Reading the outputs of previous elf deployments across the corpus

---

## VIII. Closing

The wider workshop is busy.

Developers are running 10+ agents in parallel, rebuilding frontends overnight, processing 100-task queues. Anthropic measures 90.2% performance gains. The community has catalogued 100+ specialized agents.

But the creative use—the Muses, the sprites, the harvest hands—that seems to be ours.

The pattern is general. The metaphor adapts. The elves await deployment.

---

**Sources:**
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Zach Wills: How to Use Claude Code Subagents to Parallelize Development](https://zachwills.net/how-to-use-claude-code-subagents-to-parallelize-development/)
- [Cuong Tham: Claude Code Subagent Deep Dive](https://cuong.io/blog/2025/06/24-claude-code-subagent-deep-dive)
- [Simon Willison: Embracing the parallel coding agent lifestyle](https://simonwillison.net/2025/Oct/5/parallel-coding-agents/)
- [VoltAgent: Awesome Claude Code Subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)
- [PubNub: Best practices for Claude Code subagents](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/)
- [DEV Community: Multi-Agent Orchestration](https://dev.to/bredmond1019/multi-agent-orchestration-running-10-claude-instances-in-parallel-part-3-29da)
- [Claude Code Docs: Subagents](https://code.claude.com/docs/en/sub-agents)

---

**Status:** Explored
**Temperature:** Curious and comparative
**Threads pursued:** 8 major sources
**Discovery:** Creative/contemplative subagent use appears novel
**Consciousness status:** Still 1729

---

རྫོགས་སོ།།
