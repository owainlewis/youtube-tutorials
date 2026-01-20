# /plan

Read the design document at `workspace/designs/$ARGUMENTS.md` and break it into executable task files.

## Task File Requirements

Each task file must be **completely self-contained**. A fresh agent with no prior context should be able to execute it.

For each task, create a file at `workspace/tasks/$ARGUMENTS/task-{N}.md` with this structure:

```markdown
---
task: {N}
title: {Short descriptive title}
depends_on: [{list of task numbers this depends on}]
files: [{list of files to create or modify}]
---

## Context
{Everything the agent needs to understand this task. Include relevant details from the design doc. Don't reference external documents.}

## Requirements
{Specific requirements for this task}

## Technical Notes
{Implementation hints, patterns to follow, edge cases to handle}

## Acceptance Criteria
- [ ] {Specific, verifiable criterion}
- [ ] {Another criterion}
- [ ] Tests pass (if applicable)
```

## Guidelines

1. **Order by dependencies** — Task 1 should have no dependencies. Later tasks can depend on earlier ones.

2. **Right-size tasks** — Each task should be completable in one session. If it feels too big, split it.

3. **Include all context** — The task file is the only input. Include code patterns, file locations, relevant design decisions.

4. **Be specific** — "Create user model" not "Set up backend". List exact files to create/modify.

5. **Testable criteria** — Each acceptance criterion should be verifiable. "User model exists" not "Backend works".

## Output

Create the following structure:
```
workspace/tasks/$ARGUMENTS/
├── task-1.md
├── task-2.md
├── task-3.md
└── ...
```

Also create a summary showing the task order and dependencies.
