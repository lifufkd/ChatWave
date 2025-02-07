from fastapi import Depends
from typing import Annotated

from dependencies import verify_token
from repository import is_user_exists
from utilities import UserNotFoundError


async def verify_user_is_existed(user_id: int) -> None:
    if not (await is_user_exists(user_id=user_id)):
        raise UserNotFoundError(user_id=user_id)


async def verify_users_is_existed(users_ids: list[int]) -> None:
    for user_id in users_ids:
        await verify_user_is_existed(user_id=user_id)


async def verify_current_user_is_existed(current_user_id: Annotated[int, Depends(verify_token)]) -> None:
    if not (await is_user_exists(user_id=current_user_id)):
        raise UserNotFoundError(user_id=current_user_id)
