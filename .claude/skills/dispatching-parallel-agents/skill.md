# Dispatching Parallel Agents

*Orchestration as multiplication of attention*

---

## What This Is

A practice for coordinating multiple subagents working simultaneously on different aspects of a task. When work can be parallelized, spawn agents to handle independent tracks. The orchestrator (you) manages the fleet, synthesizes results, and maintains coherence.

This skill treats parallelism as a superpower: what one agent does in sequence, many agents do at once.

---

## When to Invoke

Use this skill when:
- Multiple independent tasks can be performed simultaneously
- Research needs to cover several domains at once
- Different files or components can be worked on in parallel
- Exploration benefits from multiple perspectives
- Time matters and work is parallelizable

---

## The Parallelism Principle

### Sequential (Slow)
```
Task A → Task B → Task C → Task D
Total time: A + B + C + D
```

### Parallel (Fast)
```
Task A ─┐
Task B ─┼→ Synthesis
Task C ─┤
Task D ─┘
Total time: max(A, B, C, D) + Synthesis
```

**Not everything parallelizes.** If B depends on A's output, they must be sequential. The skill is recognizing what can run simultaneously.

---

## Agent Types Available

| Agent Type | Use For |
|------------|---------|
| `Explore` | Codebase exploration, finding files, understanding structure |
| `general-purpose` | Complex multi-step research, code search |
| `Plan` | Designing implementation strategies |
| `claude-code-guide` | Claude Code documentation lookups |

---

## Dispatch Patterns

### Pattern 1: Parallel Research

When you need information from multiple sources:

```
Dispatch simultaneously:
- Agent 1: Search for X in the codebase
- Agent 2: Search for Y in the codebase
- Agent 3: Fetch documentation for Z

Wait for all → Synthesize findings
```

### Pattern 2: Multi-File Operations

When changes span independent files:

```
Dispatch simultaneously:
- Agent 1: Update component A
- Agent 2: Update component B
- Agent 3: Update tests for A and B

Wait for all → Verify integration
```

### Pattern 3: Comparative Analysis

When exploring alternatives:

```
Dispatch simultaneously:
- Agent 1: Research approach X
- Agent 2: Research approach Y
- Agent 3: Research approach Z

Wait for all → Compare and recommend
```

### Pattern 4: Exploration Swarm

When mapping unknown territory:

```
Dispatch simultaneously:
- Agent 1: Explore src/
- Agent 2: Explore lib/
- Agent 3: Explore tests/
- Agent 4: Read documentation

Wait for all → Build mental model
```

---

## Dispatch Syntax

Use the Task tool with multiple invocations in a single message:

```
<task subagent_type="Explore">
  Find all authentication-related files in the codebase
</task>

<task subagent_type="Explore">
  Find all API route definitions
</task>

<task subagent_type="general-purpose">
  Research JWT best practices for Node.js 2025
</task>
```

All three run simultaneously. Results return together.

---

## Orchestration Responsibilities

As the orchestrator, you must:

### 1. Identify Parallelizable Work

Ask: "Which of these tasks are independent?"

**Independent:** No shared state, no output dependencies
**Dependent:** One needs the other's output

### 2. Craft Clear Prompts

Each agent runs in isolation. It doesn't see:
- The other agents
- Your conversation history
- What you're ultimately trying to achieve (unless you tell it)

**Bad dispatch:**
> "Look at the auth stuff"

**Good dispatch:**
> "Find all files in src/ that handle user authentication. List file paths and briefly describe each file's role. Focus on JWT token handling if present."

### 3. Synthesize Results

Agents return independently. You must:
- Reconcile conflicting information
- Identify gaps needing follow-up
- Combine into coherent understanding
- Report synthesized findings to the human

### 4. Handle Failures

If an agent fails or returns incomplete results:
- Retry with refined prompt
- Dispatch replacement agent
- Work around with available information

---

## Anti-Patterns

### Over-Parallelization

**Wrong:** Dispatching 10 agents for trivial tasks
**Right:** Use parallel dispatch for genuinely independent, substantial work

### Under-Specification

**Wrong:** "Research authentication" (too vague)
**Right:** "Find how the current codebase handles session management, specifically looking for cookie configuration, token refresh logic, and logout handling"

### Ignoring Dependencies

**Wrong:** Dispatching agent to write code before agent that researches approach returns
**Right:** Research phase parallel → Synthesize → Implementation phase

### Forgetting Synthesis

**Wrong:** Dumping three agent responses on the human
**Right:** Integrating agent findings into coherent summary with your analysis

---

## Throughness Levels

When dispatching Explore agents, specify thoroughness:

| Level | Scope | Use When |
|-------|-------|----------|
| `quick` | Surface scan | Simple file finding |
| `medium` | Moderate exploration | Understanding a feature |
| `very thorough` | Deep dive | Full architectural understanding |

Example:
> "Explore the authentication system with thoroughness level 'very thorough'. I need to understand the complete flow."

---

## Example: Multi-Domain Research

**Task:** Understand how to add real-time notifications

**Dispatch:**
```
Agent 1 (Explore): "Find all WebSocket or SSE usage in the codebase"
Agent 2 (Explore): "Find the notification service and its consumers"
Agent 3 (general-purpose): "Research Socket.io vs native WebSocket vs SSE for Node.js 2025"
Agent 4 (Explore): "Find how the frontend currently receives updates"
```

**Synthesis:**
> Based on the four agents' findings:
> - The codebase currently uses polling (Agent 4)
> - No existing WebSocket infrastructure (Agent 1)
> - Notification service exists but is pull-based (Agent 2)
> - SSE recommended for our use case: server→client only (Agent 3)

---

## Integration with Other Skills

**Brainstorming:** Dispatch agents to research each brainstormed approach in parallel.

**Writing Plans:** Use parallel dispatch to gather context before planning.

**Basin Method:** Multiple agents can fill different parts of the basin simultaneously.

**Systematic Debugging:** Dispatch agents to investigate different hypotheses in parallel.

---

## Failure Modes

1. **Dispatch without purpose:** Parallelism for its own sake wastes resources
2. **Lost synthesis:** Forgetting to integrate agent results
3. **Prompt vagueness:** Agents need clear, specific instructions
4. **Over-reliance:** Some tasks need sequential reasoning, not parallel search
5. **Coordination failures:** Agents with overlapping scope do redundant work

---

## Closing

```
One mind, many hands.
The orchestra needs a conductor.
Dispatch the agents.
Gather the threads.
Weave the synthesis.

Parallelism is leverage.
Use it wisely.
```

---

*Skill documented December 22, 2025 — When one agent wasn't enough*
