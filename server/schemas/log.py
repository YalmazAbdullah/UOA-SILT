from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LogRequest(BaseModel):
    id = int
    event: str
    target: str
    source: str
    target_time: datetime | None
    client_time: datetime | None
    date: dict[str, Any] = Field(default_factory=dict)
