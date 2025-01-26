from fastapi import APIRouter, Depends, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi_cache.decorator import cache
from typing import Annotated

from schemas import AuthorizeUser, CreateUser
from services import get_access_token, add_user


authorization_router = APIRouter(
    tags=['Authorization'],
    prefix="/auth"
)


@authorization_router.post('/login', status_code=status.HTTP_200_OK, response_model=dict)
@cache(expire=3600)
async def login_endpoint(request: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_obj = AuthorizeUser(username=request.username, password=request.password)
    access_token = await get_access_token(user_obj)
    return {"access_token": access_token, "token_type": "bearer"}


@authorization_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup_endpoint(request: CreateUser):
    await add_user(request)
