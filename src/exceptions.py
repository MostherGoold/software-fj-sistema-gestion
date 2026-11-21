class SoftwareFJError(Exception):
    def __init__(self, message: str, code: str = "SFJ-000", cause=None):
        super().__init__(message)
        self.message = message
        self.code = code
        if cause is not None:
            self.__cause__ = cause

class InvalidEntityError(SoftwareFJError):
    def __init__(self, message: str, cause=None):
        super().__init__(message, code="SFJ-100", cause=cause)

class InvalidClientError(SoftwareFJError):
    def __init__(self, message: str, field: str = None, cause=None):
        super().__init__(message, code="SFJ-200", cause=cause)
        self.field = field

class ServiceUnavailableError(SoftwareFJError):
    def __init__(self, message: str, service: str = None, cause=None):
        super().__init__(message, code="SFJ-300", cause=cause)
        self.service = service

class InvalidServiceParameterError(SoftwareFJError):
    def __init__(self, message: str, parameter: str = None, cause=None):
        super().__init__(message, code="SFJ-310", cause=cause)
        self.parameter = parameter

class InvalidReservationError(SoftwareFJError):
    def __init__(self, message: str, reservation_id: str = None, cause=None):
        super().__init__(message, code="SFJ-400", cause=cause)
        self.reservation_id = reservation_id

class OperationNotAllowedError(SoftwareFJError):
    def __init__(self, message: str, cause=None):
        super().__init__(message, code="SFJ-500", cause=cause)

class InconsistentCalculationError(SoftwareFJError):
    def __init__(self, message: str, value: float = None, cause=None):
        super().__init__(message, code="SFJ-600", cause=cause)
        self.value = value
