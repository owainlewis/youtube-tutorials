package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"
	"time"
)

type fakeProvider struct {
	responses []Message
	calls     [][]Message
}

func (f *fakeProvider) Complete(_ context.Context, _ string, messages []Message, _ []ToolDefinition) (Message, error) {
	f.calls = append(f.calls, append([]Message(nil), messages...))
	if len(f.responses) == 0 {
		return Message{}, errors.New("no fake response")
	}
	response := f.responses[0]
	f.responses = f.responses[1:]
	return response, nil
}

func TestAgentLoop(t *testing.T) {
	provider := &fakeProvider{responses: []Message{
		{Role: "assistant", ToolCalls: []ToolCall{{
			ID: "call_1", Type: "function",
			Function: FunctionCall{Name: "echo", Arguments: `{"text":"hello"}`},
		}}},
		{Role: "assistant", Content: "done", StopReason: "stop"},
	}}
	tools := map[string]Tool{"echo": {
		Name: "echo",
		Run: func(_ context.Context, raw json.RawMessage) (string, error) {
			var args struct {
				Text string `json:"text"`
			}
			if err := json.Unmarshal(raw, &args); err != nil {
				return "", err
			}
			return args.Text, nil
		},
	}}
	var events []Event
	agent := NewAgent(provider, tools, func(event Event) { events = append(events, event) })

	got, err := agent.Run(context.Background(), "say hello")
	if err != nil || got != "done" {
		t.Fatalf("Run() = %q, %v", got, err)
	}
	if len(provider.calls) != 2 {
		t.Fatalf("provider calls = %d, want 2", len(provider.calls))
	}
	result := provider.calls[1][2]
	if result.Role != "tool" || result.ToolCallID != "call_1" || result.Content != "hello" {
		t.Fatalf("tool result = %#v", result)
	}
	want := []string{"tool_start", "tool_finish", "assistant_text", "done"}
	for i, kind := range want {
		if events[i].Kind != kind {
			t.Fatalf("event %d = %q, want %q", i, events[i].Kind, kind)
		}
	}
}

func TestREPLRunsMultipleMessagesInOneConversation(t *testing.T) {
	provider := &fakeProvider{responses: []Message{
		{Role: "assistant", Content: "first answer", StopReason: "stop"},
		{Role: "assistant", Content: "second answer", StopReason: "stop"},
	}}
	var output bytes.Buffer
	renderer := NewRenderer(&output)
	agent := NewAgent(provider, nil, renderer.Handle)

	err := runREPL(
		context.Background(),
		strings.NewReader("first question\nfollow up\n/exit\n"),
		agent,
		renderer,
	)
	if err != nil {
		t.Fatal(err)
	}
	if len(provider.calls) != 2 {
		t.Fatalf("provider calls = %d, want 2", len(provider.calls))
	}
	secondCall := provider.calls[1]
	if len(secondCall) != 3 ||
		secondCall[0].Content != "first question" ||
		secondCall[1].Content != "first answer" ||
		secondCall[2].Content != "follow up" {
		t.Fatalf("second request transcript = %#v", secondCall)
	}
	if got := output.String(); !strings.Contains(got, "first answer") ||
		!strings.Contains(got, "second answer") {
		t.Fatalf("output = %q", got)
	}
}

func TestREPLEOFEndsPromptLine(t *testing.T) {
	var output bytes.Buffer
	renderer := NewRenderer(&output)
	agent := NewAgent(&fakeProvider{}, nil, renderer.Handle)

	if err := runREPL(context.Background(), strings.NewReader(""), agent, renderer); err != nil {
		t.Fatal(err)
	}
	if got := output.String(); got != "› \n" {
		t.Fatalf("output = %q, want prompt followed by newline", got)
	}
}

func TestREPLCancellationInterruptsIdlePrompt(t *testing.T) {
	reader, writer := io.Pipe()
	defer reader.Close()
	defer writer.Close()

	output := &promptWriter{prompted: make(chan struct{})}
	renderer := NewRenderer(output)
	agent := NewAgent(&fakeProvider{}, nil, renderer.Handle)
	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan error, 1)
	go func() {
		done <- runREPL(ctx, reader, agent, renderer)
	}()

	select {
	case <-output.prompted:
	case <-time.After(time.Second):
		t.Fatal("REPL did not show its prompt")
	}
	cancel()

	select {
	case err := <-done:
		if err != nil {
			t.Fatal(err)
		}
	case <-time.After(time.Second):
		t.Fatal("REPL did not stop after cancellation")
	}
}

