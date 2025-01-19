from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Annotated, Optional
from utilities import ValidateModelNotEmpty, request_limit


class UserIds(BaseModel):
    conversations_ids: list[int]

    @field_validator('conversations_ids', mode='after')
    def set_limits(cls, values):
        return request_limit(values)


class CreateGroup(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=64)]
    description: Annotated[Optional[str], Field(None)]


class EditConversation(ValidateModelNotEmpty):
    name: Annotated[Optional[str], Field(None, min_length=1, max_length=64)]
    description: Annotated[Optional[str], Field(None)]


class EditConversationExtended(EditConversation):
    avatar_name: Annotated[Optional[str], Field(None)]
    avatar_type: Annotated[Optional[str], Field(None)]


class GroupsAvatars(UserIds):
    pass


class AddMembersToConversation(BaseModel):
    group_id: int
    users_ids: list[int]

    @field_validator('users_ids', mode='after')
    def set_limits(cls, values):
        return request_limit(values)