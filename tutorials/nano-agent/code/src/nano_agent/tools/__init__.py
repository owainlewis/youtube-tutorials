"""Tool registry."""

from nano_agent.tools.edit_file import SCHEMA as EDIT_FILE_SCHEMA
from nano_agent.tools.edit_file import edit_file
from nano_agent.tools.find_files import SCHEMA as FIND_FILES_SCHEMA
from nano_agent.tools.find_files import find_files
from nano_agent.tools.list_directory import SCHEMA as LIST_DIRECTORY_SCHEMA
from nano_agent.tools.list_directory import list_directory
from nano_agent.tools.read_file import SCHEMA as READ_FILE_SCHEMA
from nano_agent.tools.read_file import read_file
from nano_agent.tools.run_bash import SCHEMA as RUN_BASH_SCHEMA
from nano_agent.tools.run_bash import run_bash
from nano_agent.tools.spawn_agent import SCHEMA as SPAWN_AGENT_SCHEMA
from nano_agent.tools.write_file import SCHEMA as WRITE_FILE_SCHEMA
from nano_agent.tools.write_file import write_file


def get_tools() -> dict:
    """Return the full tool registry."""
    return {
        "read_file": {
            "function": read_file,
            "schema": READ_FILE_SCHEMA,
        },
        "edit_file": {
            "function": edit_file,
            "schema": EDIT_FILE_SCHEMA,
        },
        "write_file": {
            "function": write_file,
            "schema": WRITE_FILE_SCHEMA,
        },
        "find_files": {
            "function": find_files,
            "schema": FIND_FILES_SCHEMA,
        },
        "list_directory": {
            "function": list_directory,
            "schema": LIST_DIRECTORY_SCHEMA,
        },
        "run_bash": {
            "function": run_bash,
            "schema": RUN_BASH_SCHEMA,
        },
        "spawn_agent": {
            "function": None,  # Handled directly by the agent loop
            "schema": SPAWN_AGENT_SCHEMA,
        },
    }
