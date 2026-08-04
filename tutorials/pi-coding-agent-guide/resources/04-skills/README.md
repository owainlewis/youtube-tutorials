# Optional Pi Skill Example

A skill is a folder with a `SKILL.md` file. Its name and description help the
model decide when to load the full instructions.

This directory includes a [`code-review` skill](./code-review/SKILL.md). Try it
for one session without installing it globally:

```bash
pi --skill /path/to/youtube-tutorials/tutorials/pi-coding-agent-guide/resources/04-skills/code-review
```

Then invoke it inside Pi:

```text
/skill:code-review
```

Project skills can live under `.pi/skills/` or `.agents/skills/`. User skills
can live under `~/.pi/agent/skills/` or `~/.agents/skills/`.

Skills are Markdown, but they are still active instructions to an agent that can
run tools. Review third-party skills before use. See Pi's current
[skill documentation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md)
for discovery rules and frontmatter fields.
