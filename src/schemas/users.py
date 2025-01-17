from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Annotated, Optional
from datetime import datetime, date
from utilities import validate_password, validate_nicknames, validate_nicknames_and_ids, request_limit


class AnswerLimit(BaseModel):
    limit: Annotated[int, Field(0, ge=1, le=1000)]


class UserIds(BaseModel):
    users_ids: list[int]

    @field_validator('users_ids', mode='after')
    def set_limits(cls, values):
        return request_limit(values)


class AuthorizeUser(BaseModel):
    id: Annotated[Optional[int], Field(None)]
    username: str
    password: str
    password_hash: Annotated[Optional[str], Field(None)]


class CreateUser(BaseModel):
    nickname: Annotated[str, Field(min_length=3, max_length=128)]
    username: Annotated[str, Field(min_length=3, max_length=64)]
    password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator('password')
    def validate_password(cls, value):
        return validate_password(value)


class CreateUserExtended(CreateUser):
    password_hash: Annotated[Optional[str], Field(None)]


class PublicUser(BaseModel):
    id: int
    nickname: Annotated[str, Field(min_length=3, max_length=128)]
    birthday: Optional[date]
    bio: Optional[str]
    last_online: Optional[datetime]
    created_at: datetime


class PrivateUser(PublicUser):
    username: Annotated[str, Field(min_length=3, max_length=64)]
    updated_at: Optional[datetime]


class UpdateUser(BaseModel):
    nickname: Annotated[Optional[str], Field(None, min_length=3, max_length=128)]
    password: Annotated[Optional[str], Field(None, min_length=8, max_length=128)]
    birthday: Annotated[Optional[date], Field(None)]
    bio: Annotated[Optional[str], Field(None)]

    @field_validator('password')
    def validate_password(cls, value):
        return validate_password(value)


class UpdateUserExtended(UpdateUser):
    password_hash: Annotated[Optional[str], Field(None)]


class SearchUser(AnswerLimit):
    ids: Annotated[Optional[list[int]], Field(None)]
    nickname: Annotated[Optional[str], Field(None)]

    @field_validator('nickname', mode='before')
    def validate_nicknames(cls, value):
        return validate_nicknames(value)

    @model_validator(mode='before')
    def check_only_one_field_filled(cls, values):
        return validate_nicknames_and_ids(values)

    @field_validator('ids', mode='after')
    def set_limits(cls, values):
        return request_limit(values)


class Avatars(UserIds):
    pass


class UserOnline(UserIds):
    pass


class UserOnlineExtended(BaseModel):
    user_id: int
    last_online: Optional[datetime]
