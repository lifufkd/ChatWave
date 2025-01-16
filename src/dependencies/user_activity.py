from fastapi import Depends
from typing import Annotated

from dependencies import verify_token
from repository import update_user_last_online_in_db


async def process_user_last_online_update(current_user_id: Annotated[int, Depends(verify_token)]) -> None:
    await update_user_last_online_in_db(user_id=current_user_id)

