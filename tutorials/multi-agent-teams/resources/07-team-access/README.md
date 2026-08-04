# 07 - Add Team Access

This runbook configures production sign-in, invites one member, grants access to one agent, and verifies the checked-in Git-branch workflow with a second account.

## Secure Remote Access First

Do not expose the Multica service ports directly to the public internet. Use the HTTPS and reverse-proxy setup in the [external Multica remote-access guide](https://multica.ai/docs/self-host-quickstart#remote-access).

## Configure Sign-In And Signup

Multica uses email verification codes by default. A self-hosted instance without an email service writes codes and invitation links to the backend logs, which is suitable for local setup but not a shared production instance.

Before inviting anyone:

1. Configure Resend or SMTP for email delivery.
2. Keep `APP_ENV=production`.
3. Do not set `MULTICA_DEV_VERIFICATION_CODE` on a public instance.
4. Restrict new accounts with `ALLOW_SIGNUP`, `ALLOWED_EMAILS`, or `ALLOWED_EMAIL_DOMAINS`.
5. Recreate the containers after environment changes so they load the new configuration.

Google sign-in is optional. The [external Multica sign-in guide](https://multica.ai/docs/auth-setup) documents email delivery, Google OAuth, signup restrictions, and exact environment variables.

Invitations do not bypass signup restrictions. If signup is closed and the invitee has no account, add that address to `ALLOWED_EMAILS` until the account is created.

## Invite A Member

An `owner` or `admin` can:

1. Open **Settings**, then **Members**.
2. Enter the teammate's email address.
3. Choose `admin` or `member`.
4. Send the invitation.

The current workspace roles are:

| Role | Scope |
|---|---|
| `owner` | Workspace settings, member management, ownership changes, and workspace deletion |
| `admin` | Workspace settings and management of `admin` and `member` accounts |
| `member` | Day-to-day work such as issues and comments |

Workspace roles do not decide who can run an agent. See the [external members and roles guide](https://multica.ai/docs/members-roles).

## Grant Agent Access Separately

Each agent has an Access scope:

- **Only me**
- **Entire workspace**
- **Specific people**

Only the agent owner can change this scope. For the first team test, choose **Specific people** and add the invited member. Do not use **Entire workspace** until every workspace member should be able to run that agent.

The [external agent configuration guide](https://multica.ai/docs/agents-create#access) explains this boundary.

## Verify With A Second Account

Use the invited account in a separate browser profile:

1. Sign in and accept the workspace invitation.
2. Create an issue with status `todo`.
3. Assign it to the agent shared through **Specific people**.
4. Confirm the issue moves through `in_progress` to `in_review`.
5. Inspect the Git branch and files required by the attached skill.
6. Confirm the second account can comment but cannot change settings its role does not allow.
7. Mark the issue `done` only after reviewing the branch.

The checked-in skills produce Git branches. This tutorial does not configure Notion or gist output.

## Final Checklist

- Multica is reached through HTTPS.
- Production email delivery works.
- Signup restrictions match the intended team.
- Every person has the minimum workspace role they need.
- Every agent has an explicit Access scope.
- A second account completed one reviewed Git-branch workflow.
- Provider and VPS costs have been checked against current pricing.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
