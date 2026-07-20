from pathlib import Path

# from server.database.sqlite_database import SQLiteDatabase
from server.services.logging_service import LoggingService
from server.services.session_service import SessionService

# read cnf file to get experiment name
database = SQLiteDatabase(Path("research_logger.db"))

session_manager = SessionService(
    database=database,
    recordings_root=Path("recordings")
)

log_service = LoggingService(
    database=database
)

def get_session_service():
    return session_manager

def get_logging_service():
    return log_service