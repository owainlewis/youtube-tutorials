# 05 - Configure Specialized Agents

This runbook copies one checked-in skill into a Multica workspace, binds it to an agent, and verifies one Git-branch output.

Multica keeps workspace skills separately from repository files. A `SKILL.md` in this tutorial is source material. It is not registered with Multica until you create or import a workspace skill. See the [external Multica skills guide](https://multica.ai/docs/skills).

## The Included Skills

```text
skills/
├── ai-news-research/
│   ├── SKILL.md
│   └── references/
│       └── sources.md
├── linkedin-post/
│   └── SKILL.md
└── youtube-description/
    └── SKILL.md
```

| Skill | Required input | Checked-in output contract |
|---|---|---|
| `ai-news-research` | The checked-in source list | `content/research/{YYYY-MM-DD}-ai-news.md` on `agent/news-{YYYY-MM-DD}` |
| `linkedin-post` | `content/youtube/{slug}/transcript.md`, or a transcript in the task | `content/linkedin/{slug}.md` on `agent/linkedin-{slug}` |
| `youtube-description` | `content/youtube/{slug}/transcript.md` with timestamps | `description.md` and `chapters.md` beside the transcript on `agent/description-{slug}` |

These are the only skills included with this tutorial.

## Create The Workspace Skill

Start with `ai-news-research` because its supporting source list is included.

1. Open the workspace **Skills** page.
2. Choose **New skill**.
3. Choose **Create manually**.
4. Copy [`skills/ai-news-research/SKILL.md`](./skills/ai-news-research/SKILL.md) into the main skill file.
5. Add [`references/sources.md`](./skills/ai-news-research/references/sources.md) as a supporting file at the same relative path.
6. Save the workspace skill.

You can also use Multica's **Import from URL** or **Copy from a runtime** options when the source is in a supported location. Copying from a runtime takes a snapshot, so later repository changes do not update the workspace skill automatically.

Read imported skills before binding them. Multica does not review or sandbox their instructions for you.

## Create And Bind The Agent

Follow the [external agent configuration guide](https://multica.ai/docs/agents-create):

1. Open the workspace **Agents** page and choose **New agent**.
2. Choose **Start blank**.
3. Give the agent a unique name such as `News Research Agent`.
4. Select the connected runtime that has an authenticated agent CLI.
5. Add short instructions that define the agent's responsibility, allowed output paths, and when to stop.
6. Attach the workspace skill from the agent's **Skills** tab.
7. Leave **Access** as **Only me** for the first run.

The required agent fields are name and runtime. Skills are bound in Multica after they exist in the workspace. There is no repository skill-path field.

## Verify One Run

1. Create a Multica issue with status `todo`.
2. Give it a concrete date and ask for the AI news digest defined by the skill.
3. Assign it to `News Research Agent`.
4. Confirm the issue moves to `in_progress` while the task runs.
5. Confirm it reaches `in_review` after delivery.
6. Inspect the expected `agent/news-{YYYY-MM-DD}` branch and `content/research/{YYYY-MM-DD}-ai-news.md` file.
7. Review the sources and content before marking the issue `done`.

The current Multica states are `backlog`, `todo`, `in_progress`, `in_review`, `done`, `blocked`, and `cancelled`. The [external issue guide](https://multica.ai/docs/issues) explains when assignment creates a task.

If the result needs work, add a concrete comment and @-mention the agent from the editor suggestions. The mention creates a follow-up task. Inspect the new commit before marking the issue `done`. See the [external Multica comments guide](https://multica.ai/docs/comments).

## Schedule Only After The Manual Run

Multica calls recurring jobs **Autopilots**. After the manual run passes, use the [external Autopilots guide](https://multica.ai/docs/autopilots) to create the schedule. Confirm the first scheduled result independently.

## Next

[06 - Connect Multica to your Git repo](../06-git-access/)

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
