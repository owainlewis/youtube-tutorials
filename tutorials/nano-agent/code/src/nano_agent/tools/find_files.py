"""Find files tool."""

import glob
import os

SCHEMA = {
    "name": "find_files",
    "description": "Find files matching a glob pattern.",
    "input_schema": {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "The glob pattern to match (e.g. '**/*.py').",
            },
            "path": {
                "type": "string",
                "description": "The directory to search in. Defaults to current directory.",
                "default": ".",
            },
        },
        "required": ["pattern"],
    },
}


async def find_files(pattern: str, path: str = ".") -> str:
    """Find files matching a glob pattern relative to path."""
    try:
        matches = glob.glob(os.path.join(path, pattern), recursive=True)
    except (PermissionError, OSError) as e:
        return f"Error: {e}"
    if not matches:
        return f"No files found matching pattern: {pattern}"
    return "\n".join(sorted(matches))
