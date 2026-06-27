"""Write file tool."""

import os

SCHEMA = {
    "name": "write_file",
    "description": "Write content to a file, creating parent directories if needed.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to write.",
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file.",
            },
        },
        "required": ["file_path", "content"],
    },
}


async def write_file(file_path: str, content: str) -> str:
    """Write content to a file, creating parent directories if needed."""
    try:
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
    except (PermissionError, OSError) as e:
        return f"Error: {e}"

    return f"Successfully wrote {len(content)} characters to {file_path}"
