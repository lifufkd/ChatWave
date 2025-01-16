from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi_cache.decorator import cache
from typing import Annotated

from schemas import AuthorizeUser, CreateUser
from services import login, signup
from utilities import UserNotFoundError, InvalidPasswordError, UserAlreadyExists


authorization_router = APIRouter(
    tags=['Authorization'],
    prefix="/auth"
)


@authorization_router.post('/login', status_code=status.HTTP_200_OK, response_model=dict)
@cache(expire=3600)
async def login_endpoint(request: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        user_obj = AuthorizeUser(username=request.username, password=request.password)
        access_token = await login(user_obj)
        return {"access_token": access_token, "token_type": "bearer"}
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    except InvalidPasswordError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )


@authorization_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup_endpoint(request: CreateUser):
    try:
        await signup(request)
    except UserAlreadyExists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')
