from typing import Union, Literal

from utilities import MessagesTypes


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
    def __init__(
            self,
            file_type_name:
            Union[
                Literal[
                    MessagesTypes.IMAGE,
                    MessagesTypes.VIDEO,
                    MessagesTypes.AUDIO,
                    MessagesTypes.FILE
                ]
            ],
            file_types: str
    ):
        detail = f"Invalid {file_type_name} type. Only {file_types} are allowed."
        super().__init__(detail)


class FIleToBig(Exception):
    def __init__(
            self,
            file_type_name:
            Union[
                Literal[
                    MessagesTypes.IMAGE,
                    MessagesTypes.VIDEO,
                    MessagesTypes.AUDIO,
                    MessagesTypes.FILE
                ]
            ],
            size_limit: int
    ):
        detail = f"{file_type_name} size exceeds {size_limit} MB limit."
        super().__init__(detail)


class ImageCorrupted(Exception):
    def __init__(self):
        detail = "Image file is corrupted"
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
