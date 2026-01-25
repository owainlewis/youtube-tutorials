# Spec

Generate a specification for AI-assisted implementation.

## Feature

$ARGUMENTS

## Instructions

Read CLAUDE.md first. Ask only if blocked.

Create `.ai/specs/<feature-slug>.md`:
```markdown
# Feature Name

## Why

[1-2 sentences: What problem this solves. Why it matters now.]

## What

[Concrete deliverable. Specific enough to verify when done.]

## Constraints

### Must
- [Required patterns, libraries, conventions]

### Must Not
- [No new dependencies unless specified]
- [Don't modify unrelated code]

### Out of Scope
- [Adjacent features we're explicitly not building]

## Current State

[What exists now. Saves agent from exploring.]

- Relevant files: `path/to/file.ts`
- Existing patterns to follow

## Tasks

### T1: [Title]
**What:** [What to build]
**Files:** `path/to/file`, `path/to/test`
**Verify:** `command to run` or manual check

### T2: [Title]
**What:** ...
**Files:** ...
**Verify:** ...

## Validation

[End-to-end verification after all tasks complete]

- `command to verify entire feature works`
- `npm test` or equivalent
- Manual check: [what to verify in UI/API]
```

## Guidelines

- Each task runs in a fresh session — include all context needed
- Every task needs a verify step
- Constraints prevent over-engineering — be explicit about what NOT to do
- Current State saves the agent from exploring your codebase
- Keep the whole spec under 50 lines if possible

## Output

After writing:
- Spec saved to `.ai/specs/<slug>.md`
- To implement: start a fresh session and run `read .ai/specs/<slug>.md and implement T1`
- After each task: commit with `T1: [task name]`
