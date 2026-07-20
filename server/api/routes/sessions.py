from fastapi import APIRouter, Depends

from server.api.dependencies import get_session_service
from server.schemas.session import SessionRequest
from server.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("")
def create_session(
    request: SessionRequest,
    service: SessionService = Depends(get_session_service)
):
    session = service.create_session(request.subject_id)
    return session.id

@router.put("")
def start_session(
    request: SessionRequest,
    service: SessionService = Depends(get_session_service)
):
    session = service.start_session(request.subject_id)
    return

@router.put("")
def end_session(
    request: SessionRequest,
    service: SessionService = Depends(get_session_service)
):
    session = service.end_session(request.subject_id)
    return

@router.get("")
def get_session(
    request: SessionRequest,
    service: SessionService = Depends(get_session_service)
):
    session = service.create_session(request.subject_id)
    return session

@router.get("")
def get_new_sessions(
    service: SessionService = Depends(get_session_service)
):
    sessions = service.create_session()
    return sessions