# Script: Nested Subagents in Claude Code + Codex

## Working title

**Nested Subagents in Claude Code + Codex: Orchestrator-Worker Patterns**

## Title options

- **Nested Subagents in Claude Code + Codex**
- **Claude Code and Codex Can Spawn Agents Now**
- **The Orchestrator-Worker Pattern for AI Coding Agents**
- **Claude Code Nested Subagents vs Codex Subagents**

## Core angle

Anthropic just added nested subagents to Claude Code.

Codex already supports subagents, custom agents, and configurable nesting depth.

The interesting video is not just a Claude Code feature update.

It is a practical comparison:

> Both Claude Code and Codex are moving toward the same pattern: one orchestrator, bounded workers, specialist subagents, evidence summaries, and human approval.

## Script

Claude Code just got nested subagents.

That means agents can now kick off other agents.

And if you use Codex, this will sound familiar, because Codex already has subagent workflows, custom agents, and a setting called `max_depth` that controls how deep agent delegation can go.

So I think the interesting video is not just “Claude Code added a new feature”.

The interesting question is:

How should we actually use nested agents in real coding workflows?

Because the answer is not “spawn as many agents as possible”.

That is how you get expensive chaos.

The useful pattern is orchestrator-worker.

One agent owns the goal.

Workers handle bounded pieces of the work.

Specialist workers answer narrow questions.

Evidence moves back up the chain.

And the human still approves consequential changes.

That is the pattern I want to show you in this video.

We’ll look at Claude Code nested subagents.

We’ll compare that with how Codex supports subagents and custom agents.

Then I’ll show the workflow I’d actually use: orchestrator-worker code review and debugging.

The prompts and example config files are linked below.

Let’s get into it.

First, why do we need subagents at all?

AI coding agents are useful because they can call tools.

They can search the repo.

They can read files.

They can run tests.

They can inspect logs.

They can use MCP servers.

They can verify framework docs.

They can try a theory, discover it was wrong, and try another one.

That is useful.

But it creates noise.

If every file read, test failure, command output, browser trace, log line, and partial theory ends up in the main conversation, the main agent has to make important decisions inside a messy context window.

That is where subagents help.

A subagent can go away, do the noisy work, and return only the useful result.

The main session keeps the goal and the decision-making clean.

Nested subagents take that one step further.

Now a worker can protect its own context too.

If a worker is reviewing a branch and finds a narrow question, it can send that question to a specialist.

If a debugging worker finds a suspicious migration, it can spawn a specialist to inspect migrations.

If a reviewer sees a framework API it is not sure about, it can ask a docs researcher to verify the behavior through an MCP server.

The specialist returns evidence to the worker.

The worker returns a summary to the orchestrator.

The orchestrator gives the human one clear view of the risks.

That is the whole pattern.

Orchestrator.

Worker.

Specialist.

Evidence.

Review.

Approval.

Now, this is different from simple parallel agents.

A flat parallel workflow is where the main session asks three agents to do three tasks.

One security reviewer.

One test reviewer.

One maintainability reviewer.

They all report directly back to the main session.

That can be useful.

But it is not the most interesting version.

The nested version is different.

The main session asks a general review worker to review the branch.

That review worker inspects the diff and decides what specialist checks are needed.

If permissions changed, it asks for a security specialist.

If behavior changed, it asks for a test specialist.

If the patch relies on a framework API, it asks a docs researcher to verify the docs.

Those specialists report back to the review worker.

The review worker synthesizes everything.

The orchestrator gives me one prioritized review.

That is much closer to how I want to use AI coding agents.

The top-level agent is not spraying work everywhere.

It is delegating responsibility.

This is also where Claude Code and Codex become interesting to compare.

Claude Code now has nested subagents.

Codex has subagent workflows and custom agents.

In Codex, you can define project-specific agents under `.codex/agents`.

For example, you might define a `pr_explorer` agent that is read-only and only maps code paths.

You might define a `reviewer` agent that focuses on correctness, security, and tests.

You might define a `docs_researcher` agent that uses a docs MCP server to verify framework behavior.

Then your project config can set something like:

`agents.max_threads = 6`

and

`agents.max_depth = 1`

The important detail is that depth setting.

Codex treats the root session as depth zero.

