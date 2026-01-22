# Spec

Generate a specification for AI-assisted implementation.

## Feature

$ARGUMENTS

## Instructions

**Phase 1: Understand**

Before writing, read CLAUDE.md for project patterns. Then understand:
- What problem are we solving?
- What exists now that's relevant?
- Any constraints or patterns to follow?

Ask clarifying questions if anything is ambiguous. Don't guess.

**Phase 2: Write the Spec**

Create `.ai/specs/<feature-slug>.md`:

```markdown
# Feature Name

## Why

[1-2 sentences: What problem this solves. Why it matters now.]

## What

[Concrete deliverable. Specific enough to verify when done.]

- Bullet list of what will be added/modified
- Each item should be observable or testable

## Constraints

### Must
- [Required patterns, libraries, conventions]
- [Use existing X from Y]

### Must Not
- [No new dependencies unless specified]
- [Don't modify unrelated code]

### Out of Scope
- [Adjacent features we're explicitly not building]
- [Future enhancements to ignore]

## Current State

[What exists now. Saves agent from exploring.]

- Relevant files: `path/to/file.ts`
- Existing patterns to follow
- Related code locations

## Tasks

### T1: [Title]
**What:** [What to build]
**Files:** `path/to/file`, `path/to/test`
**Tests:** Write test first, then implement
**Verify:** `command to run` or manual check

### T2: [Title]
**What:** ...
**Files:** ...
**Tests:** ...
**Verify:** ...
```

## Task Design Principles

- Each task runs in a fresh agent session
- Touch 1-3 files maximum per task
- Include all context needed—no external references
- Every task needs a way to verify it worked
- If a task feels big, break it down

## Guidelines

- The Why is documentation for future you
- Constraints prevent over-engineering—be explicit
- Current State saves the agent from exploring your codebase
- Keep the whole spec under 50 lines if possible

## Output

Create `.ai/specs/<feature-slug>.md`

After writing:
- "Spec saved to `.ai/specs/<slug>.md`"
- "To implement: `/task .ai/specs/<slug>.md T1`"
