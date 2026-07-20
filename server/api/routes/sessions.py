from fastapi import APIRouter, Depends

from server.api.dependencies import get_session_service
from server.schemas.session import CreateSessionRequest, SessionResponse
from server.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("")
def create_session(
    request: CreateSessionRequest,
    manager: SessionService = Depends(get_session_service)
):
    session = manager.create_session(request.subject_id)
    return session.id