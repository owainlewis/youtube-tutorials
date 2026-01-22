# Slash Commands for Coding Agents

Encode best practices into reusable commands for AI coding assistants.

## Overview

This tutorial demonstrates how to create slash commands that capture expert workflows. Instead of writing detailed prompts every time, you encode them once and invoke them with a simple `/command`.

**Commands included:**

| Command | Purpose |
|---------|---------|
| `/plan` | Generate technical specification from a feature description |
| `/task` | Decompose spec into atomic, executable tasks |
| `/review` | Senior engineer code review focused on simplicity |
| `/test` | Generate comprehensive tests with edge cases |
| `/security` | OWASP-focused security vulnerability audit |
| `/commit` | Generate conventional commit message from staged changes |
| `/debug` | Systematic debugging with hypothesis formation |

## Quick Start

### 1. Copy Commands to Your Project

```bash
cp -r .claude/commands/ /your-project/.claude/commands/
```

### 2. Use in Claude Code

```
/plan Add user authentication with email/password
/task Implement the auth spec
/review Check my changes
/test Write tests for the auth module
/commit
```

## Example Application

The `examples/todo-api/` directory contains a simple FastAPI todo application that demonstrates the full workflow.

### Running the Example

```bash
cd examples/todo-api

# Install dependencies
uv sync

# Run the API
uv run uvicorn main:app --reload

# Run tests
uv run pytest
```

### API Endpoints

- `GET /todos` - List all todos
- `POST /todos` - Create a todo
- `GET /todos/{id}` - Get a specific todo
- `PATCH /todos/{id}` - Update a todo
- `DELETE /todos/{id}` - Delete a todo

## Documentation

See [docs/commands.md](docs/commands.md) for detailed documentation including:

- Rationale for each command
- When to use each command
- Example workflows
- Customization guide

## Workflow Philosophy

These commands follow a deliberate development flow:

```
/plan → /task → implement → /review → /test → /security → /commit
```

Not every change needs every command. Use what makes sense:

- **Bug fix**: `/debug` → fix → `/test` → `/commit`
- **New feature**: `/plan` → `/task` → implement → `/review` → `/test` → `/commit`
- **Quick change**: implement → `/commit`

## Project Structure

```
.claude/
└── commands/
    ├── plan.md       # Generate specification
    ├── task.md       # Decompose into tasks
    ├── review.md     # Code review
    ├── test.md       # Generate tests
    ├── security.md   # Security audit
    ├── commit.md     # Commit message
    └── debug.md      # Systematic debugging
docs/
└── commands.md       # Full documentation
examples/
└── todo-api/         # Sample application
    ├── main.py
    ├── pyproject.toml
    └── tests/
```

## Requirements

- Claude Code CLI
- Python 3.12+ with uv (for the example)
