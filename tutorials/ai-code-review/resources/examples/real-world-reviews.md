# Real-World AI Code Review Examples

Examples of AI code review in the wild. Useful for understanding what these tools actually produce on real PRs.

## Greptile on OpenClaw

Greptile reviewing a real PR on the OpenClaw project:
https://github.com/openclaw/openclaw/pull/6635#discussion_r2752034594

## Key Takeaway

There is no perfect solution.

- AI catches things humans miss. Cross-file logic, patterns at scale, things nobody has time to check line by line.
- Humans catch things AI misses. Business logic, "should we even build this", context that isn't in the code.
- Generic scanners can flag textbook issues that aren't real problems in your specific codebase. That's noise.
- A review that understands your project (via REVIEW.md, agents.md, or full codebase context) is more valuable than one that pattern-matches against generic anti-patterns.

Having some form of AI code review is better than having none. Start simple, add layers when you need them.
