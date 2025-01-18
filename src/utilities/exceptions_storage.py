from fastapi import status
from fastapi.exceptions import HTTPException


credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
)


class UserNotFoundError(Exception):
    pass


class ConversationNotFoundError(Exception):
    pass


class AccessDeniedError(Exception):
    pass


class IsNotAGroupError(Exception):
    pass


class IsNotAChatError(Exception):
    pass


class InvalidPasswordError(Exception):
    pass


class UserAlreadyExists(Exception):
    pass


class InvalidFileType(Exception):
    def __init__(self, detail: str):
        self.message = detail
        super().__init__(detail)


class FIleToBig(Exception):
    def __init__(self, detail: str):
        self.message = detail
        super().__init__(detail)


class ImageCorrupted(Exception):
    def __init__(self, detail: str):
        self.message = detail
        super().__init__(detail)


class ChatAlreadyExists(Exception):
    pass


class SameUsersIds(Exception):
    pass


class FileNotFound(Exception):
    pass
