"""Read file tool."""

MAX_OUTPUT = 10000

SCHEMA = {
    "name": "read_file",
    "description": "Read the contents of a file at the given path.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to read.",
            },
        },
        "required": ["file_path"],
    },
}


async def read_file(file_path: str) -> str:
    """Read a file and return its contents."""
    try:
        with open(file_path) as f:
            content = f.read()
    except (FileNotFoundError, PermissionError) as e:
        return f"Error: {e}"

    if len(content) > MAX_OUTPUT:
        return content[:MAX_OUTPUT] + "\n[truncated]"
    return content
