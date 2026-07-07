from __future__ import annotations

from agent import Agent, StaticFileMemory, run_repl


def main() -> None:
    agent = Agent(memory=StaticFileMemory())
    run_repl(agent, "Static-memory agent")


if __name__ == "__main__":
    main()
