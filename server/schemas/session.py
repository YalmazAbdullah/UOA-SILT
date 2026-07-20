from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    subject_id: str


class SessionResponse(BaseModel):
    session_id: UUID
    subject_id: str
    state: str
    created_at: datetime
    started_at: datetime
    ended_at: datetime


class SessionStateResponse(BaseModel):
    session_id: UUID
    state: str
