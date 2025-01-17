from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated

from dependencies import verify_token, process_user_last_online_update
from services import add_chat_conversation, add_group_conversation
from schemas import CreateGroup
from utilities import SameUsersIds, UserNotFoundError, ChatAlreadyExists

conversations_router = APIRouter(
    tags=["Conversations"],
    prefix="/conversations",
    dependencies=[Depends(process_user_last_online_update)],
)

anonymous_conversations_router = APIRouter(
    tags=["Conversations"],
    prefix="/conversations",
    dependencies=[Depends(process_user_last_online_update)],
)


@conversations_router.post("/create_chat", status_code=status.HTTP_200_OK)
async def create_chat_endpoint(current_user_id: Annotated[int, Depends(verify_token)], companion_id: int):
    try:
        await add_chat_conversation(current_user_id=current_user_id, companion_id=companion_id)
    except SameUsersIds:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="You can't create a chat with yourself")
    except ChatAlreadyExists:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Chat already exists")
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User not found")

    return {"detail": "Chat created successfully"}


@conversations_router.post("/create_group", status_code=status.HTTP_200_OK)
async def create_chat_endpoint(current_user_id: Annotated[int, Depends(verify_token)], group_data: CreateGroup):
    try:
        await add_group_conversation(current_user_id=current_user_id, group_data=group_data)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User not found")

    return {"detail": "Group created successfully"}

