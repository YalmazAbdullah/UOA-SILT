from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

from .enums import SessionState


@dataclass
class Session:
    id: UUID
    subject_id: str
    state: SessionState
    created_at: datetime
    started_at: datetime | None
    ended_at: datetime | None
