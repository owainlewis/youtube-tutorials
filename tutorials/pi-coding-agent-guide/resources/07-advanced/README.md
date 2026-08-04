# Optional Advanced Pi Modes

Use interactive mode until another process needs to control Pi. The other modes
solve integration problems, not normal terminal usage.

## Print Mode

Run one prompt and print the final text response:

```bash
pi --no-session -p "Explain the purpose of this repository. Do not edit files."
```

This requires a configured provider and sends repository context to that model.

## JSON Mode

Stream agent events as JSON lines:

```bash
pi --no-session --mode json "Explain the purpose of this repository. Do not edit files."
```

Consumers must handle event schema changes and errors. Do not parse the normal
interactive interface as machine-readable output.

## RPC Mode

Start a process controlled through standard input and output:

```bash
pi --no-session --mode rpc
```

Use the upstream [RPC documentation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/rpc.md)
for the current protocol before writing a client.

## SDK

Pi also exposes an SDK for TypeScript applications. SDK imports and session
construction are versioned application code. Follow the upstream
[SDK documentation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md)
instead of copying a dated model ID or constructor from this tutorial.
