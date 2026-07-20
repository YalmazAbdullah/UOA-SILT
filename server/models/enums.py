from enum import Enum


class SessionState(str, Enum):
    CREATED = "created"
    RECORDING = "recording"
    ENDED = "ended"


class Source(str, Enum):
    TARGET = "target"
    CLIENT = "client"
