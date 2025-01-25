from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi_cache.decorator import cache
from typing import Annotated

from schemas import (
    PrivateUser,
    UpdateUser,
    PublicUser,
    Avatars,
    UserOnline,
    UserOnlineExtended,
    GetUsers,
    GetConversationsExtended
)
from dependencies import verify_token, update_user_last_online, verify_user_is_existed
from services import (
    get_private_user,
    update_profile,
    get_public_users,
    update_avatar,
    get_avatars_paths,
    users_online,
    get_avatar_path,
    delete_avatar,
    process_search_users,
    get_conversations,
    delete_account, leave_group
)
from utilities import (
    InvalidFileType,
    FIleToBig,
    ImageCorrupted,
    FileNotFound,
    FileManager,
    UserNotFoundError,
    ConversationNotFoundError,
    IsNotAGroupError,
    AccessDeniedError
)

users_router = APIRouter(
    tags=["Users"],
    prefix="/users",
    dependencies=[Depends(update_user_last_online), Depends(verify_user_is_existed)]
)

anonymous_users_router = APIRouter(
    tags=["Users"],
    prefix="/users"
)


@users_router.get("/me", status_code=status.HTTP_200_OK, response_model=PrivateUser)
async def get_current_user_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)]
):
    profile_data = await get_private_user(current_user_id)
    return profile_data


@anonymous_users_router.get("", status_code=status.HTTP_200_OK, response_model=list[PublicUser])
async def get_users_endpoint(
        users_ids: GetUsers = Query()
):
    users_objects = await get_public_users(request_obj=users_ids)
    return users_objects


@anonymous_users_router.get("/search", status_code=status.HTTP_200_OK, response_model=list[PublicUser])
async def search_users_endpoint(
        search_query: str = Query(min_length=3, max_length=128)
):
    users_objects = await process_search_users(search_query=search_query)
    return users_objects


@anonymous_users_router.get("/{user_id}/avatar", status_code=status.HTTP_200_OK)
async def get_user_avatar_endpoint(
        user_id: int
):
    filepath = await get_avatar_path(user_id=user_id)
    return FileResponse(filepath)


@anonymous_users_router.get("/avatars", status_code=status.HTTP_200_OK)
async def get_users_avatars_endpoint(
        avatars: Avatars = Query()
):
    avatars_paths = await get_avatars_paths(avatars.users_ids)
    zip_obj = FileManager().archive_files(avatars_paths)
    return StreamingResponse(zip_obj, media_type="application/zip")


@users_router.get("/conversations", status_code=status.HTTP_200_OK, response_model=list[GetConversationsExtended])
async def get_current_user_conversations_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)]
):
    conversations_objs = await get_conversations(current_user_id=current_user_id)
    return conversations_objs


@anonymous_users_router.get("/last_online", status_code=status.HTTP_200_OK, response_model=list[UserOnlineExtended])
async def get_users_last_online_endpoint(
        users_ids: UserOnline = Query()
):
    users_last_online = await users_online(user_ids=users_ids)
    return users_last_online


@users_router.put("/me/avatar", status_code=status.HTTP_204_NO_CONTENT)
async def update_current_user_avatar_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        avatar: UploadFile = File()
):
    await update_avatar(user_id=current_user_id, avatar=avatar)


@users_router.patch("/me", status_code=status.HTTP_204_NO_CONTENT)
async def update_current_user_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        profile_data: UpdateUser
):
    await update_profile(user_id=current_user_id, profile=profile_data)


@users_router.delete("/me/avatar", status_code=status.HTTP_202_ACCEPTED)
async def delete_current_user_avatar_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)]
):
    filepath = await get_avatar_path(user_id=current_user_id)
    await delete_avatar(
        user_id=current_user_id,
        avatar_path=filepath
    )


@users_router.delete("/conversations/{group_id}", status_code=status.HTTP_202_ACCEPTED)
async def current_user_leave_from_group_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int,
        delete_messages: bool = False
):
    await leave_group(
        current_user_id=current_user_id,
        group_id=group_id,
        delete_messages=delete_messages
    )


@users_router.delete("/me", status_code=status.HTTP_202_ACCEPTED)
async def delete_current_user_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)]
):
    await delete_account(user_id=current_user_id)
