# How I'd Learn Software Engineering (When AI Writes the Code)

This is a practical map of the skills I would build if I were learning software engineering now. AI can generate code, but you still need enough engineering judgment to decide what to build, review the result, and run it safely.

This repo includes detailed guides for four parts of the map and three worked system design questions. The other four parts are explained here as areas to practise. They do not have separate companion guides.

## The Map

There are eight areas of competence. The first six are durable software engineering skills. The last two cover how to practise with AI tools in the loop.

```text
How I'd Learn Software Engineering
│
├── 1. Core Fundamentals
│   How code works. One language deeply. Reading code fluently.
│
├── 2. System Design
│   How to put systems together and reason about tradeoffs.
│
├── 3. Product Thinking
│   Requirements, users, and deciding what to build before coding.
│
├── 4. The Development Process
│   Spec, plan, build, review, refactor, debug, and commit.
│
├── 5. Operations
│   Deployment, Linux, monitoring, and incident response.
│
├── 6. Communication
│   Writing clearly, explaining decisions, and working with other people.
│
├── 7. AI Tools And Workflows
│   Project context, clear specifications, and code review workflows.
│
└── 8. Deliberate Practice
    Build real things, ship end to end, and sometimes work without AI.
```

## How To Use The Materials

Start with the area that matches your current weakness. You do not need to complete the material in order.

1. Use the [core fundamentals checklist](./resources/core-fundamentals/) to build code-reading fluency in Python.
2. Work through the [three system design questions](./resources/system-design/) and explain each tradeoff in your own words.
3. Use the [development process guide](./resources/development-process/) to take one small feature from spec to commit.
4. Compare your project setup with the [AI tools and workflows guide](./resources/ai-tools/).
5. Use the [roadmap mind map](./resources/slides/mindmap.html) as a visual summary.

The checked-in inventory is:

```text
resources/
├── ai-tools/                 guide and example CLAUDE.md
├── core-fundamentals/        Python learning checklist
├── development-process/      software development workflow
├── system-design/            guide and 3 worked questions
└── slides/mindmap.html       visual roadmap
```

## What I Would Spend Less Time On

- **Leetcode grinding.** Use it when an interview requires it, not as your whole learning plan.
- **Memorizing framework APIs.** Learn the concepts and look up syntax when you need it.
- **Deep theory before practice.** Learn enough theory to explain the system you are building, then return when a real problem needs more depth.
- **Tutorial-only learning.** Build and ship small projects as soon as you understand the basics.

These areas are not useless. The useful question is whether the next hour helps you build, explain, review, or operate real software.

## References

- External: [Blueprint Skills](https://github.com/owainlewis/blueprint)
- External: [CS50 from Harvard](https://www.edx.org/cs50)
- External: [Designing Data-Intensive Applications](https://dataintensive.net/)

## Summary

- The one thing to remember: AI changes how you write code, but it does not remove the need for engineering judgment.
- The honest limitation: this repo contains four detailed guides and three worked system design questions, not a complete course for all eight areas.
- What to try next: pick one guide, complete one exercise, and write down what you learned without asking an AI tool to explain it for you.

## License

Licensed under the [MIT License](../../LICENSE).
