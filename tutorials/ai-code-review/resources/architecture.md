# Architecture: 4 Layers of AI Code Review

## The Problem

Code review was already the bottleneck. Most teams struggle to review 2-3 PRs per developer per day. AI coding agents generate 10x more PRs with the same number of reviewers.

The answer isn't to skip review. It's to layer checks so humans only focus on what requires human judgement.

## The Core Idea

Each layer filters out a category of problems so the next layer sees less noise. By the time a human reviews, the only things left are the things only a human can judge.

## The Pipeline

```
You write code with an AI agent (Claude Code, Cursor, Codex, etc.)
                    |
                    v
    ┌───────────────────────────────┐
    │  LAYER 1: AUTOMATE            │
    │                               │
    │  Linting, formatting, type    │
    │  checking, tests, security    │
    │  scans. Deterministic. Run    │
    │  via hooks on every edit.     │
    │                               │
    │  Principle: don't make people │
    │  review things automated      │
    │  tools could catch.           │
    └───────────────┬───────────────┘
                    |
                    v
    ┌───────────────────────────────┐
    │  LAYER 2: REVIEW LOCALLY      │
    │                               │
    │  1. Actually run the code     │
    │  2. Read the diff             │
    │  3. Get an AI review:         │
    │     - Custom command          │
    │     - Codex /review           │
    │     - CodeRabbit plugin       │
    │                               │
    │  Fresh context. Different     │
    │  model catches different      │
    │  things.                      │
    └───────────────┬───────────────┘
                    |
                git push
                    |
                    v
    ┌───────────────────────────────┐
    │  LAYER 3: REVIEW ON CI        │
    │                               │
    │  Automatic on every PR.       │
    │  Safety net for when you      │
    │  forget to run Layer 2.       │
    │                               │
    │  - Codex on GitHub            │
    │  - CodeRabbit CI              │
    │  - claude-code-security-review│
    └───────────────┬───────────────┘
                    |
                    v
    ┌───────────────────────────────┐
    │  LAYER 4: HUMAN REVIEW        │
    │                               │
    │  Architecture. Business       │
    │  logic. "Should we build      │
    │  this?" What AI cannot judge. │
    │                               │
    │  By now, everything           │
    │  mechanical is handled.       │
    └───────────────┬───────────────┘
                    |
                    v
                  MERGE
```

## How Hooks Work (Layer 1)

```
Claude writes code
       |
       v
Claude says "done"
       |
       v
Stop hook fires (lint + tests + security)
       |
       v
Pass?  --> Claude finishes normally
Fail?  --> Claude gets error output, must fix issues first
```

The same checks that run in CI now run locally before Claude can finish. This eliminates the feedback loop of push, CI fails, fix, push again.

## What Each Layer Catches

```
┌─────────┬──────────────────────────────────────┬──────────────────────┐
│ Layer   │ What it catches                      │ Cost / Effort        │
├─────────┼──────────────────────────────────────┼──────────────────────┤
│ 1       │ Lint errors, type errors, formatting,│ Free. Automatic.     │
│         │ failing tests, known security issues  │                      │
├─────────┼──────────────────────────────────────┼──────────────────────┤
│ 2       │ Broken features, scope creep, bugs,  │ Free. 5-10 minutes.  │
│         │ over-engineering, project-specific    │                      │
│         │ rule violations                       │                      │
├─────────┼──────────────────────────────────────┼──────────────────────┤
│ 3       │ Cross-file issues, architectural     │ Free/Paid. Automatic.│
│         │ bugs, things you forgot to check     │                      │
├─────────┼──────────────────────────────────────┼──────────────────────┤
│ 4       │ Business logic, architecture,        │ Time. Judgement.     │
│         │ "should we build this?"               │                      │
└─────────┴──────────────────────────────────────┴──────────────────────┘
```

## AI Review vs Human Review

```
AI Review                              Human Review
─────────────────────                  ─────────────────────
Superior at:                           Superior at:
pattern matching, speed,               judgement, context,
consistency                            strategy

Tasks:                                 Tasks:
- Security scans (OWASP, injection)    - Does this solve the business problem?
- Bug detection (logic, null, races)   - Is this the right architecture?
- Style guide adherence                - Does it meet acceptance criteria?
- Syntax, completeness                 - Business logic verification
- Scales to volume and large PRs       - Will this cause problems in 3 months?
- Never gets tired, never skips        - Should we even build this?
```

## The Key Insight

There is no perfect tool. AI catches things humans miss. Humans catch things AI misses. The value is in layering them.

Start with Layer 1. Add layers as you need them. Every issue you catch becomes a rule in your CLAUDE.md or REVIEW.md. The system gets better over time.
