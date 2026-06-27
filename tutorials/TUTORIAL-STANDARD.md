# Tutorial Consistency Review

This repo has 26 top-level tutorial folders.

The strongest direction is to make every tutorial feel like one clear lesson with optional code samples.

Use the YouTube skill for the writing standard, but adapt the file shape for a public repo.

These are teaching documents.

Clarity matters more than completeness.

Diagrams, slides, tables, and code samples are there to make the idea easier to understand.

`video.md` is the internal recording doc pattern.

For this repo, use `lesson.md` as the public lesson and keep `README.md` as a short entry point.

## Recommended Folder Shape

```text
tutorials/<slug>/
  README.md
  lesson.md
  code/
  resources/
```

This is the standard shape:

- `lesson.md` is the one lesson.
- `README.md` explains what the lesson is and what is inside.
- `code/` is optional.
- `resources/` holds docs, files, images, prompts, references, configs, and slides.

Use `code/` only when there is runnable code or a real sample project.

Use `resources/` for prompts, skills, configs, diagrams, slides, and copyable reference files.

Put polished slide decks in `resources/slides/`.

Avoid extra Markdown files unless the tutorial is genuinely a course.

When extra Markdown is needed, link it from `lesson.md` and make its role obvious.

## README.md

The README should be short.

It should help someone decide what the tutorial is and where to start.

Suggested shape:

```md
# <Tutorial Title>

One plain paragraph describing the result.

## Start Here

- Read the lesson: [lesson.md](./lesson.md)
- Run the code: [code/](./code/)
- Copy the resources: [resources/](./resources/)

## Requirements

- <tool>
- <account or API key>
- <runtime>
```

Do not put the full lesson, filming notes, long reference material, and code walkthrough all in README.

## lesson.md

The lesson is the main document.

It should read like a clear technical newsletter Owain can also use as recording prep.

Suggested shape:

```md
# <Tutorial Title>

## Title Options

Optional for lessons that are still being packaged for YouTube.

## Opening Script

Use this only when the lesson doubles as a recording doc.

Write the opening as one complete block ending with:

So, let's get into it.

## Before We Build

Explain what the viewer will build, inspect, or understand.

## <Natural Teaching Section>

Explain the basic idea first.

Then add the nuance.

## <Natural Teaching Section>

Show the workflow, tradeoff, or demo step.

## Demo

Use this section only when the tutorial needs runnable code.

Include the command, expected result, and likely failure point.

## Summary

- The one thing to remember:
- The honest limitation:
- What to try next:
```

Do not expose planning-only headings like `One-Line Promise`, `Core Idea`, `Idea Spine`, `Point Of View`, `HOOK`, or `INTRO`.

If the lesson needs title options or an opening script, include them in normal reader-facing sections.

The agent-memory script is the model:

- title options
- one complete opening script
- `Before We Build`
- normal teaching sections such as `The two parts of memory`, `The Memory Map`, and `Models do not remember by default`
- demo steps folded into the lesson where useful
- a short summary and CTA

## Writing Rules

Write like Owain talks to a capable developer.

Use plain language.

Name the topic quickly.

Explain the basics first.

Add nuance only after the simple model is clear.

Show real commands, files, and tradeoffs.

Pick fights with weak ideas, not people.

Use diagrams when they make the model easier to remember.

Prefer simple Mermaid diagrams inside `lesson.md`.

Use image files only when Mermaid is not enough.

Use slides when the lesson needs visual polish on camera.

Slides should support the teaching.

They should not replace the lesson.

Avoid hype.

Avoid clever analogies.

Avoid em dashes.

Avoid thought-leader framing.

Avoid phrases like "supercharge", "unlock", "dive in", "game-changer", "the future is", and "it is not about X, it is about Y".

## Code Sample Rules

Runnable code should live under `code/` unless the tutorial is already a complete app folder.

Small copyable files can live under `resources/`.

Use one setup path per tutorial.

Include `.env.example` when secrets are required.

Include exact commands for install, run, test, and reset where relevant.

Keep generated files, virtualenvs, caches, and nested repos out of the tutorial folders.

Do not commit `.venv`, `__pycache__`, `.pytest_cache`, `.lsp`, `.clj-kondo`, or nested `.git` directories.

## Slide Rules

Slides are optional.

Use them when a diagram, flow, comparison, or key mental model needs more polish than Markdown can provide.

For most lessons, prefer this order:

1. Plain prose in `lesson.md`.

2. Mermaid diagrams inside `lesson.md`.

3. A polished HTML slide deck under `resources/slides/`.

Use the templates in `tutorials/templates/slides/` as the starting point.

The slide style is based on the Agentic Engineer course decks.

Keep slides clear and sparse:

- one idea per slide
- short headings
- large readable text
- SVG-style diagrams built from HTML and CSS when useful
- arrows, cards, rails, and pipelines for workflow ideas
- no dense paragraphs
- no decorative diagrams that do not teach

Every slide deck should have:

- a title slide
- the core model or problem
- one or more visual explanation slides
- a demo or workflow slide when relevant
- a final takeaway slide

If the slides are just a pretty version of the whole lesson, cut them down.

The lesson is the source of truth.

The slides are visual support.

## Current Repo Audit

No top-level tutorial currently has `video.md` or `lesson.md`.

All 26 top-level tutorials use `README.md` as the primary entry point.

