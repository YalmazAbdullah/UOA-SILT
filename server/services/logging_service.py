from uuid import UUID

from server.schemas.log import EnterLogRequest
from server.models.log import Log

class LoggingService:
    def __init__(self, database) -> None:
        self.database = database

    def enter_log(self, session_id: UUID, request: EnterLogRequest):
        entry = Log(
            log_id=request.id,
            session_id=session_id,
            event=request.event,
            target=request.target,
            source=request.source,
            target_time=request.target_time,
            client_time=request.client_time,
            server_time=request.server_time,
            data=request.data,
        )
        return self.database.enter_log(entry)