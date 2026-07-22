class SessionCreationFailed(Exception):
    pass

class SessionNotFound(Exception):
    pass

class InvalidSessionState(Exception):
    pass

class SessionUpdatingFailed(Exception):
    pass

class LogWriteFailed(Exception):
    pass