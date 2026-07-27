# Prompts

Use these prompts with the dependency-free Python server in [`../code/`](../code/).

## Claude Code: direct mode

Use after starting Claude Code with `sbx run claude --name claude-direct`.

```text
Add a GET /health endpoint that returns HTTP 200 with the JSON body
{"status": "ok"}. Add a focused unittest, run the full test suite, and
summarize the files you changed. Do not commit.
```

Expected evidence:

- Claude edits the direct-mounted host working tree.
- `git diff` on the host shows changes immediately.
- Claude runs `python3 -m unittest -v` before finishing.

## Codex: clone mode

Use after starting Codex with `sbx run --clone codex --name codex-clone`.

```text
First configure this clone to use Git author name "Sandbox Demo" and email
"sandbox-demo@example.com". Create a branch named demo/codex-health. Add a
GET /health endpoint that returns HTTP 200 with the JSON body
{"status": "ok"}. Add a focused unittest, run the full test suite, and
commit the finished change. Do not push to origin.
```

Expected evidence:

- The host working tree stays clean.
- Codex commits on `demo/codex-health` inside the sandbox clone.
- The branch becomes reviewable after `git fetch sandbox-codex-clone`.

## Safety review

Use this as a final agent pass, but inspect the evidence yourself too.

```text
Review only the current diff for security and correctness. Check for
unexpected changes to hidden files, Git configuration or hooks, CI files,
build scripts, package scripts, dependencies, and network behavior. Run the
smallest relevant test command. Report evidence and remaining risks. Do not
edit or commit anything.
```
