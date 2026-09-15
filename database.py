import sqlite3
from pathlib import Path

MIGRATIONS = [
    """
    CREATE TABLE IF NOT EXISTS perfect_games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        app_id TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );
    """
]


class Database:
    _conn = None

    def __init__(self, db_path: str = "steam_games.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.migrate()

    def migrate(self):
        with self.conn:
            for migration in MIGRATIONS:
                self.conn.execute(migration)

    @classmethod
    def _get_connection(cls) -> sqlite3.Connection:
        if cls._conn is None:
            cls._conn = cls().conn
        return cls._conn

    @classmethod
    def query(cls, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        conn = cls._get_connection()
        cursor = conn.execute(sql, params)
        return cursor.fetchall()

    @classmethod
    def execute(cls, sql: str, params: tuple = ()):
        conn = cls._get_connection()
        with conn:
            cursor = conn.execute(sql, params)
            conn.commit()
            return cursor

    @classmethod
    def close(cls):
        if cls._conn is not None:
            cls._conn.close()
            cls._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @classmethod
    def get_perfect_games_ids(cls) -> list[str]:
        sql = "SELECT app_id FROM perfect_games"
        return [row["app_id"] for row in cls.query(sql)]

    @classmethod
    def add_perfect_game(cls, app_id: str):
        cls.execute("INSERT OR IGNORE INTO perfect_games (app_id) VALUES (?)", (app_id,))

    @classmethod
    def remove_perfect_game(cls, app_id: str):
        cls.execute("DELETE FROM perfect_games WHERE app_id = ?", (app_id,))