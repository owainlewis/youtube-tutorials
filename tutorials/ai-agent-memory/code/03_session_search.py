from __future__ import annotations

from memory_utils import (
    ask_model,
    build_instructions,
    connect_sessions,
    load_static_memory,
    save_message,
    search_sessions,
)


def main() -> None:
    startup_memory = load_static_memory()

    print("Session-search agent. Type 'exit' to quit.\n")
    with connect_sessions() as db:
        while True:
            user_message = input("you> ").strip()
            if user_message.lower() in {"exit", "quit"}:
                break

            retrieved_memory = search_sessions(db, user_message)
            instructions = build_instructions(
                startup_memory=startup_memory,
                retrieved_memory=retrieved_memory,
            )

            reply = ask_model(instructions, user_message)

            save_message(db, "user", user_message)
            save_message(db, "assistant", reply)

            print(f"\nagent> {reply}\n")


if __name__ == "__main__":
    main()
