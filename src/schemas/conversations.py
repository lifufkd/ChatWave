from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Annotated, Optional

from .users import UserRole
from utilities import ValidateModelNotEmpty, request_limit, ConversationTypes, ConversationMemberRoles


class ConversationsIds(BaseModel):
    conversations_ids: list[int]

    @field_validator('conversations_ids', mode='after')
    def set_limits(cls, values):
        return request_limit(values)


class CreateEmptyConversation(BaseModel):
    creator_id: int
    type: ConversationTypes


class CreateGroup(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=64)]
    description: Annotated[Optional[str], Field(None)]


class CreateGroupDB(CreateEmptyConversation, CreateGroup):
    pass


class EditConversation(ValidateModelNotEmpty):
    name: Annotated[Optional[str], Field(None, min_length=1, max_length=64)]
    description: Annotated[Optional[str], Field(None)]


class EditConversationDB(EditConversation):
    avatar_name: Annotated[Optional[str], Field(None)]
    avatar_type: Annotated[Optional[str], Field(None)]


class GetConversations(BaseModel):
    id: int
    type: ConversationTypes
    name: Annotated[Optional[str], Field(min_length=1, max_length=64)]
    description: Optional[str]
    avatar_name: Optional[str]
    avatar_type: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class GetConversationsWithMembers(GetConversations):
    members: list["UserRole"]


class DeleteGroupMembers(BaseModel):
    user_id: int
    delete_messages: bool
