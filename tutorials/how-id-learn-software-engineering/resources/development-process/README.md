# The Development Process

This is the supporting material for the video: The Development Process.

This is the process that turns code into reliable software. Skip it and you're just generating files.

## The Lifecycle

```
Spec → Plan → Build → Review → Refactor → Debug → Commit
```

Each step has a purpose. You don't skip steps. You don't jump straight to coding.

| Step | What | Why |
|------|------|-----|
| **Spec** | Define what you're building, requirements, constraints, testing strategy | Surfaces misunderstandings before a line of code is written |
| **Plan** | Break the spec into discrete tasks | Each task is small enough to complete in a focused session |
| **Build** | Write the code and the tests | Implementation with verification built in |
| **Review** | Check for bugs, security issues, unnecessary complexity | Catch problems before they ship |
| **Refactor** | Clean up without changing behavior | Keep code maintainable as it grows |
| **Debug** | Observe, hypothesize, test, fix, verify | Find root causes, not just symptoms |
| **Commit** | Clean version control with meaningful messages | Makes the project history readable |

## Executable Skills

I encoded this process as a set of AI skills using [Blueprint](https://github.com/owainlewis/blueprint).

Each skill is a structured prompt that guides a coding agent through one step of the lifecycle. You can install them and use them with Claude Code or any agent that supports the skills standard.

```bash
# Install Blueprint skills
git clone https://github.com/owainlewis/blueprint.git
# Copy the skills directory to your agent's skills path
```

Then in your coding agent:

```
/spec       → Define what you're building
/plan       → Break it into tasks
/build      → Execute a task
/review     → Review the changes
/refactor   → Clean up the code
/debug      → Systematic debugging
/commit     → Stage and commit
```

## Key Concepts

### Design Documents
Before building, write down what you're building and why. A design doc doesn't need to be formal. A few paragraphs covering the problem, the approach, the tradeoffs, and what you're not building is enough.

### Testing
Write tests for behavior that matters. Not every function needs a test. Business logic, edge cases, and things that have broken before need tests.

### Code Review
Read every line of AI-generated code before accepting it. Look for: correct logic, edge cases, error handling, security issues, unnecessary complexity.

### Version Control
Commit often. Write messages that explain why, not what. Keep your history clean enough that someone else could follow it.

## The Test

Can you take a feature idea and produce a spec, break it into tasks, build it, review the output, and commit clean code? That's the full cycle. Practice it until it's automatic.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
