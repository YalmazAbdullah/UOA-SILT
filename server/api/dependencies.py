from pathlib import Path

from server.services.sqlite_service import SQLiteDatabase
from server.services.logging_service import LoggingService, StreamManager
from server.services.session_service import SessionService
from server.config import DATABASE_NAME, DATABASE_PATH

database = SQLiteDatabase(Path(DATABASE_PATH+DATABASE_NAME+".db"))

session_service = SessionService(
    database=database
)

stream_manager = StreamManager()
log_service = LoggingService(
    database=database,
    stream_manager= stream_manager
)

def get_session_service():
    return session_service

def get_logging_service():
    return log_service