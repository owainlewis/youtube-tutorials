# CLAUDE.md

## Project

- Runtime: Bun
- Build: `bun run build`

## Linear

- Fetch issues using the Linear MCP tool.
- Always read the parent issue (if one exists) for full context.
- If a description references a spec file (`Spec: specs/<feature>.md`), read it before implementing.
- Issue lifecycle: Backlog → Todo → In Progress → In Review → Done (Done happens after merge, not by you).

## Branching

Branch format: `<prefix>/<issue-id-lowercase>-<slug>`

Prefix by label:
- `feature/` — `feature` (or no label)
- `fix/` — `bug`
- `cleanup/` — `cleanup` or `tech-debt`
- `docs/` — `docs`

## Commits

- Format: `<summary> (<ISSUE-ID>)` — e.g. `Add auth middleware (PROJ-12)`
- Never amend. Never force push.
- Never commit code that doesn't build.

## Pull Requests

Create with `gh pr create`. Body must include: summary, verification (`bun run build` result), Linear issue link.

## Error Handling

If anything fails — build, push, PR creation — stop and report. No silent workarounds.
