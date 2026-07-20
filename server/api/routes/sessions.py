from fastapi import APIRouter, Depends, status

from server.api.dependencies import get_session_service
from server.schemas.session import CreateSessionRequest, SessionRequest, SessionResponse
from server.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_session(
    request: CreateSessionRequest,
    service: SessionService = Depends(get_session_service)
):
    session = service.create_session(request.subject_id)
    return {"session_id": str(session.session_id)}

@router.put("/start")
def start_session(
    request: SessionRequest,
    service: SessionService = Depends(get_session_service)
):
    service.start_session(request.session_id)
    return

@router.put("/end")
def end_session(
    request: SessionRequest,
    service: SessionService = Depends(get_session_service)
):
    service.end_session(request.session_id)
    return

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    request: SessionRequest,
    service: SessionService = Depends(get_session_service)
):
    session = service.get_session(request.session_id)
    return session

@router.get("/incomplete_sessions", response_model=list[SessionResponse])
def get_incomplete_sessions(
    service: SessionService = Depends(get_session_service)
):
    sessions = service.get_incomplete_sessions()
    return sessions