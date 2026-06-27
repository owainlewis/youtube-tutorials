"""Run bash command tool."""

import asyncio

MAX_OUTPUT = 10000

SCHEMA = {
    "name": "run_bash",
    "description": "Run a bash command and return the output.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The bash command to execute.",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds. Defaults to 30.",
                "default": 30,
            },
        },
        "required": ["command"],
    },
}


async def run_bash(command: str, timeout: int = 30) -> str:
    """Run a bash command and return combined stdout/stderr."""
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        process.kill()
        await process.communicate()
        return f"Command timed out after {timeout} seconds"

    output = stdout.decode("utf-8", errors="replace") + stderr.decode("utf-8", errors="replace")
    result = f"Exit code: {process.returncode}\n{output}"

    if len(result) > MAX_OUTPUT:
        return result[:MAX_OUTPUT] + "\n[truncated]"
    return result
