# Backlog Manager Prompt

Use this prompt with the `backlog-manager` skill.

Replace:

- `owner/repo` with your GitHub repository.
- `PROJECT_URL` with your GitHub Project URL if you use one.
- `REPO_PATH` with the local repository path if the agent has filesystem access.

## Dry Run

```text
$backlog-manager dry-run GitHub backlog for owner/repo

Repository path: REPO_PATH
Project board: PROJECT_URL

Review the repository and issue tracker.

Do not mutate GitHub in dry-run mode.

Report:
- labels that are missing
- open issues that need risk labels
- open issues that need type labels
- issues that should be agent-ready
- issues that need a human decision
- stale tickets where linked PRs are already merged
- evidence-backed maintenance issues you would create
- anything unsafe or blocked

Only suggest new issues when there is clear evidence of a real problem in the codebase, docs, tests, CI, or project configuration.
```

## Apply

```text
$backlog-manager apply GitHub backlog for owner/repo

Repository path: REPO_PATH
Project board: PROJECT_URL

Apply the backlog-manager workflow.

Allowed actions:
- create missing managed labels
- apply risk/type/agent labels
- add or update Agent Assessment comments
- create evidence-backed maintenance issues
- update issue status when linked PRs prove the work is complete

Do not:
- write code
- open PRs
- merge anything
- create speculative tickets
- mark vague or risky work as agent-ready

End with a concise run report.
```

