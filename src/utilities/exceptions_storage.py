class InvalidCredentials(Exception):
    def __init__(self):
        detail = "Could not validate credentials"
        super().__init__(detail)


class UserNotFoundError(Exception):
    def __init__(self, detail: str = ""):
        super().__init__(detail)


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


class UserAlreadyInConversation(Exception):
    def __init__(self, detail: str = ""):
        super().__init__(detail)


class MessageNotFound(Exception):
    pass
