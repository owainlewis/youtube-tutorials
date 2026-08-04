# Optional Pi Configuration

Start with Pi's defaults. Use these examples only when a repeated problem
justifies project or user configuration.

Pi reads global settings from `~/.pi/agent/settings.json` and project settings
from `.pi/settings.json`. Project settings override global settings.

## Append Project Instructions

[`APPEND_SYSTEM.md`](./APPEND_SYSTEM.md) adds a small set of rules without
replacing Pi's default system prompt. Copy it into a project as
`.pi/APPEND_SYSTEM.md`, then edit the rules to match that repository.

An instruction is not a permission boundary. Remove the `write` and `edit` tools
or use an isolated environment when you require enforcement.

## Settings

[`settings.json`](./settings.json) is deliberately small. It avoids a default
model ID so the live provider catalog remains the source of truth.

See the current [settings reference](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/settings.md)
before adding a key.

## Custom Models

[`models.json`](./models.json) shows the minimum shape for a local
OpenAI-compatible endpoint. Replace the placeholder ID with a model served by
your local runtime.

Built-in providers do not need this file. Configure them through `/login` and
choose a model through `/model`.

See the current [custom model reference](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/models.md)
for supported APIs, compatibility flags, limits, and optional cost metadata.
