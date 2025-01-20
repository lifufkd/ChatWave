from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Query
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
    add_members_to_conversation
)
from schemas import CreateGroup, EditConversation, GroupsAvatars, AddMembersToConversation
from utilities import (
    UserNotFoundError,
    ChatAlreadyExists,
    ConversationTypes,
    SameUsersIds,
    IsNotAGroupError,
    ConversationMemberRoles,
    ConversationNotFoundError,
    AccessDeniedError,
    InvalidFileType,
    FIleToBig,
    ImageCorrupted,
    FileNotFound,
    FileManager,
    UserAlreadyInConversation
)

conversations_router = APIRouter(
    tags=["Conversations"],
    prefix="/conversations",
    dependencies=[Depends(update_user_last_online), Depends(verify_user_is_existed)],
)

anonymous_conversations_router = APIRouter(
    tags=["Conversations"],
    prefix="/conversations"
)


@conversations_router.post("/chat", status_code=status.HTTP_200_OK)
async def create_chat_endpoint(current_user_id: Annotated[int, Depends(verify_token)], companion_id: int):
    try:
        await add_chat_conversation(current_user_id=current_user_id, companion_id=companion_id)
    except SameUsersIds:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="You can't create a chat with yourself")
    except ChatAlreadyExists:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Chat already exists")
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"detail": "Chat created successfully"}


@conversations_router.post("/group", status_code=status.HTTP_200_OK)
async def create_group_endpoint(current_user_id: Annotated[int, Depends(verify_token)], group_data: CreateGroup):
    try:
        await add_group_conversation(current_user_id=current_user_id, group_data=group_data)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"detail": "Group created successfully"}


@conversations_router.patch("/{group_id}/group", status_code=status.HTTP_204_NO_CONTENT)
async def update_group_endpoint(current_user_id: Annotated[int, Depends(verify_token)], group_id: int, group_data: EditConversation):
    try:
        await update_conversation(current_user_id=current_user_id, group_id=group_id, group_obj=group_data)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    except IsNotAGroupError:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Conversation not a group")
    except AccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You does not have permission to perform this operation")


@conversations_router.post("/members", status_code=status.HTTP_200_OK, response_model=dict)
async def add_members_to_conversation_endpoint(current_user_id: Annotated[int, Depends(verify_token)], request: AddMembersToConversation):
    try:
        await add_members_to_conversation(current_user_id=current_user_id, request_data=request)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    except IsNotAGroupError:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Conversation not a group")
    except UserAlreadyInConversation:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User already in group")
    except AccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You does not have permission to perform this operation")

    return {"detail": "Members added successfully"}


@conversations_router.put("/{group_id}/avatar", status_code=status.HTTP_204_NO_CONTENT)
async def update_my_group_avatar_endpoint(current_user_id: Annotated[int, Depends(verify_token)], group_id: int, avatar: UploadFile = File()):
    try:
        await update_group_avatar(current_user_id=current_user_id, group_id=group_id, avatar=avatar)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    except IsNotAGroupError:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Conversation not a group")
    except AccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You does not have permission to perform this operation")
    except InvalidFileType as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FIleToBig as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ImageCorrupted as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@conversations_router.delete("/{group_id}/avatar", status_code=status.HTTP_202_ACCEPTED)
async def delete_my_group_avatar_endpoint(current_user_id: Annotated[int, Depends(verify_token)], group_id: int):
    try:
        filepath = await get_group_avatar_path(current_user_id=current_user_id, group_id=group_id)
        await delete_group_avatar(
            current_user_id=current_user_id,
            group_id=group_id,
            avatar_path=filepath
        )
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    except IsNotAGroupError:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Conversation not a group")
    except AccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You does not have permission to perform this operation")
    except FileNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")


@conversations_router.get("/{conversations_id}/avatar", status_code=status.HTTP_200_OK)
async def get_my_group_avatar_endpoint(current_user_id: Annotated[int, Depends(verify_token)], group_id: int):
    try:
        filepath = await get_group_avatar_path(current_user_id=current_user_id, group_id=group_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    except IsNotAGroupError:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Conversation not a group")
    except AccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You does not have permission to perform this operation")
    except FileNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return FileResponse(filepath)


@conversations_router.get("/avatars", status_code=status.HTTP_200_OK)
async def get_my_groups_avatars_endpoint(current_user_id: Annotated[int, Depends(verify_token)], request_obj: GroupsAvatars = Query()):
    try:
        avatars_paths = await get_groups_avatars_paths(current_user_id=current_user_id, request_obj=request_obj)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    except IsNotAGroupError:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Conversation not a group")
    except AccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You does not have permission to perform this operation")
    except FileNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    zip_obj = FileManager().pack_to_zip_files(avatars_paths)
    return StreamingResponse(zip_obj, media_type="application/zip")
