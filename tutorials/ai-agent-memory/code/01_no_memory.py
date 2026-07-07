from __future__ import annotations

from memory_utils import ask_model, build_instructions


SYSTEM_PROMPT = build_instructions()


def main() -> None:
    history: list[str] = []

    print("No-memory agent. Type 'exit' to quit.\n")
    while True:
        user_message = input("you> ").strip()
        if user_message.lower() in {"exit", "quit"}:
            break

        history.append(f"user: {user_message}")
        reply = ask_model(SYSTEM_PROMPT, "\n".join(history))
        history.append(f"assistant: {reply}")

        print(f"\nagent> {reply}\n")


if __name__ == "__main__":
    main()
