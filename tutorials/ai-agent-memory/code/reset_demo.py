from __future__ import annotations

from memory_utils import DB_PATH


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Deleted {DB_PATH.name}")
    else:
        print(f"{DB_PATH.name} does not exist")


if __name__ == "__main__":
    main()
