from typing import Annotated, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

from utilities import MessagesStatus, MessagesTypes, request_limit


class MessagesIds(BaseModel):
    messages_ids: list[int]

    @field_validator('messages_ids', mode='after')
    def set_limits(cls, values):
        return request_limit(values)


class CreateTextMessage(BaseModel):
    content: str = Field(max_length=8192)


class CreateTextMessageDB(BaseModel):
    content: str
    status: MessagesStatus
    type: MessagesTypes


class CreateMediaMessage(BaseModel):
    file: bytes
    file_name: str
    file_type: str
    caption: Annotated[Optional[str], Field(max_length=8192)]
    is_voice_message: bool


class CreateMediaMessageDB(BaseModel):
    file_content_name: str
    file_content_type: str
    status: MessagesStatus
    type: MessagesTypes
    content: Annotated[Optional[str], Field(max_length=8192)]


class GetMessage(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    status: MessagesStatus
    type: MessagesTypes
    content: Optional[str]
    file_content_name: Optional[str]
    file_content_type: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
