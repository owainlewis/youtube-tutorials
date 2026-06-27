"""List directory tool."""

import os

SCHEMA = {
    "name": "list_directory",
    "description": "List the contents of a directory.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "The directory to list. Defaults to current directory.",
                "default": ".",
            },
        },
        "required": [],
    },
}


async def list_directory(path: str = ".") -> str:
    """List entries in a directory, with '/' suffix for subdirectories."""
    try:
        entries = sorted(os.listdir(path))
    except (FileNotFoundError, PermissionError) as e:
        return f"Error: {e}"

    result = []
    for entry in entries:
        full = os.path.join(path, entry)
        result.append(entry + "/" if os.path.isdir(full) else entry)
    return "\n".join(result)
