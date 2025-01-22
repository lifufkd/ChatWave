from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import Annotated, Optional

from dependencies import update_user_last_online, verify_token, verify_user_is_existed
from utilities import (
    ConversationNotFoundError,
    AccessDeniedError,
    InvalidFileType,
    FIleToBig, ImageCorrupted, MessageNotFound, FileNotFound, FileManager,
)
from services import create_text_message, create_media_message, update_message, get_messages, get_message_media_path, \
    get_messages_media_paths
from schemas import CreateTextMessage, CreateMediaMessage, UpdateMessage, GetMessages, MessagesIds

messages_router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
    dependencies=[Depends(update_user_last_online), Depends(verify_user_is_existed)]
)


@messages_router.get("", status_code=status.HTTP_200_OK)
async def get_messages_media_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        messages_ids: MessagesIds = Query()
):
    try:
        messages_media_paths = await get_messages_media_paths(
            sender_id=current_user_id,
            messages_ids=messages_ids.messages_ids
        )
        zip_obj = FileManager().archive_files(messages_media_paths)
        return StreamingResponse(zip_obj, media_type="application/zip")
    except FileNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    except MessageNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    except AccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You does not have permission to perform this operation")
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")


@messages_router.get("/{message_id}/media", status_code=status.HTTP_200_OK)
async def get_message_media_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        message_id: int
):
    try:
        filepath = await get_message_media_path(sender_id=current_user_id, message_id=message_id)
    except FileNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return FileResponse(filepath)


@messages_router.post("/{conversation_id}/text", status_code=status.HTTP_201_CREATED)
async def send_text_message_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: int,
        content: CreateTextMessage
):
    try:
        await create_text_message(sender_id=current_user_id, conversation_id=conversation_id, content=content)
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    except AccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You does not have permission to perform this operation")

    return {"detail": "Message sent successfully"}


@messages_router.post("/{conversation_id}/media", status_code=status.HTTP_201_CREATED)
async def send_media_message_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: int,
        is_voice_message: bool = False,
        caption: Optional[str] = Form(None),
        file: UploadFile = File()
):

    try:
        new_message_obj = CreateMediaMessage(
            file=file.file.read(),
            file_name=file.filename,
            file_type=file.content_type,
            caption=caption,
            is_voice_message=is_voice_message
        )
        await create_media_message(sender_id=current_user_id, conversation_id=conversation_id, content=new_message_obj)
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    except AccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You does not have permission to perform this operation")
    except InvalidFileType as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FIleToBig as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ImageCorrupted as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"detail": "Message sent successfully"}


@messages_router.patch("/{message_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_message_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        message_id: int,
        content: UpdateMessage
):
    try:
        await update_message(sender_id=current_user_id, message_id=message_id, message_data=content)
    except MessageNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    except AccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You does not have permission to perform this operation")
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return {"detail": "Message successfully updated"}


@messages_router.get("/{conversation_id}", status_code=status.HTTP_200_OK, response_model=list[GetMessages])
async def get_messages_endpoint(
        current_user_id: Annotated[int, Depends(verify_token)],
        conversation_id: int,
        limit: int = Query(10, ge=1, le=1000),
        offset: int = 0
):
    try:
        messages_objs = await get_messages(
            sender_id=current_user_id,
            conversation_id=conversation_id,
            limit=limit,
            offset=offset
        )
        return messages_objs
    except AccessDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You does not have permission to perform this operation")
    except ConversationNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
