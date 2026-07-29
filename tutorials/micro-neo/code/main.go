package main

import (
	"bufio"
	"context"
	"errors"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"
)

const (
	defaultModel = "anthropic/claude-sonnet-4.6"
	systemPrompt = `You are Micro Neo, a focused coding agent.

Work in the current workspace. Inspect relevant files before making changes.
Prefer small, targeted edits. Run relevant tests after changing code.
Use relative file paths with the provided tools.

Before tool calls, briefly explain what you are checking or changing.
When the task is complete, summarize the changes and verification.`
)

func main() {
	if err := run(); err != nil {
		os.Exit(1)
	}
}

func run() error {
	modelDefault := os.Getenv("OPENROUTER_MODEL")
	if modelDefault == "" {
		modelDefault = defaultModel
	}

	model := flag.String("model", modelDefault, "OpenRouter model slug")
	workspace := flag.String("workspace", ".", "workspace available to Micro Neo")
	maxTurns := flag.Int("max-turns", 50, "maximum model turns")
	flag.Parse()

	apiKey := strings.TrimSpace(os.Getenv("OPENROUTER_API_KEY"))
	if apiKey == "" {
		fmt.Fprintln(os.Stderr, "OPENROUTER_API_KEY is required")
		return errors.New("missing OpenRouter API key")
	}

	absoluteWorkspace, err := filepath.Abs(*workspace)
	if err != nil {
		fmt.Fprintln(os.Stderr, "workspace:", err)
		return err
	}
	tools, err := NewTools(absoluteWorkspace)
	if err != nil {
		fmt.Fprintln(os.Stderr, "workspace:", err)
		return err
	}

	renderer := NewRenderer(os.Stdout)
	provider := OpenRouter{
		APIKey: apiKey,
		Model:  *model,
	}
	agent := NewAgent(provider, systemPrompt, tools, *maxTurns, renderer.Handle)

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	renderer.Banner(*model, absoluteWorkspace)

	if prompt := strings.TrimSpace(strings.Join(flag.Args(), " ")); prompt != "" {
		_, err := agent.Run(ctx, prompt)
		return err
	}

	scanner := bufio.NewScanner(os.Stdin)
	scanner.Buffer(make([]byte, 1<<10), 1<<20)
	for {
		renderer.Prompt()
		if !scanner.Scan() {
			fmt.Fprintln(os.Stdout)
			return scanner.Err()
		}
		prompt := strings.TrimSpace(scanner.Text())
		if prompt == "" {
			continue
		}
		if prompt == "/exit" || prompt == "/quit" {
			return nil
		}
		if _, err := agent.Run(ctx, prompt); err != nil {
			if ctx.Err() != nil {
				return ctx.Err()
			}
		}
		fmt.Fprintln(os.Stdout)
	}
}
