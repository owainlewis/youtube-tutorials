# 06 - Connect Multica To A Git Repository

The checked-in skills write files, create a branch, commit, and push. This runbook gives the Multica project a repository and gives the runner only the GitHub access needed for that output.

## Understand The Two Connections

Multica separates:

- **GitHub integration**, which reads authorized pull request and CI metadata.
- **Project resources**, which tell agent runs which repository to use and where to work.

The GitHub integration does not push commits for an agent. The agent CLI on the runtime needs its own repository credentials. See the [external GitHub integration guide](https://multica.ai/docs/github-integration) and [external project resources guide](https://multica.ai/docs/project-resources).

## Connect The Repository To Multica

An `owner` or `admin` can:

1. Open **Settings**, then **GitHub**.
2. Connect the GitHub App and authorize only the repositories this workspace needs.
3. Open or create the Multica project for these jobs.
4. Under **Resources**, choose **Add resource**.
5. Choose the authorized GitHub repository and its default ref.

A GitHub repository resource uses a runtime-managed working directory for each task. Do not add a local-directory resource unless you specifically need agents to edit an existing checkout in place.

## Give The Runtime Push Access

On the runner machine, authenticate GitHub CLI with a fine-grained token restricted to the output repository. Grant only the repository permissions required to create and push branches. Add pull-request permission only if the job will open pull requests.

```bash
gh auth login --with-token
gh auth status
gh repo view OWNER/REPOSITORY
```

Paste the token through standard input when `gh auth login --with-token` asks for it. Do not put the token in this repository, a skill file, an issue, or an agent prompt.

## Verify The Checked-In Contract

Create the test issue inside the project that owns the repository resource. Assign it to the agent with the imported `ai-news-research` skill.

After the issue reaches `in_review`, verify:

```bash
git ls-remote --heads origin 'agent/news-*'
```

Open the new branch in GitHub and confirm it contains only the expected digest file under `content/research/`. Review the commit before merging or marking the Multica issue `done`.

The other included skills use these branches:

```text
agent/linkedin-{slug}
agent/description-{slug}
```

## Optional Pull Request Tracking

If you open a pull request, include the Multica issue identifier in the branch name or title so the GitHub integration can link it. A close intent such as `Closes MUL-123` is required for a merged pull request to move the issue to `done` automatically. Otherwise, review the output and change the issue status yourself.

## Next

[07 - Add team access](../07-team-access/)

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
