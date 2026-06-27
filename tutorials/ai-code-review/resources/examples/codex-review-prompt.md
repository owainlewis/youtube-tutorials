# Reference: OpenAI Codex Review Prompt

Source: https://github.com/openai/codex/blob/main/codex-rs/core/review_prompt.md

One of the best code review prompts available. Open source (MIT). Study it and adapt it for your own review commands.

## Key Principles

### What counts as a bug worth flagging

1. It meaningfully impacts accuracy, performance, security, or maintainability
2. It's discrete and actionable (not a general codebase issue)
3. Fixing it doesn't demand more rigor than the rest of the codebase has
4. It was introduced in this change (pre-existing bugs don't count)
5. **The author would likely fix it if they knew about it**
6. It doesn't rely on unstated assumptions
7. Speculation isn't enough. Identify provably affected code.
8. It's clearly not an intentional change

### How to write review comments

1. Clear about why it's a bug
2. Appropriate severity (don't overclaim)
3. Brief. One paragraph max. No code chunks over 3 lines.
4. Explicitly state the scenarios/inputs needed for the bug to arise
5. Matter-of-fact tone. No flattery, no "Great job!"
6. Author can grasp it immediately without close reading

### Priority levels

- **P0**: Drop everything. Blocking release/operations. Universal, no assumptions needed.
- **P1**: Urgent. Next cycle.
- **P2**: Normal. Fix eventually.
- **P3**: Low. Nice to have.

## Why This Is Useful

This prompt is vendor-agnostic. Adapt it into:
- A Claude Code slash command or SKILL.md
- A REVIEW.md section
- A Cursor rule
- A standalone prompt for any agent

The principles work everywhere. That's the advantage of writing your own review.
