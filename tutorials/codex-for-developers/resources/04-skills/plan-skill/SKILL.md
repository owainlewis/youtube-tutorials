---
name: plan
description: Write a short implementation plan or a longer execution plan before coding. Use when starting new work, when a ticket needs clearer boundaries, when a change spans multiple files or interfaces, or when a multi-hour task needs a living plan.
---

# Plan

## Purpose

Turn a ticket, feature request, or rough idea into a plan that is clear enough to implement against.

For smaller work, that means a short working plan.

For larger multi-hour work, that means a longer living execution plan in the style of `PLANS.md`.

## When to use

- Starting a new feature or meaningful change
- A Linear ticket is good, but still needs cleaner implementation intent
- Requirements, scope, or success criteria are unclear
- The change touches multiple files, interfaces, config, schema, or data flow
- The task is large enough that you want a document to guide several implementation passes

## Choose the right level of planning

### 1. Lightweight plan

Use this when:

- the ticket is already fairly descriptive
- the change is small or medium
- you mainly need clearer scope, steps, and verification

Output:

- a short Markdown plan
- usually 5-20 lines
- enough for one focused implementation session

### 2. Full execution plan

Use this when:

- the task may take multiple hours
- the work spans multiple milestones
- you need a living document during implementation
- another engineer or agent should be able to continue from the plan alone

Output:

- a self-contained plan in the style of `PLANS.md`
- prose-first, explicit, and updateable during implementation

## Process

1. Read the ticket, product context, `AGENTS.md`, and relevant code before planning.
2. Restate the goal in plain English.
3. Decide whether this needs a lightweight plan or a full execution plan.
4. If a material decision is missing, ask a concise question or state an explicit assumption.
5. Write the plan so someone could implement from it without relying on hidden context.

## What a lightweight plan should contain

- Goal
- Context
- Scope
- Non-goals
- Proposed steps
- Risks
- Verification

Example:

```md
# GRA-141 Plan

Goal: persist scraped jobs into Postgres while keeping CSV export.

Context:
- Current scraper exports CSV.
- We want minimal persistence without broadening scope into UI or API work.

Scope:
- Add DB configuration.
- Define a minimal jobs table.
- Persist jobs from the scraper flow.

Non-goals:
- No new UI.
- No API endpoints.
- No broad data model redesign.

Steps:
1. Add DB configuration and connection setup.
2. Define minimal `jobs` table.
3. Implement job upsert logic.
4. Wire scraper CLI to persist jobs.
5. Keep CSV export optional.
6. Add tests for upsert and rerun behavior.
7. Run review and cleanup.

Verification:
- Targeted tests pass.
- Existing CLI flow still works.
```

## What a full execution plan should contain

A full execution plan should be self-contained and readable by someone with only the working tree and the plan.

Required sections:

- Purpose
- Progress
- Surprises & Discoveries
- Decision Log
- Outcomes & Retrospective
- Context and Orientation
- Plan of Work
- Concrete Steps
- Validation and Acceptance
- Rollback or Safety Notes, if relevant

For larger tasks:

- write in plain English
- explain non-obvious terms immediately
- name files by path
- keep the plan updated as work progresses

## Rules

- Keep the plan as short as the task allows.
- Do not write a greenfield design if the codebase already has patterns to follow.
- Call out schema, config, CLI, API, or file-format changes explicitly.
- Make requirements specific enough that someone can review the implementation against them.
- If the request is tiny and obvious, skip the long plan and move straight to a lightweight plan or direct implementation.
- If the task is long-running, treat the plan as a living document and update it during execution.
- If the plan starts getting large because the task is actually several tasks, split the work.

## Resources

For this repo, use:

- `resources/plan-template.md` for a short working plan
- `resources/execplan-template.md` for a longer `PLANS.md`-style execution plan
