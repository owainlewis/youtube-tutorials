package main

import (
	"context"
	"encoding/json"
	"errors"
	"strings"
	"testing"
)

type providerCall struct {
	System   string
	Messages []Message
	Tools    []ToolDefinition
}

type fakeProvider struct {
	responses []Message
	err       error
	calls     []providerCall
}

func (f *fakeProvider) Complete(
	_ context.Context,
	system string,
	messages []Message,
	tools []ToolDefinition,
) (Message, error) {
	f.calls = append(f.calls, providerCall{
		System:   system,
		Messages: append([]Message(nil), messages...),
		Tools:    append([]ToolDefinition(nil), tools...),
	})
	if f.err != nil {
		return Message{}, f.err
	}
	if len(f.responses) == 0 {
		return Message{}, errors.New("fake provider has no response")
	}
	response := f.responses[0]
	f.responses = f.responses[1:]
	return response, nil
}

func TestAgentRunsToolAndReturnsFinalText(t *testing.T) {
	provider := &fakeProvider{responses: []Message{
		{
			Role: "assistant",
			ToolCalls: []ToolCall{{
				ID:   "call_123",
				Type: "function",
				Function: FunctionCall{
					Name:      "echo",
					Arguments: `{"text":"hello"}`,
				},
			}},
		},
		{Role: "assistant", Content: "done"},
	}}
	tools := map[string]Tool{
		"echo": {
			Name:       "echo",
			Parameters: objectSchema(map[string]any{"text": stringProperty("Text")}, "text"),
			Run: func(_ context.Context, raw json.RawMessage) (string, error) {
				var args struct {
					Text string `json:"text"`
				}
				if err := json.Unmarshal(raw, &args); err != nil {
					return "", err
				}
				return args.Text, nil
			},
		},
	}

	var events []Event
	agent := NewAgent(provider, "system", tools, 5, func(event Event) {
		events = append(events, event)
	})

	got, err := agent.Run(context.Background(), "say hello")
	if err != nil {
		t.Fatal(err)
	}
	if got != "done" {
		t.Fatalf("Run() = %q, want done", got)
	}
	if len(provider.calls) != 2 {
		t.Fatalf("provider calls = %d, want 2", len(provider.calls))
	}

	secondCall := provider.calls[1]
	if len(secondCall.Messages) != 3 {
		t.Fatalf("second request messages = %d, want 3", len(secondCall.Messages))
	}
	toolResult := secondCall.Messages[2]
	if toolResult.Role != "tool" || toolResult.ToolCallID != "call_123" || toolResult.Content != "hello" {
		t.Fatalf("tool result = %#v", toolResult)
	}
	if len(events) != 4 {
		t.Fatalf("events = %d, want 4", len(events))
	}
	if events[0].Kind != EventToolStart || events[1].Kind != EventToolFinish ||
		events[2].Kind != EventAssistantText || events[3].Kind != EventDone {
		t.Fatalf("unexpected event order: %#v", events)
	}
}

func TestAgentTurnsUnknownToolIntoMatchingResult(t *testing.T) {
	provider := &fakeProvider{responses: []Message{
		{
			Role: "assistant",
			ToolCalls: []ToolCall{{
				ID:       "missing_1",
				Type:     "function",
				Function: FunctionCall{Name: "missing", Arguments: `{}`},
			}},
		},
		{Role: "assistant", Content: "recovered"},
	}}
	agent := NewAgent(provider, "", nil, 5, nil)

	if _, err := agent.Run(context.Background(), "try a tool"); err != nil {
		t.Fatal(err)
	}

	result := provider.calls[1].Messages[2]
	if result.ToolCallID != "missing_1" {
		t.Fatalf("tool result ID = %q, want missing_1", result.ToolCallID)
	}
	if !strings.Contains(result.Content, "unknown tool") {
		t.Fatalf("tool result = %q, want unknown tool error", result.Content)
	}
}

func TestAgentTurnsToolErrorIntoMatchingResult(t *testing.T) {
	provider := &fakeProvider{responses: []Message{
		{
			Role: "assistant",
			ToolCalls: []ToolCall{{
				ID:       "broken_1",
				Type:     "function",
				Function: FunctionCall{Name: "broken", Arguments: `{}`},
			}},
		},
		{Role: "assistant", Content: "recovered"},
	}}
	tools := map[string]Tool{
		"broken": {
			Name:       "broken",
			Parameters: objectSchema(nil),
			Run: func(context.Context, json.RawMessage) (string, error) {
				return "useful output", errors.New("tool failed")
			},
		},
	}
	agent := NewAgent(provider, "", tools, 5, nil)

	if _, err := agent.Run(context.Background(), "try a tool"); err != nil {
		t.Fatal(err)
	}

	result := provider.calls[1].Messages[2]
	if result.ToolCallID != "broken_1" {
		t.Fatalf("tool result ID = %q, want broken_1", result.ToolCallID)
	}
	if !strings.Contains(result.Content, "tool failed") || !strings.Contains(result.Content, "useful output") {
		t.Fatalf("tool result = %q, want error and output", result.Content)
	}
}

