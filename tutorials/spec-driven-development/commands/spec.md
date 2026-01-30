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

[1-2 sentences: Problem solved. Why now.]

## What

[Concrete deliverable. How you'll know it's done.]

## Context

**Relevant files:**
- `path/to/file.ts` — [what it does]
- `path/to/other.ts` — [why it matters]

**Patterns to follow:**
- [Existing convention to match, with example file]

**Key decisions already made:**
- [Tech choices, libraries, approaches locked in]

## Constraints

**Must:**
- [Required patterns/conventions]

**Must not:**
- [No new dependencies unless specified]
- [Don't modify unrelated code]
- [Don't refactor existing code]

**Out of scope:**
- [Adjacent features explicitly not included]

## Tasks

Break into tasks that:
- Can each be completed in one session
- Have a clear verify step
- Are safe to commit independently

### T1: [Noun phrase — what gets built]

**Do:** [Specific changes]

**Files:** `path/to/file`, `path/to/test`

**Verify:** `command` or "Manual: [check]"

### T2: [Title]
...

## Done

[End-to-end verification after all tasks]

- [ ] `build/test command passes`
- [ ] Manual: [what to verify in UI/API]
- [ ] No regressions in [related area]
```

## Guidelines

**Sizing tasks:**
- Group changes that must ship together (schema + types + migration = 1 task)
- Split at natural commit boundaries
- If a task might hit context limits, it's too big

**Writing good verify steps:**
- Prefer commands over manual checks
- Manual checks should be specific: "Click X, see Y" not "verify it works"
- Include the unhappy path when relevant

**Context section tips:**
- List only files the agent will actually touch or need to reference
- "Patterns to follow" with a concrete example file beats abstract description
- Capture decisions so the agent doesn't re-litigate them

**When to skip sections:**
- Trivial features (< 3 files): inline everything, skip Context
- Bug fixes: Why + What + single Task may suffice
- Spikes/exploration: just Why + What + time box

## Scaling

**Small (1-3 files):** Abbreviated spec, 1-2 tasks, ~20 lines
**Medium (4-10 files):** Full spec, 2-4 tasks, ~40 lines  
**Large (10+ files):** Consider splitting into multiple specs

## Output

After writing:
1. Spec saved to `.ai/specs/<slug>.md`
2. Review for completeness — could a new agent implement T1 with no other context?
3. To implement: fresh session → `read .ai/specs/<slug>.md and implement T1`
4. After each task: `git commit -m "T1: [task name]"`
```
