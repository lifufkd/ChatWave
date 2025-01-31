from fastapi import APIRouter, Depends, UploadFile, File, status, Query, Body, Form, Header
from fastapi.responses import FileResponse, StreamingResponse
from typing import Annotated, Optional

from dependencies import verify_token
from utilities import FileRangeError
from validators import update_user_last_online, verify_current_user_is_existed
from storage import FileManager
from services import (
    create_text_message,
    create_media_message,
    update_user_message,
    fetch_message_media_metadata,
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
        message_id: int,
        range: str | None = Header(None),
):
    file_manager = FileManager()
    metadata = await fetch_message_media_metadata(sender_id=current_user_id, message_id=message_id)

    if range:
        file_size = await file_manager.check_file_size(metadata["file_path"])
        byte_range = range.replace('bytes=', '').split('-')
        start_byte = round(float(byte_range[0]))
        end_byte = round(float(byte_range[1])) if byte_range[1] else file_size - 1

        if start_byte > file_size:
            raise FileRangeError()

        headers = {"Content-Range": f"bytes {start_byte}-{end_byte}/{file_size}", "Accept-Ranges": "bytes"}
        file_generator_obj = await file_manager.range_file_chunk_generator(
            file_path=metadata["file_path"],
            start_byte=start_byte,
            end_byte=end_byte
        )
        return StreamingResponse(file_generator_obj,
                                 headers=headers,
                                 media_type=metadata["file_type"],
                                 status_code=206)

    file_generator_obj = await file_manager.file_chunk_generator(file_paths=[metadata["file_path"]])
    return StreamingResponse(file_generator_obj, media_type=metadata["file_type"])


@messages_router.get("/media", status_code=status.HTTP_200_OK)
async def get_messages_medias(
        current_user_id: Annotated[int, Depends(verify_token)],
        message_id: MessagesIds = Query()
):
    messages_media_paths = await fetch_messages_media_paths(
        sender_id=current_user_id,
        messages_ids=message_id.messages_ids
    )
    files_generator_obj = await FileManager().file_chunk_generator(file_paths=messages_media_paths)

    return StreamingResponse(files_generator_obj, media_type="application/octet-stream")


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
