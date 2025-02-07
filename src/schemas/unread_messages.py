from typing import Optional, Annotated
from pydantic import BaseModel, Field, model_validator

from utilities import check_exclusive_fields


class UnreadMessageBase(BaseModel):
    user_id: int
    conversation_id: int


class GetUnreadMessages(UnreadMessageBase):
    id: int
    message_id: Optional[int]
    call_id: Optional[int]


class UnreadMessageExistedDTO(UnreadMessageBase):
    message_id: Annotated[Optional[int], Field(None)]
    call_id: Annotated[Optional[int], Field(None)]


class FilterUnreadMessages(BaseModel):
    user_id: Annotated[Optional[int], Field(None)]
    conversation_id: Annotated[Optional[int], Field(None)]
    message_id: Annotated[Optional[int], Field(None)]
    call_id: Annotated[Optional[int], Field(None)]


class AddUnreadMessages(BaseModel):
    message_id: Annotated[Optional[int], Field(None)]
    call_id: Annotated[Optional[int], Field(None)]

    @model_validator(mode="before")
    def set_check_exclusive_fields(cls, values):
        return check_exclusive_fields(values)


class AddUnreadMessagesDB(BaseModel):
    users_ids: list[int]
    conversation_id: int
    message_id: Annotated[Optional[int], Field(None)]
    call_id: Annotated[Optional[int], Field(None)]
