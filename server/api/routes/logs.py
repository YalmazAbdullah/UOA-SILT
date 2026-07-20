from uuid import UUID

from fastapi import APIRouter, Depends

from server.api.dependencies import get_logging_service
from server.schemas.log import LogRequest
from server.services.logging_service import LoggingService

router = APIRouter(prefix="/sessions/{session_id}/logs", tags=["logs"])

@router.post("")
def add_log(
    session_id: UUID,
    request: LogRequest,
    service: LoggingService = Depends(get_logging_service)
):
    entry = service.add_log(session_id, request) 