Some README files are already close to a good lesson.

Good examples to model:

- `loop-engineering`
- `nested-subagents-claude-code`
- `multi-agent-teams`
- `background-agents`

These read like a clear technical explanation with a point of view.

The main issue is file shape, not quality.

The older folders often mix several jobs in one README:

- repo index
- lesson
- filming checklist
- command reference
- code walkthrough
- resource list

The folders most worth normalising first:

- `github-ai-workflow`, because the README is very long and mixes filming flow, tutorial, prompts, command reference, and links.
- `spec-driven-development`, because the README is useful but too much of the spec template and examples live inside the lesson.
- `codex-for-developers`, because it is closer to a course than one companion tutorial.
- `linear-workflow`, because it mixes lesson, setup, implementation flow, and config reference.
- `testing-ai-generated-code`, because it has a strong topic but several sections should move into `lesson.md` plus `resources/`.
- `pi-coding-agent-guide`, because it is already a course and should keep chapters, but needs a consistent top-level lesson and resource map.
- `6-types-of-rag`, `intent-based-classification`, `postgresql-only-database-ai`, and `nano-agent`, because they have real code and should use a clear `code/` or app-folder convention.

## Suggested Migration Plan

1. Add `lesson.md` to every top-level tutorial.

2. Move the main teaching material out of README and into `lesson.md`.

3. Reduce each README to title, short description, start links, and requirements.

4. Move copyable prompts, skills, configs, automation files, and polished slide decks to `resources/`.

5. Move runnable examples to `code/`, unless the whole folder is a runnable app.

6. Remove ignored runtime output from local tutorial folders.

7. Run an editorial pass for em dashes, hype phrases, and overlong README sections.

## Per-Tutorial Notes

| Tutorial | Current Shape | Recommended Change |
| --- | --- | --- |
| `6-types-of-rag` | Short README, separate walkthrough, architecture, slides, src, sql, data | Use `lesson.md` as the lesson, keep `src/`, `sql/`, and `data/` as code/data because this is already a runnable project. |
| `agent-teams` | One long README plus prompts | Move lesson to `lesson.md`, move prompts to `resources/`. |
| `ai-code-review` | Good compact README plus examples, hooks, slides | Move the lesson to `lesson.md`, keep hooks/examples as `resources/`. |
| `ai-git-workflow` | README is mostly resource guide | Add `lesson.md`, keep slash commands under `resources/commands` or existing `commands/` with clear README link. |
| `autonomous-ai-coding-workflow` | README plus resources | Move lesson to `lesson.md`, keep loop prompts in `resources/`. |
| `background-agents` | Strong single lesson in README | Best first conversion: rename teaching body into `lesson.md`, make README short. |
| `codex-automations` | README has no proper heading structure | Add `lesson.md` with opening, natural teaching sections, demo, and summary. |
| `codex-for-developers` | Large course-style README plus chapter resources | Treat as a course: top-level `lesson.md` as the full guide, chapter folders as resources. |
| `codex-skills-i-use` | Demo-script shaped README | Convert to lesson sections and move skill list into resources if it grows. |
| `deploy-ai-on-gcp` | Lesson plus deploy resources | Move the lesson to `lesson.md`, keep app examples and Terraform as code samples. |
| `github-ai-workflow` | Very long all-in-one README | Highest-value cleanup: split into `lesson.md`, `resources/prompts`, and `resources/commands`. |
| `how-id-learn-software-engineering` | Map/course index | Keep README as course index, add `lesson.md` for the main video lesson. |
| `intent-based-classification` | README plus docs and code | Fold chapter docs into `lesson.md` or keep `docs/` only if this remains a mini-course. |
| `linear-workflow` | Long tutorial/reference hybrid | Split lesson into `lesson.md`, keep `CLAUDE.md` and examples as resources. |
| `loop-engineering` | Strong lesson already | Move current body to `lesson.md`, keep README short. |
| `mcp-airtable` | Setup tutorial with resource example | Move lesson to `lesson.md`, move sample skill into `resources/`. |
| `micro-agents-demo` | Demo project with docs and context | Keep as app folder, add `lesson.md` that explains the pattern and links to docs. |
| `multi-agent-teams` | Strong lesson plus chapter READMEs | Keep course chapters, add top-level `lesson.md` as the main lesson. |
| `nano-agent` | Runnable project with architecture docs | Keep app layout, add `lesson.md`; move TODO/TASKS out of public lesson path if not needed. |
| `nested-subagents-claude-code` | Strong single lesson | Move current body to `lesson.md`, keep README short. |
| `pi-agent-workflow` | Short README plus long reference and code | Add `lesson.md`, keep long reference under `resources/` or `docs/`. |
| `pi-coding-agent-guide` | Full course with chapters | Keep chapters, add top-level `lesson.md` as the course spine. |
| `postgresql-only-database-ai` | Runnable project plus chapter docs | Keep project layout, add `lesson.md` as the main lesson and link chapters as optional deep dives. |
| `spec-driven-development` | Strong but very long all-in-one README | Split lesson, template, examples, and commands into separate linked resources. |
| `stop-vibe-coding` | Presentation-focused README | Add `lesson.md` as the lesson, keep `presentation.html` as an asset. |
| `testing-ai-generated-code` | Good teaching topic with examples and slides | Move lesson to `lesson.md`, examples to `code/` or `resources/examples`. |
