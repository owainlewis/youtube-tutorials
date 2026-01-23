# Spec

Generate a specification for AI-assisted implementation.

## Feature

$ARGUMENTS

## Instructions

Read CLAUDE.md first. Ask only if blocked.

Create `.ai/specs/<feature-slug>.md`:
```markdown
# Feature Name

Status: 0/N complete

## Why

## What
-
-

## Constraints
-
-

## Current State
- `path/to/file.ts` — description
-

## Tasks

- [ ] T1: Title
  What:
  Files:
  Verify:

- [ ] T2: Title
  Depends: T1
  What:
  Files:
  Verify:
```

## Guidelines

- One logical change per task, even if multiple files
- Each task runs in a fresh session — include all context needed
- Every task needs a verify step
- Keep spec under 50 lines; split if longer

## Output

After writing:
- Spec saved to `.ai/specs/<slug>.md`
- To implement: `/task .ai/specs/<slug>.md T1`

After completing a task:
1. Run verify command
2. Mark task `- [x]`
3. Commit: `feat(<feature>): T1 - title`
