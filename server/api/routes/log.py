from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from server.api.dependencies import get_logging_service
from server.schemas.log import EnterLogRequest
from server.services.logging_service import LoggingService
import server.common.exceptions as exceptions

router = APIRouter(prefix="/logs/{session_id:uuid}", tags=["logs"])

@router.post("", status_code=status.HTTP_201_CREATED)
def enter_log(
    session_id: UUID,
    request: EnterLogRequest,
    service: LoggingService = Depends(get_logging_service)
):
    try:
        service.enter_log(session_id, request) 
    
    except exceptions.LogWriteFailed:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database failed to write log entery"
        )
    