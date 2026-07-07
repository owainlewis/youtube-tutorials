from __future__ import annotations

import os
from typing import Any

from memory_utils import USER_ID, ask_model, build_instructions, load_static_memory


def memory_text(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("memory") or item.get("content") or item)
    return str(item)


def result_items(response: Any) -> list[Any]:
    if isinstance(response, dict):
        results = response.get("results", [])
        return results if isinstance(results, list) else []
    return response if isinstance(response, list) else []


def main() -> None:
    try:
        from mem0 import MemoryClient
    except ImportError as exc:
        raise SystemExit(
            "Install the Mem0 extra with: uv run --extra mem0 04_mem0_memory.py"
        ) from exc

    api_key = os.environ.get("MEM0_API_KEY")
    if not api_key:
        raise SystemExit("Set MEM0_API_KEY before running this example.")

    client = MemoryClient(api_key=api_key)
    startup_memory = load_static_memory()

    print("Mem0-memory agent. Type 'exit' to quit.\n")
    while True:
        user_message = input("you> ").strip()
        if user_message.lower() in {"exit", "quit"}:
            break

        response = client.search(user_message, filters={"user_id": USER_ID})
        memories = [memory_text(item) for item in result_items(response)]

        instructions = build_instructions(
            startup_memory=startup_memory,
            retrieved_memory=memories,
        )
        reply = ask_model(instructions, user_message)

        client.add(
            messages=[
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": reply},
            ],
            user_id=USER_ID,
        )

        print(f"\nagent> {reply}\n")


if __name__ == "__main__":
    main()
