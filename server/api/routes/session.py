from fastapi import APIRouter, Depends, status, HTTPException, status

from server.api.dependencies import get_session_service
from server.schemas.session import CreateSessionRequest, SessionResponse
from server.services.session_service import SessionService
import server.common.exceptions as exceptions


router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_session(
    request: CreateSessionRequest,
    service: SessionService = Depends(get_session_service),
):
    try:
        session = service.create_session(request.subject_id)
        return {"session_id": str(session.session_id)}
    
    except exceptions.SessionCreationFailed:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Session creation failed due to database error."
        )
    
@router.get("/all", response_model=list[SessionResponse])
def get_sessions(
    service: SessionService = Depends(get_session_service)
):
    sessions = service.get_sessions()
    return sessions

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    try:
        session = service.get_session(session_id)
        return session
    
    except exceptions.SessionNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Session with ID {session_id} does not exist."
        )

@router.put("/start/{session_id}")
def start_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    try:
        service.start_session(session_id)
        return {"detail": "Session started"}
    
    except exceptions.SessionNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Session with ID {session_id} does not exist."
        )
        
    except exceptions.InvalidSessionState:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Session cannot be started because it is not in the CREATED state."
        )
    
    except exceptions.SessionUpdatingFailed:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Session was not updated due to databse error."
        )
    
@router.put("/end/{session_id}")
def end_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    try:
        service.end_session(session_id)
        return {"detail": "Session endeded"}
    
    except exceptions.SessionNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Session with ID {session_id} does not exist."
        )
        
    except exceptions.InvalidSessionState:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Session cannot be endeed because it is not in the STARTED state."
        )
    
    except exceptions.SessionUpdatingFailed:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Session was not updated due to databse error."
        )