# How I Review AI-Generated Code

Companion repo for the video. Everything you need to set up a complete AI code review pipeline.

## The Problem

Code review was already the bottleneck. Developers take hours or days to review a single PR. Most teams struggle to review two or three a day.

AI makes this 10x worse. Same number of reviewers, 10x more PRs.

The answer isn't to skip review. It's to layer your checks so humans only focus on what requires human judgement.

## The 4 Layers

```
LAYER 1: AUTOMATE THE OBVIOUS
   Linting, formatting, tests, security scans.
   Run via hooks. Deterministic. No judgement.
   Principle: don't make people review things automated tools could catch.

LAYER 2: REVIEW LOCALLY (before push)
   Actually run the code. (Don't be lazy.)
   Read the diff. Check for silent side effects.
   Get an AI review in fresh context.
   Three options: custom command, Codex /review, CodeRabbit plugin.

LAYER 3: REVIEW ON CI (on the PR)
   Automatic AI review on every PR before a human sees it.
   Safety net for when you forget to run Layer 2.
   Codex on GitHub, CodeRabbit CI, claude-code-security-review.

LAYER 4: HUMAN REVIEW
   Architecture, business logic, "should we build this?"
   By now, everything mechanical is handled.
```

Each layer filters out a category of problems so the next layer sees less noise.

## Quick Start

### Layer 1: Automated Hooks

Copy the hooks config into your project:

```bash
# Copy the full hooks config (PostToolUse linting + Stop hook)
cp hooks/settings.json .claude/settings.local.json

# Copy the stop-checks script
mkdir -p .claude/hooks
cp hooks/stop-checks.sh .claude/hooks/stop-checks.sh
chmod +x .claude/hooks/stop-checks.sh
```

This gives you two hooks:

- **PostToolUse** runs ruff on every Python file edit (swap for your stack's linter)
- **Stop** runs linting + security scanning every time Claude tries to finish a task. If checks fail, Claude is blocked and must fix the issues.

See `hooks/stop-checks.sh` for the full script. Edit it for your stack.

You can also use the agent-based stop hook for AI-powered review. See `hooks/stop-hook.json` for that config.

### Layer 2: AI Review Locally

**Option A: Custom command with REVIEW.md (recommended)**

1. Copy the example REVIEW.md to your project root:

```bash
cp examples/REVIEW.md ./REVIEW.md
```

2. Edit it with your team's specific rules.

3. Run a review using Blueprint or your own command:

```bash
# Install Blueprint plugin
/plugin marketplace add owainlewis/blueprint
/plugin install blueprint@owainlewis-blueprint

# Review your changes
/blueprint:code-review
```

Or write your own review command. See `examples/codex-review-prompt.md` for an excellent reference prompt to adapt.

**Option B: Codex /review**

```bash
# Built into Codex CLI
codex /review
# Four presets: base branch, uncommitted, specific commit, custom
```

**Option C: CodeRabbit plugin**

```bash
# Install CodeRabbit CLI
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
coderabbit auth login

# Install the Claude Code plugin
/plugin install coderabbit

# Review your changes
/coderabbit:review
```

### Layer 3: CI Review

**Codex on GitHub:**
- Enable in your Codex web settings
- Every PR gets automatically reviewed
- Included with ChatGPT Plus subscription

**CodeRabbit on GitHub:**
- Install the GitHub App: https://github.com/apps/coderabbitai
- Free for open source

**Claude Code Security Review (GitHub Action):**
- https://github.com/anthropics/claude-code-security-review
- Security-focused review using Opus. Covers OWASP, injection, auth, secrets, XSS.

## Files in This Repo

```
ai-code-review/
├── README.md                           # This file
├── ARCHITECTURE.md                     # Visual diagram of all 4 layers
├── SLIDES.html                         # Branded slide deck for the video
├── hooks/
│   ├── settings.json                   # Full hooks config (PostToolUse + Stop)
│   ├── stop-checks.sh                  # Stop hook script (lint + security + debug checks)
│   └── stop-hook.json                  # Alternative: agent-based Stop hook for AI review
└── examples/
    ├── REVIEW.md                       # Example review rules for your project
    ├── codex-review-prompt.md          # OpenAI's review prompt (great reference)
    ├── agents-md-review.md             # Review section for agents.md (Codex)
    └── real-world-reviews.md           # Real examples + key takeaway
```

## Related

- [Blueprint plugin](https://github.com/owainlewis/blueprint) - Full SDLC workflow including /code-review with REVIEW.md support
- [CodeRabbit](https://coderabbit.ai) - AI code review (local CLI + GitHub App)
- [Codex](https://openai.com/codex) - OpenAI's coding agent with built-in /review
- [Codex review prompt source](https://github.com/openai/codex/blob/main/codex-rs/core/review_prompt.md) - One of the best review prompts available
- [claude-code-security-review](https://github.com/anthropics/claude-code-security-review) - Anthropic's security-focused GitHub Action
- [Greptile](https://greptile.com) - Codebase-aware code review
