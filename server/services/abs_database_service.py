from abc import ABC, abstractmethod
from uuid import UUID

from server.models.session import Session
from server.models.log import Log


class DatabaseService(ABC):
    @abstractmethod
    def create_session(self, session: Session):
        pass

    @abstractmethod
    def get_session(self, session_id: UUID):
        pass

    @abstractmethod
    def get_sessions(self):
        pass

    @abstractmethod
    def update_session(self, session_id:str, session_state:str):
        pass

    @abstractmethod
    def enter_log(self, log:Log):
        pass

    # @abstractmethod
    # def get_logs(self,):
    #     pass