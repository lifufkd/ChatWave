from pydantic import BaseModel, Field, field_validator
from typing import Annotated, Optional
from datetime import datetime, date
from utilities import validate_password, request_limit, ConversationMemberRoles


class UsersIds(BaseModel):
    users_ids: list[int]

    @field_validator('users_ids', mode='after')
    def set_limits(cls, values):
        return request_limit(values)


class CreateUser(BaseModel):
    nickname: Annotated[str, Field(min_length=3, max_length=128)]
    username: Annotated[str, Field(min_length=3, max_length=64)]
    password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator('password')
    def validate_password(cls, value):
        return validate_password(value)


class CreateUserDB(BaseModel):
    nickname: Annotated[str, Field(min_length=3, max_length=128)]
    username: Annotated[str, Field(min_length=3, max_length=64)]
    password_hash: str


class PublicUser(BaseModel):
    id: int
    nickname: Annotated[str, Field(min_length=3, max_length=128)]
    birthday: Optional[date]
    bio: Optional[str]
    avatar_name: Optional[str]
    avatar_type: Optional[str]
    last_online: Optional[datetime]
    created_at: datetime


class PrivateUser(PublicUser):
    username: Annotated[str, Field(min_length=3, max_length=64)]
    updated_at: Optional[datetime]


class UserRole(BaseModel):
    user_id: int
    user_role: ConversationMemberRoles


class UpdateUser(BaseModel):
    nickname: Annotated[Optional[str], Field(None, min_length=3, max_length=128)]
    password: Annotated[Optional[str], Field(None, min_length=8, max_length=128)]
    birthday: Annotated[Optional[date], Field(None)]
    bio: Annotated[Optional[str], Field(None, max_length=8192)]

    @field_validator('password')
    def validate_password(cls, value):
        return validate_password(value)


class UpdateUserDB(BaseModel):
    nickname: Annotated[Optional[str], Field(None, min_length=3, max_length=128)]
    password_hash: Annotated[Optional[str], Field(None)]
    birthday: Annotated[Optional[date], Field(None)]
    bio: Annotated[Optional[str], Field(None, max_length=8192)]
    avatar_name: Annotated[Optional[str], Field(None)]
    avatar_type: Annotated[Optional[str], Field(None)]


class Avatar(BaseModel):
    file: bytes
    file_name: str
    content_type: str


class UserOnline(BaseModel):
    user_id: int
    last_online: Optional[datetime]
