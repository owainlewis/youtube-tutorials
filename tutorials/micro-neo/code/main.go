package main

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"
)

const (
	defaultModel       = "anthropic/claude-sonnet-4.6"
	openRouterEndpoint = "https://openrouter.ai/api/v1/chat/completions"
	maxFileBytes       = 64 << 10
	maxToolResultBytes = 32 << 10

	systemPrompt = `You are Micro Neo, a focused coding agent.

Work in the current workspace. Inspect relevant files before making changes.
Prefer small, targeted edits. Run relevant tests after changing code.
Use relative file paths with the provided tools.

Before tool calls, briefly explain what you are checking or changing.
When the task is complete, summarize the changes and verification.`
)

// MODEL MESSAGES

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

type Provider interface {
	Complete(context.Context, string, []Message, []ToolDefinition) (Message, error)
}

// AGENT LOOP

var ErrMaxTurns = errors.New("maximum agent turns reached")

type Event struct {
	Kind      string
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

func NewAgent(provider Provider, tools map[string]Tool, onEvent func(Event)) *Agent {
	return &Agent{
		provider: provider,
		system:   systemPrompt,
		tools:    tools,
		maxTurns: 50,
		onEvent:  onEvent,
	}
}

func (a *Agent) Run(ctx context.Context, prompt string) (string, error) {
	a.transcript = append(a.transcript, Message{Role: "user", Content: prompt})

	for turn := 0; turn < a.maxTurns; turn++ {
		response, err := a.provider.Complete(ctx, a.system, a.transcript, a.toolDefinitions())
		if err != nil {
			a.emit(Event{Kind: "error", Err: err})
			return "", err
		}
		if response.Role == "" {
			response.Role = "assistant"
		}
		a.transcript = append(a.transcript, response)

		if strings.TrimSpace(response.Content) != "" {
			a.emit(Event{Kind: "assistant_text", Text: response.Content})
		}

		if len(response.ToolCalls) == 0 {
			if response.StopReason != "" && response.StopReason != "stop" {
				err := fmt.Errorf("model stopped before completing the turn: %s", response.StopReason)
				a.emit(Event{Kind: "error", Err: err})
				return strings.TrimSpace(response.Content), err
			}
			if strings.TrimSpace(response.Content) == "" {
				err := errors.New("model returned no text or tool calls")
				a.emit(Event{Kind: "error", Err: err})
				return "", err
			}
			a.emit(Event{Kind: "done"})
			return strings.TrimSpace(response.Content), nil
		}

		for _, call := range response.ToolCalls {
			a.emit(Event{
				Kind:      "tool_start",
				ToolName:  call.Function.Name,
				Arguments: call.Function.Arguments,
			})

			started := time.Now()
			result, toolErr := a.runTool(ctx, call)
			result = capText(result, maxToolResultBytes)
			a.emit(Event{
				Kind:      "tool_finish",
				ToolName:  call.Function.Name,
				Result:    result,
				Duration:  time.Since(started),
				ToolError: toolErr != nil,
			})

			// Every tool call gets a result with the matching call ID.
			a.transcript = append(a.transcript, Message{
				Role:       "tool",
				ToolCallID: call.ID,
				Content:    result,
			})
		}

		if err := ctx.Err(); err != nil {
			a.emit(Event{Kind: "error", Err: err})
			return "", err
		}
	}

	a.emit(Event{Kind: "error", Err: ErrMaxTurns})
	return "", ErrMaxTurns
}

func (a *Agent) runTool(ctx context.Context, call ToolCall) (result string, err error) {
	if err := ctx.Err(); err != nil {
		return "error: skipped because the active turn was canceled", err
	}
	tool, ok := a.tools[call.Function.Name]
	if !ok {
		return fmt.Sprintf("error: unknown tool %q", call.Function.Name), errors.New("unknown tool")
	}

	defer func() {
		if recovered := recover(); recovered != nil {
			err = fmt.Errorf("tool panicked: %v", recovered)
			result = "error: " + err.Error()
		}
	}()

	output, runErr := tool.Run(ctx, json.RawMessage(call.Function.Arguments))
	if runErr == nil {
		return output, nil
	}
	if output == "" {
		return "error: " + runErr.Error(), runErr
	}
	return fmt.Sprintf("error: %v\n%s", runErr, output), runErr
}

func (a *Agent) toolDefinitions() []ToolDefinition {
	names := make([]string, 0, len(a.tools))
	for name := range a.tools {
		names = append(names, name)
	}
	sort.Strings(names)

	definitions := make([]ToolDefinition, 0, len(names))
	for _, name := range names {
		tool := a.tools[name]
		definitions = append(definitions, ToolDefinition{
			Type: "function",
			Function: FunctionDefinition{
				Name:        tool.Name,
				Description: tool.Description,
				Parameters:  tool.Parameters,
			},
		})
	}
	return definitions
}

func (a *Agent) emit(event Event) {
	if a.onEvent != nil {
		a.onEvent(event)
	}
}

// OPENROUTER

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
		Message      Message `json:"message"`
		FinishReason string  `json:"finish_reason"`
		Error        *struct {
			Message string `json:"message"`
		} `json:"error,omitempty"`
	} `json:"choices"`
	Error *struct {
		Message string `json:"message"`
	} `json:"error,omitempty"`
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

	allMessages := append([]Message{{Role: "system", Content: system}}, messages...)
	body, err := json.Marshal(chatRequest{
		Model:             o.Model,
		Messages:          allMessages,
		Tools:             tools,
		ParallelToolCalls: false,
	})
	if err != nil {
		return Message{}, err
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, endpoint, bytes.NewReader(body))
	if err != nil {
		return Message{}, err
	}
	req.Header.Set("Authorization", "Bearer "+o.APIKey)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("HTTP-Referer", "https://github.com/owainlewis/youtube-tutorials")
	req.Header.Set("X-OpenRouter-Title", "Micro Neo")

	resp, err := client.Do(req)
	if err != nil {
		return Message{}, fmt.Errorf("call OpenRouter: %w", err)
	}
	defer resp.Body.Close()

	responseBody, err := io.ReadAll(io.LimitReader(resp.Body, 10<<20))
	if err != nil {
		return Message{}, err
	}
	var decoded chatResponse
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		if json.Unmarshal(responseBody, &decoded) == nil && decoded.Error != nil {
			return Message{}, fmt.Errorf("OpenRouter returned %s: %s", resp.Status, decoded.Error.Message)
		}
		return Message{}, fmt.Errorf("OpenRouter returned %s", resp.Status)
	}
	if err := json.Unmarshal(responseBody, &decoded); err != nil {
		return Message{}, fmt.Errorf("decode OpenRouter response: %w", err)
	}
	if decoded.Error != nil {
		return Message{}, errors.New(decoded.Error.Message)
	}
	if len(decoded.Choices) == 0 {
		return Message{}, errors.New("OpenRouter returned no choices")
	}
	if decoded.Choices[0].Error != nil {
		return Message{}, errors.New(decoded.Choices[0].Error.Message)
	}

	message := decoded.Choices[0].Message
	message.StopReason = decoded.Choices[0].FinishReason
	return message, nil
}

