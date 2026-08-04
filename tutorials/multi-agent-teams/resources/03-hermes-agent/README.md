# 03 - Install Hermes Agent on the VPS

This is the supporting material for the video: 03 - Install Hermes Agent on the VPS.

Hermes Agent is one possible runner for the checked-in news research and LinkedIn repurposing skills. Multica can use it when the `hermes` command is installed and authenticated on the runner machine.

## Install

Use the current Linux install command from the [external Hermes Agent documentation](https://hermes-agent.nousresearch.com/docs/):

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

Verify the binary:

```bash
hermes --version
```

## Configure a provider

Hermes supports several model providers. Follow the [external quickstart](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart/) and choose the provider you intend to pay for and operate.

The documented portal setup path is:

```bash
hermes setup --portal
```

Do not paste API keys into this repository. Keep provider credentials in the location created by the Hermes setup flow.

## Verify the runner

Start one interactive session:

```bash
hermes
```

Ask it to perform a small read-only task, then exit. This proves the binary can reach the configured model before Multica tries to invoke it.

When Multica is installed, confirm that the runtime detects `hermes`. If it does not, compare the service user's `PATH` with the shell where this command succeeds:

```bash
command -v hermes
```

## Keep the first job narrow

Start with one checked-in skill:

```text
tutorials/multi-agent-teams/resources/05-skills-and-agents/skills/ai-news-research/SKILL.md
```

Verify the output manually before adding a schedule or another job. Provider support, permissions, and tool behavior can change, so use the current Hermes and Multica documentation when the observed behavior differs from this guide.

## Next

[04 - Install Multica](../04-multica/)

## Go Deeper

To go deeper on AI engineering, join my AI engineering community: [aiengineer.co](https://aiengineer.co).
