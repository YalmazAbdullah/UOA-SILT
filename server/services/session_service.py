from uuid import uuid4, UUID
from datetime import datetime, timezone

from server.models.enums import SessionState
from server.models.session import Session
from server.schemas.session import SessionResponse
import server.common.exceptions as exceptions

def _raw_session_row_to_response(raw_data):
    response = SessionResponse(
        session_id=UUID(raw_data["session_id"]),
        subject_id=raw_data["subject_id"],
        session_state=SessionState(raw_data["session_state"]),
        created_at=datetime.fromisoformat(raw_data["created_at"]),
        started_at=datetime.fromisoformat(raw_data["started_at"]) if raw_data["started_at"]!=None else None,
        ended_at=datetime.fromisoformat(raw_data["started_at"]) if raw_data["started_at"]!=None else None
    )
    return response

class SessionService:
    def __init__(self, database) -> None:
        self.database = database

    def create_session(self, subject_id:str):
        session_id = uuid4()
        # Convert request schema to model before writing to database
        session = Session(
            session_id=session_id,
            subject_id=subject_id,
            session_state=SessionState.CREATED,
            created_at=datetime.now(timezone.utc),
            started_at=None,
            ended_at=None,
        )
        status = self.database.create_session(session)
        if not status:
            raise exceptions.SessionCreationFailed
        return session 

    def get_session(self, session_id:str):
        raw_data = self.database.get_session(session_id)
        if raw_data is None:
            raise exceptions.SessionNotFound
        # Transform raw data into schema
        session = _raw_session_row_to_response(raw_data)
        return session

    def get_sessions(self):
        raw_data = self.database.get_sessions()
        if raw_data is None:
            return []
        response = []
        for session in raw_data:
            response.append(_raw_session_row_to_response(session))
        return response

    def start_session(self, session_id:str):
        # Fetch session 
        session = self.get_session(session_id)
        if session.session_state != SessionState.CREATED:
            raise exceptions.InvalidSessionState
        # Update the session to started
        session.session_state = SessionState.STARTED
        session.started_at = datetime.now(timezone.utc)
        status = self.database.update_session(str(session.session_id), session.session_state.value)
        if not status:
            raise exceptions.SessionUpdatingFailed
        return session 
    
    def end_session(self, session_id:str):
        # Fetch session 
        session = self.get_session(session_id)
        if session.session_state != SessionState.STARTED:
            raise exceptions.InvalidSessionState
        # Update the session to ended
        session.session_state = SessionState.ENDED
        session.started_at = datetime.now(timezone.utc)
        status = self.database.update_session(str(session.session_id), session.session_state.value)
        if not status:
            raise exceptions.SessionUpdatingFailed
        return session 