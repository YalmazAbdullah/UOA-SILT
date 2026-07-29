from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import WebSocket, WebSocketDisconnect

from server.api.dependencies import get_logging_service
from server.schemas.log import EnterLogRequest
from server.services.logging_service import LoggingService
import server.common.exceptions as exceptions

router = APIRouter(prefix="/logs/{session_id:uuid}", tags=["logs"])

@router.post("", status_code=status.HTTP_201_CREATED)
async def enter_log(
    session_id: UUID,
    request: EnterLogRequest,
    service: LoggingService = Depends(get_logging_service)
):
    try:
        await service.enter_log(session_id, request) 
    
    except exceptions.LogWriteFailed:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database failed to write log entery"
        )

@router.websocket("/ws")
async def stream_logs(
    session_id: UUID,
    websocket: WebSocket,
    service: LoggingService = Depends(get_logging_service)
):
    await service.stream_manager.connect(
        session_id,
        websocket
    )
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        service.stream_manager.disconnect(
            session_id,
            websocket
        )
