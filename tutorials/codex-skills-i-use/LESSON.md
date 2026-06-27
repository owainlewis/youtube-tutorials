# 7 Codex Skills I Use As An AI Engineer

Companion notes for the YouTube tutorial. This version focuses on seven skills I use as a practical engineering workflow rather than a giant library of agent tricks.

> The thesis: skills are most useful when they encode repeatable ways of working. A small set of sharp skills can move an idea from vague feature request to spec, plan, issues, clear human-facing writing, implementation cleanup, review, and deeper design thinking.

## The Workflow

The demo uses **Dispatch**, a local task execution app, as the running example. The feature is making Dispatch task execution portable across multiple workers.

| # | Skill | Command | Demo Moment |
|---|---|---|---|
| 1 | Spec | `$spec` | Write a spec for portable Dispatch task execution. |
| 2 | Plan | `$plan` | Break the spec into concrete implementation tasks, then push them to GitHub Issues. |
| 3 | Explain Visually | `$explain-visually` | Explain the new worker/task model in a browser-friendly visual artifact. |
| 4 | Clarify | `$clarify` | Turn a vague ask into a clean, self-contained prompt. Grill out the unknowns one question at a time, then output the final prompt as the deliverable. |
| 5 | PR Feedback | `$address-pr-feedback` | Walk through an open PR, triage comments, fix valid issues, and prepare replies. |
| 6 | Refactor | `$refactor` | Clean up implementation code without changing behavior. |
| 7 | Design Doc | `$design-doc` | Discuss when a spec is not enough and the design needs tradeoff analysis. |

## Demo Script

### 1. Spec

Start by quickly showing the Dispatch app: tasks, workers, runs, and the current working-directory field. Then use the spec skill to shape the feature.

```text
$spec

Write a spec for making Dispatch task execution portable across multiple workers.

Right now tasks can include a working directory, but that is brittle because the control plane does not know which host/worker will run the task or what paths exist on that machine. We want workers to create a fresh isolated workspace for every run, and we want tasks to be scheduled to eligible workers using labels and optional host/worker pinning.

The design should make tasks portable by default. Checkout/setup should happen as explicit task steps inside the run workspace. Absolute local paths should not be part of normal task creation because they break when tasks move across hosts.

Focus on the data model, worker behavior, claim/routing rules, UI changes, migration from existing workDir behavior, and the smallest implementation path for the current local JSON-store prototype.
```

The useful thing to show is not that the agent writes a long document. It is that the skill forces alignment before implementation: requirements, data model, migration, UI behavior, and the smallest path through the current prototype.

### 2. Plan

Use the plan skill on the completed spec.

```text
$plan docs/portable-task-execution/spec.md
```

Show how the skill turns the spec into task-sized chunks with context, relevant files, acceptance criteria, and verification steps.

Then push those tasks to GitHub Issues. The important point is that each issue should be self-contained enough for a human or agent to pick up later without needing the original chat.

Example issue flow:

```text
Create GitHub issues from this plan. Keep each issue scoped to one task, include acceptance criteria and verification, and link back to the spec.
```

### 3. Explain Visually

Use this after the spec or plan exists, when you want the system to be easy to explain.

```text
$explain-visually docs/portable-task-execution/spec.md
```

For the Dispatch feature, the visual explanation should make the portability shift obvious:

- before: a task points at a local path that might only exist on one machine
- after: a worker claims an eligible task, creates a fresh workspace, and runs checkout/setup steps inside that workspace
- routing: labels and optional host/worker pins decide which workers may claim the task

### 4. Clarify

Use clarify when the ask is vague, voice-dictated, or a plan you want stress-tested before you start writing code. The skill turns your messy intent into a **clean, self-contained prompt** as its deliverable - not a side effect of execution, but the artifact itself. You can run it now, save it, or hand it to another agent.

Most failed agent work comes from acting on an unclear brief. The skill source is here: [clarify/SKILL.md](https://github.com/owainlewis/agent-skills/blob/main/skills/clarify/SKILL.md).

```text
$clarify

I want a script in this repo that takes any MP3 and runs it through the Auphonic API to enhance the audio. API key is in .env already.
```

What the skill does:

1. Reads the codebase first - never asks a question the project conventions already answer.
2. Interviews you one question at a time, recommending an answer with reasoning for each.
3. Walks down the decision tree - each answer reshapes the next question.
4. Outputs a `Final prompt:` block - self-contained, imperative, ready to run cold by any agent.
5. Asks what's next: execute now, save to a file, or stop (you'll use it elsewhere).

Good demo targets:

- A voice-dictated feature request with hidden decisions (file location, output naming, failure behavior).
- A pull from the plan in step 2 that's underspecified at the edges.
- "Grill me on this design before I start coding" - the stress-test mode.

The point to show is the contrast: ask the agent the same vague question with and without `$clarify`. Without it, the agent picks defaults and ships the wrong thing. With it, the agent surfaces every hidden decision upfront - one question, one recommended answer at a time - and the output is a portable prompt you can use anywhere, not a one-shot conversation.

Two rules that make the skill work:

- **Always recommend an answer.** A neutral menu of options dumps the work back on you. A recommendation with reasoning lets you accept and move on, or push back if the agent missed something.
- **The deliverable is the prompt, not the build.** Execution is optional. The clean prompt is the thing - that's what makes it reusable across agents and sessions.

### 5. PR Feedback

Show an open PR and use the PR feedback skill as a review triage loop.

```text
$address-pr-feedback <PR URL>
```

The point is judgment. Review comments are input, not commands. The skill should classify feedback, inspect the current code, implement valid fixes, verify them, and draft concise replies.

### 6. Refactor

Use refactor once behavior is working and tests give you a safety net.

```text
$refactor
```

For this Dispatch feature, good refactor targets might be worker eligibility checks, run workspace creation, or JSON-store migration helpers. The skill should preserve behavior while making the code easier to read and change.

### 7. Design Doc

Use a design doc when the problem has real ambiguity, tradeoffs, cross-cutting concerns, or a need for consensus before code.

The reference for this section is [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/). The key lesson for the tutorial: a design doc is not an implementation manual. It is where you record context, goals, non-goals, alternatives, tradeoffs, cross-cutting concerns, and why one design wins.

```text
$design-doc

Write a lightweight design doc for Dispatch portable task execution. Focus on the tradeoffs between host-pinned local execution, label-routed worker execution, and fully remote workspace provisioning.
```

## Skill List

| Skill | Use It When |
|---|---|
| Spec | You know the feature direction, but the agent needs a precise implementation brief before coding. |
| Plan | You have a spec and want executable tasks for GitHub Issues, Linear, or delegated agents. |
| Explain Visually | You need to teach a system, concept, PR, or architecture in a visual HTML artifact. |
| Clarify | The ask is vague, dictated, or multi-part, and you want a clean, portable prompt - not a one-shot conversation - as the output. |
| PR Feedback | You have an open PR with review comments and need to separate real fixes from noise. |
| Refactor | The behavior works, but the implementation needs to become simpler and easier to maintain. |
| Design Doc | The design is ambiguous enough that tradeoffs and consensus matter before implementation. |

## Notes

This tutorial no longer bundles local `resources/skills` files. It is a companion walkthrough for using the skills already installed in your Codex environment.

To see available skills in Codex:

```bash
codex
```

Then run:

```text
/skills
```

## Watch the video

(Link added after publication.)
