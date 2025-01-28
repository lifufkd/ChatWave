from fastapi import APIRouter, Depends, UploadFile, File, status, Form, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import Annotated, Optional

from dependencies import verify_token
from validators import update_user_last_online, verify_current_user_is_existed
from storage import FileManager
from services import (
    create_text_message,
    create_media_message,
    update_message,
    get_message_media_path,
    get_messages_media_paths,
    delete_messages
)
from schemas import CreateTextMessage, CreateMediaMessage, UpdateMessage, MessagesIds

messages_router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
    dependencies=[Depends(update_user_last_online), Depends(verify_current_user_is_existed)]
)


@messages_router.get("/{message_id}/media", status_code=status.HTTP_200_OK)
async def get_message_media_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        message_id: int
):
    filepath = await get_message_media_path(sender_id=current_user_id, message_id=message_id)
    return FileResponse(filepath)


@messages_router.get("/media", status_code=status.HTTP_200_OK)
async def get_messages_medias_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        message_id: MessagesIds = Query()
):
    messages_media_paths = await get_messages_media_paths(
        sender_id=current_user_id,
        messages_ids=message_id.messages_ids
    )
    zip_obj = await FileManager().archive_files(messages_media_paths)
    return StreamingResponse(zip_obj, media_type="application/zip")


@messages_router.post("/{conversation_id}/text", status_code=status.HTTP_201_CREATED)
async def send_text_message_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: int,
        content: CreateTextMessage
):
    await create_text_message(sender_id=current_user_id, conversation_id=conversation_id, content=content)
    return {"detail": "Message sent successfully"}


@messages_router.post("/{conversation_id}/media", status_code=status.HTTP_201_CREATED)
async def send_media_message_endpoint(
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
    await create_media_message(sender_id=current_user_id, conversation_id=conversation_id, content=new_message_obj)
    return {"detail": "Message sent successfully"}


@messages_router.patch("/{message_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_message_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        message_id: int,
        content: UpdateMessage
):
    await update_message(sender_id=current_user_id, message_id=message_id, message_data=content)
    return {"detail": "Message successfully updated"}


@messages_router.delete("", status_code=status.HTTP_202_ACCEPTED)
async def delete_messages_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        message_id: list[int] = Query()
):
    await delete_messages(current_user_id=current_user_id, messages_ids=message_id)
