# Slash Commands for AI Coding Agents

5 slash commands that encode a real engineering workflow. Works on Claude Code, OpenCode, Cursor, and any agent that supports custom commands.

## The Commands

| Command | Purpose | Output |
|---------|---------|--------|
| `/design` | Create a technical design doc | `workspace/designs/{feature}.md` |
| `/plan` | Break design into task files | `workspace/tasks/{feature}/task-*.md` |
| `/task` | Execute one task file | Code changes |
| `/review` | Review recent changes | Feedback report |
| `/commit` | Commit with clean message | Git commit |

## Installation

**Claude Code:**
```bash
cp -r .claude/commands/ your-project/.claude/commands/
```

**OpenCode:**
```bash
cp -r .opencode/command/ your-project/.opencode/command/
```

## The Workflow

```
/design user-authentication
    → outputs: workspace/designs/user-authentication.md

/plan user-authentication
    → outputs: workspace/tasks/auth/task-1.md
               workspace/tasks/auth/task-2.md
               workspace/tasks/auth/task-3.md

[CLEAR CONTEXT or spawn sub-agent]

/task workspace/tasks/auth/task-1.md
/review
/commit

[REPEAT for remaining tasks]
```

## Why This Works

These commands map to the software development lifecycle:

- **Design** → Requirements & Architecture
- **Plan** → Work Breakdown
- **Task** → Implementation
- **Review** → Quality Assurance
- **Commit** → Version Control

The key insight: each task file is self-contained. Clear context between planning and execution. The agent executing `/task` only sees the task file—no planning conversation, no design debates.

## Example Project

The `examples/rag-chatbot/` folder contains a complete RAG chatbot built using this workflow:

- Design document in `workspace/designs/rag-chatbot.md`
- 7 task files in `workspace/tasks/rag-chatbot/`
- Full implementation with FastAPI, PostgreSQL/pgvector, and Tailwind UI

See [examples/rag-chatbot/README.md](examples/rag-chatbot/README.md) for details.

## Customization

These are starting points. Modify them for your team:

- Add your tech stack to `/design`
- Adjust task file format in `/plan`
- Add your commit message conventions to `/commit`
- Add `/test` and `/deploy` for your CI/CD

## Learn More

- [Video: 5 Slash Commands Top 1% Agentic Engineers Use](https://youtube.com/@owainlewis)
- [Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code)
- [OpenCode Docs](https://opencode.ai/docs)

## License

MIT - Use however you want.
