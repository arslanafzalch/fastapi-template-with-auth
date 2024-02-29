from fastapi import status, HTTPException


class NotFoundException(HTTPException):
    """
    Exception to be raised when a resource is not found.

    :param detail: ``(str)``: Detail message
    """

    def __init__(self, detail: str = "User not found"):
        self.detail = detail
        self.status_code = status.HTTP_404_NOT_FOUND


class CouldNotPerformDBOperationException(HTTPException):
    """
    Exception to be raised when a resource is not found.

    :param detail: ``(str)``: Detail message
    :param extra: ``(str)``: Extra message
    """

    def __init__(self, detail: str = "Could not perform DB operation", extra: str = ""):
        self.detail = {"message": detail, "cause": extra}
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class CouldNotSentEmailException(HTTPException):
    """
    Exception to be raised when a resource is not found.

    :param detail: ``(str)``: Detail message
    """

    def __init__(self, detail: str = "Could not sent email."):
        self.detail = detail
        self.status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class AlreadyReportedException(HTTPException):
    """
    Exception to be raised when a resource is not found.

    :param detail: ``(str)``: Detail message
    """

    def __init__(self, detail: str = "Already reported"):
        self.detail = detail
        self.status_code = status.HTTP_208_ALREADY_REPORTED


class InvalidImageException(HTTPException):
    """
    Exception to be raised when a resource is not found.

    :param detail: ``(str)``: Detail message
    """

    def __init__(self, detail: str = "Invalid image"):
        self.detail = detail
        self.status_code = status.HTTP_400_BAD_REQUEST
