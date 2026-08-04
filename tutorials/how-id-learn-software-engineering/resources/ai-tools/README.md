# AI Tools & Workflows

This is the supporting material for the video: AI Tools & Workflows.

Most people use AI coding tools like a chatbot. Type a question, get an answer, copy paste. That's the lowest level.

Professionals configure their tools, structure their prompts as specs, and review output systematically.

## Pick One Tool Deeply

I recommend Claude Code. But Cursor, Codex, and others work too. The point is: pick one and learn it properly.

## Context Engineering

The biggest lever is giving your AI tool context about your project. In Claude Code, this is a `CLAUDE.md` file at the root of your project.

See [CLAUDE.md](./CLAUDE.md) for an example.

A good context file includes:
- What the project is and how it's structured
- Key conventions (naming, patterns, file organization)
- How to build, test, and run the project
- What NOT to do (common mistakes, things to avoid)

## Spec-Driven Prompting

Don't prompt AI with vague questions. Write specs.

**Bad:** "Build me an auth system"

**Good:** "Build an authentication system using JWT tokens. The system should support email/password login, token refresh, and logout. Store users in PostgreSQL. Use bcrypt for password hashing. Include rate limiting on the login endpoint. Write tests for the happy path and the following edge cases: expired tokens, invalid passwords, duplicate emails."

The more specific your prompt, the better the output. This is why product thinking and system design matter. You can't write a good spec if you don't understand what you're building.

## Code Review Workflow

Every time AI generates code:

1. Read every line before accepting
2. Check: does this do what I asked?
3. Check: are there edge cases it missed?
4. Check: is this the simplest way to do this?
5. Check: are there security issues?
6. Run the tests
7. Test it manually

This is the new core workflow. Author to editor.

## Example Project Configuration

```
my-project/
├── CLAUDE.md           # Project context for AI tools
├── .ai/
│   ├── specs/          # Feature specifications
│   └── tasks/          # Task breakdowns
├── src/
├── tests/
└── README.md
```

## Resources

- External: [Claude Code documentation](https://code.claude.com/docs/en/overview)
- External: [Blueprint Skills](https://github.com/owainlewis/blueprint)
- External: [OpenAI prompt engineering guide](https://developers.openai.com/api/docs/guides/prompt-engineering)

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
