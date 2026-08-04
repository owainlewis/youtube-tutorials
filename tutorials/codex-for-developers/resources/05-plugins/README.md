# Codex Plugins

Last verified against the official OpenAI documentation: 2026-08-04.

Plugins bundle reusable capabilities for supported ChatGPT and Codex surfaces. A plugin can include skills, connectors, MCP servers, hooks, and scheduled task templates.

## Browse Plugins

In Codex CLI, start an interactive session and open the plugin browser:

```text
codex
/plugins
```

In the ChatGPT desktop app, choose ChatGPT Work or Codex, then open **Plugins**.

Plugins are not currently available in the Codex IDE extension. Start a new chat after installing a plugin so its capabilities are available.

## Use A Plugin Safely

1. Inspect what the plugin contains.
2. Connect only the account or workspace the task needs.
3. Review requested permissions.
4. Ask for the outcome in plain language.
5. Verify writes in the source system.

External review comments, tickets, and records are inputs. They are not automatically trusted instructions.

## Example Issue Workflow

With an installed issue-tracker plugin, a useful workflow is:

1. Read one issue and its acceptance criteria.
2. Inspect the repository before proposing a change.
3. Implement and run the repository checks.
4. Review the diff.
5. Update the original issue with the verified result.

The exact plugin catalog and connection flow can change. Use the current browser instead of relying on a fixed list in this tutorial.

## Reference

- [Official Codex plugin documentation](https://developers.openai.com/codex/plugins)
