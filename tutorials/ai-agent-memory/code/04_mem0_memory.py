from __future__ import annotations

from agent import Agent, Mem0Memory, run_repl


def main() -> None:
    agent = Agent(memory=Mem0Memory())
    run_repl(agent, "Mem0-memory agent")


if __name__ == "__main__":
    main()
