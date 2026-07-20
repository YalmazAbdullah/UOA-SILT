import json
import sqlite3

from datetime import datetime
from pathlib import Path
from uuid import UUID

from abs_database_service import DatabaseService
from server.models.enums import SessionState
from server.models.log import Log
from server.models.session import Session

class SQLiteDatabase(DatabaseService):

    def __init__(self, path: Path):
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.initialize()

    def initialize(self):
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            subject_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            started_at TEXT,
            ended_at TEXT,
            state TEXT NOT NULL,
            recording_directory TEXT
        );

        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            client_time REAL NOT NULL,
            server_time TEXT NOT NULL,
            event_name TEXT NOT NULL,
            data TEXT NOT NULL,
            source TEXT NOT NULL
        );
        """)
        self.connection.commit()

    def save_session(self, session: Session):
        self.connection.execute(
            """
            INSERT INTO sessions
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(session.id),
                session.subject_id,
                session.created_at.isoformat(),
                session.started_at.isoformat() if session.started_at else None,
                session.ended_at.isoformat() if session.ended_at else None,
                session.state.value,
                str(session.recording_directory)
            )
        )
        self.connection.commit()

    def update_session(self, session: Session):
        self.connection.execute(
            """
            UPDATE sessions
            SET started_at=?, ended_at=?, state=?
            WHERE id=?
            """,
            (
                session.started_at.isoformat() if session.started_at else None,
                session.ended_at.isoformat() if session.ended_at else None,
                session.state.value,
                str(session.id)
            )
        )
        self.connection.commit()

    # def get_session(self, session_id: UUID):
    #     cursor = self.connection.execute(
    #         "SELECT * FROM sessions WHERE id=?",
    #         (str(session_id),)
    #     )

    #     row = cursor.fetchone()
    #     if row is None:
    #         return None

    #     return Session(
    #         id=UUID(row["id"]),
    #         subject_id=row["subject_id"],
    #         created_at=datetime.fromisoformat(row["created_at"]),
    #         started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
    #         ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
    #         state=SessionState(row["state"]),
    #         recording_directory=Path(row["recording_directory"])
    #     )

    def save_log(self, log: LogEntry):
        cursor = self.connection.execute(
            """
            INSERT INTO logs
            (session_id, client_time, server_time, event_name, data, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(log.session_id),
                log.client_time,
                log.server_time.isoformat(),
                log.event_name,
                json.dumps(log.data),
                log.source
            )
        )

        self.connection.commit()
        log.id = cursor.lastrowid
        return log

    # def get_logs(self, session_id: UUID, limit: int = 100):
    #     cursor = self.connection.execute(
    #         """
    #         SELECT * FROM logs
    #         WHERE session_id=?
    #         ORDER BY id DESC
    #         LIMIT ?
    #         """,
    #         (str(session_id), limit)
    #     )

    #     rows = cursor.fetchall()

    #     return [
    #         LogEntry(
    #             id=row["id"],
    #             session_id=UUID(row["session_id"]),
    #             client_time=row["client_time"],
    #             server_time=datetime.fromisoformat(row["server_time"]),
    #             event_name=row["event_name"],
    #             data=json.loads(row["data"]),
    #             source=row["source"]
    #         )
    #         for row in rows
    #     ]