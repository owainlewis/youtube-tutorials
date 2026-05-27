# GitHub AI Workflow

> Build, review, merge, and release software by driving GitHub from an AI agent with the GitHub CLI.

This is the companion project for the YouTube tutorial on using Claude Code, Codex, and the GitHub CLI as a complete development workflow.

The goal is not to memorize more commands. The goal is to create a repeatable system where an agent can:

- create a repo
- set up GitHub issues and project tracking
- write a spec
- break the spec into tasks
- implement each task on a branch
- open pull requests
- address code review feedback
- merge cleanly
- cut a release with built binaries

The GitHub CLI is the bridge. Once `gh` is authenticated, the agent can operate GitHub from the terminal without you clicking around the web UI.

---

## Demo Project

For the video, build a small Go CLI from scratch.

Suggested demo app: **shiplog**

`shiplog` is a tiny Go CLI that helps generate release notes from a GitHub repository. It can list merged pull requests between two refs, group them by label, and print Markdown release notes.

Why this works well for the tutorial:

- It is small enough to build in one filming session.
- It naturally uses GitHub concepts: PRs, labels, tags, and releases.
- It gives the release pipeline finale a real purpose.
- Go produces single binaries for macOS, Linux, and Windows.

You can swap this for any small CLI idea. The workflow is the point.

---

## Prerequisites

- Git
- Go
- GitHub account
- GitHub CLI
- Claude Code, Codex, or another coding agent with terminal access

Install GitHub CLI:

```bash
# macOS
brew install gh
```

For Linux and Windows, use the official installation instructions:

```text
https://cli.github.com/
```

Authenticate:

```bash
gh auth login
gh auth status
```

Confirm the CLI works:

```bash
gh --version
```

---

## Filming Flow

Use this as the end-to-end checklist while filming.

1. Install and authenticate GitHub CLI
2. Create the GitHub repo
3. Set up the project board
4. Write the spec
5. Break the spec into GitHub issues
6. Build the first feature end-to-end on camera
7. Address PR feedback
8. Squash and merge
9. Fast-forward through the remaining features
10. Add the release pipeline
11. Tag `v0.1.0` and watch the workflow publish binaries
12. Close with the bigger automation idea

---

## Step 1: Install GitHub CLI

Use this section only briefly on camera. The point is to establish that `gh` is the tool that lets agents operate GitHub.

```bash
brew install gh
gh auth login
gh auth status
gh --version
```

Talking point:

GitHub has a command for nearly every action we normally do through the web interface: repos, issues, PRs, releases, workflow runs, labels, and more. That means an agent can drive the workflow from the terminal.

---

## Step 2: Create The Repo

Prompt:

```text
Create a new public GitHub repo called shiplog. Initialize it with a README and a Go module. Add a standard Go .gitignore.

Set the description to "Generate Markdown release notes from merged GitHub pull requests."

Add these topics:
- cli
- golang
- github
- release-notes
- ai-workflow
```

Expected agent actions:

```bash
gh repo create shiplog --public --clone --add-readme
cd shiplog
go mod init github.com/YOUR_USERNAME/shiplog
gh repo edit --description "Generate Markdown release notes from merged GitHub pull requests."
gh repo edit --add-topic cli --add-topic golang --add-topic github --add-topic release-notes --add-topic ai-workflow
```

Filming note:

Show the repo page after creation. Point out that the agent handled the small setup details you would otherwise forget.

---

## Step 3: Set Up The Project Board

Prompt:

```text
Create a GitHub Project board linked to this repo. I want views or statuses for Backlog, In Progress, In Review, and Done. I'll use it to track every development task.
```

Expected agent actions:

```bash
gh project create --title "shiplog"
gh project list
gh project item-add PROJECT_NUMBER --owner YOUR_USERNAME --url ISSUE_URL
```

Notes:

- GitHub Projects can vary by account and organization setup, so let the agent inspect what permissions and project commands are available.
- If the project command needs an owner, use `--owner YOUR_USERNAME` or the organization name.
- If custom fields/statuses are awkward through `gh project`, it is fine for the agent to create the project and then explain the one manual adjustment.

Filming note:

This is a good moment to say: "The agent is not just writing code. It is setting up the development system around the code."

---

## Step 4: Write The Spec

