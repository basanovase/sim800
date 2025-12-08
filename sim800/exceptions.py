class SIM800Error(Exception):
    """Base exception for all SIM800 errors."""
    pass


class SIM800CommandError(SIM800Error):
    """Raised when an AT command returns an error response."""

    def __init__(self, command, response=None):
        self.command = command
        self.response = response
        message = "Command '{}' failed".format(command)
        if response:
            message += ": {}".format(response)
        super().__init__(message)


class SIM800TimeoutError(SIM800Error):
    """Raised when a command times out waiting for response."""

    def __init__(self, command, timeout_ms):
        self.command = command
        self.timeout_ms = timeout_ms
        super().__init__("Command '{}' timed out after {}ms".format(command, timeout_ms))


class SIM800ConnectionError(SIM800Error):
    """Raised when a network connection fails."""

    def __init__(self, message, ip=None, port=None):
        self.ip = ip
        self.port = port
        super().__init__(message)


class SIM800InitializationError(SIM800Error):
    """Raised when module initialization fails."""
    pass


class SIM800SMSError(SIM800Error):
    """Raised when SMS operations fail."""

    def __init__(self, message, number=None):
        self.number = number
        super().__init__(message)


class SIM800FTPError(SIM800Error):
    """Raised when FTP operations fail."""

    def __init__(self, message, filename=None, path=None):
        self.filename = filename
        self.path = path
        super().__init__(message)


class SIM800HTTPError(SIM800Error):
    """Raised when HTTP operations fail."""

    def __init__(self, message, url=None, status_code=None):
        self.url = url
        self.status_code = status_code
        super().__init__(message)
