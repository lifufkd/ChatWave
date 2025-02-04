import asyncio
from fastapi import (
    APIRouter,
    Depends,
    status,
    UploadFile,
    File,
    Query,
    Body,
    WebSocket,
    WebSocketDisconnect
)
from fastapi.responses import StreamingResponse
from typing import Annotated
from schemas import (
    PrivateUser,
    UpdateUser,
    PublicUser,
    Avatar,
    UsersIds,
    UserOnline,
    GetConversationsDB, GetUnreadMessages
)
from dependencies import verify_token
from storage import FileManager
from utilities import UserNotFoundError, web_socket_invalid_data
from validators import update_user_last_online, verify_current_user_is_existed
from services import (
    fetch_private_user,
    update_user_profile,
    fetch_public_users,
    upload_user_avatar,
    fetch_users_avatars_paths,
    fetch_users_online_status,
    fetch_user_avatar_metadata,
    remove_user_avatar,
    search_users_by_nickname,
    fetch_user_conversations,
    remove_user_account,
    leave_group, fetch_user_unread_messages
)

users_router = APIRouter(
    tags=["Users"],
    prefix="/users",
    dependencies=[Depends(update_user_last_online), Depends(verify_current_user_is_existed)]
)

anonymous_users_router = APIRouter(
    tags=["Users"],
    prefix="/users"
)


@users_router.get("/me", status_code=status.HTTP_200_OK, response_model=PrivateUser)
async def get_current_user(
        current_user_id: Annotated[int, Depends(verify_token)]
):
    profile_data = await fetch_private_user(user_id=current_user_id)
    return profile_data


@anonymous_users_router.get("", status_code=status.HTTP_200_OK, response_model=list[PublicUser])
async def get_users(
        user_id: UsersIds = Query()
):
    users_objects = await fetch_public_users(users_ids=user_id.users_ids)
    return users_objects


@anonymous_users_router.get("/search", status_code=status.HTTP_200_OK, response_model=list[PublicUser])
async def search_users(
        search_query: str = Query(min_length=3, max_length=128),
        limit: int | None = Query(None, ge=1, le=1000),
):
    users_objects = await search_users_by_nickname(search_query=search_query, limit=limit)
    return users_objects


@anonymous_users_router.get("/{user_id}/avatar", status_code=status.HTTP_200_OK)
async def get_user_avatar(
        user_id: int
):
    metadata = await fetch_user_avatar_metadata(user_id=user_id)
    return StreamingResponse(metadata["file_path"].open("rb"), media_type=metadata["file_type"])


@anonymous_users_router.get("/avatars", status_code=status.HTTP_200_OK)
async def get_users_avatars(
        user_id: UsersIds = Query()
):
    avatars_paths = await fetch_users_avatars_paths(users_ids=user_id.users_ids)
    zip_obj = await FileManager().archive_files(avatars_paths)
    return StreamingResponse(zip_obj, media_type="application/zip")


@users_router.get("/conversations", status_code=status.HTTP_200_OK, response_model=list[GetConversationsDB])
async def get_current_user_conversations(
        current_user_id: Annotated[int, Depends(verify_token)]
):
    conversations_objs = await fetch_user_conversations(user_id=current_user_id)
    return conversations_objs


@anonymous_users_router.get("/online", status_code=status.HTTP_200_OK, response_model=list[UserOnline])
async def get_users_last_online_rest(
        user_id: UsersIds = Query()
):
    users_last_online = await fetch_users_online_status(users_ids=user_id.users_ids)
    return users_last_online


@anonymous_users_router.websocket("/ws/online")
async def get_users_last_online_ws(websocket: WebSocket):
    copy_users_ids = list()

    async def send_status_periodically():
        while True:
            if not copy_users_ids:
                await asyncio.sleep(5)
                continue

            result = list()
            users_online_status_objs = await fetch_users_online_status(users_ids=copy_users_ids)
            for user_online_obj in users_online_status_objs:
                result.append(
                    {
                        "user_id": user_online_obj.user_id,
                        "last_online": user_online_obj.last_online.strftime("%Y-%m-%d %H:%M:%S")
                    }
                )

            await websocket.send_json(result)
            await asyncio.sleep(5)

    await websocket.accept()
    task = asyncio.create_task(send_status_periodically())

    try:
        while True:
            users_ids = await websocket.receive_json()
            if not isinstance(users_ids, list):
                raise web_socket_invalid_data
            if users_ids != copy_users_ids:
                try:
                    copy_users_ids = [int(user_id) for user_id in users_ids.copy()]
                except ValueError:
                    raise web_socket_invalid_data
    except WebSocketDisconnect:
        pass
    finally:
        if not task:
            return
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


@users_router.get("/messages/unread", status_code=status.HTTP_200_OK, response_model=list[GetUnreadMessages])
async def get_current_user_unread_messages(
        current_user_id: Annotated[int, Depends(verify_token)]
):
    unread_messages_objs = await fetch_user_unread_messages(user_id=current_user_id)
    return unread_messages_objs


@users_router.put("/me/avatar", status_code=status.HTTP_204_NO_CONTENT)
async def update_current_user_avatar(
        current_user_id: Annotated[int, Depends(verify_token)],
        avatar: UploadFile = File()
):
    avatar_obj = Avatar(
        file=await avatar.read(),
        file_name=avatar.filename,
        content_type=avatar.content_type
    )
    await upload_user_avatar(user_id=current_user_id, avatar_data=avatar_obj)


@users_router.patch("/me", status_code=status.HTTP_204_NO_CONTENT)
async def update_current_user(
        current_user_id: Annotated[int, Depends(verify_token)],
        request: UpdateUser = Body()
):
    await update_user_profile(user_id=current_user_id, profile_data=request)


@users_router.delete("/me/avatar", status_code=status.HTTP_202_ACCEPTED)
async def delete_current_user_avatar(
        current_user_id: Annotated[int, Depends(verify_token)]
):
    metadata = await fetch_user_avatar_metadata(user_id=current_user_id)
    await remove_user_avatar(
        user_id=current_user_id,
        avatar_path=metadata["file_path"]
    )


@users_router.delete("/conversations/{group_id}", status_code=status.HTTP_202_ACCEPTED)
async def current_user_leave_from_group(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int,
        delete_messages: bool = False
):
    await leave_group(
        user_id=current_user_id,
        group_id=group_id,
        delete_messages=delete_messages
    )


@users_router.delete("/me", status_code=status.HTTP_202_ACCEPTED)
async def delete_current_user(
        current_user_id: Annotated[int, Depends(verify_token)]
):
    await remove_user_account(user_id=current_user_id)
