# Repository Instructions

This repo contains public teaching material for Owain's YouTube tutorials.

The quality bar is simple.

Each tutorial should feel like one clear lesson, not a folder of notes.

## Before Editing

Read `/Users/owainlewis/.codex/CONTEXT.md` before writing or rewriting Owain's content.

Use [tutorials/TUTORIAL-STANDARD.md](./tutorials/TUTORIAL-STANDARD.md) as the source of truth for tutorial structure and writing style.

Use the YouTube skill when creating or rewriting a lesson.

## Create A Tutorial

Use the scaffold command.

```bash
just new-tutorial my-topic "My Tutorial Title"
```

This creates:

```text
tutorials/my-topic/
  README.md
  LESSON.md
  code/
  resources/
  resources/prompts.md
  resources/slides/
```

Do not hand-create a new tutorial folder unless the Justfile is unavailable.

After scaffolding, edit `LESSON.md` first.

The lesson is the source of truth.

## Tutorial Standards

Every tutorial should have:

- `README.md` as the short entry point.
- `LESSON.md` as the one main teaching document.
- `code/` for runnable code and setup files.
- `resources/` for prompts, references, checklists, images, slides, and supporting files.
- `resources/prompts.md` for reusable prompts.
- `resources/slides/` for polished slide decks or visual explainers.

Keep the tutorial root clean.

Move extra Markdown files into `resources/` unless they are `README.md` or `LESSON.md`.

Tutorial-specific `AGENTS.md` and `CLAUDE.md` examples belong in `resources/`, not at the tutorial root.

If a reference file becomes required reading, fold the teaching back into `LESSON.md`.

## Writing Standards

Write like Owain talks to a capable developer.

Use plain language.

Explain basics first, nuance second.

Use concrete commands, files, examples, and tradeoffs.

Use diagrams when they make the idea easier to understand.

Prefer Mermaid diagrams in `LESSON.md`.

Use slides when the idea needs visual polish for recording.

Avoid hype, guru phrasing, clever analogies, and em dashes.

Do not invent stories, metrics, results, or claims.

## Coding Standards

Runnable code belongs in `code/`.

Small copyable examples that are not meant to run can live in `resources/`.

Include exact install, run, test, and reset commands when code is part of the lesson.

Keep one setup path per tutorial.

Use `.env.example` only for templates that are intentionally part of a code sample.

Never commit real `.env` files, tokens, local databases, virtualenvs, caches, generated output, or nested Git repos.

Do not commit `.venv`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `.lsp`, `.clj-kondo`, `.DS_Store`, `node_modules`, `dist`, `build`, or `uv.lock`.

Run relevant tests when code changes.

If there is no test suite, run the smallest command that proves the sample still works.

## Checks

Run this before committing structural or code changes:

```bash
just check
```

For tutorial-only prose changes, at least run:

```bash
git diff --check
```

## Git

Keep changes focused.

Do not edit lockfiles, generated files, vendored files, or unrelated tutorials unless required.

Do not add an agent co-author.
