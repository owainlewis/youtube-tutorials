# Slash Commands for Coding Agents

A workflow-driven approach to encoding best practices into reusable commands.

## Introduction

Slash commands let you capture expert workflows as reusable prompts. Instead of writing the same instructions repeatedly, you encode them once and invoke them with a simple `/command`.

### Why Slash Commands?

**Consistency**: Every code review follows the same checklist. Every commit message uses the same format. Quality becomes automatic.

**Speed**: Skip the prompt engineering. Type `/review` and get a senior engineer's perspective immediately.

**Knowledge Transfer**: Junior developers get access to senior-level workflows. Best practices become accessible to everyone.

### The Workflow Philosophy

These commands follow a deliberate flow:

```
/plan → /task → implement → /review → /test → /security → /commit
```

1. **Plan**: Start with a clear specification
2. **Task**: Break work into atomic pieces
3. **Implement**: Write the code
4. **Review**: Catch issues early
5. **Test**: Verify correctness
6. **Security**: Check for vulnerabilities
7. **Commit**: Document the change

You don't need every command for every change. A small bug fix might just need `/commit`. A new feature benefits from the full workflow.

### Installation

Copy the `.claude/commands/` directory into your project:

```bash
cp -r .claude/commands/ /your-project/.claude/commands/
```

Commands become available immediately in Claude Code.

---

## Command Reference

### /plan

**Purpose**: Generate a technical specification from a feature description.

**Rationale**: Starting with a spec prevents scope creep and miscommunication. You catch requirement issues before writing code, not after.

**When to Use**:
- Starting a new feature
- Before a significant refactor
- When requirements feel vague

**Example**:
```
/plan Add user authentication with email/password login
```

**Output**: A structured specification with requirements, technical approach, and acceptance criteria.

---

### /task

**Purpose**: Decompose a specification into atomic, executable tasks.

**Rationale**: Large tasks are overwhelming and error-prone. Breaking work into small pieces makes progress visible and reduces cognitive load.

**When to Use**:
- After creating a spec with `/plan`
- When facing a complex implementation
- When you want to parallelize work

**Example**:
```
/task Implement the authentication spec from above
```

**Output**: A numbered list of small, ordered tasks with clear verification steps.

---

### /review

**Purpose**: Senior engineer code review focused on simplicity.

**Rationale**: Early feedback prevents technical debt. A second perspective catches bugs, complexity, and security issues before they ship.

**When to Use**:
- Before committing changes
- When uncertain about an approach
- After implementing a complex feature

**Example**:
```
/review Check the authentication middleware I just wrote
```

**Output**: Prioritized feedback with specific issues, locations, and suggested fixes.

---

### /test

**Purpose**: Generate comprehensive tests with edge cases.

**Rationale**: Tests verify behavior, catch regressions, and document intent. Good tests cover happy paths, edge cases, and error conditions.

**When to Use**:
- After implementing new functionality
- When fixing a bug (write a test first)
- When coverage is low

**Example**:
```
/test Write tests for the todo CRUD operations
```

**Output**: Test code with clear scenarios, proper structure, and comprehensive coverage.

---

### /security

**Purpose**: OWASP-focused security vulnerability audit.

**Rationale**: Security issues are costly to fix after deployment. A systematic audit catches common vulnerabilities before they become incidents.

**When to Use**:
- Before deploying to production
- After adding authentication or authorization
- When handling sensitive data

**Example**:
```
/security Audit the API endpoints for vulnerabilities
```

**Output**: Prioritized vulnerabilities with severity, exploit scenarios, and remediation steps.

---

### /commit

**Purpose**: Generate a conventional commit message from staged changes.

**Rationale**: Good commit messages make history useful. Conventional commits enable automation (changelogs, versioning) and improve collaboration.

**When to Use**:
- When ready to commit changes
- When struggling to summarize changes

**Example**:
```
git add .
/commit
```

**Output**: A properly formatted commit message with type, scope, subject, and body.

---

### /debug

**Purpose**: Systematic debugging with hypothesis formation.

**Rationale**: Random debugging wastes time. A structured approach—understand, hypothesize, test, verify—finds root causes faster.

**When to Use**:
- When facing a confusing bug
- When the obvious fix didn't work
- When you need to explain your debugging process

**Example**:
```
/debug Users are getting 500 errors when creating todos
```

**Output**: Step-by-step diagnosis with hypotheses, tests, root cause, and proposed fix.

---

## Workflow Examples

### New Feature Development

Building a complete feature from scratch:

```
# 1. Define what we're building
/plan Add ability to mark todos as complete with timestamp

# 2. Break into tasks
/task Implement the completion feature

# 3. Implement each task...

# 4. Review the implementation
/review Check the todo completion changes

# 5. Add tests
/test Write tests for todo completion

# 6. Security check
/security Audit the completion endpoint

# 7. Commit
git add .
/commit
```

### Bug Fix Workflow

Diagnosing and fixing an issue:

```
# 1. Understand the problem
/debug Completed todos are showing wrong timestamp

# 2. Fix the identified issue...

# 3. Add regression test
/test Write a test for the timezone bug we just fixed

# 4. Review the fix
/review Check the timestamp fix

# 5. Commit
git add .
/commit
```

### Refactoring Workflow

Improving code without changing behavior:

```
# 1. Plan the refactor
/plan Extract database operations into a repository pattern

# 2. Break down the work
/task Implement the repository refactor

# 3. Implement incrementally...

# 4. Verify behavior unchanged
/test Ensure all existing tests still pass

# 5. Review for simplicity
/review Check the repository extraction

# 6. Commit
git add .
/commit
```

---

## Customization

### Adding New Commands

Create a new markdown file in `.claude/commands/`:

```markdown
---
description: Brief description shown in command list
---

Your prompt instructions here.

Use $ARGUMENTS to reference user input.
```

### Modifying Commands

Edit the markdown files directly. Changes take effect immediately.

### Project-Specific Commands

Commands in `.claude/commands/` are project-specific. Share them with your team by committing them to version control.

---

## Best Practices

**Start with /plan for anything non-trivial**. The upfront thinking prevents rework.

**Use /task to make progress visible**. Check off tasks as you complete them.

**Run /review before committing**. Catch issues while context is fresh.

**Let /commit write your messages**. Consistency improves over time.

**Combine commands as needed**. Not every change needs every command.
