# GitHub CLI Reference

These are the `gh` commands used in the workflow.

## Auth

```bash
gh auth login
gh auth status
```

## Repos

```bash
gh repo create
gh repo edit
gh repo view --web
```

## Issues

```bash
gh issue create
gh issue list
gh issue view 1
```

## Pull Requests

```bash
gh pr create
gh pr view --comments
gh pr checks
gh pr diff
gh pr merge --squash --delete-branch
```

## Actions

```bash
gh run list
gh run watch
gh run view --log
```

## Releases

```bash
gh release create
gh release view
gh release upload
```
