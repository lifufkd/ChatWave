from typing import Union, Literal
from fastapi import WebSocketDisconnect

from utilities import MessagesTypes


class InvalidCredentials(Exception):
    def __init__(self):
        detail = "Could not validate credentials"
        super().__init__(detail)


web_socket_invalid_data = WebSocketDisconnect(code=1000, reason="Invalid data type received")


class UserNotFoundError(Exception):
    def __init__(self, user_id: int | None = None):
        if user_id is None:
            detail = "User not found"
        else:
            detail = f"User with id ({user_id}) not found"
        super().__init__(detail)


class ConversationNotFoundError(Exception):
    def __init__(self, conversation_id: int | None = None):
        if conversation_id is None:
            detail = "Conversation not found"
        else:
            detail = f"Conversation with id ({conversation_id}) not found"
        super().__init__(detail)


class AccessDeniedError(Exception):
    def __init__(self):
        detail = "You does not have permission to perform this operation"
        super().__init__(detail)


class IsNotAGroupError(Exception):
    def __init__(self, conversation_id: int | None = None):
        if conversation_id is None:
            detail = "Conversation not a group"
        else:
            detail = f"Conversation with id ({conversation_id}) not a group"
        super().__init__(detail)


class IsNotAChatError(Exception):
    def __init__(self, conversation_id: int | None = None):
        if conversation_id is None:
            detail = "Conversation not a chat"
        else:
            detail = f"Conversation with id ({conversation_id}) not a chat"
        super().__init__(detail)


class InvalidPasswordError(Exception):
    def __init__(self):
        detail = "Invalid password"
        super().__init__(detail)


class UserAlreadyExists(Exception):
    def __init__(self, user_id: int | None = None):
        if user_id is None:
            detail = f"User already exists"
        else:
            detail = f"User with id ({user_id}) already exists"
        super().__init__(detail)


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
    def __init__(self, chat_id: int | None = None):
        if chat_id is None:
            detail = f"Chat already exists"
        else:
            detail = f"Chat with id ({chat_id}) already exists"
        super().__init__(detail)


class SameUsersIds(Exception):
    def __init__(self):
        detail = f"You cant perform this operation with your self"
        super().__init__(detail)


class FileNotFound(Exception):
    def __init__(self):
        detail = "File not found"
        super().__init__(detail)


class UserAlreadyInConversation(Exception):
    def __init__(self, user_id: int | None = None, conversation_id: int | None = None):
        if user_id is None:
            detail = "User already in conversation"
        else:
            detail = f"User with id ({user_id}) already in conversation with id ({conversation_id})"
        super().__init__(detail)


class UserNotInConversation(Exception):
    def __init__(self, user_id: int | None = None, conversation_id: int | None = None):
        if user_id is None:
            detail = "User not in conversation"
        else:
            detail = f"User with id ({user_id}) not in conversation with id ({conversation_id})"
        super().__init__(detail)


class MessageNotFound(Exception):
    def __init__(self, message_id: int | None = None):
        if message_id is None:
            detail = "Message not found"
        else:
            detail = f"Message with id ({message_id}) not found"
        super().__init__(detail)


class FileRangeError(Exception):
    def __init__(self):
        detail = "File range error"
        super().__init__(detail)
