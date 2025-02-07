from fastapi import APIRouter, Depends, status, Query, Body, Header
from fastapi.responses import StreamingResponse
from typing import Annotated

from dependencies import verify_token, update_last_online
from utilities import FileRangeError
from validators import verify_current_user_is_existed
from storage import FileManager
from services import (
    update_user_message,
    fetch_message_media_metadata,
    fetch_messages_media_paths,
    remove_messages,
    parse_bytes_file_range,
    stream_file
)
from schemas import MessagesIds, CreateTextMessage

messages_router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
    dependencies=[Depends(update_last_online), Depends(verify_current_user_is_existed)]
)


@messages_router.get("/{message_id}/media", status_code=status.HTTP_200_OK)
async def get_message_media(
        current_user_id: Annotated[int, Depends(verify_token)],
        message_id: int,
        range: str | None = Header(None),
):
    metadata = await fetch_message_media_metadata(sender_id=current_user_id, message_id=message_id)

    if range:
        file_size = await FileManager().check_file_size(metadata["file_path"])
        start_byte, end_byte = await parse_bytes_file_range(bytes_range=range, file_size=file_size)
        if start_byte > file_size:
            raise FileRangeError()

        return await stream_file(
            file_path=metadata["file_path"],
            file_type=metadata["file_type"],
            file_size=file_size,
            start_byte=start_byte,
            end_byte=end_byte,
        )

    return await stream_file(
        file_path=metadata["file_path"],
        file_type=metadata["file_type"]
    )


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
