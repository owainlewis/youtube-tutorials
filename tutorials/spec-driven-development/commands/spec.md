# Write Feature Spec

Create a plan and task list for AI-assisted implementation. Two files: `plan.md` (the thinking) and `tasks.md` (the checklist).

## Feature

$ARGUMENTS

## Instructions

**Phase 1: Clarify**

Before writing, understand:
- What problem are we solving?
- What's the scope?
- Any constraints or patterns to follow?

Read CLAUDE.md first for project patterns. Ask clarifying questions if needed.

**Phase 2: Write the Plan**

Create `.ai/features/{feature-slug}/plan.md`:

```markdown
# {Feature Name}

## Why

[1-2 sentences: What problem this solves. Why it matters.]

## What Changes

[Bullet list of what will be added/modified]
- Add X to Y
- Update Z to handle W
- Create new component for Q

## How

[Technical approach, constraints, patterns to follow]
- Use existing pattern from X
- No new dependencies
- Follow convention Y

## Files Affected

[Specific file paths and what changes]
- `path/to/file.ts` - what changes
- `path/to/new.ts` - new file
```

**Phase 3: Write the Tasks**

Create `.ai/features/{feature-slug}/tasks.md`:

```markdown
# Tasks: {Feature Name}

## Data Layer
- [ ] Task 1
- [ ] Task 2

## UI / API
- [ ] Task 3
- [ ] Task 4

## Integration
- [ ] Task 5

## Verification
- [ ] Task 6
- [ ] Task 7
```

Group tasks by layer: Data → UI/API → Integration → Verification.

## Guidelines

- plan.md should be 15-30 lines. If longer, split the feature.
- tasks.md checkboxes will be updated during execution.
- File paths must be specific — constrains AI to your architecture.
- The "Why" section is documentation for future you.
- Each task should be completable in one focused session.

## Output

Create folder `.ai/features/{feature-slug}/` with both files.

After writing:
- "Plan saved to `.ai/features/{slug}/plan.md`"
- "Tasks saved to `.ai/features/{slug}/tasks.md`"
- "To implement: `read .ai/features/{slug} and implement, updating checkboxes as you go`"
