from enum import Enum


class SessionState(str, Enum):
    CREATED = "created"
    STARTED = "started"
    ENDED = "ended"


class Source(str, Enum):
    TARGET = "target"
    CLIENT = "client"
