from uuid import UUID
from datetime import datetime,timezone
from collections import defaultdict

from fastapi import WebSocket

from server.schemas.log import EnterLogRequest,GetLogResponse
from server.models.log import Log
import server.common.exceptions as exceptions


class StreamManager:
    def __init__(self) -> None:
        # Keeps track of subsrcibers for each session
        self._connections: dict[UUID, set[WebSocket]] = defaultdict(set)

    async def connect(self, session_id: UUID, websocket:WebSocket):
        await websocket.accept()
        self._connections[session_id].add(websocket)

    def disconnect(self, session_id: UUID, websocket: WebSocket):
        subscribers = self._connections.get(session_id)
        # check if there are any subscribers
        if subscribers is None:
            return 
        # remove specific subscriber
        subscribers.discard(websocket)
        # check again and remove session entery if empty.
        if not subscribers:
            del self._connections[session_id]

    async def publish(self, session_id: UUID, log: GetLogResponse):
        subscribers = self._connections.get(session_id)
        # if no subscribers for this session then ignore
        if subscribers is None:
            return
        disconnected = []
        for subscriber in subscribers:
            try:
                await subscriber.send_json(log.model_dump(mode = "json"))
            except Exception as e:
                disconnected.append(subscriber)
        for subscriber in disconnected:
            subscribers.remove(subscriber)
        # check again and remove session entery if empty.
        if not subscribers:
            del self._connections[session_id]


class LoggingService:
    def __init__(self, database, stream_manager) -> None:
        self._database = database
        self.stream_manager = stream_manager

    # Convert request schema to model before writing to database
    async def enter_log(self, session_id: str, request: EnterLogRequest):
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
        status = self._database.enter_log(entry)
        if not status:
            raise exceptions.LogWriteFailed
        await self.stream_manager.publish(
                    session_id,
                    GetLogResponse(
                        log_id=status.id,
                        target_time=entry.target_time,
                        client_time=entry.client_time,
                        server_time=entry.server_time,
                        source=entry.source,
                        target=entry.target,
                        event=entry.event,
                        data=entry.data,
                    )
                )