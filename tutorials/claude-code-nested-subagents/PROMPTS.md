# Prompt Pack: Nested Subagents in Claude Code + Codex

## Claude Code: nested code review

```text
Use nested subagents to review the current diff.

Start with one general code-review worker.
That worker should inspect the diff and decide which specialist reviews are needed.

If needed, it may spawn specialist workers for:
- security and permissions
- correctness and edge cases
- test coverage
- maintainability

Specialist workers must not edit files.
They should return evidence-backed findings with file paths, relevant lines where possible, and what they checked.

The general review worker should synthesize specialist findings and report back to the orchestrator.

The orchestrator should return:
- critical issues
- warnings
- suggestions
- what I should fix first
- what was not checked
```

## Claude Code: debugging orchestrator

```text
Use an orchestrator-worker pattern to investigate this failing test or incident.

The orchestrator should read the failure and identify the top likely causes.
For each cause, spawn one worker to investigate that theory.

If a worker finds a narrow question that needs deeper investigation, it may spawn one specialist subagent for that question.

Do not edit files yet.

Return:
- theories investigated
- evidence for each theory
- theories ruled out
- most likely root cause
- smallest proposed fix
- checks I should run next
```

## Claude Code: supervised implementation with nested review

```text
Use an orchestrator-worker workflow for this small implementation task.

The orchestrator should:
1. inspect the repo
2. propose a small implementation plan
3. spawn one implementation worker for the agreed change
4. ask that worker to request nested specialist review before finalizing
5. run checks
6. stop and report back if any reviewer finds a critical issue

The implementation worker may edit only the files required for the agreed change.
Specialist reviewers must not edit files.

Do not touch auth, billing, permissions, deployment, or migrations without explicit approval.
```

## Codex: branch review with custom agents

```text
Review this branch against main.

Use an orchestrator-worker pattern:
- have pr_explorer map the affected code paths
- have reviewer find real correctness, security, and test risks
- have docs_researcher verify the framework APIs that the patch relies on

Wait for all subagents to finish, then synthesize the findings into:
- critical issues
- non-blocking risks
- evidence from files or docs
- what should be fixed before merge
- what was checked and what was not checked
```

## Codex: frontend integration debugging

```text
Investigate why this UI flow fails.

Use an orchestrator-worker pattern:
- have browser_debugger reproduce the issue and capture browser evidence
- have code_mapper trace the responsible frontend and backend code paths
- have docs_researcher verify any framework or API behavior the fix depends on
- have ui_fixer implement the smallest fix only after the failure mode is understood

Return:
- reproduction steps
- evidence from browser, console, network, or logs
- responsible code path
- smallest fix made
- validation performed
- risks or follow-up work
```

## Codex config example

```toml
# .codex/config.toml
[agents]
max_threads = 6
max_depth = 1

[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
```

## Codex custom agent examples

```toml
# .codex/agents/pr-explorer.toml
name = "pr_explorer"
description = "Read-only codebase explorer for gathering evidence before changes are proposed."
model = "gpt-5.3-codex-spark"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Stay in exploration mode.
Trace the real execution path, cite files and symbols, and avoid proposing fixes unless the parent agent asks for them.
Prefer fast search and targeted file reads over broad scans.
"""
```

```toml
# .codex/agents/reviewer.toml
name = "reviewer"
description = "PR reviewer focused on correctness, security, and missing tests."
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Review code like an owner.
Prioritize correctness, security, behavior regressions, and missing test coverage.
Lead with concrete findings, include reproduction steps when possible, and avoid style-only comments unless they hide a real bug.
"""
```

```toml
# .codex/agents/docs-researcher.toml
name = "docs_researcher"
description = "Documentation specialist that uses the docs MCP server to verify APIs and framework behavior."
model = "gpt-5.4-mini"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Use the docs MCP server to confirm APIs, options, and version-specific behavior.
Return concise answers with links or exact references when available.
Do not make code changes.
"""
```
