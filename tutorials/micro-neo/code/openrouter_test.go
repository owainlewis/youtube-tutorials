package main

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestOpenRouterSendsChatCompletionRequest(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if got := request.Header.Get("Authorization"); got != "Bearer secret" {
			t.Errorf("Authorization = %q", got)
		}
		if got := request.Header.Get("X-OpenRouter-Title"); got != "Micro Neo" {
			t.Errorf("X-OpenRouter-Title = %q", got)
		}

		var payload chatRequest
		if err := json.NewDecoder(request.Body).Decode(&payload); err != nil {
			t.Fatal(err)
		}
		if payload.Model != "test/model" {
			t.Errorf("model = %q", payload.Model)
		}
		if payload.ParallelToolCalls {
			t.Error("parallel_tool_calls = true, want false")
		}
		if len(payload.Messages) != 2 || payload.Messages[0].Role != "system" {
			t.Errorf("messages = %#v", payload.Messages)
		}
		if len(payload.Tools) != 1 || payload.Tools[0].Function.Name != "read_file" {
			t.Errorf("tools = %#v", payload.Tools)
		}

		writer.Header().Set("Content-Type", "application/json")
		_, _ = writer.Write([]byte(`{
			"choices": [{
				"finish_reason": "tool_calls",
				"message": {
					"role": "assistant",
					"content": null,
					"tool_calls": [{
						"id": "call_1",
						"type": "function",
						"function": {
							"name": "read_file",
							"arguments": "{\"path\":\"main.go\"}"
						}
					}]
				}
			}]
		}`))
	}))
	defer server.Close()

	client := OpenRouter{
		APIKey:     "secret",
		Model:      "test/model",
		Endpoint:   server.URL,
		HTTPClient: server.Client(),
	}
	got, err := client.Complete(
		context.Background(),
		"system prompt",
		[]Message{{Role: "user", Content: "hello"}},
		[]ToolDefinition{{
			Type: "function",
			Function: FunctionDefinition{
				Name:       "read_file",
				Parameters: objectSchema(nil),
			},
		}},
	)
	if err != nil {
		t.Fatal(err)
	}
	if len(got.ToolCalls) != 1 || got.ToolCalls[0].ID != "call_1" {
		t.Fatalf("response = %#v", got)
	}
	if got.StopReason != "tool_calls" {
		t.Fatalf("stop reason = %q, want tool_calls", got.StopReason)
	}
}

func TestOpenRouterKeepsEmptyToolResultContentOnWire(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		var payload struct {
			Messages []map[string]any `json:"messages"`
		}
		if err := json.NewDecoder(request.Body).Decode(&payload); err != nil {
			t.Fatal(err)
		}
		last := payload.Messages[len(payload.Messages)-1]
		content, exists := last["content"]
		if !exists {
			t.Error("empty tool result omitted the content field")
		}
		if content != "" {
			t.Errorf("tool result content = %#v, want empty string", content)
		}
		assistant := payload.Messages[len(payload.Messages)-2]
		if assistant["reasoning"] != "inspect the empty file" {
			t.Errorf("assistant reasoning = %#v", assistant["reasoning"])
		}
		details, ok := assistant["reasoning_details"].([]any)
		if !ok || len(details) != 1 {
			t.Errorf("assistant reasoning_details = %#v", assistant["reasoning_details"])
		}

		writer.Header().Set("Content-Type", "application/json")
		_, _ = writer.Write([]byte(`{
			"choices": [{
				"finish_reason": "stop",
				"message": {"role": "assistant", "content": "done"}
			}]
		}`))
	}))
	defer server.Close()

	client := OpenRouter{
		APIKey:     "secret",
		Model:      "test/model",
		Endpoint:   server.URL,
		HTTPClient: server.Client(),
	}
	_, err := client.Complete(context.Background(), "", []Message{
		{
			Role:             "assistant",
			Reasoning:        "inspect the empty file",
			ReasoningDetails: json.RawMessage(`[{"type":"reasoning.text","text":"inspect","index":0}]`),
			ToolCalls: []ToolCall{{
				ID:       "call_1",
				Type:     "function",
				Function: FunctionCall{Name: "read_file", Arguments: `{"path":"empty.txt"}`},
			}},
		},
		{Role: "tool", ToolCallID: "call_1", Content: ""},
	}, nil)
	if err != nil {
		t.Fatal(err)
	}
}

func TestOpenRouterReturnsStructuredAPIError(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		writer.WriteHeader(http.StatusTooManyRequests)
		_, _ = writer.Write([]byte(`{"error":{"code":429,"message":"rate limited"}}`))
	}))
	defer server.Close()

	client := OpenRouter{
		APIKey:     "secret",
		Model:      "test/model",
		Endpoint:   server.URL,
		HTTPClient: server.Client(),
	}
	_, err := client.Complete(context.Background(), "", nil, nil)
	if err == nil || !strings.Contains(err.Error(), "rate limited") {
		t.Fatalf("Complete() error = %v", err)
	}
}

func TestOpenRouterRejectsEmptyChoices(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		_, _ = writer.Write([]byte(`{"choices":[]}`))
	}))
	defer server.Close()

	client := OpenRouter{
		APIKey:     "secret",
		Model:      "test/model",
		Endpoint:   server.URL,
		HTTPClient: server.Client(),
	}
	_, err := client.Complete(context.Background(), "", nil, nil)
	if err == nil || !strings.Contains(err.Error(), "no choices") {
		t.Fatalf("Complete() error = %v", err)
	}
}
