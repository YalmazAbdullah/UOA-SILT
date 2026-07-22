from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

class EnterLogRequest(BaseModel):
    target_time: datetime | None
    client_time: datetime | None
    source: str
    target: str
    event: str
    data: dict[str, Any] = Field(default_factory=dict)

class GetLogResponse(BaseModel):
    log_id: int
    target_time: datetime | None
    client_time: datetime | None
    server_time: datetime | None
    source: str
    target: str
    event: str
    data: dict[str, Any] = Field(default_factory=dict)
