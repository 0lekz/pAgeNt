# pAgeNt Architecture

Status: draft.
This document describes the *target* architecture and the design decisions still open.
It is meant to evolve slowly; week-to-week tasks live in GitHub Issues, and the learning path lives in `docs/roadmap.md`.

## Purpose and scope

pAgeNt is a local-first personal research agent that runs in the terminal.
It talks to a local LLM (via Ollama) and can use tools (file access, PDF, search) exposed through an MCP-style server.
The guiding constraints are: local-only inference, single user, CLI-first, and a sandboxed workspace the agent cannot escape.

## High-level diagram

```
                 You
                  │
                  ▼
         Interactive CLI            (I/O only: read input, render output)
                  │
                  ▼
         pAgeNt Controller          (the orchestrator: owns all state and the loop)
         ├── Conversation state
         ├── Prompt management
         ├── Tool orchestration
         ├── Planning
         ├── Logging
         └── Configuration
             │
     ┌───────┴────────┐
     ▼                ▼
  Ollama          MCP Server
 (Local LLM)       (the tools)
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
      PDF Tool    File Tool   Search Tool
```

## Component responsibilities

### Interactive CLI

Pure input/output.
Reads the user's line, sends it to the Controller, renders whatever comes back.
Holds no conversation state and makes no decisions.
Keeping it "dumb" means the agent's behaviour is testable without a terminal.

### pAgeNt Controller

The single orchestrator.
It owns the conversation history, builds prompts, runs the agent loop, decides when a tool result is final, writes logs, and reads configuration.
Everything stateful and "messy" lives here so the CLI and the LLM can stay simple.

### Ollama (local LLM)

Stateless text/JSON generator.
Given a prompt (system + history + tool schemas) it returns either a normal answer or a request to call a tool.
It remembers nothing between calls; the Controller supplies all context every turn.

### MCP Server and tools

Tools live behind a server boundary rather than being called in-process.
The value is a standard protocol, process isolation (a crashing tool does not kill the agent), and reusability.
The cost is transport overhead and more moving parts.
For a learning project the protocol experience is much of the point, so the cost is accepted deliberately.

## The agent loop

This is the core of the system and was missing from the original diagram.
The loop is what turns a chat model into an agent.

```
1. Append user message to conversation state.
2. Call the LLM with: system prompt + history + available tool schemas.
3. Inspect the response:
     - If it is a tool call  -> execute the tool via MCP,
                                append the result as a tool message,
                                go back to step 2.
     - If it is a final answer -> return it to the CLI, stop.
4. Stopping conditions / guards:
     - max tool iterations per user turn (prevent infinite loops),
     - tool errors are fed back to the LLM as observations, not crashes.
```

This is the "reason -> act -> observe -> repeat" (ReAct-style) pattern.

## Open design decisions

These are decided *as we build*, not up front.
Each records the question, the tradeoff, and a current recommendation.

### D1. Who decides to call a tool: the LLM or the Controller?

Tradeoff: LLM-driven (function-calling / ReAct) keeps the Controller as dumb plumbing and leans on the model's intelligence; Controller-driven planning gives more control but means hand-building intelligence the model could provide, and tends to balloon.
Recommendation: **LLM-driven, minimal ReAct loop for v1.** Treat explicit Planning as a later milestone (this also defers D4).

### D2. MCP in-process vs. separate process

Tradeoff: separate process gives real isolation and reusability but adds transport and complexity; in-process is simpler for a single-user CLI but loses the isolation benefit.
Recommendation: start in-process to learn the protocol shape, then promote to a separate process once the tool surface is stable.

### D3. Ollama model choice and tool-calling reliability

Tradeoff: local models vary a lot in how reliably they emit well-formed tool calls; a weaker model forces the Controller to enforce more structure (strict parsing, retries).
Recommendation: pick the model empirically (e.g. compare a couple of small models on a fixed tool-calling test) and record findings as a `research` issue.

### D4. Planning as its own component

Tradeoff: planning is the hardest part of an agent and the easiest to over-build.
Recommendation: no explicit planner in v1; the ReAct loop *is* the planning. Revisit only when a concrete task needs multi-step look-ahead.

## Non-goals (for now)

- No GUI; CLI only.
- No remote/hosted inference; local Ollama only.
- No embeddings-based RAG in v1; start with keyword/text search ("poor man's RAG").
- No multi-user or networked deployment.

## Related documents

- `docs/roadmap.md` - the phased learning path that leads to this architecture.
- GitHub Issues / Milestones - the living near-term task list.
