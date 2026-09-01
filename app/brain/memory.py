import sqlite3
from pathlib import Path
from typing import Any


class MemoryStore:
    """
    Persistent SQLite storage for SpongeBob AI.

    Stores:
    - conversations
    - messages
    - projects
    - requirements
    - decisions
    - memories
    """

    def __init__(
        self,
        database_path: str = "data/spongebob.db",
    ):
        self.database_path = Path(database_path)

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    def _connect(self):
        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize_database(self):
        with self._connect() as connection:
            connection.execute(
                "PRAGMA foreign_keys = ON"
            )

            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (
                        conversation_id
                    )
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    goal TEXT,
                    state_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    field_name TEXT NOT NULL,
                    value TEXT,
                    confidence TEXT,
                    source TEXT,
                    resolved INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (
                        project_id
                    )
                    REFERENCES projects(id)
                    ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    decision_area TEXT NOT NULL,
                    selected_value TEXT NOT NULL,
                    source TEXT,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (
                        project_id
                    )
                    REFERENCES projects(id)
                    ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    # ============================================================
    # CONVERSATIONS
    # ============================================================

    def create_conversation(
        self,
        title: str = "",
    ) -> int:

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO conversations (title)
                VALUES (?)
                """,
                (title,),
            )

            return int(cursor.lastrowid)

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ) -> None:

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO messages (
                    conversation_id,
                    role,
                    content
                )
                VALUES (?, ?, ?)
                """,
                (
                    conversation_id,
                    role,
                    content,
                ),
            )

            connection.execute(
                """
                UPDATE conversations
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (conversation_id,),
            )

    def get_messages(
        self,
        conversation_id: int,
    ) -> list[dict[str, Any]]:

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    role,
                    content,
                    created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY id ASC
                """,
                (conversation_id,),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def get_conversation(
        self,
        conversation_id: int,
    ) -> dict[str, Any] | None:

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    title,
                    created_at,
                    updated_at
                FROM conversations
                WHERE id = ?
                """,
                (conversation_id,),
            ).fetchone()

        if row is None:
            return None

        conversation = dict(row)

        conversation["messages"] = (
            self.get_messages(
                conversation_id
            )
        )

        return conversation

    def list_conversations(
        self,
    ) -> list[dict[str, Any]]:

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    title,
                    created_at,
                    updated_at
                FROM conversations
                ORDER BY updated_at DESC
                """
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    # ============================================================
    # PROJECTS
    # ============================================================

    def create_project(
        self,
        name: str,
        goal: str = "",
        state_json: str = "{}",
    ) -> int:

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO projects (
                    name,
                    goal,
                    state_json
                )
                VALUES (?, ?, ?)
                """,
                (
                    name,
                    goal,
                    state_json,
                ),
            )

            return int(cursor.lastrowid)

    def get_project(
        self,
        project_id: int,
    ) -> dict[str, Any] | None:

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    name,
                    goal,
                    state_json,
                    created_at,
                    updated_at
                FROM projects
                WHERE id = ?
                """,
                (project_id,),
            ).fetchone()

        if row is None:
            return None

        return dict(row)

    def list_projects(
        self,
    ) -> list[dict[str, Any]]:

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    name,
                    goal,
                    state_json,
                    created_at,
                    updated_at
                FROM projects
                ORDER BY updated_at DESC
                """
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def save_project_state(
        self,
        project_id: int,
        goal: str,
        state_json: str,
    ) -> None:

        with self._connect() as connection:
            connection.execute(
                """
                UPDATE projects
                SET
                    goal = ?,
                    state_json = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    goal,
                    state_json,
                    project_id,
                ),
            )

    # ============================================================
    # REQUIREMENTS
    # ============================================================

    def save_requirement(
        self,
        project_id: int,
        field_name: str,
        value: str,
        confidence: str,
        source: str,
        resolved: bool = True,
    ) -> None:

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO requirements (
                    project_id,
                    field_name,
                    value,
                    confidence,
                    source,
                    resolved
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    field_name,
                    value,
                    confidence,
                    source,
                    int(resolved),
                ),
            )

    def get_requirements(
        self,
        project_id: int,
    ) -> list[dict[str, Any]]:

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    project_id,
                    field_name,
                    value,
                    confidence,
                    source,
                    resolved,
                    created_at
                FROM requirements
                WHERE project_id = ?
                ORDER BY id ASC
                """,
                (project_id,),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    # ============================================================
    # DECISIONS
    # ============================================================

    def save_decision(
        self,
        project_id: int,
        decision_area: str,
        selected_value: str,
        source: str,
        reason: str,
    ) -> None:

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO decisions (
                    project_id,
                    decision_area,
                    selected_value,
                    source,
                    reason
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    decision_area,
                    selected_value,
                    source,
                    reason,
                ),
            )

    def get_decisions(
        self,
        project_id: int,
    ) -> list[dict[str, Any]]:

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    project_id,
                    decision_area,
                    selected_value,
                    source,
                    reason,
                    created_at
                FROM decisions
                WHERE project_id = ?
                ORDER BY id ASC
                """,
                (project_id,),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    # ============================================================
    # MEMORIES
    # ============================================================

    def save_memory(
        self,
        key: str,
        value: str,
        category: str = "general",
    ) -> None:

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO memories (
                    key,
                    value,
                    category
                )
                VALUES (?, ?, ?)
                """,
                (
                    key,
                    value,
                    category,
                ),
            )

    def recall_memory(
        self,
        key: str,
    ) -> list[dict[str, Any]]:

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    key,
                    value,
                    category,
                    created_at,
                    updated_at
                FROM memories
                WHERE key = ?
                ORDER BY id DESC
                """,
                (key,),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]