Read the spec at `.ai/specs/content-repurposer.md` and build the full application using agent teams.

## Team Lead Responsibilities

The team lead (you) must plan the work before spawning agents:

1. **Read the spec** — Understand the full requirements, API contract, and tech stack.
2. **Create a task list** — Break the work into clear, scoped tasks with detailed descriptions. Each task should have enough context for an agent to work autonomously.
3. **Define the API contract upfront** — Backend and frontend must agree on endpoints, request/response shapes, and SSE event formats. Include this in both agents' task descriptions so they build to the same contract.
4. **Spawn agents and assign tasks** — Start backend and frontend in parallel. The reviewer waits until both are done.
5. **Coordinate fixes** — When the reviewer reports issues, create fix tasks and assign them to the owning agent. Verify fixes are applied before closing.

## Agents

Use agent teams to build this. Create three agents:

1. **backend** — Builds the Python/FastAPI backend
2. **frontend** — Builds the Next.js frontend
3. **reviewer** — Reviews code from both agents to ensure high quality, consistency, and that the API contract is respected

Backend and frontend agents should work in parallel. The reviewer should check their work as it's completed.

## Agent Ownership Rules

Each agent owns its code. The reviewer must NOT make direct fixes.

- **reviewer** — Identify issues and report them back to the team lead with: the bug description, the file/line, and the suggested fix. Do NOT edit code directly.
- **team lead** — Receives review findings, creates fix tasks, and assigns them to the owning agent (backend bugs → backend agent, frontend bugs → frontend agent).
- **backend / frontend** — Fix bugs assigned to them, then notify the team lead when done.
- **reviewer** — After fixes are applied, verify they are correct.

This keeps clear code ownership and prevents agents from stepping on each other's work.
