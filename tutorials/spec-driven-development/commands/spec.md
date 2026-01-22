# Spec

Generate a specification for a feature.

## Feature

$ARGUMENTS

## Instructions

Create a spec file at `.ai/specs/<feature-name>.md`.

## Format

# Feature Name

## Goal
What we're building and why. One sentence.

## Tasks

### T1: [Title]
Files: `path/to/file`, `tests/path/to/test_file.py`
Do: Write test first, then implement [what to build]
Verify: `uv run pytest tests/path/to/test_file.py`
Done: How you know it works

### T2: [Title]
Files: `path/to/file`, `tests/path/to/test_file.py`
Do: Write test first, then implement...
Verify: `uv run pytest ...`
Done: ...

## Questions
If ANYTHING is ambiguous, list it here. Don't guess.

## Guidelines

- Read CLAUDE.md first for project patterns
- Keep scope tight—if it feels like multiple features, pick one
- Each task should be self-contained with all context needed
- Tasks should be completable in one chat session
- The Verify command should be runnable immediately after implementation