func TestAgentPairsFailedAndCancelledToolResults(t *testing.T) {
	ctx, cancel := context.WithCancel(context.Background())
	changed := false
	provider := &fakeProvider{responses: []Message{{
		Role: "assistant",
		ToolCalls: []ToolCall{
			{ID: "first", Function: FunctionCall{Name: "cancel", Arguments: `{}`}},
			{ID: "second", Function: FunctionCall{Name: "change", Arguments: `{}`}},
		},
	}}}
	tools := map[string]Tool{
		"cancel": {Name: "cancel", Run: func(context.Context, json.RawMessage) (string, error) {
			cancel()
			return "cancelled", nil
		}},
		"change": {Name: "change", Run: func(context.Context, json.RawMessage) (string, error) {
			changed = true
			return "changed", nil
		}},
	}
	agent := NewAgent(provider, tools, nil)
	_, err := agent.Run(ctx, "cancel")
	if !errors.Is(err, context.Canceled) || changed {
		t.Fatalf("Run() error = %v, changed = %v", err, changed)
	}
	if len(agent.transcript) != 4 ||
		agent.transcript[2].ToolCallID != "first" ||
		agent.transcript[3].ToolCallID != "second" ||
		!strings.Contains(agent.transcript[3].Content, "canceled") {
		t.Fatalf("transcript = %#v", agent.transcript)
	}
}

func TestAgentRejectsIncompleteResponsesAndStopsAtLimit(t *testing.T) {
	lengthProvider := &fakeProvider{responses: []Message{{
		Role: "assistant", Content: "partial", StopReason: "length",
	}}}
	got, err := NewAgent(lengthProvider, nil, nil).Run(context.Background(), "go")
	if got != "partial" || err == nil || !strings.Contains(err.Error(), "length") {
		t.Fatalf("Run() = %q, %v", got, err)
	}

	loopProvider := &fakeProvider{responses: []Message{{
		Role:      "assistant",
		ToolCalls: []ToolCall{{ID: "call_1", Function: FunctionCall{Name: "echo", Arguments: `{}`}}},
	}}}
	agent := NewAgent(loopProvider, map[string]Tool{"echo": {
		Name: "echo", Run: func(context.Context, json.RawMessage) (string, error) { return "ok", nil },
	}}, nil)
	agent.maxTurns = 1
	_, err = agent.Run(context.Background(), "loop")
	if !errors.Is(err, ErrMaxTurns) || agent.transcript[2].ToolCallID != "call_1" {
		t.Fatalf("error = %v, transcript = %#v", err, agent.transcript)
	}
}

func TestOpenRouterRequestAndResponse(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.Header.Get("Authorization") != "Bearer secret" {
			t.Errorf("missing authorization header")
		}
		var payload chatRequest
		if err := json.NewDecoder(request.Body).Decode(&payload); err != nil {
			t.Fatal(err)
		}
		if payload.Model != "test/model" || payload.ParallelToolCalls || payload.Messages[0].Role != "system" {
			t.Fatalf("payload = %#v", payload)
		}
		writer.Header().Set("Content-Type", "application/json")
		_, _ = writer.Write([]byte(`{"choices":[{"finish_reason":"tool_calls","message":{
			"role":"assistant","content":null,"reasoning":"inspect",
			"reasoning_details":[{"type":"reasoning.text","text":"inspect"}],
			"tool_calls":[{"id":"call_1","type":"function","function":{"name":"read_file","arguments":"{}"}}]
		}}]}`))
	}))
	defer server.Close()

	client := OpenRouter{APIKey: "secret", Model: "test/model", Endpoint: server.URL, HTTPClient: server.Client()}
	got, err := client.Complete(context.Background(), "system", []Message{{Role: "user", Content: "hello"}}, nil)
	if err != nil || len(got.ToolCalls) != 1 || got.StopReason != "tool_calls" ||
		got.Reasoning != "inspect" || len(got.ReasoningDetails) == 0 {
		t.Fatalf("Complete() = %#v, %v", got, err)
	}
}

