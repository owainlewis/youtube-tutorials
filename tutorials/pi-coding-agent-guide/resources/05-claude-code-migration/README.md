# Optional Claude Code Migration Notes

Do not try to reproduce an existing tool feature for feature. Start Pi with its
defaults on a small repository, then add only the behaviour you miss.

## Concepts That Transfer

| Existing habit | Pi path |
| --- | --- |
| Repository instructions | `AGENTS.md` or `CLAUDE.md` |
| A reusable task method | A skill under `.pi/skills/` or `.agents/skills/` |
| A reusable prompt | A prompt template under `.pi/prompts/` |
| Tool hooks or custom behaviour | A TypeScript extension under `.pi/extensions/` |
| Session compaction | `/compact` |
| Model selection | `/model` |

The names look similar, but behaviour and security controls are not guaranteed
to match. Pi's built-in model tools include shell and file access. Extensions
can intercept calls, but a small extension is not a sandbox.

## Migration Check

1. Install and authenticate with the process in [`LESSON.md`](../../LESSON.md).
2. Start Pi in a clean working tree.
3. Confirm it loaded the intended project instructions.
4. Give it one small task.
5. Inspect the diff and run the repository's own checks.
6. Add a skill or extension only when the basic run exposes a repeated gap.

Compare current products from their current documentation. Counts of prompt
tokens, providers, models, integrations, or extension examples age too quickly
to make a reliable migration rule.
