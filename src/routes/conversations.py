from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Query, Body
from fastapi.responses import StreamingResponse, FileResponse
from typing import Annotated
from dependencies import verify_token, update_user_last_online, verify_user_is_existed
from services import (
    add_chat_conversation,
    add_group_conversation,
    update_conversation,
    update_group_avatar,
    get_group_avatar_path,
    get_groups_avatars_paths,
    delete_group_avatar,
    add_members_to_conversation,
    delete_members_from_group,
    delete_conversation,
    search_messages, get_messages, delete_all_messages
)
from schemas import (
    CreateGroup,
    EditConversation,
    AddMembersToConversation,
    DeleteGroupMembers,
    GetMessages,
    ConversationsIds
)
from utilities import (
    UserNotFoundError,
    ChatAlreadyExists,
    SameUsersIds,
    IsNotAGroupError,
    ConversationNotFoundError,
    AccessDeniedError,
    InvalidFileType,
    FIleToBig,
    ImageCorrupted,
    FileNotFound,
    FileManager,
    UserAlreadyInConversation, IsNotAChatError
)

conversations_router = APIRouter(
    tags=["Conversations"],
    prefix="/conversations",
    dependencies=[Depends(update_user_last_online), Depends(verify_user_is_existed)],
)


@conversations_router.get("/{conversation_id}/messages", status_code=status.HTTP_200_OK, response_model=list[GetMessages])
async def get_messages_from_conversation_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: int,
        limit: int = Query(10, ge=1, le=1000),
        offset: int = 0
):
    messages_objs = await get_messages(
        sender_id=current_user_id,
        conversation_id=conversation_id,
        limit=limit,
        offset=offset
    )
    return messages_objs


@conversations_router.get("/{conversation_id}/messages/search", status_code=status.HTTP_200_OK)
async def search_messages_in_conversation_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: int,
        search_query: str = Query(min_length=3, max_length=100),
):
    messages_objs = await search_messages(
        current_user_id=current_user_id,
        conversations_id=conversation_id,
        search_query=search_query
    )
    return messages_objs


@conversations_router.get("/{group_id}/avatar", status_code=status.HTTP_200_OK)
async def get_group_avatar_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int
):
    filepath = await get_group_avatar_path(current_user_id=current_user_id, group_id=group_id)
    return FileResponse(filepath)


@conversations_router.get("/avatars", status_code=status.HTTP_200_OK)
async def get_groups_avatars_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: ConversationsIds = Query()
):
    avatars_paths = await get_groups_avatars_paths(current_user_id=current_user_id, request_obj=conversation_id)
    zip_obj = FileManager().archive_files(avatars_paths)
    return StreamingResponse(zip_obj, media_type="application/zip")


@conversations_router.post("/chat", status_code=status.HTTP_200_OK)
async def create_chat_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        companion_id: int
):
    await add_chat_conversation(current_user_id=current_user_id, companion_id=companion_id)
    return {"detail": "Chat created successfully"}


@conversations_router.post("/group", status_code=status.HTTP_200_OK)
async def create_group_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_data: CreateGroup
):
    await add_group_conversation(current_user_id=current_user_id, group_data=group_data)
    return {"detail": "Group created successfully"}


@conversations_router.post("/{group_id}/members", status_code=status.HTTP_200_OK, response_model=dict)
async def add_members_to_group_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int,
        request: AddMembersToConversation = Body()
):
    await add_members_to_conversation(current_user_id=current_user_id, group_id=group_id, request_data=request)
    return {"detail": "Members added successfully"}


@conversations_router.put("/{group_id}/avatar", status_code=status.HTTP_204_NO_CONTENT)
async def update_group_avatar_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int,
        avatar: UploadFile = File()
):
    await update_group_avatar(current_user_id=current_user_id, group_id=group_id, avatar=avatar)


@conversations_router.patch("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_group_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int,
        group_data: EditConversation
):
    await update_conversation(current_user_id=current_user_id, group_id=group_id, group_obj=group_data)


@conversations_router.delete("/{group_id}/avatar", status_code=status.HTTP_202_ACCEPTED)
async def delete_group_avatar_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int
):
    filepath = await get_group_avatar_path(current_user_id=current_user_id, group_id=group_id)
    await delete_group_avatar(
        current_user_id=current_user_id,
        group_id=group_id,
        avatar_path=filepath
    )


@conversations_router.delete("/{group_id}/members", status_code=status.HTTP_202_ACCEPTED)
async def delete_members_from_group_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int,
        members: list[DeleteGroupMembers] = Body()
):
    await delete_members_from_group(
        current_user_id=current_user_id,
        group_id=group_id,
        members=members
    )


@conversations_router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: int
):
    await delete_conversation(current_user_id=current_user_id, conversation_id=conversation_id)


@conversations_router.delete("/{chat_id}/messages", status_code=status.HTTP_202_ACCEPTED)
async def delete_chat_messages_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        chat_id: int
):
    await delete_all_messages(current_user_id=current_user_id, chat_id=chat_id)
