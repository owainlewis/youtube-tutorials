# Codex Automations: Bug Fix and Bug Scan

These are generic, shareable Codex automation resources based on real workflows. They are designed to be copied and customized per project.

What Automations Are:
Automations let Codex run background tasks on a schedule you define. When an automation finishes, results land in a review queue so you can pick up the work and continue if needed. Learn more in the Codex app announcement: [Introducing the Codex app](https://openai.com/index/introducing-the-codex-app/).

Why This Matters:
Recurring, background agents reduce the chance of missed bugs and keep routine work moving without interrupting your day. These examples show how to turn code review and bug fixing into consistent, repeatable workflows.

Files:
- resources/bug-fix-automation.toml
- resources/bug-scan-automation.toml

Usage:
1. Copy a resource file into your Codex automations folder.
2. Replace placeholders like {project}, {repo_root}, and {auto_fix_label}.
3. Adjust the schedule if needed.

Conventions:
- Use stable, repo-rooted paths in tickets and summaries.
- Add a clear fingerprint for each bug, so duplicates are easy to detect.
- Use draft PRs unless the fix is trivial.
- If required tools or permissions are unavailable, report and stop.

Output Summary Format:
- Issue
- Branch
- Tests run
- PR
- Status change
- Notes or blockers

Placeholders:
- {project}: Linear project name or id.
- {repo_root}: Absolute path to the repo root.
- {auto_fix_label}: Label to mark tickets as eligible for automation.
- {branch_prefix}: Branch prefix, for example codex/.
- {in_review_status}: Status name for "in review" in your workflow.

Security and Permissions:
Codex tasks run in isolated sandboxes, and permission models can limit file access or require approval for elevated actions. See [Introducing the Codex app](https://openai.com/index/introducing-the-codex-app/) and [Introducing upgrades to Codex](https://openai.com/index/introducing-upgrades-to-codex/) for details.

Implementation Notes:
Automation internals can evolve over time. Treat on-disk layout details as helpful context rather than a stable API.
