from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

class SessionRequest(BaseModel):
    subject_id: str

class SessionsResponse(BaseModel):
    session_id: str
    subject_id: str
    session_state: str
    created_at: datetime