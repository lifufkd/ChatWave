from fastapi import APIRouter, Depends, UploadFile, File, status, Query, Body, Form
from fastapi.responses import FileResponse, StreamingResponse
from typing import Annotated, Optional

from dependencies import verify_token
from validators import update_user_last_online, verify_current_user_is_existed
from storage import FileManager
from services import (
    create_text_message,
    create_media_message,
    update_user_message,
    fetch_message_media_path,
    fetch_messages_media_paths,
    remove_messages
)
from schemas import CreateMediaMessage, MessagesIds, GetMessage, CreateTextMessage

messages_router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
    dependencies=[Depends(update_user_last_online), Depends(verify_current_user_is_existed)]
)


@messages_router.get("/{message_id}/media", status_code=status.HTTP_200_OK)
async def get_message_media(
        current_user_id: Annotated[int, Depends(verify_token)],
        message_id: int
):
    filepath = await fetch_message_media_path(sender_id=current_user_id, message_id=message_id)
    return FileResponse(filepath)


@messages_router.get("/media", status_code=status.HTTP_200_OK)
async def get_messages_medias(
        current_user_id: Annotated[int, Depends(verify_token)],
        message_id: MessagesIds = Query()
):
    messages_media_paths = await fetch_messages_media_paths(
        sender_id=current_user_id,
        messages_ids=message_id.messages_ids
    )
    zip_obj = await FileManager().archive_files(messages_media_paths)
    return StreamingResponse(zip_obj, media_type="application/zip")


@messages_router.post("/{conversation_id}/text", status_code=status.HTTP_200_OK, response_model=GetMessage)
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


@messages_router.post("/{conversation_id}/media", status_code=status.HTTP_200_OK, response_model=GetMessage)
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


@messages_router.patch("/{message_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_message(
        current_user_id: Annotated[int, Depends(verify_token)],
        message_id: int,
        request: CreateTextMessage = Body()
):
    await update_user_message(sender_id=current_user_id, message_id=message_id, content=request.content)


@messages_router.delete("", status_code=status.HTTP_202_ACCEPTED)
async def delete_messages(
        current_user_id: Annotated[int, Depends(verify_token)],
        message_id: MessagesIds = Query()
):
    await remove_messages(user_id=current_user_id, messages_ids=message_id.messages_ids)
