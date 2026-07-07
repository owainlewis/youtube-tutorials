from __future__ import annotations

from agent import Agent, NoMemory, run_repl


def main() -> None:
    agent = Agent(memory=NoMemory())
    run_repl(agent, "No-memory agent")


if __name__ == "__main__":
    main()
