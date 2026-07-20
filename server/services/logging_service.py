from uuid import UUID
from datetime import datetime,timezone

from server.schemas.log import EnterLogRequest
from server.models.log import Log

class LoggingService:
    def __init__(self, database) -> None:
        self.database = database

    def enter_log(self, session_id: UUID, request: EnterLogRequest):
        entry = Log(
            log_id=None,
            session_id=session_id,
            target_time=request.target_time,
            client_time=request.client_time,
            server_time=datetime.now(timezone.utc),
            source=request.source,
            target=request.target,
            event=request.event,
            data=request.data,
        )
        self.database.enter_log(entry)