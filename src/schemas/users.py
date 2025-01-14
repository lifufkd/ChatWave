from pydantic import BaseModel, Field


class AuthorizeUser(BaseModel):
    id: int | None = None
    username: str
    password: str
    password_hash: str | None = None


class CreateUser(BaseModel):
    nickname: str = Field(min_length=3, max_length=128)
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)


class CreateUserExtended(CreateUser):
    password_hash: str | None = None


