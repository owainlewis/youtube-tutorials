from __future__ import annotations

from agent import Agent, SessionSearchMemory, run_repl


def main() -> None:
    memory = SessionSearchMemory()
    try:
        agent = Agent(memory=memory)
        run_repl(agent, "Session-search agent")
    finally:
        memory.close()


if __name__ == "__main__":
    main()
