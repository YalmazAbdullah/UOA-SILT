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
            id=session_id,
            subject_id=subject_id,
            state=SessionState.CREATED,
            created_at=datetime.now(timezone.utc),
            started_at=None,
            ended_at=None,
        )
        self.database.create_session(session)
        return session

    # def get_session(self, session_id: UUID):
    #     session = self.database.get_session(session_id)
    #     if session is None:
    #         raise SessionNotFound()
    #     return session

    # def start_session(self, session_id: UUID):
    #     session = self.database.get_session(session_id)
    #     if session is None:
    #         raise SessionNotFound()
    #     if session.state != SessionState.CREATED:
    #         raise InvalidSessionState
    #     session.state = SessionState.RECORDING
    #     session.started_at = datetime.now(timezone.utc)
    #     self.database.update_session(session)
    #     return session

    # def end_session(self, session_id: UUID):
    #     session = self.database.get_session(session_id)
    #     if session is None:
    #         raise SessionNotFound
    #     if session.state != SessionState.RECORDING:
    #         raise InvalidSessionState
    #     session.state = SessionState.ENDED
    #     session.ended_at = datetime.now(timezone.utc)
    #     self.database.update_session(session)
    #     return session_id
