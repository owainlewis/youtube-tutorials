from __future__ import annotations

from memory_utils import ask_model, build_instructions, load_static_memory


def main() -> None:
    startup_memory = load_static_memory()
    instructions = build_instructions(startup_memory=startup_memory)

    print("Static-memory agent. Type 'exit' to quit.\n")
    while True:
        user_message = input("you> ").strip()
        if user_message.lower() in {"exit", "quit"}:
            break

        reply = ask_model(instructions, user_message)
        print(f"\nagent> {reply}\n")


if __name__ == "__main__":
    main()
