---
name: code-review
description: Review code changes for bugs, security issues, performance problems, and style violations. Use when asked to review code, a PR, or recent changes.
---

# Code Review

When reviewing code, follow this process:

## Step 1: Understand the Change

Run `git diff` (or `git diff --staged` for staged changes) to see what changed.
Read the modified files in full to understand the surrounding context.

## Step 2: Check for Issues

Review each changed file for:

**Correctness**
- Logic errors, off-by-one errors, race conditions
- Missing null/undefined checks at system boundaries
- Incorrect error handling (swallowed errors, wrong error types)

**Security**
- SQL injection, XSS, command injection
- Hardcoded secrets or credentials
- Overly permissive file/network access

**Performance**
- N+1 queries, unnecessary loops, large allocations
- Missing indexes for new database queries
- Blocking operations in async code

**Maintainability**
- Unclear naming, overly complex logic
- Dead code, unused imports
- Missing types in TypeScript

## Step 3: Report

Format your review as:

1. **Summary:** One sentence on what the change does
2. **Issues:** Specific problems with file paths and line numbers
3. **Suggestions:** Optional improvements (clearly marked as optional)

Be direct. Don't pad with praise. Focus on things that matter.
