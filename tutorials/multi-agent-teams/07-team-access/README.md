# 07 - Add Team Access

This is the supporting material for the video: 07 - Add Team Access.

This is what makes it an AI team instead of a personal toy. Anyone on your team can log in, create tickets, and use the agents.

## Multica auth

> The exact auth model depends on your Multica version. Common options:
>
> - Username/password (basic, fine for a small team)
> - Magic link (email-based, no password)
> - SSO (Google Workspace, Okta, etc. - for larger teams)
>
> For 1-10 people, basic auth or magic link is enough.

## Add team members

1. Multica → Settings → Users → Invite
2. Enter their email and a role
3. They receive an invite link

## Roles

Adjust per Multica's permission model. Common shape:

- **Admin** - configure agents, manage runners, change auth settings
- **Editor** - create and assign tickets, review outputs
- **Viewer** - read-only

For most small teams, everyone is an editor.

## Securing the URL

By default Multica is reachable at `http://<vps-ip>:<port>`. Fine for testing, not for team production.

Improve:

1. **Put it behind a domain with HTTPS** - see [04 - Install Multica](../04-multica/#optional-put-multica-behind-a-real-domain-with-https) for the Caddy setup
2. **Restrict by IP** if your team uses a VPN:
   ```bash
   sudo ufw allow from <ip-range> to any port <multica-port>
   ```
3. **Require auth on every action** - set short session timeouts in Multica's auth config

## Cost split

Multiple team members using the same agents stack up the API bill on whoever's API key Multica is using. Two options:

- **Single shared API key**, billed centrally - simpler, less granular tracking
- **Per-user API keys**, configured per Multica user - more granular but more setup

Start with shared. Revisit if usage gets large.

## Verify with a second user

The whole point of this guide. Test it:

1. A teammate (or use a second browser / incognito window) logs into Multica
2. They create a ticket assigned to a specialized agent
3. The agent runs successfully
4. The output lands in the shared repo or Notion
5. They can see the result

If this works, you've shipped a real AI team. Multiple humans, multiple agents, shared workspace.

## Done

You now have:

- A VPS running Multica as the agent control plane
- Claude Code and Hermes Agent as runners
- Specialized agents with one skill file each
- Git as the artifact store
- Team-accessible via authenticated URL

Cost: ~$5-10/month for the VPS plus your API usage.

## Where to go from here

- **Add more skills.** Every mechanical, verifiable task is a candidate. Audit your weekly work for things that fit.
- **Schedule more automations.** Daily reports, weekly digests, post-publish repurposing. Multica's scheduled automations are underused.
- **Don't over-delegate.** Re-read the [delegation framework](../README.md#the-thesis-what-to-delegate-what-to-keep) in the main README. If you find yourself iterating on an agent's output more than fixing it once, take the task back.

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
