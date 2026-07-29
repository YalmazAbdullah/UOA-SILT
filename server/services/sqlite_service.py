import os
import json
import sqlite3
from datetime import datetime,timezone
from pathlib import Path
from uuid import UUID

from server.services.abs_database_service import DatabaseService
from server.models.log import Log
from server.models.session import Session


class SQLiteDatabase(DatabaseService):

    def __init__(self, path: Path):
        self._connection = sqlite3.connect(path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self.initialize()

    def initialize(self):
        self._connection.executescript("""
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
            event TEXT NOT NULL,
            data TEXT
        );
        """)
        self._connection.commit()

    def create_session(self, session: Session):
        try:
            self._connection.execute(
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
            self._connection.commit()
            return True
        
        except sqlite3.Error as e:
            self._connection.rollback()
            return False 

    def get_session(self, session_id: UUID):
        try:
            cursor = self._connection.execute(
                "SELECT * FROM sessions WHERE session_id=?",
                (str(session_id),)
            )
            row = cursor.fetchone()
            return row 
        
        except sqlite3.Error as e:
            self._connection.rollback()
            return
        
    def get_sessions(self):
        cursor = self._connection.execute(
            "SELECT * FROM sessions"
        )
        rows = cursor.fetchall()
        return rows

    def update_session(self, session_id:str, session_state:str):
        try:
            self._connection.execute(
                """
                UPDATE sessions
                SET session_state = ?, started_at = ?
                WHERE session_id = ?
                """,
                (
                    session_state,
                    datetime.now(timezone.utc).isoformat(),
                    session_id
                )
            )
            self._connection.commit()
            return True
        
        except sqlite3.Error as e:
            self._connection.rollback()
            return False 

    def enter_log(self, log: Log):
        try:
            cursor = self._connection.execute(
                """
                INSERT INTO logs (
                session_id, 
                target_time, client_time, server_time, 
                source, target, 
                event, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(log.session_id),
                    log.target_time.isoformat() if log.target_time else None,
                    log.client_time.isoformat() if log.client_time else None,
                    log.server_time,
                    log.source,
                    log.target,
                    log.event,
                    json.dumps(log.data)
                )
            )           
            self._connection.commit()
            log.id = cursor.lastrowid
            return log

        except sqlite3.Error as e:
            self._connection.rollback()
            return False
