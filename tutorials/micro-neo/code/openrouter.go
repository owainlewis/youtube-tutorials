package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

const openRouterEndpoint = "https://openrouter.ai/api/v1/chat/completions"

type OpenRouter struct {
	APIKey     string
	Model      string
	Endpoint   string
	HTTPClient *http.Client
}

type chatRequest struct {
	Model             string           `json:"model"`
	Messages          []Message        `json:"messages"`
	Tools             []ToolDefinition `json:"tools"`
	ParallelToolCalls bool             `json:"parallel_tool_calls"`
}

type chatResponse struct {
	Choices []struct {
		Message      Message   `json:"message"`
		FinishReason string    `json:"finish_reason"`
		Error        *apiError `json:"error,omitempty"`
	} `json:"choices"`
	Error *apiError `json:"error,omitempty"`
}

type apiError struct {
	Code    json.RawMessage `json:"code,omitempty"`
	Message string          `json:"message"`
}

func (o OpenRouter) Complete(
	ctx context.Context,
	system string,
	messages []Message,
	tools []ToolDefinition,
) (Message, error) {
	endpoint := o.Endpoint
	if endpoint == "" {
		endpoint = openRouterEndpoint
	}
	client := o.HTTPClient
	if client == nil {
		client = &http.Client{Timeout: 2 * time.Minute}
	}

	requestMessages := make([]Message, 0, len(messages)+1)
	if strings.TrimSpace(system) != "" {
		requestMessages = append(requestMessages, Message{Role: "system", Content: system})
	}
	requestMessages = append(requestMessages, messages...)

	payload, err := json.Marshal(chatRequest{
		Model:             o.Model,
		Messages:          requestMessages,
		Tools:             tools,
		ParallelToolCalls: false,
	})
	if err != nil {
		return Message{}, fmt.Errorf("encode OpenRouter request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint, bytes.NewReader(payload))
	if err != nil {
		return Message{}, fmt.Errorf("create OpenRouter request: %w", err)
	}
	req.Header.Set("Authorization", "Bearer "+o.APIKey)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("HTTP-Referer", "https://github.com/owainlewis/youtube-tutorials/tree/main/tutorials/micro-neo")
	req.Header.Set("X-OpenRouter-Title", "Micro Neo")

	resp, err := client.Do(req)
	if err != nil {
		return Message{}, fmt.Errorf("call OpenRouter: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(io.LimitReader(resp.Body, 10<<20))
	if err != nil {
		return Message{}, fmt.Errorf("read OpenRouter response: %w", err)
	}

	var decoded chatResponse
	if err := json.Unmarshal(body, &decoded); err != nil {
		if resp.StatusCode < http.StatusOK || resp.StatusCode >= http.StatusMultipleChoices {
			return Message{}, fmt.Errorf("OpenRouter returned %s: %s", resp.Status, capText(string(body), 4<<10))
		}
		return Message{}, fmt.Errorf("decode OpenRouter response: %w", err)
	}

	if resp.StatusCode < http.StatusOK || resp.StatusCode >= http.StatusMultipleChoices {
		return Message{}, openRouterError(resp.Status, decoded.Error)
	}
	if decoded.Error != nil {
		return Message{}, openRouterError(resp.Status, decoded.Error)
	}
	if len(decoded.Choices) == 0 {
		return Message{}, errors.New("OpenRouter returned no choices")
	}
	if decoded.Choices[0].Error != nil {
		return Message{}, openRouterError(resp.Status, decoded.Choices[0].Error)
	}

	message := decoded.Choices[0].Message
	message.StopReason = decoded.Choices[0].FinishReason
	return message, nil
}

func openRouterError(status string, apiErr *apiError) error {
	if apiErr == nil || strings.TrimSpace(apiErr.Message) == "" {
		return fmt.Errorf("OpenRouter returned %s", status)
	}
	return fmt.Errorf("OpenRouter returned %s: %s", status, apiErr.Message)
}
