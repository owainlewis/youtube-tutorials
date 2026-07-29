package main

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestReadFileRejectsWorkspaceEscape(t *testing.T) {
	parent := t.TempDir()
	root := filepath.Join(parent, "workspace")
	if err := os.Mkdir(root, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(parent, "secret.txt"), []byte("secret"), 0o644); err != nil {
		t.Fatal(err)
	}
	tools := mustTools(t, root)

	_, err := runTestTool(tools["read_file"], map[string]any{"path": "../secret.txt"})
	if err == nil {
		t.Fatal("read_file accepted a path outside the workspace")
	}
}

func TestReadFileRejectsSymlinkEscape(t *testing.T) {
	parent := t.TempDir()
	root := filepath.Join(parent, "workspace")
	if err := os.Mkdir(root, 0o755); err != nil {
		t.Fatal(err)
	}
	outside := filepath.Join(parent, "secret.txt")
	if err := os.WriteFile(outside, []byte("secret"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.Symlink(outside, filepath.Join(root, "link.txt")); err != nil {
		t.Fatal(err)
	}
	tools := mustTools(t, root)

	_, err := runTestTool(tools["read_file"], map[string]any{"path": "link.txt"})
	if err == nil || !strings.Contains(err.Error(), "escapes") {
		t.Fatalf("read_file error = %v, want workspace escape", err)
	}
}

func TestReadFileBoundsLargeFileBeforeReturningIt(t *testing.T) {
	root := t.TempDir()
	content := strings.Repeat("x", maxFileBytes*2)
	if err := os.WriteFile(filepath.Join(root, "large.txt"), []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	tools := mustTools(t, root)

	got, err := runTestTool(tools["read_file"], map[string]any{"path": "large.txt"})
	if err != nil {
		t.Fatal(err)
	}
	if len(got) > maxFileBytes {
		t.Fatalf("read_file returned %d bytes, limit is %d", len(got), maxFileBytes)
	}
	if !strings.Contains(got, "[truncated from 131072 bytes]") {
		t.Fatalf("read_file result missing truncation marker: %q", got[len(got)-80:])
	}
}

func TestEditFileRequiresOneExactMatch(t *testing.T) {
	root := t.TempDir()
	path := filepath.Join(root, "example.txt")
	if err := os.WriteFile(path, []byte("old old"), 0o640); err != nil {
		t.Fatal(err)
	}
	tools := mustTools(t, root)

	_, err := runTestTool(tools["edit_file"], map[string]any{
		"path":     "example.txt",
		"old_text": "old",
		"new_text": "new",
	})
	if err == nil || !strings.Contains(err.Error(), "found 2 matches") {
		t.Fatalf("edit_file error = %v", err)
	}

	if err := os.WriteFile(path, []byte("hello world"), 0o640); err != nil {
		t.Fatal(err)
	}
	got, err := runTestTool(tools["edit_file"], map[string]any{
		"path":     "example.txt",
		"old_text": "hello",
		"new_text": "goodbye",
	})
	if err != nil {
		t.Fatal(err)
	}
	if got != "updated example.txt" {
		t.Fatalf("edit_file result = %q", got)
	}
	content, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if string(content) != "goodbye world" {
		t.Fatalf("file content = %q", content)
	}
	info, err := os.Stat(path)
	if err != nil {
		t.Fatal(err)
	}
	if info.Mode().Perm() != 0o640 {
		t.Fatalf("file mode = %o, want 640", info.Mode().Perm())
	}
}

func TestEditFileRejectsLargeFiles(t *testing.T) {
	root := t.TempDir()
	path := filepath.Join(root, "large.txt")
	original := strings.Repeat("old", maxFileBytes)
	if err := os.WriteFile(path, []byte(original), 0o644); err != nil {
		t.Fatal(err)
	}
	tools := mustTools(t, root)

	_, err := runTestTool(tools["edit_file"], map[string]any{
		"path":     "large.txt",
		"old_text": "old",
		"new_text": "new",
	})
	if err == nil || !strings.Contains(err.Error(), "too large") {
		t.Fatalf("edit_file error = %v, want size limit", err)
	}
	content, readErr := os.ReadFile(path)
	if readErr != nil {
		t.Fatal(readErr)
	}
	if string(content) != original {
		t.Fatal("large file changed after rejected edit")
	}
}

func TestEditFileRejectsMissingOrUnknownArguments(t *testing.T) {
	root := t.TempDir()
	path := filepath.Join(root, "example.txt")
	if err := os.WriteFile(path, []byte("keep this"), 0o644); err != nil {
		t.Fatal(err)
	}
	tools := mustTools(t, root)

	_, err := runTestTool(tools["edit_file"], map[string]any{
		"path":     "example.txt",
		"old_text": "keep this",
	})
	if err == nil || !strings.Contains(err.Error(), "new_text is required") {
		t.Fatalf("missing new_text error = %v", err)
	}

	_, err = runTestTool(tools["edit_file"], map[string]any{
		"path":     "example.txt",
		"old_text": "keep this",
		"new_txt":  "deleted by typo",
	})
	if err == nil || !strings.Contains(err.Error(), "unknown field") {
		t.Fatalf("misspelled new_text error = %v", err)
	}

	content, readErr := os.ReadFile(path)
	if readErr != nil {
		t.Fatal(readErr)
	}
	if string(content) != "keep this" {
		t.Fatalf("file changed after invalid arguments: %q", content)
	}
}

func TestSearchReturnsRelativeMatches(t *testing.T) {
	root := t.TempDir()
	if err := os.Mkdir(filepath.Join(root, "pkg"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(
		filepath.Join(root, "pkg", "example.go"),
		[]byte("package pkg\n\nconst answer = 42\n"),
		0o644,
	); err != nil {
		t.Fatal(err)
	}
	tools := mustTools(t, root)

	got, err := runTestTool(tools["search"], map[string]any{"query": "answer"})
	if err != nil {
		t.Fatal(err)
	}
	if got != "pkg/example.go:3:const answer = 42" {
		t.Fatalf("search result = %q", got)
	}
}

func TestRunCommandUsesWorkspaceAndCapsOutput(t *testing.T) {
	root := t.TempDir()
	tools := mustTools(t, root)
	resolvedRoot, err := filepath.EvalSymlinks(root)
	if err != nil {
		t.Fatal(err)
	}

	got, err := runTestTool(tools["run_command"], map[string]any{"command": "pwd"})
	if err != nil {
		t.Fatal(err)
	}
	if strings.TrimSpace(got) != resolvedRoot {
		t.Fatalf("pwd = %q, want %q", strings.TrimSpace(got), resolvedRoot)
	}

	got, err = runTestTool(tools["run_command"], map[string]any{
		"command": "yes x | head -c 4000000",
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(got) > maxToolResultBytes || !strings.Contains(got, "[truncated from 4000000 bytes]") {
		t.Fatalf("capped output length = %d, marker present = %v", len(got), strings.Contains(got, "[truncated"))
	}
}

func TestBoundedOutputDoesNotBufferPastLimit(t *testing.T) {
	output := &boundedOutput{limit: 1024}
	chunk := make([]byte, 1<<20)

	written, err := output.Write(chunk)
	if err != nil {
		t.Fatal(err)
	}
	if written != len(chunk) {
		t.Fatalf("Write() = %d, want %d", written, len(chunk))
	}
	if len(output.data) != 1024 {
		t.Fatalf("buffered bytes = %d, want 1024", len(output.data))
	}
	if output.total != len(chunk) {
		t.Fatalf("total bytes = %d, want %d", output.total, len(chunk))
	}
	if len(output.String()) > 1024 || !strings.Contains(output.String(), "[truncated from 1048576 bytes]") {
		t.Fatalf("bounded output = %q", output.String())
	}
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
