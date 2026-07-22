from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    subject_id: str

class SessionResponse(BaseModel):
    session_id: UUID
    subject_id: str
    session_state: str
    created_at: datetime
    started_at: datetime| None
    ended_at: datetime| None