Prompt:

```text
Use the spec skill.

I want to build a Go CLI called shiplog.

The tool generates Markdown release notes from merged GitHub pull requests. It should be able to:

- detect the current GitHub repo from the local git remote
- accept a previous tag and a new tag
- find merged pull requests between those refs
- group pull requests by label, such as feature, bug, docs, chore
- print clean Markdown release notes to stdout
- optionally write the output to a file

Write a complete spec covering:

- requirements
- command structure
- flags and arguments
- technical approach
- external dependencies
- error handling
- test strategy

Save it to specs/initial-spec.md.
```

Review checklist:

- Is the CLI small enough for the demo?
- Are commands and flags clear?
- Are the first few issues independently buildable?
- Is there a realistic happy path for the release pipeline?

Filming note:

This is where you show the "plan first" habit. Correct any misunderstanding before code exists.

---

## Step 5: Break The Spec Into Tasks

Prompt:

```text
Use the plan skill.

Take the spec at specs/initial-spec.md and break it down into GitHub issues.

Each issue should include:

- a clear title
- a short description
- acceptance criteria as a checklist
- relevant context from the spec

Push the issues to GitHub using gh issue create.

Add each issue to the project board in the Backlog column.

Use labels:
- feature
- bug
- chore
- docs
```

Suggested issue breakdown:

1. Initialize Go CLI structure
2. Detect GitHub repository from git remote
3. Fetch merged pull requests between refs
4. Group pull requests by labels
5. Render Markdown release notes
6. Add file output flag
7. Add tests and fixtures
8. Add GitHub Actions CI
9. Add release workflow

Useful commands:

```bash
gh label create feature --color 0E8A16 --description "New user-facing functionality"
gh label create bug --color D73A4A --description "Bug fixes"
gh label create chore --color C5DEF5 --description "Maintenance work"
gh label create docs --color 0075CA --description "Documentation"

gh issue create --title "Initialize Go CLI structure" --label feature
```

Filming note:

Show the populated board. This makes the workflow tangible before any code is written.

---

## Step 6: Build The First Feature

Prompt:

```text
Use the implement skill.

Take issue #1 from the project board.

1. Move the issue to In Progress on the board.
2. Check out a new Git branch named after the issue.
3. Write the code to satisfy all acceptance criteria.
4. Run formatting and tests.
5. Use a sub-agent with a fresh context window to review your output for quality and catch any issues.
6. Fix any valid review findings.
7. Open a pull request back to main using gh pr create.

The PR description should include:

- summary
- testing notes
- any follow-up work
- Closes #1
```

Expected agent actions:

```bash
git checkout -b feature/initialize-go-cli
go fmt ./...
go test ./...
gh pr create --base main --head feature/initialize-go-cli
```

PR description template:

```markdown
## Summary
- Initialize the Go CLI project structure
- Add the first command entrypoint
- Add basic tests

## Testing
- `go test ./...`

Closes #1
```

Teaching points:

- Good branch names come from issue titles.
- PR descriptions should be generated from the actual diff.
- `Closes #1` connects the PR to the issue and closes it automatically on merge.
- A fresh review context catches different mistakes than the implementing context.

---

## Step 7: Address Code Review Feedback

Prompt:

```text
Use the address PR feedback skill.

Pull down all comments on this PR using gh pr view and gh api.

Work through them one by one.

For each comment, decide whether it is:

- valid feedback that needs a code change
- valid feedback that does not need a code change
- feedback you disagree with

Do not blindly accept every suggestion.

When you push a fix, reply on the comment thread saying what changed and why.

For comments you do not act on, reply explaining your reasoning.
```

Useful commands:

```bash
gh pr view --comments
gh pr checks
gh api repos/:owner/:repo/pulls/PR_NUMBER/comments
```

Filming note:

This is one of the strongest workflow examples. The agent is not just "fixing comments"; it is doing review triage and communication.

---

## Step 8: Squash And Merge

Prompt:

```text
Squash and merge this PR.

Use a clean commit message that follows conventional commits and references the issue.
```

Useful command:

```bash
gh pr merge --squash --delete-branch
```

Example commit message:

```text
feat: initialize Go CLI structure

Adds the initial command entrypoint, module layout, and baseline tests for shiplog.

Closes #1
```