A direct child agent is depth one.

The default depth of one gives you direct subagents but prevents deeper recursion.

You can raise it, but you should do that deliberately.

Because deeper recursion means more tokens, more latency, and more unpredictability.

That is exactly why the orchestrator-worker pattern matters.

You do not want broad delegation instructions that accidentally turn into repeated fan-out.

You want narrow roles.

You want clear permissions.

You want workers that return evidence.

And you want the orchestrator to decide what happens next.

So the first demo I would run is a branch review.

In Claude Code, the prompt might be:

Use nested subagents to review the current diff.

Start with one general code-review worker.

That worker should inspect the diff and decide which specialist reviews are needed.

If it finds security, correctness, test coverage, or maintainability concerns, it should spawn specialist workers for those concerns.

Specialists must not edit files.

They should return evidence-backed findings.

The general reviewer should synthesize the findings and report back to the orchestrator.

The orchestrator should tell me what to fix first.

That is a safe demo because it is read-only.

No files are edited.

No deployment happens.

No one touches auth, billing, permissions, or migrations.

The agents only investigate and report.

In Codex, I would show almost the same pattern, but with custom agents.

Review this branch against main.

Have `pr_explorer` map the affected code paths.

Have `reviewer` find real correctness, security, and test risks.

Have `docs_researcher` verify the framework APIs that the patch relies on.

Wait for all subagents to finish.

Then summarize critical issues, non-blocking risks, evidence from files or docs, and what should be fixed before merge.

That gives you a very clear comparison.

Claude Code shows the new nested-subagent capability.

Codex shows explicit custom agents and project-level agent config.

The pattern is the same.

One orchestrator.

Multiple bounded workers.

Specialists where needed.

Evidence comes back.

The human decides.

The second demo I would show is debugging.

Debugging is where this pattern makes a lot of sense.

A failing test or production bug usually has multiple possible causes.

It might be application code.

It might be a database change.

It might be a test fixture.

It might be a browser flow.

It might be a framework behavior you are misunderstanding.

A weak agent workflow lets one conversation wander through all of those theories.

A better workflow uses an orchestrator.

The orchestrator reads the failure and lists the most likely causes.

It assigns one worker per theory.

One worker maps the code path.

One worker reproduces the browser issue.

One worker checks docs or framework behavior.

If a worker finds a narrow question, it can call a specialist.

Then the orchestrator compares the evidence and reports the most likely root cause.

Only after that do we fix the code.

That order matters.

Understand first.

Then edit.

The third demo is supervised implementation.

This is where I would be more careful.

Read-only review and investigation are low risk.

Editing code is different.

So for implementation, I want the orchestrator to create a small plan first.

Then it can spawn one implementation worker for one bounded change.

After the implementation, that worker asks for nested review.

A correctness specialist checks behavior.

A test specialist checks coverage.

A security specialist checks sensitive changes.

If any reviewer finds a critical issue, stop and report back.

That is the version I trust.

Not agents editing forever.

Not agents recursively spawning other agents because it looks impressive.

A small implementation worker with nested review and human approval.

Now, the obvious risk with nested subagents is cost and unpredictability.

Every agent does model and tool work.

Every nested branch can create more work.

So you need constraints.

Use nested agents first for read-only tasks.

Ask every worker to return evidence.

Keep editing permissions narrow.

Make workers answer specific questions.

Do not let nested agents touch auth, billing, permissions, deployment, or migrations without approval.

Do not use vague prompts like “improve this codebase”.

Use prompts like:

Review this diff.

Investigate this failing test.

Map the affected code path.

Verify this framework API.

Compare these two implementations.

Find the blast radius of this change.

That is where nested agents become useful.

The short version is this.

Claude Code now has nested subagents.

Codex already has subagents, custom agents, and configurable depth.

The feature is interesting in both tools for the same reason.

It lets us build cleaner orchestrator-worker workflows.

The main agent owns the goal.

Workers handle bounded work.

Specialists answer narrow questions.

The main context stays cleaner.

And the human still approves the important decisions.

That is the pattern I would build around.

Not an AI company in your terminal.

A controlled engineering workflow.

Orchestrator.

Workers.

Specialists.

Evidence.

Review.

Approval.

That is why nested subagents matter.