// TOOLS

func NewTools(workspace string) (map[string]Tool, error) {
	root, err := filepath.Abs(workspace)
	if err != nil {
		return nil, err
	}
	info, err := os.Stat(root)
	if err != nil {
		return nil, err
	}
	if !info.IsDir() {
		return nil, fmt.Errorf("workspace is not a directory: %s", root)
	}
	root, err = filepath.EvalSymlinks(root)
	if err != nil {
		return nil, err
	}

	return map[string]Tool{
		"read_file": {
			Name:        "read_file",
			Description: "Read a text file from the workspace. Use a relative path.",
			Parameters: objectSchema(map[string]any{
				"path": stringProperty("Path relative to the workspace"),
			}, "path"),
			Run: func(_ context.Context, raw json.RawMessage) (string, error) {
				var args struct {
					Path string `json:"path"`
				}
				if err := decodeArguments(raw, &args); err != nil {
					return "", err
				}
				path, err := workspacePath(root, args.Path)
				if err != nil {
					return "", err
				}
				content, size, truncated, _, err := readBoundedFile(path, maxFileBytes)
				if err != nil {
					return "", err
				}
				if truncated {
					return truncatedPrefix(content, size, maxFileBytes), nil
				}
				return string(content), nil
			},
		},
		"edit_file": {
			Name:        "edit_file",
			Description: "Replace exactly one occurrence of old_text in a workspace file.",
			Parameters: objectSchema(map[string]any{
				"path":     stringProperty("Path relative to the workspace"),
				"old_text": stringProperty("Exact text to replace"),
				"new_text": stringProperty("Replacement text"),
			}, "path", "old_text", "new_text"),
			Run: func(_ context.Context, raw json.RawMessage) (string, error) {
				var args struct {
					Path    string  `json:"path"`
					OldText string  `json:"old_text"`
					NewText *string `json:"new_text"`
				}
				if err := decodeArguments(raw, &args); err != nil {
					return "", err
				}
				if args.OldText == "" || args.NewText == nil {
					return "", errors.New("old_text and new_text are required")
				}
				path, err := workspacePath(root, args.Path)
				if err != nil {
					return "", err
				}
				content, _, truncated, mode, err := readBoundedFile(path, maxFileBytes)
				if err != nil {
					return "", err
				}
				if truncated {
					return "", fmt.Errorf("file is too large to edit: limit is %d bytes", maxFileBytes)
				}
				if count := strings.Count(string(content), args.OldText); count != 1 {
					return "", fmt.Errorf("old_text must match once, found %d matches", count)
				}
				updated := strings.Replace(string(content), args.OldText, *args.NewText, 1)
				if err := os.WriteFile(path, []byte(updated), mode.Perm()); err != nil {
					return "", err
				}
				relative, _ := filepath.Rel(root, path)
				return "updated " + filepath.ToSlash(relative), nil
			},
		},
		"run_command": {
			Name:        "run_command",
			Description: "Run a shell command with the workspace as its working directory.",
			Parameters: objectSchema(map[string]any{
				"command": stringProperty("Shell command to run"),
			}, "command"),
			Run: func(ctx context.Context, raw json.RawMessage) (string, error) {
				var args struct {
					Command string `json:"command"`
				}
				if err := decodeArguments(raw, &args); err != nil {
					return "", err
				}
				if strings.TrimSpace(args.Command) == "" {
					return "", errors.New("command is required")
				}
				return runCommand(ctx, root, args.Command)
			},
		},
	}, nil
}

