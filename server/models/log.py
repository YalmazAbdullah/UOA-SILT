from dataclasses import dataclass
from typing import Any
from uuid import UUID
from datetime import datetime

from server.models.enums import Source


@dataclass
class Log:
    id: int
    session_id: UUID
    event: str
    target: str | None
    source: Source
    target_time: datetime | None
    client_time: datetime | None
    server_time: datetime
    data: dict[str, Any]
