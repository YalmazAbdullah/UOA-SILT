from uuid import uuid4, UUID
from datetime import datetime, timezone

from server.models.enums import SessionState
from server.models.session import Session


class SessionNotFound(Exception):
    pass


class InvalidSessionState(Exception):
    pass


class SessionService:
    def __init__(self, database) -> None:
        self.database = database

    def create_session(self, subject_id):
        session_id = uuid4()
        session = Session(
            session_id=session_id,
            subject_id=subject_id,
            session_state=SessionState.CREATED,
            created_at=datetime.now(timezone.utc),
            started_at=None,
            ended_at=None,
        )
        self.database.create_session(session)
        return session
    
    def start_session(self, session_id):
        session = self.database.get_session(session_id)
        # Handle potential errors
        if session is None:
            raise SessionNotFound()
        if session.state != SessionState.CREATED:
            raise InvalidSessionState
        session.state = SessionState.STARTED
        session.started_at = datetime.now(timezone.utc)
        self.database.update_session(session)
        return session

    def end_session(self, session_id):
        session = self.database.get_session(session_id)
        # Handle potential errors
        if session is None:
            raise SessionNotFound()
        if session.state != SessionState.STARTED:
            raise InvalidSessionState
        session.state = SessionState.ENDED
        session.ended_at = datetime.now(timezone.utc)
        self.database.update_session(session)
        return session

    def get_session(self):
        new_sessions = self.database.get_new_sessions()
        return new_sessions
    
    def get_new_sessions(self):
        new_sessions = self.database.get_new_sessions()
        return new_sessions
