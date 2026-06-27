# Pull Request

Push the current branch and open a pull request.

## Instructions

1. Run `git status` to check for uncommitted changes — commit them first if needed
2. Run `git log main..HEAD --oneline` to see all commits on this branch
3. Push the branch: `git push -u origin <branch-name>`
4. Create the PR using `gh pr create`

## PR format

### Title

Follow commit format: `type(scope): description`

### Body

```markdown
## What
1-2 sentences. What does this PR do?

## Why
The problem this solves or the reason for the change.

## How to test
Step-by-step instructions to verify this works.
```

## Rules

- Target branch is `main` unless otherwise specified
- PR title should be under 72 characters
- Description should be generated from the actual diff and commit history — not generic
- Include specific test steps, not just "verify it works"

## Example

```
gh pr create \
  --title "feat(auth): add password reset flow" \
  --body "## What
Adds password reset via email verification tokens.

## Why
Users were permanently locked out after forgetting their password.

## How to test
1. Go to /login and click 'Forgot password'
2. Enter a registered email
3. Check inbox for reset link
4. Follow link and set new password
5. Login with new password"
```
