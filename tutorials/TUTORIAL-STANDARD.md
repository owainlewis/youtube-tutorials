# Tutorial Consistency Review

This repo has 26 top-level tutorial folders.

The standard is one clear lesson with a predictable repo shape around it.

Use the YouTube skill for the writing standard, but adapt the file shape for a public repo.

These are teaching documents.

Clarity matters more than completeness.

The goal is one tutorial that can become a newsletter issue and a YouTube video.

It should feel like one thing.

Not a folder of notes.

Diagrams, slides, tables, and code samples are there to make the idea easier to understand.

`video.md` is the internal recording doc pattern.

For this repo, use `LESSON.md` as the public lesson and keep `README.md` as a short entry point.

## Core Principle

Every tutorial has one main teaching document.

That document is `LESSON.md`.

If a reader only opens `LESSON.md`, they should be able to understand the idea, follow the argument, and know what to try next.

Everything else is supporting material.

```text
LESSON.md  -> the teaching
code/      -> things to run
resources/ -> things to reference, copy, show, or reuse
```

Do not spread the lesson across several Markdown files.

Do not make the reader assemble the teaching sequence from multiple docs.

If an older tutorial has content split across chapter docs, fold the teaching into `LESSON.md` during the cleanup pass.

Keep the old files only when they are useful references.

## Required Folder Shape

Create new tutorials with:

```bash
just new-tutorial my-topic "My Tutorial Title"
```

This keeps new lessons consistent from the start.

```text
tutorials/<slug>/
  README.md
  LESSON.md
  code/
    .gitkeep
  resources/
    .gitkeep
    prompts.md
    slides/
      .gitkeep
```

This is the standard shape:

- `LESSON.md` is the one lesson.
- `README.md` explains what the lesson is and what is inside.
- `code/` holds runnable code, sample apps, fixtures, `.env.example`, and setup files.
- `resources/` holds reference material, files, images, prompts, checklists, configs, and loose assets.
- `resources/prompts.md` holds reusable prompts when the tutorial has them.
- `resources/slides/` holds polished slide decks and visual explainers.

Keep the folders even when they are empty.

Use `.gitkeep` for empty folders.

Use `code/` for anything someone runs.

Use `resources/` for anything someone reads, copies, opens, or reuses.

Be loose with `resources/`.

It is fine for resources to contain prompts, skills, configs, diagrams, slides, reference files, images, checklists, and docs that support the lesson.

Avoid extra Markdown files at the tutorial root.

When extra Markdown is needed, put it under `resources/` and make its role obvious.

Reference files should support the lesson.

They should not contain essential teaching that is missing from `LESSON.md`.

## Lesson Vs Reference

Use this rule when cleaning older tutorials.

| Material | Where It Goes | Why |
| --- | --- | --- |
| Main explanation | `LESSON.md` | This is the source of truth. |
| Newsletter-style argument | `LESSON.md` | The lesson should repurpose cleanly. |
| YouTube opening or talk track | `LESSON.md` | The video should come from the same document. |
| Mental model diagrams | `LESSON.md` first | Keep the core idea in the lesson. |
| Polished slide deck | `resources/slides/` | Slides support the lesson. |
| Prompts | `resources/prompts.md` | Prompts are reusable reference material. |
| Checklists | `resources/checklist.md` | Checklists support action after the lesson. |
| Images | `resources/images/` | Images support the lesson or slides. |
| External links | `resources/references.md` | Links are reference material. |
| Runnable examples | `code/` | Code is there to prove or practice the lesson. |

If a reference file becomes required reading, fold its explanation back into `LESSON.md`.

## README.md

The README should be short.

It should help someone decide what the tutorial is and where to start.

Suggested shape:

```md
# <Tutorial Title>

This is the supporting material for the video: <Tutorial Title>.

## Start Here

- Read the lesson: [LESSON.md](./LESSON.md)
- Browse code samples: [code/](./code/)
- Browse resources: [resources/](./resources/)
- Browse slides: [resources/slides/](./resources/slides/)

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
```

Do not put the full lesson, filming notes, long reference material, and code walkthrough all in README.

## LESSON.md

The lesson is the main document.

It should read like a clear technical newsletter Owain can also use as recording prep.

It should be complete enough to stand alone.

Resources can deepen the lesson, but they should not be required to understand it.

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

## References

Optional.

Link to prompts, checklists, slides, images, and external docs when they help.

Keep this short.

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

The lesson should not send the reader away for the next part of the explanation.

Links are for references, not for the main teaching path.

## Writing Rules

Write like Owain talks to a capable developer.

Use plain language.

Name the topic quickly.

Explain the basics first.

Add nuance only after the simple model is clear.

Show real commands, files, and tradeoffs.

Pick fights with weak ideas, not people.

Use diagrams when they make the model easier to remember.

Prefer simple Mermaid diagrams inside `LESSON.md`.

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

Runnable code should live under `code/`.

If an older tutorial is already a complete app folder, migrate it carefully rather than breaking paths in one mechanical move.

Small copyable files can live under `resources/`.

Use one setup path per tutorial.

Put `.env.example`, `.env-sample`, or similar templates beside the code that uses them.

Never commit real `.env` files.

Include exact commands for install, run, test, and reset where relevant.

Keep generated files, virtualenvs, caches, and nested repos out of the tutorial folders.

Do not commit `.venv`, `__pycache__`, `.pytest_cache`, `.lsp`, `.clj-kondo`, or nested `.git` directories.

## Slide Rules

Slides are optional.

Use them when a diagram, flow, comparison, or key mental model needs more polish than Markdown can provide.

For most lessons, prefer this order:

1. Plain prose in `LESSON.md`.

2. Mermaid diagrams inside `LESSON.md`.

3. A polished HTML slide deck under `resources/slides/`.

Use the templates in `tutorials/_templates/resources/slides/` as the starting point.

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

## Current Cleanup Direction

The structural standard is now:

- every tutorial has `README.md`
- every tutorial has `LESSON.md`
- every tutorial has `code/`
- every tutorial has `resources/`
- every tutorial has `resources/slides/`

The next pass is editorial.

Older lessons should be rewritten so they read like teaching documents, not repo dumps.

The main cleanup jobs are:

- remove filming-control labels from lessons
- move copyable prompts to `resources/prompts.md`
- move command references to `resources/`
- move checklists and reference docs to `resources/`
- move polished slide decks to `resources/slides/`
- move runnable examples to `code/` when it does not break the sample
- remove ignored runtime output from local tutorial folders
- add Mermaid diagrams where they clarify the lesson
- fold split teaching docs back into `LESSON.md`

Do not force every older runnable app into `code/` in one mechanical move.

Move code only when the imports, scripts, Docker files, README commands, and lesson commands can be updated together.
