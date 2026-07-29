package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"sort"
	"strings"
	"time"
)

var ErrMaxTurns = errors.New("maximum agent turns reached")

type Message struct {
	Role             string          `json:"role"`
	Content          string          `json:"content"`
	ToolCalls        []ToolCall      `json:"tool_calls,omitempty"`
	ToolCallID       string          `json:"tool_call_id,omitempty"`
	Reasoning        string          `json:"reasoning,omitempty"`
	ReasoningDetails json.RawMessage `json:"reasoning_details,omitempty"`
	StopReason       string          `json:"-"`
}

type ToolCall struct {
	ID       string       `json:"id"`
	Type     string       `json:"type"`
	Function FunctionCall `json:"function"`
}

type FunctionCall struct {
	Name      string `json:"name"`
	Arguments string `json:"arguments"`
}

type ToolDefinition struct {
	Type     string             `json:"type"`
	Function FunctionDefinition `json:"function"`
}

type FunctionDefinition struct {
	Name        string         `json:"name"`
	Description string         `json:"description"`
	Parameters  map[string]any `json:"parameters"`
}

type Tool struct {
	Name        string
	Description string
	Parameters  map[string]any
	Run         func(context.Context, json.RawMessage) (string, error)
}

func (t Tool) Definition() ToolDefinition {
	return ToolDefinition{
		Type: "function",
		Function: FunctionDefinition{
			Name:        t.Name,
			Description: t.Description,
			Parameters:  t.Parameters,
		},
	}
}

type Provider interface {
	Complete(context.Context, string, []Message, []ToolDefinition) (Message, error)
}

type EventKind string

const (
	EventAssistantText EventKind = "assistant_text"
	EventToolStart     EventKind = "tool_start"
	EventToolFinish    EventKind = "tool_finish"
	EventDone          EventKind = "done"
	EventError         EventKind = "error"
)

type Event struct {
	Kind      EventKind
	Text      string
	ToolName  string
	Arguments string
	Result    string
	Duration  time.Duration
	ToolError bool
	Err       error
}

type Agent struct {
	provider   Provider
	system     string
	tools      map[string]Tool
	maxTurns   int
	onEvent    func(Event)
	transcript []Message
}

func NewAgent(provider Provider, system string, tools map[string]Tool, maxTurns int, onEvent func(Event)) *Agent {
	if maxTurns <= 0 {
		maxTurns = 50
	}
	if tools == nil {
		tools = map[string]Tool{}
	}
	return &Agent{
		provider: provider,
		system:   system,
		tools:    tools,
		maxTurns: maxTurns,
		onEvent:  onEvent,
	}
}

func (a *Agent) Run(ctx context.Context, prompt string) (string, error) {
	prompt = strings.TrimSpace(prompt)
	if prompt == "" {
		return "", nil
	}

	a.transcript = append(a.transcript, Message{Role: "user", Content: prompt})

	for turn := 0; turn < a.maxTurns; turn++ {
		response, err := a.provider.Complete(ctx, a.system, a.transcript, a.toolDefinitions())
		if err != nil {
			a.emit(Event{Kind: EventError, Err: err})
			return "", err
		}
		if response.Role == "" {
			response.Role = "assistant"
		}
		a.transcript = append(a.transcript, response)

		if strings.TrimSpace(response.Content) != "" {
			a.emit(Event{Kind: EventAssistantText, Text: response.Content})
		}

		if len(response.ToolCalls) == 0 {
			if response.StopReason != "" && response.StopReason != "stop" {
				err := fmt.Errorf("model stopped before completing the turn: %s", response.StopReason)
				a.emit(Event{Kind: EventError, Err: err})
				return strings.TrimSpace(response.Content), err
			}
			if strings.TrimSpace(response.Content) == "" {
				err := errors.New("model returned no text or tool calls")
				a.emit(Event{Kind: EventError, Err: err})
				return "", err
			}
			a.emit(Event{Kind: EventDone})
			return strings.TrimSpace(response.Content), nil
		}

		for _, call := range response.ToolCalls {
			a.emit(Event{
				Kind:      EventToolStart,
				ToolName:  call.Function.Name,
				Arguments: call.Function.Arguments,
			})

			started := time.Now()
			result, toolErr := a.runTool(ctx, call)
			result = capText(result, maxToolResultBytes)
			a.emit(Event{
				Kind:      EventToolFinish,
				ToolName:  call.Function.Name,
				Result:    result,
				Duration:  time.Since(started),
				ToolError: toolErr != nil,
			})

			a.transcript = append(a.transcript, Message{
				Role:       "tool",
				ToolCallID: call.ID,
				Content:    result,
			})
		}

		if err := ctx.Err(); err != nil {
			a.emit(Event{Kind: EventError, Err: err})
			return "", err
		}
	}

	a.emit(Event{Kind: EventError, Err: ErrMaxTurns})
	return "", ErrMaxTurns
}

func (a *Agent) Transcript() []Message {
	out := make([]Message, len(a.transcript))
	copy(out, a.transcript)
	for i := range out {
		out[i].ToolCalls = append([]ToolCall(nil), out[i].ToolCalls...)
	}
	return out
}

func (a *Agent) toolDefinitions() []ToolDefinition {
	names := make([]string, 0, len(a.tools))
	for name := range a.tools {
		names = append(names, name)
	}
	sort.Strings(names)

	definitions := make([]ToolDefinition, 0, len(names))
	for _, name := range names {
		definitions = append(definitions, a.tools[name].Definition())
	}
	return definitions
}

func (a *Agent) runTool(ctx context.Context, call ToolCall) (result string, err error) {
	if err := ctx.Err(); err != nil {
		return "error: skipped because the active turn was canceled", err
	}

	tool, ok := a.tools[call.Function.Name]
	if !ok {
		return fmt.Sprintf("error: unknown tool %q", call.Function.Name), errors.New("unknown tool")
	}

	arguments := json.RawMessage(call.Function.Arguments)
	if len(arguments) == 0 {
		arguments = json.RawMessage(`{}`)
	}

	defer func() {
		if recovered := recover(); recovered != nil {
			err = fmt.Errorf("tool panicked: %v", recovered)
			result = "error: " + err.Error()
		}
	}()

	output, runErr := tool.Run(ctx, arguments)
	if runErr != nil {
		if output == "" {
			return "error: " + runErr.Error(), runErr
		}
		return fmt.Sprintf("error: %v\n%s", runErr, output), runErr
	}
	return output, nil
}

func (a *Agent) emit(event Event) {
	if a.onEvent != nil {
		a.onEvent(event)
	}
}
