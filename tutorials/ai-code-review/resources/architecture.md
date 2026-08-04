# Architecture: Four Layers of AI Code Review

This is a compact visual reference for the workflow taught in [`../LESSON.md`](../LESSON.md). Read the lesson for the setup commands, tradeoffs, and failure modes.

## The Pipeline

```mermaid
flowchart TD
    A["Agent changes code"] --> B["Layer 1: deterministic checks"]
    B --> C["Layer 2: fresh local review"]
    C --> D["Layer 3: pull request checks"]
    D --> E["Layer 4: human judgement"]
    E --> F["Merge or revise"]
    B -->|"Fail"| A
    C -->|"Finding"| A
    D -->|"Fail or finding"| A
    E -->|"Concern"| A
```

## What Each Layer Does

| Layer | Main question | Examples |
| --- | --- | --- |
| Deterministic checks | Does the change satisfy rules a machine can prove? | Formatting, linting, types, tests, static security checks |
| Fresh local review | What looks wrong in the diff before push? | Correctness, regressions, scope, missing tests, project rules |
| Pull request checks | Does the branch pass in a clean environment? | CI, required checks, optional automated review |
| Human judgement | Is this the right change to ship? | Intent, product behaviour, architecture, risk, operations |

## Feedback Loop

```mermaid
flowchart LR
    A["Run checks"] --> B{"Pass?"}
    B -->|"No"| C["Use the output to revise"]
    C --> A
    B -->|"Yes"| D["Continue to the next review layer"]
```

Each layer has a boundary. Tests cannot decide product intent. A model review cannot prove that a command passed. Human approval should not replace repeatable checks.

Start with deterministic checks and one fresh local review. Add services only when they solve a specific gap in that workflow.
