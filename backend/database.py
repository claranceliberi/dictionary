import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "dictionary.db"


def get_db() -> sqlite3.Connection:
    # The database is built into the image at build time and never changes at
    # runtime, so open it read-only and immutable: no journal, no WAL or -shm
    # files, no locking, and it works from a read-only filesystem.
    conn = sqlite3.connect(f"{DB_PATH.resolve().as_uri()}?mode=ro&immutable=1", uri=True)
    conn.row_factory = sqlite3.Row
    return conn
