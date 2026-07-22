from uuid import UUID
from datetime import datetime,timezone

from server.schemas.log import EnterLogRequest
from server.models.log import Log
import server.common.exceptions as exceptions

class LoggingService:
    def __init__(self, database) -> None:
        self.database = database
    # Convert request schema to model before writing to database
    def enter_log(self, session_id: str, request: EnterLogRequest):
        entry = Log(
            log_id=None,
            session_id=session_id,
            target_time=request.target_time,
            client_time=request.client_time,
            server_time=datetime.now(timezone.utc).isoformat(),
            source=request.source,
            target=request.target,
            event=request.event,
            data=request.data,
        )
        status = self.database.enter_log(entry)
        if not status:
            raise exceptions.LogWriteFailed