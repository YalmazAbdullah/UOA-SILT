import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import UUID

from abs_database_service import DatabaseService
from server.models.enums import SessionState
from server.models.log import Log
from server.models.session import Session
from server.schemas.session import SessionsResponse

class SQLiteDatabase(DatabaseService):

    def __init__(self, path: Path):
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.initialize()

    def initialize(self):
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            subject_id TEXT NOT NULL,
            session_state TEXT NOT NULL,
            created_at TEXT NOT NULL,
            started_at TEXT,
            ended_at TEXT
        );

        CREATE TABLE IF NOT EXISTS logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            target_time TEXT,
            client_time TEXT,
            server_time TEXT NOT NULL,
            source TEXT NOT NULL,
            target TEXT,
            event_name TEXT NOT NULL,
            data TEXT
        );
        """)
        self.connection.commit()

    def create_session(self, session: Session):
        self.connection.execute(
            """
            INSERT INTO sessions
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(session.session_id),
                session.subject_id,
                session.session_state.value,
                session.created_at.isoformat(),
                session.started_at.isoformat() if session.started_at else None,
                session.ended_at.isoformat() if session.ended_at else None,
            )
        )
        self.connection.commit()

    def get_session(self, session_id: UUID):
        cursor = self.connection.execute(
            "SELECT * FROM sessions WHERE session_id=?",
            (str(session_id),)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return SessionsResponse(
            session_id=UUID(row["session_id"]),
            subject_id=row["subject_id"],
            session_state=SessionState(row["state"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )
    
    def get_new_sessions(self):
        cursor = self.connection.execute(
            "SELECT * FROM sessions WHERE session_state = ?",
            (SessionState.CREATED.value,)
        )
        rows = cursor.fetchall()
        if rows is None:
            return None
        sessions = []
        for row in rows:
            sessions.append(
                SessionsResponse(
                    session_id=UUID(row["session_id"]),
                    subject_id=row["subject_id"],
                    session_state=SessionState(row["session_state"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
            )
        return sessions
    
    def update_session(self, session: Session):
        self.connection.execute(
            """
            UPDATE sessions
            SET session_state = ?, started_at = ?, ended_at = ?
            WHERE session_id = ?
            """,
            (
                session.session_state.value,
                session.started_at.isoformat() if session.started_at else None,
                session.ended_at.isoformat() if session.ended_at else None,
                str(session.session_id)
            )
        )
        self.connection.commit()

    def enter_log(self, log: Log):
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