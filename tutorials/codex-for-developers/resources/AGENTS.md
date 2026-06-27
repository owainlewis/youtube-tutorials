# Recruiter Intelligence

Recruiter Intelligence helps recruitment agencies find leads by identifying businesses actively hiring in their area.

See `docs/product-spec.md` for product direction, scope, phases, or workflow.

## Commands

See `justfile` for all available commands. Run `just` to list them.

## Workflow

Linear project `Recruiter Intelligence` is the source of truth for current work. Agents have Linear MCP access.

- Pick up tickets from Linear. Move to `In Progress` on start, `Done` when verified.
- Keep work scoped to the active ticket unless asked otherwise.
- Prefer high-level tickets over many tiny ones while product direction is evolving.
- Commit messages include the Linear ID when the work maps to a ticket (e.g. `GRA-141 Add minimal Postgres persistence`).
