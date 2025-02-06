from fastapi import APIRouter, Depends, status, Query, Body, Header
from fastapi.responses import StreamingResponse
from typing import Annotated

from dependencies import verify_token, update_user_last_online
from utilities import FileRangeError
from validators import verify_current_user_is_existed
from storage import FileManager
from services import (
    update_user_message,
    fetch_message_media_metadata,
    fetch_messages_media_paths,
    remove_messages
)
from schemas import MessagesIds, CreateTextMessage

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
