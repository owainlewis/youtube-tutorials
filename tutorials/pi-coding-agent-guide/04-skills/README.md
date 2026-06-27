# Skills

This is the supporting material for the video: Skills.

Skills are on-demand capability packages. Unlike extensions (which run code), skills are Markdown files that inject extra context into the conversation when the agent decides they're relevant.

## How Skills Work

1. Pi loads the skill name and description at startup (cheap, just frontmatter)
2. When the agent encounters a task that matches a skill's description, it loads the full content
3. The skill's instructions guide the agent's behavior for that specific task

This is "progressive disclosure." The agent only loads what it needs, keeping the context window clean.

## Skill Locations

```
~/.pi/agent/skills/       # Global skills
~/.agents/skills/          # Alternative global location
.pi/skills/                # Project-local skills
.agents/skills/            # Alternative project-local location
```

## Creating a Skill

A skill is a directory with a `SKILL.md` file:

```
my-skill/
└── SKILL.md
```

The `SKILL.md` has frontmatter (name + description) and instructions:

```markdown
---
name: my-skill
description: What this skill does (the agent reads this to decide if it's relevant)
---

Instructions for the agent when this skill is active...
```

## Example: Code Review Skill

See [code-review/SKILL.md](./code-review/SKILL.md) for a working example.

## Invoking Skills

- **Automatic:** The agent recognizes when a skill is relevant and loads it
- **Manual:** `/skill:name` to force-load a skill
- **CLI:** `pi --skill ./path/to/skill`

## Skills vs Extensions

| | Skills | Extensions |
|---|---|---|
| Format | Markdown | TypeScript |
| Loaded | On-demand (lazy) | At startup (eager) |
| Purpose | Extra context/instructions | Custom tools, events, UI |
| Runs code? | No | Yes |
| Security risk | Low (just text) | High (full system access) |

Use skills for prompting patterns you reuse. Use extensions for behavior you need to code.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
