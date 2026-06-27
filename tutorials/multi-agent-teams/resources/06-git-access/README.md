# 06 - Connect Multica to your Git repo

This is the supporting material for the video: 06 - Connect Multica to your Git repo.

Agents need somewhere to push their output. Git is the right answer because it's free, durable, and gives you a diff-based review interface for free.

## Create a fine-grained Personal Access Token (PAT)

Don't use a deploy key. Deploy keys can push branches but cannot open pull requests. PR creation requires the GitHub API, which needs a token.

Steps:

1. GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token
2. **Token name**: `vps-agents`
3. **Expiration**: 90 days (the maximum for fine-grained)
4. **Repository access**: Only select repositories → pick the repo your agents will commit to
5. **Permissions** → Repository:
   - Contents: Read and write (for `git push`)
   - Pull requests: Read and write (for `gh pr create`)
   - Metadata: Read-only (auto-required)
6. Generate. Copy the `github_pat_...` value immediately - you won't see it again.

## Authenticate gh CLI on the VPS

```bash
echo 'export GITHUB_TOKEN="github_pat_..."' >> ~/.bashrc
source ~/.bashrc

echo "$GITHUB_TOKEN" | gh auth login --with-token
gh auth setup-git
gh auth status
```

This makes both `git push` (over HTTPS) and `gh pr create` work without further prompts.

## Clone the repo on the VPS

```bash
gh repo clone <your-username>/<your-repo> ~/<repo-name>
cd ~/<repo-name>
```

If the repo has Python or Node deps:

```bash
uv sync       # if pyproject.toml
npm install   # if package.json
```

## Test push and PR creation manually

This is the test the agent will replicate:

```bash
cd ~/<repo-name>
git checkout -b agent/test-pr-$(date +%Y-%m-%d)
echo "# Test from VPS agent" > .test-from-vps.md
git add .test-from-vps.md
git commit -m "Test commit from VPS agent"
git push -u origin HEAD
gh pr create --title "Test PR from agent" --body "Verifying agent can push and open PRs"
```

Expected: a URL to the new PR is printed. Open it in your browser, verify it looks right, close it without merging.

If this works manually, the agent will work the same way (it just runs the same commands).

## Configure Multica to use the repo

Point Multica's agents at the cloned repo as their working directory. Each agent's runs happen inside this directory, so files they write end up in the repo automatically.

> The exact Multica config field will depend on the version. Check current Multica docs.

## Branch strategy

Agents commit to `agent/{task-type}-{slug}-{date}` branches, never directly to main. You merge after reviewing.

Examples:
- `agent/research-hermes-2026-05-08`
- `agent/linkedin-multica-2026-05-13`
- `agent/description-VIDEO_ID-2026-05-14`

## Local sync via Obsidian Git

If you use Obsidian as your editor, install the [Obsidian Git plugin](https://github.com/Vinzent03/obsidian-git):

1. Settings → Community plugins → Browse → search "Git" → install **Obsidian Git**
2. Settings → Obsidian Git:
   - Auto-pull on startup: yes
   - Auto-pull interval: 10 minutes
   - Auto-push: no (you push after reviewing)

When an agent commits a new file on a branch, your vault auto-pulls it within 10 minutes. The new file appears in the sidebar. Review the diff, edit, merge.

## Token rotation (every 90 days)

Fine-grained PATs expire at 90 days max. To rotate:

1. Generate a new fine-grained PAT with the same scope
2. Update `~/.bashrc` on the VPS
3. Re-run `echo "$GITHUB_TOKEN" | gh auth login --with-token`

Set a calendar reminder.

## Next

[07 - Add team access](../07-team-access/)

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
