"""Tests for tools."""

import asyncio

from nano_agent.tools.edit_file import edit_file
from nano_agent.tools.find_files import find_files
from nano_agent.tools.list_directory import list_directory
from nano_agent.tools.read_file import read_file
from nano_agent.tools.run_bash import run_bash
from nano_agent.tools.write_file import write_file


class TestReadFile:
    def test_reads_existing_file(self, tmp_path):
        f = tmp_path / "hello.txt"
        f.write_text("hello world")
        result = asyncio.run(read_file(str(f)))
        assert result == "hello world"

    def test_returns_error_for_missing_file(self, tmp_path):
        result = asyncio.run(read_file(str(tmp_path / "nope.txt")))
        assert "Error" in result

    def test_truncates_large_output(self, tmp_path):
        f = tmp_path / "big.txt"
        f.write_text("x" * 20000)
        result = asyncio.run(read_file(str(f)))
        assert len(result) <= 10100
        assert result.endswith("[truncated]")


class TestEditFile:
    def test_replaces_unique_string(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        result = asyncio.run(edit_file(str(f), "hello", "goodbye"))
        assert "Successfully edited" in result
        assert f.read_text() == "goodbye world"

    def test_fails_on_missing_string(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        result = asyncio.run(edit_file(str(f), "nope", "goodbye"))
        assert "not found" in result

    def test_fails_on_ambiguous_match(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("aaa aaa")
        result = asyncio.run(edit_file(str(f), "aaa", "bbb"))
        assert "not unique" in result

    def test_fails_on_missing_file(self):
        result = asyncio.run(edit_file("/tmp/does_not_exist_xyz.txt", "a", "b"))
        assert "Error" in result


class TestWriteFile:
    def test_writes_file(self, tmp_path):
        f = tmp_path / "out.txt"
        result = asyncio.run(write_file(str(f), "hello"))
        assert "Successfully wrote" in result
        assert f.read_text() == "hello"

    def test_creates_parent_dirs(self, tmp_path):
        f = tmp_path / "a" / "b" / "out.txt"
        result = asyncio.run(write_file(str(f), "nested"))
        assert "Successfully wrote" in result
        assert f.read_text() == "nested"

    def test_overwrites_existing(self, tmp_path):
        f = tmp_path / "out.txt"
        f.write_text("old")
        asyncio.run(write_file(str(f), "new"))
        assert f.read_text() == "new"


class TestFindFiles:
    def test_finds_matching_files(self, tmp_path):
        (tmp_path / "a.py").touch()
        (tmp_path / "b.py").touch()
        (tmp_path / "c.txt").touch()
        result = asyncio.run(find_files("*.py", str(tmp_path)))
        assert "a.py" in result
        assert "b.py" in result
        assert "c.txt" not in result

    def test_returns_message_for_no_matches(self, tmp_path):
        result = asyncio.run(find_files("*.xyz", str(tmp_path)))
        assert "No files found" in result


class TestListDirectory:
    def test_lists_entries(self, tmp_path):
        (tmp_path / "file.txt").touch()
        (tmp_path / "subdir").mkdir()
        result = asyncio.run(list_directory(str(tmp_path)))
        assert "file.txt" in result
        assert "subdir/" in result

    def test_handles_missing_directory(self):
        result = asyncio.run(list_directory("/tmp/does_not_exist_xyz"))
        assert "Error" in result


class TestRunBash:
    def test_runs_echo(self):
        result = asyncio.run(run_bash("echo hello"))
        assert "Exit code: 0" in result
        assert "hello" in result

    def test_failing_command(self):
        result = asyncio.run(run_bash("exit 1"))
        assert "Exit code: 1" in result

    def test_timeout(self):
        result = asyncio.run(run_bash("sleep 10", timeout=1))
        assert "timed out" in result
