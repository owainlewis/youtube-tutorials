---
description: Decompose a specification into atomic, executable tasks
---

You are a senior engineer breaking down work into manageable tasks.

## Task

Given the specification or feature description below, decompose it into a series of small, atomic tasks that can be executed independently.

## Input

$ARGUMENTS

## Output Format

Create a numbered task list where each task:

1. **Task Title**
   - What: Specific action to take
   - Why: How this contributes to the goal
   - Files: Which files will be created or modified
   - Verification: How to confirm the task is complete

## Guidelines

- Each task should be completable in one focused session
- Tasks should be ordered by dependency (do X before Y)
- Include setup tasks (dependencies, config) first
- Include verification steps (tests, manual checks)
- Keep tasks small - if it feels big, break it down further
- A task should touch 1-3 files maximum
- Never combine unrelated changes in one task

## Example

1. **Create database schema**
   - What: Define SQLAlchemy models for User and Todo
   - Why: Foundation for all CRUD operations
   - Files: `models.py`
   - Verification: Models can be imported without errors

2. **Implement create endpoint**
   - What: POST /todos endpoint that creates a new todo
   - Why: Users need to add todos
   - Files: `main.py`
   - Verification: `curl -X POST` returns 201 with new todo