func TestAgentPreservesToolResultBeforeMaxTurns(t *testing.T) {
	provider := &fakeProvider{responses: []Message{{
		Role: "assistant",
		ToolCalls: []ToolCall{{
			ID:       "call_1",
			Type:     "function",
			Function: FunctionCall{Name: "echo", Arguments: `{}`},
		}},
	}}}
	tools := map[string]Tool{
		"echo": {
			Name:       "echo",
			Parameters: objectSchema(nil),
			Run: func(context.Context, json.RawMessage) (string, error) {
				return "ok", nil
			},
		},
	}
	agent := NewAgent(provider, "", tools, 1, nil)

	_, err := agent.Run(context.Background(), "loop")
	if !errors.Is(err, ErrMaxTurns) {
		t.Fatalf("Run() error = %v, want ErrMaxTurns", err)
	}
	transcript := agent.Transcript()
	if len(transcript) != 3 {
		t.Fatalf("transcript messages = %d, want 3", len(transcript))
	}
	if transcript[2].Role != "tool" || transcript[2].ToolCallID != "call_1" {
		t.Fatalf("last transcript message = %#v", transcript[2])
	}
}

func TestAgentReportsProviderFailure(t *testing.T) {
	want := errors.New("provider unavailable")
	provider := &fakeProvider{err: want}
	var event Event
	agent := NewAgent(provider, "", nil, 1, func(got Event) {
		event = got
	})

	_, err := agent.Run(context.Background(), "hello")
	if !errors.Is(err, want) {
		t.Fatalf("Run() error = %v, want %v", err, want)
	}
	if event.Kind != EventError || !errors.Is(event.Err, want) {
		t.Fatalf("event = %#v", event)
	}
}

func TestAgentDoesNotTreatLengthLimitAsDone(t *testing.T) {
	provider := &fakeProvider{responses: []Message{{
		Role:       "assistant",
		Content:    "partial response",
		StopReason: "length",
	}}}
	var events []Event
	agent := NewAgent(provider, "", nil, 5, func(event Event) {
		events = append(events, event)
	})

	got, err := agent.Run(context.Background(), "write a long answer")
	if err == nil || !strings.Contains(err.Error(), "length") {
		t.Fatalf("Run() error = %v, want length error", err)
	}
	if got != "partial response" {
		t.Fatalf("Run() text = %q, want partial response", got)
	}
	if len(events) != 2 || events[0].Kind != EventAssistantText || events[1].Kind != EventError {
		t.Fatalf("events = %#v, want assistant text then error", events)
	}
}

func TestAgentSkipsRemainingToolsAfterCancellationAndPairsResults(t *testing.T) {
	provider := &fakeProvider{responses: []Message{{
		Role: "assistant",
		ToolCalls: []ToolCall{
			{
				ID:       "cancel_1",
				Type:     "function",
				Function: FunctionCall{Name: "cancel", Arguments: `{}`},
			},
			{
				ID:       "mutate_1",
				Type:     "function",
				Function: FunctionCall{Name: "mutate", Arguments: `{}`},
			},
		},
	}}}
	ctx, cancel := context.WithCancel(context.Background())
	mutated := false
	tools := map[string]Tool{
		"cancel": {
			Name:       "cancel",
			Parameters: objectSchema(nil),
			Run: func(context.Context, json.RawMessage) (string, error) {
				cancel()
				return "canceled", nil
			},
		},
		"mutate": {
			Name:       "mutate",
			Parameters: objectSchema(nil),
			Run: func(context.Context, json.RawMessage) (string, error) {
				mutated = true
				return "mutated", nil
			},
		},
	}
	agent := NewAgent(provider, "", tools, 5, nil)

	_, err := agent.Run(ctx, "cancel this turn")
	if !errors.Is(err, context.Canceled) {
		t.Fatalf("Run() error = %v, want context.Canceled", err)
	}
	if mutated {
		t.Fatal("tool after cancellation was executed")
	}

	transcript := agent.Transcript()
	if len(transcript) != 4 {
		t.Fatalf("transcript messages = %d, want 4", len(transcript))
	}
	if transcript[2].ToolCallID != "cancel_1" || transcript[3].ToolCallID != "mutate_1" {
		t.Fatalf("tool result IDs = %q, %q", transcript[2].ToolCallID, transcript[3].ToolCallID)
	}
	if !strings.Contains(transcript[3].Content, "canceled") {
		t.Fatalf("skipped tool result = %q", transcript[3].Content)
	}
}
