from typing import Optional, Annotated
from pydantic import BaseModel, Field
from datetime import datetime

from utilities import MessagesStatus, MessagesTypes


class CreateTextMessage(BaseModel):
    content: str


class CreateMediaMessage(BaseModel):
    file: bytes
    file_name: str
    file_type: str
    is_voice_message: bool


class CreateMediaMessageDB(BaseModel):
    file_content_name: str
    file_content_type: str
    status: MessagesStatus
    type: MessagesTypes


class CreateTextMessageExtended(CreateTextMessage):
    status: MessagesStatus
    type: MessagesTypes

