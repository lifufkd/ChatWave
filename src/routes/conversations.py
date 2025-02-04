from fastapi import APIRouter, Depends, status, UploadFile, File, Query, Body, Form
from fastapi.responses import StreamingResponse
from typing import Annotated, Optional

from dependencies import verify_token
from schemas.unread_messages import AddUnreadMessages
from utilities import EntitiesTypes
from validators import update_user_last_online, verify_current_user_is_existed
from services import (
    create_private_conversation,
    create_group_conversation,
    edit_group_details,
    upload_group_avatar,
    fetch_group_avatar_metadata,
    fetch_group_avatars_paths,
    add_group_members,
    remove_group_avatar,
    remove_group_members,
    delete_conversation_by_id,
    search_conversation_messages,
    fetch_messages,
    delete_all_messages,
    create_media_message,
    create_text_message, add_unread_messages
)
from schemas import (
    CreateGroup,
    EditConversation,
    UsersIds,
    DeleteGroupMembers,
    GetMessage,
    ConversationsIds,
    GetConversations,
    Avatar,
    CreateMediaMessage,
    CreateTextMessage
)
from storage import FileManager

conversations_router = APIRouter(
    tags=["Conversations"],
    prefix="/conversations",
    dependencies=[Depends(update_user_last_online), Depends(verify_current_user_is_existed)],
)


@conversations_router.get("/{conversation_id}/messages", status_code=status.HTTP_200_OK, response_model=list[GetMessage])
async def get_messages_from_conversation(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: int,
        limit: int = Query(10, ge=1, le=1000),
        offset: int = Query(0, ge=0),
):
    messages_objs = await fetch_messages(
        sender_id=current_user_id,
        conversation_id=conversation_id,
        limit=limit,
        offset=offset
    )
    return messages_objs


@conversations_router.get("/{conversation_id}/messages/search", status_code=status.HTTP_200_OK, response_model=list[GetMessage])
async def search_messages_in_conversation(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: int,
        search_query: str = Query(min_length=3, max_length=128),
        limit: int = Query(10, ge=1, le=1000)
):
    messages_objs = await search_conversation_messages(
        user_id=current_user_id,
        conversations_id=conversation_id,
        search_query=search_query,
        limit=limit
    )
    return messages_objs


@conversations_router.get("/{group_id}/avatar", status_code=status.HTTP_200_OK)
async def get_group_avatar(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int
):
    metadata = await fetch_group_avatar_metadata(user_id=current_user_id, group_id=group_id)
    return StreamingResponse(metadata["file_path"].open("rb"), media_type=metadata["file_type"])


@conversations_router.get("/avatars", status_code=status.HTTP_200_OK)
async def get_groups_avatars(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: ConversationsIds = Query()
):
    avatars_paths = await fetch_group_avatars_paths(
        user_id=current_user_id,
        conversations_ids=conversation_id.conversations_ids
    )
    zip_obj = await FileManager().archive_files(avatars_paths)
    return StreamingResponse(zip_obj, media_type="application/zip")


@conversations_router.post("/chat", status_code=status.HTTP_200_OK, response_model=GetConversations)
async def create_chat(
        current_user_id: Annotated[int, Depends(verify_token)],
        recipient_id: int
):
    new_conversation = await create_private_conversation(user_id=current_user_id, recipient_id=recipient_id)
    return new_conversation


@conversations_router.post("/group", status_code=status.HTTP_200_OK, response_model=GetConversations)
async def create_group(
        current_user_id: Annotated[int, Depends(verify_token)],
        request: CreateGroup = Body()
):
    new_conversation = await create_group_conversation(user_id=current_user_id, group_data=request)
    return new_conversation


@conversations_router.post("/{group_id}/members", status_code=status.HTTP_201_CREATED)
async def add_members_to_group(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int,
        user_id: UsersIds = Query()
):
    await add_group_members(user_id=current_user_id, group_id=group_id, users_ids=user_id.users_ids)


@conversations_router.post("/{conversation_id}/text", status_code=status.HTTP_200_OK, response_model=GetMessage)
async def send_text_message(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: int,
        request: CreateTextMessage = Body()
):
    new_message_obj = await create_text_message(
        sender_id=current_user_id,
        conversation_id=conversation_id,
        content=request.content
    )
    return new_message_obj


@conversations_router.post("/{conversation_id}/media", status_code=status.HTTP_200_OK, response_model=GetMessage)
async def send_media_message(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: int,
        is_voice_message: bool = False,
        caption: Optional[str] = Form(None),
        file: UploadFile = File()
):
    new_message_obj = CreateMediaMessage(
        file=file.file.read(),
        file_name=file.filename,
        file_type=file.content_type,
        caption=caption,
        is_voice_message=is_voice_message
    )
    new_message_obj = await create_media_message(
        sender_id=current_user_id,
        conversation_id=conversation_id,
        content_data=new_message_obj
    )
    return new_message_obj


@conversations_router.post("/{conversation_id}/entities/{entity_id}", status_code=status.HTTP_200_OK)
async def create_unread_messages(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: int,
        entity_id: int,
        entity_type: EntitiesTypes = Query(),
        users_ids: list[int] = Query()
):
    entity_data = AddUnreadMessages(**{f"{entity_type.value}_id": entity_id})
    await add_unread_messages(
        user_id=current_user_id,
        conversation_id=conversation_id,
        users_ids=users_ids,
        entity_data=entity_data
    )


@conversations_router.put("/{group_id}/avatar", status_code=status.HTTP_204_NO_CONTENT)
async def update_group_avatar(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int,
        avatar: UploadFile = File()
):
    avatar_obj = Avatar(
        file=await avatar.read(),
        file_name=avatar.filename,
        content_type=avatar.content_type
    )
    await upload_group_avatar(user_id=current_user_id, group_id=group_id, avatar_data=avatar_obj)


@conversations_router.patch("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_group(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int,
        request: EditConversation = Body()
):
    await edit_group_details(user_id=current_user_id, group_id=group_id, group_data=request)


@conversations_router.delete("/{group_id}/avatar", status_code=status.HTTP_202_ACCEPTED)
async def delete_group_avatar(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int
):
    metadata = await fetch_group_avatar_metadata(user_id=current_user_id, group_id=group_id)
    await remove_group_avatar(
        user_id=current_user_id,
        group_id=group_id,
        avatar_path=metadata["file_path"]
    )


@conversations_router.delete("/{group_id}/members", status_code=status.HTTP_202_ACCEPTED)
async def delete_members_from_group(
        current_user_id: Annotated[int, Depends(verify_token)],
        group_id: int,
        request: list[DeleteGroupMembers] = Body()
):
    await remove_group_members(
        user_id=current_user_id,
        group_id=group_id,
        members_data=request
    )


@conversations_router.delete("/{conversation_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_conversation(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: int
):
    await delete_conversation_by_id(user_id=current_user_id, conversation_id=conversation_id)


@conversations_router.delete("/{chat_id}/messages", status_code=status.HTTP_202_ACCEPTED)
async def delete_chat_messages(
        current_user_id: Annotated[int, Depends(verify_token)],
        chat_id: int
):
    await delete_all_messages(user_id=current_user_id, conversation_id=chat_id)