Filming note:

Show the issue closing, the PR merging, and the board card moving to Done.

---

## Step 9: Build The Remaining Features

Use the same loop for the remaining issues:

```text
Use the implement skill.

Take the next issue from the project board.

Move it to In Progress, create a branch, implement the acceptance criteria, run tests, use a fresh sub-agent review, open a PR, address feedback, and prepare it for squash merge.
```

Fast-forward this section in the final video.

Good B-roll:

- issues moving from Backlog to In Progress
- branches being created
- PRs opening
- CI checks going green
- project board filling up
- merged PR list

---

## Step 10: Add The Release Pipeline

This is the finale. The CLI is built; now ship it.

Planning prompt:

```text
I want to set up a release pipeline for this Go CLI as a GitHub Action.

When I push a Git tag like v0.1.0, the workflow should:

1. Check out the code at the tag
2. Build binaries for macOS arm64, macOS amd64, Linux amd64, and Windows amd64
3. Name the binaries clearly so users can tell which platform they are for
4. Generate release notes from merged PRs since the previous tag
5. Create a GitHub release using gh release create, with the tag name as the version
6. Attach all platform binaries to that release

Before you write any code, walk me through your plan. I want to sanity-check the approach.
```

Implementation prompt:

```text
Looks good.

Write the workflow file and save it to .github/workflows/release.yml.

Walk me through the key parts once it is written.
```

Example workflow:

```yaml
name: Release

on:
  push:
    tags:
      - "v*.*.*"

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version-file: go.mod

      - name: Build binaries
        shell: bash
        run: |
          mkdir -p dist

          platforms=(
            "darwin amd64 shiplog-darwin-amd64"
            "darwin arm64 shiplog-darwin-arm64"
            "linux amd64 shiplog-linux-amd64"
            "windows amd64 shiplog-windows-amd64.exe"
          )

          for platform in "${platforms[@]}"; do
            set -- $platform
            GOOS=$1 GOARCH=$2 go build -o "dist/$3" ./cmd/shiplog
          done

      - name: Create GitHub release
        env:
          GH_TOKEN: ${{ github.token }}
        shell: bash
        run: |
          gh release create "${GITHUB_REF_NAME}" dist/* \
            --repo "${GITHUB_REPOSITORY}" \
            --title "${GITHUB_REF_NAME}" \
            --generate-notes
```

Notes:

- `permissions: contents: write` allows the workflow token to create releases.
- `fetch-depth: 0` gives the workflow access to tag history.
- `--generate-notes` asks GitHub to generate release notes for the tag.
- `GH_TOKEN: ${{ github.token }}` lets `gh` authenticate inside the workflow.

Filming note:

This is the emotional center of the video. Say out loud that you do not remember every piece of GitHub Actions syntax, and that this is exactly where agents are useful.

---

## Step 11: Tag And Watch The Release

Prompt:

```text
Commit the new workflow file with a clear message.

Then tag this as v0.1.0 and push both the commit and the tag.
```

Expected commands:

```bash
git add .github/workflows/release.yml
git commit -m "ci: add release workflow"
git tag v0.1.0
git push origin main
git push origin v0.1.0
```

Watch the workflow:

```text
Use gh run watch to follow the latest workflow run.
```

Useful commands:

```bash
gh run list --limit 5
gh run watch
gh release view v0.1.0
```

Filming note:

`gh run watch` is the small reveal. Most people know GitHub Actions exist; fewer people watch them from the terminal.

---

## Step 12: Automate The Bigger Cycle

Once the core workflow is repeatable, you can automate more of it with GitHub Actions and agents.

Ideas:

- Auto-label PRs from their diffs
- Triage stale issues every week
- Draft release announcements from release notes
- Ask for missing reproduction steps on vague bug reports
- Summarize merged PRs into a weekly project update
- Run an agent review on every PR

Talking point:

The unlock is not that the agent can type commands quickly. The unlock is that your workflow becomes consistent. Every issue has acceptance criteria. Every PR has a useful description. Every merge has a clean commit message. Every release has artifacts and notes.

---

## Commit Message Prompt

Copy this into Claude Code, Codex, or your agent of choice:

