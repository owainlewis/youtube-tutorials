package main

import (
	"bytes"
	"errors"
	"strings"
	"testing"
	"time"
)

func TestRendererShowsToolActivityWithoutANSIForBuffer(t *testing.T) {
	var output bytes.Buffer
	renderer := NewRenderer(&output)

	renderer.Banner("test/model", "/tmp/project")
	renderer.Handle(Event{
		Kind:      EventToolStart,
		ToolName:  "read_file",
		Arguments: `{"path":"main.go"}`,
	})
	renderer.Handle(Event{
		Kind:     EventToolFinish,
		ToolName: "read_file",
		Duration: 5 * time.Millisecond,
	})
	renderer.Handle(Event{Kind: EventDone})

	got := output.String()
	for _, want := range []string{"Micro Neo", "test/model", "→ read_file", "✓ read_file", "✓ Done"} {
		if !strings.Contains(got, want) {
			t.Fatalf("output missing %q:\n%s", want, got)
		}
	}
	if strings.Contains(got, "\x1b[") {
		t.Fatalf("buffer output contains ANSI escapes: %q", got)
	}
}

func TestRendererShowsToolAndAgentErrors(t *testing.T) {
	var output bytes.Buffer
	renderer := NewRenderer(&output)

	renderer.Handle(Event{
		Kind:      EventToolFinish,
		ToolName:  "run_command",
		Result:    "error: command exited with code 1",
		ToolError: true,
	})
	renderer.Handle(Event{Kind: EventError, Err: errors.New("provider failed")})

	got := output.String()
	if !strings.Contains(got, "command exited with code 1") ||
		!strings.Contains(got, "provider failed") {
		t.Fatalf("error output:\n%s", got)
	}
}