func TestOpenRouterReturnsAPIError(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		writer.WriteHeader(http.StatusTooManyRequests)
		_, _ = writer.Write([]byte(`{"error":{"message":"rate limited"}}`))
	}))
	defer server.Close()
	client := OpenRouter{Model: "test", Endpoint: server.URL, HTTPClient: server.Client()}
	_, err := client.Complete(context.Background(), "", nil, nil)
	if err == nil || !strings.Contains(err.Error(), "rate limited") {
		t.Fatalf("error = %v", err)
	}
}

func TestFileToolsStayInsideWorkspaceAndEditExactlyOnce(t *testing.T) {
	parent := t.TempDir()
	root := filepath.Join(parent, "workspace")
	if err := os.Mkdir(root, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(parent, "secret"), []byte("secret"), 0o644); err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(root, "example.txt")
	if err := os.WriteFile(path, []byte("hello world"), 0o640); err != nil {
		t.Fatal(err)
	}
	tools := mustTools(t, root)

	if _, err := runTestTool(tools["read_file"], map[string]any{"path": "../secret"}); err == nil {
		t.Fatal("read_file accepted workspace escape")
	}
	got, err := runTestTool(tools["edit_file"], map[string]any{
		"path": "example.txt", "old_text": "hello", "new_text": "goodbye",
	})
	if err != nil || got != "updated example.txt" {
		t.Fatalf("edit_file = %q, %v", got, err)
	}
	content, _ := os.ReadFile(path)
	info, _ := os.Stat(path)
	if string(content) != "goodbye world" || info.Mode().Perm() != 0o640 {
		t.Fatalf("content = %q, mode = %o", content, info.Mode().Perm())
	}
}

func TestToolsBoundInputOutputAndArguments(t *testing.T) {
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "large.txt"), []byte(strings.Repeat("x", maxFileBytes*2)), 0o644); err != nil {
		t.Fatal(err)
	}
	tools := mustTools(t, root)
	got, err := runTestTool(tools["read_file"], map[string]any{"path": "large.txt"})
	if err != nil || len(got) > maxFileBytes || !strings.Contains(got, "[truncated") {
		t.Fatalf("read_file length = %d, error = %v", len(got), err)
	}
	if _, err := runTestTool(tools["edit_file"], map[string]any{
		"path": "large.txt", "old_text": "x", "new_txt": "y",
	}); err == nil || !strings.Contains(err.Error(), "unknown field") {
		t.Fatalf("invalid arguments error = %v", err)
	}
	if _, err := tools["run_command"].Run(
		context.Background(),
		json.RawMessage(`{"command":"pwd"} {}`),
	); err == nil || !strings.Contains(err.Error(), "one JSON object") {
		t.Fatalf("trailing JSON error = %v", err)
	}
	got, err = runTestTool(tools["run_command"], map[string]any{"command": "yes x | head -c 100000"})
	if err != nil || len(got) > maxToolResultBytes || !strings.Contains(got, "[truncated") {
		t.Fatalf("command length = %d, error = %v", len(got), err)
	}
}

func TestRendererShowsProgressWithoutANSI(t *testing.T) {
	var output bytes.Buffer
	renderer := NewRenderer(&output)
	renderer.Banner("test/model", "/tmp/project")
	renderer.Handle(Event{Kind: "tool_start", ToolName: "read_file", Arguments: `{"path":"main.go"}`})
	renderer.Handle(Event{Kind: "tool_finish", ToolName: "read_file", Duration: time.Millisecond})
	renderer.Handle(Event{Kind: "done"})
	got := output.String()
	for _, want := range []string{"Micro Neo", "→ read_file", "✓ read_file", "✓ Done"} {
		if !strings.Contains(got, want) {
			t.Fatalf("output missing %q:\n%s", want, got)
		}
	}
	if strings.Contains(got, "\x1b[") {
		t.Fatalf("output contains ANSI: %q", got)
	}
}

type promptWriter struct {
	bytes.Buffer
	once     sync.Once
	prompted chan struct{}
}

func (w *promptWriter) Write(data []byte) (int, error) {
	if strings.Contains(string(data), "› ") {
		w.once.Do(func() { close(w.prompted) })
	}
	return w.Buffer.Write(data)
}

func mustTools(t *testing.T, root string) map[string]Tool {
	t.Helper()
	tools, err := NewTools(root)
	if err != nil {
		t.Fatal(err)
	}
	return tools
}

func runTestTool(tool Tool, arguments any) (string, error) {
	raw, err := json.Marshal(arguments)
	if err != nil {
		return "", err
	}
	return tool.Run(context.Background(), raw)
}
