package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"time"
)

const (
	maxFileBytes       = 64 << 10
	maxSearchFileBytes = 1 << 20
	maxSearchMatches   = 100
	maxToolResultBytes = 32 << 10
)

func NewTools(workspace string) (map[string]Tool, error) {
	root, err := filepath.Abs(workspace)
	if err != nil {
		return nil, fmt.Errorf("resolve workspace: %w", err)
	}
	root, err = filepath.EvalSymlinks(root)
	if err != nil {
		return nil, fmt.Errorf("resolve workspace links: %w", err)
	}
	info, err := os.Stat(root)
	if err != nil {
		return nil, fmt.Errorf("open workspace: %w", err)
	}
	if !info.IsDir() {
		return nil, fmt.Errorf("workspace is not a directory: %s", root)
	}

	return map[string]Tool{
		"read_file": {
			Name:        "read_file",
			Description: "Read a UTF-8 text file from the workspace. Use a relative path.",
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
		"search": {
			Name:        "search",
			Description: "Search text files in the workspace for a literal string.",
			Parameters: objectSchema(map[string]any{
				"query": stringProperty("Literal text to find"),
			}, "query"),
			Run: func(_ context.Context, raw json.RawMessage) (string, error) {
				var args struct {
					Query string `json:"query"`
				}
				if err := decodeArguments(raw, &args); err != nil {
					return "", err
				}
				if args.Query == "" {
					return "", errors.New("query is required")
				}
				return searchWorkspace(root, args.Query)
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
				if args.OldText == "" {
					return "", errors.New("old_text must not be empty")
				}
				if args.NewText == nil {
					return "", errors.New("new_text is required")
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
					return "", fmt.Errorf("file is too large to edit safely: limit is %d bytes", maxFileBytes)
				}
				count := strings.Count(string(content), args.OldText)
				if count != 1 {
					return "", fmt.Errorf("old_text must match exactly once, found %d matches", count)
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
	return map[string]any{
		"type":        "string",
		"description": description,
	}
}

func decodeArguments(raw json.RawMessage, target any) error {
	if len(raw) == 0 {
		return errors.New("tool arguments are required")
	}
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(target); err != nil {
		return fmt.Errorf("invalid tool arguments: %w", err)
	}
	return nil
}

func workspacePath(root, requested string) (string, error) {
	if strings.TrimSpace(requested) == "" {
		return "", errors.New("path is required")
	}
	if filepath.IsAbs(requested) {
		return "", errors.New("path must be relative to the workspace")
	}

	candidate := filepath.Join(root, filepath.Clean(requested))
	resolved, err := filepath.EvalSymlinks(candidate)
	if err != nil {
		return "", err
	}
	if !pathWithin(root, resolved) {
		return "", errors.New("path escapes the workspace")
	}
	return resolved, nil
}

func pathWithin(root, candidate string) bool {
	relative, err := filepath.Rel(root, candidate)
	if err != nil {
		return false
	}
	return relative != ".." && !strings.HasPrefix(relative, ".."+string(filepath.Separator))
}

func readBoundedFile(path string, limit int) ([]byte, int64, bool, os.FileMode, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, 0, false, 0, err
	}
	defer file.Close()

	info, err := file.Stat()
	if err != nil {
		return nil, 0, false, 0, err
	}
	if !info.Mode().IsRegular() {
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

func truncatedPrefix(content []byte, total int64, limit int) string {
	marker := "\n\n[truncated from " + strconv.FormatInt(total, 10) + " bytes]\n"
	contentLimit := limit - len(marker)
	if contentLimit <= 0 {
		return marker[:limit]
	}
	if len(content) > contentLimit {
		content = content[:contentLimit]
	}
	return string(content) + marker
}

func searchWorkspace(root, query string) (string, error) {
	var matches []string
	err := filepath.WalkDir(root, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() {
			if path != root && (entry.Name() == ".git" || strings.HasPrefix(entry.Name(), ".")) {
				return filepath.SkipDir
			}
			return nil
		}
		if entry.Type()&os.ModeSymlink != 0 || !entry.Type().IsRegular() {
			return nil
		}
		info, err := entry.Info()
		if err != nil || info.Size() > maxSearchFileBytes {
			return nil
		}
		content, err := os.ReadFile(path)
		if err != nil || strings.IndexByte(string(content), 0) >= 0 {
			return nil
		}
		relative, _ := filepath.Rel(root, path)
		for index, line := range strings.Split(string(content), "\n") {
			if strings.Contains(line, query) {
				matches = append(matches, fmt.Sprintf(
					"%s:%d:%s",
					filepath.ToSlash(relative),
					index+1,
					strings.TrimSpace(line),
				))
				if len(matches) == maxSearchMatches {
					return fs.SkipAll
				}
			}
		}
		return nil
	})
	if err != nil {
		return "", err
	}
	if len(matches) == 0 {
		return "no matches found", nil
	}
	return strings.Join(matches, "\n"), nil
}

func runCommand(ctx context.Context, root, command string) (string, error) {
	commandCtx, cancel := context.WithTimeout(ctx, 2*time.Minute)
	defer cancel()

	cmd := exec.CommandContext(commandCtx, "/bin/bash", "-lc", command)
	cmd.Dir = root
	output := &boundedOutput{limit: maxToolResultBytes}
	cmd.Stdout = output
	cmd.Stderr = output
	err := cmd.Run()
	text := output.String()

	if commandCtx.Err() != nil {
		return text, fmt.Errorf("command timed out or was canceled: %w", commandCtx.Err())
	}
	if err == nil {
		if text == "" {
			return "command completed successfully", nil
		}
		return text, nil
	}

	var exitErr *exec.ExitError
	if errors.As(err, &exitErr) {
		return text, fmt.Errorf("command exited with code %d", exitErr.ExitCode())
	}
	return text, err
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
	marker := "\n\n[truncated from " + strconv.Itoa(b.total) + " bytes]\n"
	contentLimit := b.limit - len(marker)
	if contentLimit <= 0 {
		return marker[:b.limit]
	}
	return string(b.data[:contentLimit]) + marker
}

func capText(text string, limit int) string {
	if limit <= 0 || len(text) <= limit {
		return text
	}
	marker := "\n\n[truncated from " + strconv.Itoa(len(text)) + " bytes]\n\n"
	remaining := limit - len(marker)
	if remaining <= 0 {
		return marker[:limit]
	}
	head := remaining / 2
	tail := remaining - head
	return text[:head] + marker + text[len(text)-tail:]
}
