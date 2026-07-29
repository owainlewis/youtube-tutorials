package main

import (
	"fmt"
	"io"
	"os"
	"strings"
)

const (
	ansiReset = "\x1b[0m"
	ansiBold  = "\x1b[1m"
	ansiDim   = "\x1b[2m"
	ansiBlue  = "\x1b[34m"
	ansiGreen = "\x1b[32m"
	ansiRed   = "\x1b[31m"
)

type Renderer struct {
	writer io.Writer
	color  bool
}

func NewRenderer(writer io.Writer) *Renderer {
	renderer := &Renderer{writer: writer}
	if file, ok := writer.(*os.File); ok {
		if info, err := file.Stat(); err == nil {
			renderer.color = info.Mode()&os.ModeCharDevice != 0 && os.Getenv("NO_COLOR") == ""
		}
	}
	return renderer
}

func (r *Renderer) Banner(model, workspace string) {
	fmt.Fprintf(r.writer, "%sMicro Neo%s\n", r.style(ansiBold+ansiBlue), r.style(ansiReset))
	fmt.Fprintf(r.writer, "%smodel%s      %s\n", r.style(ansiDim), r.style(ansiReset), model)
	fmt.Fprintf(r.writer, "%sworkspace%s  %s\n\n", r.style(ansiDim), r.style(ansiReset), workspace)
}

func (r *Renderer) Prompt() {
	fmt.Fprintf(r.writer, "%s›%s ", r.style(ansiBold+ansiBlue), r.style(ansiReset))
}

func (r *Renderer) Handle(event Event) {
	switch event.Kind {
	case EventAssistantText:
		fmt.Fprintln(r.writer)
		fmt.Fprintln(r.writer, strings.TrimSpace(event.Text))
	case EventToolStart:
		fmt.Fprintf(
			r.writer,
			"\n%s→%s %s %s\n",
			r.style(ansiBlue),
			r.style(ansiReset),
			event.ToolName,
			compactArguments(event.Arguments),
		)
	case EventToolFinish:
		if event.ToolError {
			fmt.Fprintf(
				r.writer,
				"%s×%s %s %s\n",
				r.style(ansiRed),
				r.style(ansiReset),
				event.ToolName,
				event.Duration.Round(1_000_000),
			)
			fmt.Fprintln(r.writer, indent(event.Result))
			return
		}
		fmt.Fprintf(
			r.writer,
			"%s✓%s %s %s\n",
			r.style(ansiGreen),
			r.style(ansiReset),
			event.ToolName,
			event.Duration.Round(1_000_000),
		)
	case EventDone:
		fmt.Fprintf(r.writer, "\n%s✓ Done%s\n", r.style(ansiBold+ansiGreen), r.style(ansiReset))
	case EventError:
		fmt.Fprintf(r.writer, "\n%sError:%s %v\n", r.style(ansiBold+ansiRed), r.style(ansiReset), event.Err)
	}
}

func (r *Renderer) style(code string) string {
	if !r.color {
		return ""
	}
	return code
}

func compactArguments(arguments string) string {
	arguments = strings.Join(strings.Fields(arguments), " ")
	const limit = 120
	if len(arguments) <= limit {
		return arguments
	}
	return arguments[:limit-3] + "..."
}

func indent(text string) string {
	lines := strings.Split(strings.TrimSpace(text), "\n")
	for index := range lines {
		lines[index] = "  " + lines[index]
	}
	return strings.Join(lines, "\n")
}
