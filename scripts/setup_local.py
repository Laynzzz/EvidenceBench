"""Create local-only database configuration without displaying credentials."""

import secrets
from pathlib import Path


def main():
    path = Path(".env")
    if path.exists():
        print("Existing .env preserved.")
        return
    password = secrets.token_hex(24)
    path.write_text(
        f"EVIDENCEBENCH_DB_PASSWORD={password}\n"
        f"EVIDENCEBENCH_DATABASE_URL=postgresql://evidencebench:{password}@127.0.0.1:15432/evidencebench\n",
        encoding="utf-8",
    )
    print("Created ignored .env for the local database.")


if __name__ == "__main__":
    main()