func objectSchema(properties map[string]any, required ...string) map[string]any {
	return map[string]any{
		"type":                 "object",
		"properties":           properties,
		"required":             required,
		"additionalProperties": false,
	}
}

func stringProperty(description string) map[string]any {
	return map[string]any{"type": "string", "description": description}
}

func decodeArguments(raw json.RawMessage, target any) error {
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(target); err != nil {
		return fmt.Errorf("invalid tool arguments: %w", err)
	}
	if err := decoder.Decode(&struct{}{}); !errors.Is(err, io.EOF) {
		return errors.New("invalid tool arguments: expected one JSON object")
	}
	return nil
}

func workspacePath(root, requested string) (string, error) {
	if requested == "" || filepath.IsAbs(requested) {
		return "", errors.New("path must be relative to the workspace")
	}
	resolved, err := filepath.EvalSymlinks(filepath.Join(root, filepath.Clean(requested)))
	if err != nil {
		return "", err
	}
	relative, err := filepath.Rel(root, resolved)
	if err != nil || relative == ".." || strings.HasPrefix(relative, ".."+string(filepath.Separator)) {
		return "", errors.New("path escapes the workspace")
	}
	return resolved, nil
}

func readBoundedFile(path string, limit int) ([]byte, int64, bool, os.FileMode, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, 0, false, 0, err
	}
	defer file.Close()

	info, err := file.Stat()
	if err != nil || !info.Mode().IsRegular() {
		return nil, 0, false, 0, fmt.Errorf("not a regular file: %s", path)
	}
	content, err := io.ReadAll(io.LimitReader(file, int64(limit)+1))
	if err != nil {
		return nil, 0, false, 0, err
	}
	truncated := len(content) > limit || info.Size() > int64(limit)
	if len(content) > limit {
		content = content[:limit]
	}
	return content, info.Size(), truncated, info.Mode(), nil
}

func runCommand(ctx context.Context, root, command string) (string, error) {
	commandCtx, cancel := context.WithTimeout(ctx, 2*time.Minute)
	defer cancel()

	output := &boundedOutput{limit: maxToolResultBytes}
	cmd := exec.CommandContext(commandCtx, "/bin/bash", "-lc", command)
	cmd.Dir = root
	cmd.Stdout = output
	cmd.Stderr = output
	err := cmd.Run()

	if commandCtx.Err() != nil {
		return output.String(), commandCtx.Err()
	}
	if err == nil {
		if output.String() == "" {
			return "command completed successfully", nil
		}
		return output.String(), nil
	}
	var exitErr *exec.ExitError
	if errors.As(err, &exitErr) {
		return output.String(), fmt.Errorf("command exited with code %d", exitErr.ExitCode())
	}
	return output.String(), err
}

type boundedOutput struct {
	mu    sync.Mutex
	data  []byte
	limit int
	total int
}

func (b *boundedOutput) Write(p []byte) (int, error) {
	b.mu.Lock()
	defer b.mu.Unlock()

	written := len(p)
	b.total += written
	if remaining := b.limit - len(b.data); remaining > 0 {
		if len(p) > remaining {
			p = p[:remaining]
		}
		b.data = append(b.data, p...)
	}
	return written, nil
}

func (b *boundedOutput) String() string {
	b.mu.Lock()
	defer b.mu.Unlock()

	if b.total <= len(b.data) {
		return string(b.data)
	}
	return truncatedPrefix(b.data, int64(b.total), b.limit)
}

