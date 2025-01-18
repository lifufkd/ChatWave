from fastapi import Depends
from typing import Annotated

from dependencies import verify_token
from repository import update_user_last_online_in_db, check_user_is_existed
from utilities import UserNotFoundError


async def update_user_last_online(current_user_id: Annotated[int, Depends(verify_token)]) -> None:
    await update_user_last_online_in_db(user_id=current_user_id)


async def verify_user_is_existed(current_user_id: Annotated[int, Depends(verify_token)]) -> None:
    if not (await check_user_is_existed(user_id=current_user_id)):
        raise UserNotFoundError()

