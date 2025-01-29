from pathlib import Path
from validators import (
    validate_user_in_conversation,
    validate_user_is_message_owner,
    validate_user_have_access_to_message,
    validate_user_have_access_to_messages,
    validate_user_can_manage_messages
)
from repository import (
    insert_text_message,
    insert_empty_message,
    insert_media_message,
    update_message,
    get_filtered_messages,
    get_message,
    get_messages,
    delete_messages
)
from schemas import (
    CreateTextMessageDB,
    CreateMediaMessage,
    CreateMediaMessageDB,
    GetMessage
)
from storage import FileManager
from utilities import (
    MessagesStatus,
    MessagesTypes,
    many_sqlalchemy_to_pydantic,
    sqlalchemy_to_pydantic,
    FileNotFound,
    MediaPatches
)


async def create_text_message(sender_id: int, conversation_id: int, content: str) -> GetMessage:
    await validate_user_in_conversation(user_id=sender_id, conversation_id=conversation_id)

    new_message_obj = CreateTextMessageDB(
        content=content,
        status=MessagesStatus.SENT,
        type=MessagesTypes.TEXT,
    )
    new_message_id = await insert_text_message(
        sender_id=sender_id,
        conversation_id=conversation_id,
        message_data=new_message_obj
    )
    raw_message = await get_message(message_id=new_message_id)
    new_message_obj = await sqlalchemy_to_pydantic(
        sqlalchemy_model=raw_message,
        pydantic_model=GetMessage
    )

    return new_message_obj


async def create_media_message(sender_id: int, conversation_id: int, content_data: CreateMediaMessage) -> GetMessage:

    async def is_voice_message(_message_type):
        if _message_type != MessagesTypes.AUDIO:
            new_message_type = _message_type
        elif content_data.is_voice_message:
            new_message_type = MessagesTypes.VOICE
        else:
            new_message_type = MessagesTypes.AUDIO

        return new_message_type

    async def get_message_type():
        file_manager = FileManager()
        _message_type = await file_manager.detect_file_type(file_type=content_data.file_type)
        await file_manager.validate_file(
            file_content=content_data.file,
            file_type=content_data.file_type,
            file_type_filter=_message_type
        )
        _message_type = await is_voice_message(_message_type)

        return _message_type

    async def save_media_to_file():
        avatar_save_path = MediaPatches.MEDIA_MESSAGES_FOLDER.value / file_name
        await FileManager().write_file(file_path=avatar_save_path, file_data=content_data.file)

    await validate_user_in_conversation(user_id=sender_id, conversation_id=conversation_id)

    message_type = await get_message_type()
    message_id = await insert_empty_message(sender_id=sender_id, conversation_id=conversation_id)
    file_name = f"{message_id}.{content_data.file_name.split('.')[-1]}"
    new_message_obj = CreateMediaMessageDB(
        file_content_name=file_name,
        file_content_type=content_data.file_type,
        status=MessagesStatus.SENT,
        type=message_type,
        content=content_data.caption
    )

    await save_media_to_file()
    await insert_media_message(
        message_id=message_id,
        message_data=new_message_obj
    )
    raw_message = await get_message(message_id=message_id)
    new_message_obj = await sqlalchemy_to_pydantic(
        sqlalchemy_model=raw_message,
        pydantic_model=GetMessage
    )

    return new_message_obj


async def update_user_message(sender_id: int, message_id: int, content: str):
    await validate_user_is_message_owner(user_id=sender_id, message_id=message_id)

    await update_message(
        message_id=message_id,
        content=content
    )


async def fetch_messages(sender_id: int, conversation_id: int, limit: int, offset: int) -> list[GetMessage]:
    await validate_user_in_conversation(user_id=sender_id, conversation_id=conversation_id)

    raw_messages = await get_filtered_messages(
        conversation_id=conversation_id,
        limit=limit,
        offset=offset
    )
    messages_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_messages,
        pydantic_model=GetMessage
    )

    return messages_objs


async def fetch_message_media_path(sender_id: int, message_id: int) -> Path:
    await validate_user_have_access_to_message(user_id=sender_id, message_id=message_id)

    message_obj = await get_message(message_id=message_id)
    filepath = MediaPatches.MEDIA_MESSAGES_FOLDER.value / f"{message_obj.file_content_name}"
    if not (await FileManager().file_exists(file_path=filepath)):
        raise FileNotFound()

    return filepath


async def fetch_messages_media_paths(sender_id: int, messages_ids: list[int]) -> list[Path]:
    await validate_user_have_access_to_messages(user_id=sender_id, messages_ids=messages_ids)

    messages_paths = list()
    raw_messages = await get_messages(
        messages_ids=messages_ids
    )
    messages_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_messages,
        pydantic_model=GetMessage
    )
    for message_obj in messages_objs:
        if message_obj.file_content_name is None:
            continue

        messages_paths.append(MediaPatches.MEDIA_MESSAGES_FOLDER.value / message_obj.file_content_name)

    if not messages_paths:
        raise FileNotFound()

    return messages_paths


async def remove_messages(user_id: int, messages_ids: list[int]):
    await validate_user_can_manage_messages(user_id=user_id, messages_ids=messages_ids)

    await delete_messages(messages_ids=messages_ids)
