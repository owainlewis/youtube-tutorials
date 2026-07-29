# Micro Neo Demo Prompts

Run these from `tutorials/micro-neo/code/`.

## Main Demo

```bash
go run . --workspace testdata/demo \
  "Find and fix the failing test. Run the tests when you are done."
```

Expected path:

1. Run `go test ./...` and observe the failure.
2. Read `calculator.go` and `calculator_test.go`.
3. Replace subtraction with addition.
4. Run `go test ./...` again.
5. Report that the test passes.

Reset the demo from the repository root:

```bash
git restore tutorials/micro-neo/code/testdata/demo/calculator.go
```

## Read-Only Exploration

```bash
go run . --workspace . \
  "Explain how this coding agent works. Do not change any files."
```

## Failure Recovery

This prompt gives the agent a missing filename. A useful model should recover
by searching the workspace.

```bash
go run . --workspace testdata/demo \
  "Read arithmetic.go, explain the Add function, and run its tests."
```

## Try Another Model

The selected model must support tool calling.

```bash
go run . \
  --model openai/gpt-5.4 \
  --workspace testdata/demo \
  "Find and fix the failing test. Run the tests when you are done."
```