func truncatedPrefix(content []byte, total int64, limit int) string {
	marker := "\n\n[truncated from " + strconv.FormatInt(total, 10) + " bytes]\n"
	contentLimit := limit - len(marker)
	if contentLimit < 0 {
		return marker[:limit]
	}
	if len(content) > contentLimit {
		content = content[:contentLimit]
	}
	return string(content) + marker
}

func capText(text string, limit int) string {
	if len(text) <= limit {
		return text
	}
	return truncatedPrefix([]byte(text), int64(len(text)), limit)
}

// TERMINAL UI

type Renderer struct {
	writer io.Writer
	color  bool
}

func NewRenderer(writer io.Writer) *Renderer {
	renderer := &Renderer{writer: writer}
	if file, ok := writer.(*os.File); ok {
		info, err := file.Stat()
		renderer.color = err == nil && info.Mode()&os.ModeCharDevice != 0 && os.Getenv("NO_COLOR") == ""
	}
	return renderer
}

func (r *Renderer) Banner(model, workspace string) {
	fmt.Fprintf(r.writer, "%sMicro Neo%s\n", r.style("\x1b[1;34m"), r.style("\x1b[0m"))
	fmt.Fprintf(r.writer, "model      %s\nworkspace  %s\n\n", model, workspace)
}

func (r *Renderer) Prompt() {
	fmt.Fprintf(r.writer, "%s›%s ", r.style("\x1b[1;34m"), r.style("\x1b[0m"))
}

func (r *Renderer) Handle(event Event) {
	switch event.Kind {
	case "assistant_text":
		fmt.Fprintln(r.writer, "\n"+strings.TrimSpace(event.Text))
	case "tool_start":
		fmt.Fprintf(r.writer, "\n%s→%s %s %s\n", r.style("\x1b[34m"), r.style("\x1b[0m"),
			event.ToolName, capText(strings.Join(strings.Fields(event.Arguments), " "), 120))
	case "tool_finish":
		if event.ToolError {
			fmt.Fprintf(r.writer, "%s×%s %s %s\n  %s\n", r.style("\x1b[31m"), r.style("\x1b[0m"),
				event.ToolName, event.Duration.Round(time.Millisecond), strings.TrimSpace(event.Result))
		} else {
			fmt.Fprintf(r.writer, "%s✓%s %s %s\n", r.style("\x1b[32m"), r.style("\x1b[0m"),
				event.ToolName, event.Duration.Round(time.Millisecond))
		}
	case "done":
		fmt.Fprintf(r.writer, "\n%s✓ Done%s\n", r.style("\x1b[1;32m"), r.style("\x1b[0m"))
	case "error":
		fmt.Fprintf(r.writer, "\n%sError:%s %v\n", r.style("\x1b[1;31m"), r.style("\x1b[0m"), event.Err)
	}
}

func (r *Renderer) style(code string) string {
	if r.color {
		return code
	}
	return ""
}

// PROGRAM

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func run() error {
	model := flag.String("model", envOr("OPENROUTER_MODEL", defaultModel), "OpenRouter model slug")
	workspace := flag.String("workspace", ".", "workspace available to Micro Neo")
	flag.Parse()

	apiKey := strings.TrimSpace(os.Getenv("OPENROUTER_API_KEY"))
	if apiKey == "" {
		return errors.New("OPENROUTER_API_KEY is required")
	}
	root, err := filepath.Abs(*workspace)
	if err != nil {
		return err
	}
	tools, err := NewTools(root)
	if err != nil {
		return err
	}

	renderer := NewRenderer(os.Stdout)
	agent := NewAgent(OpenRouter{APIKey: apiKey, Model: *model}, tools, renderer.Handle)
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	renderer.Banner(*model, root)

	if prompt := strings.TrimSpace(strings.Join(flag.Args(), " ")); prompt != "" {
		_, err := agent.Run(ctx, prompt)
		return err
	}

	scanner := bufio.NewScanner(os.Stdin)
	for {
		renderer.Prompt()
		if !scanner.Scan() {
			return scanner.Err()
		}
		prompt := strings.TrimSpace(scanner.Text())
		if prompt == "/exit" || prompt == "/quit" {
			return nil
		}
		if prompt != "" {
			_, err := agent.Run(ctx, prompt)
			if errors.Is(err, context.Canceled) {
				return nil
			}
			fmt.Fprintln(os.Stdout)
		}
	}
}

func envOr(name, fallback string) string {
	if value := strings.TrimSpace(os.Getenv(name)); value != "" {
		return value
	}
	return fallback
}
