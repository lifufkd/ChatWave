from fastapi import Depends
from typing import Annotated

from dependencies import verify_token, redis_client
from repository import update_user_last_online


async def update_last_online(current_user_id: Annotated[int, Depends(verify_token)]) -> None:
    await update_user_last_online(user_id=current_user_id)
    await redis_client.publish(f"user:last_online_events", str(current_user_id))