```text
Write a commit message for the staged changes.

Rules:

- Use Conventional Commits format: type(scope): summary
- Use one of these types: feat, fix, docs, test, refactor, chore, ci
- Keep the summary under 72 characters
- Use imperative mood
- Add a body when it helps explain why the change was made
- Mention important tradeoffs or follow-up work
- Reference the issue number when one exists
- Do not describe unrelated changes

Before writing the message, inspect:

- git status
- git diff --staged
- recent commit style from git log --oneline -10

If the staged changes contain multiple unrelated changes, stop and suggest splitting them into separate commits.
```

Example output:

```text
feat(cli): add release note rendering

Groups merged pull requests by label and renders the result as Markdown so
release notes can be generated from the command line.

Closes #5
```

---

## Commit Message Skill

Turn the prompt above into a reusable skill.

Example `SKILL.md`:

```markdown
---
name: commit-message
description: Write high-quality conventional commit messages from staged changes.
---

# Commit Message

Inspect the staged diff and write a clean commit message.

## Workflow

1. Run `git status`.
2. Run `git diff --staged`.
3. Check recent style with `git log --oneline -10`.
4. Decide whether the staged changes are one logical change.
5. If they are not one logical change, stop and recommend a split.
6. Write a Conventional Commit message.

## Rules

- Format: `type(scope): summary`
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`
- Summary must be imperative and under 72 characters.
- Add a body when the why is not obvious.
- Reference the issue number when one exists.
- Never invent motivation that is not supported by the diff.
- Never include secrets, credentials, or private data in the message.
```

---

## Reusable Agent Prompts

### Create Repo

```text
Create a new public GitHub repo called [repo-name]. Initialize it with a README and a Go module. Add a standard Go .gitignore. Set the description to "[description]" and add the topics: cli, golang, [topic].
```

### Create Project Board

```text
Create a GitHub Project board linked to this repo. I want statuses for Backlog, In Progress, In Review, and Done.
```

### Write Spec

```text
Use the spec skill. I want to build [tool description]. Write a complete spec covering requirements, command structure, technical approach, dependencies, error handling, and tests. Save it to specs/initial-spec.md.
```

### Create Issues

```text
Use the plan skill. Take specs/initial-spec.md and break it into GitHub issues. Each issue needs a clear title, description, acceptance criteria checklist, and labels. Create the issues with gh issue create and add them to the project board.
```

### Implement Issue

```text
Use the implement skill. Take issue #[number], move it to In Progress, create a branch, implement the acceptance criteria, run tests, use a fresh sub-agent review, fix valid findings, and open a PR with a description that includes Closes #[number].
```

### Address Review

```text
Use the address PR feedback skill. Fetch all PR comments and review threads. Triage each comment as valid requiring a code change, valid requiring no code change, or invalid. Apply fixes where appropriate, push them, and reply to each thread with what changed or why no change was made.
```

### Merge

```text
Squash and merge this PR. Use a clean conventional commit message and reference the issue.
```

### Release

```text
Set up a GitHub Actions release workflow for this Go CLI. On tags like v0.1.0, build platform binaries, generate release notes, create a GitHub release, and attach the binaries. Walk me through the plan before writing the workflow.
```

---

## Useful GitHub CLI Commands

```bash
# Auth
gh auth login
gh auth status

# Repos
gh repo create
gh repo edit
gh repo view --web

# Issues
gh issue create
gh issue list
gh issue view 1

# Pull requests
gh pr create
gh pr view --comments
gh pr checks
gh pr merge --squash --delete-branch

# Actions
gh run list
gh run watch
gh run view --log

# Releases
gh release create
gh release view
gh release upload
```

---

## Filming Beats

Important moments to land:

- GitHub is the system of record for agent work.
- The agent can operate issues, branches, PRs, reviews, CI, and releases through `gh`.
- Ask for a plan before allowing the agent to write consequential files.
- Use a fresh sub-agent review before opening important PRs.
- Do not blindly accept review comments; triage them.
- `gh run watch` lets you watch CI from the terminal.
- The real value is consistency, not raw speed.

---

## Description Links

Use these in the YouTube description:

- GitHub CLI: https://cli.github.com/
- GitHub CLI manual: https://cli.github.com/manual/
- Go downloads: https://go.dev/dl/
- Conventional Commits: https://www.conventionalcommits.org/

---

## License

MIT
