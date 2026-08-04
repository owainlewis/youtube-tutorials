# Optional Custom Provider Notes

Use Pi's built-in provider catalog first. Configure `models.json` only for an
endpoint that is not already covered, such as a local OpenAI-compatible server.

The canonical [`models.json`](../02-configuration/models.json) example contains
a placeholder rather than a current public model name. Replace its `id` with a
model served by your local endpoint.

Copy the example only when you need it:

```bash
mkdir -p ~/.pi/agent
cp /path/to/youtube-tutorials/tutorials/pi-coding-agent-guide/resources/02-configuration/models.json ~/.pi/agent/models.json
```

Then edit the copy before starting Pi.

Provider compatibility is more than a base URL. Confirm the API type, model ID,
context limit, output limit, supported roles, tool-calling format, and cost
metadata. The upstream [custom model reference](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/models.md)
defines the current schema.
