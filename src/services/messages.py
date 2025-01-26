from pathlib import Path
from validators import (
    validate_user_in_conversation,
    validate_user_is_message_owner,
    validate_user_have_access_to_message,
    validate_user_have_access_to_messages,
    validate_user_in_chat,
    validate_user_can_manage_messages
)
from repository import (
    insert_text_message_to_db,
    insert_empty_message,
    insert_media_message_to_db,
    update_message_in_db,
    fetch_filtered_messages_from_db,
    get_message_from_db,
    get_messages_from_db,
    delete_conversation_messages_from_db,
    delete_messages_from_db
)
from schemas import (
    CreateTextMessage,
    CreateTextMessageExtended,
    CreateMediaMessage,
    CreateMediaMessageDB,
    UpdateMessage,
    GetMessages
)
from storage import FileManager
from utilities import (
    MessagesStatus,
    MessagesTypes,
    generic_settings,
    many_sqlalchemy_to_pydantic,
    FileNotFound
)


async def create_text_message(sender_id: int, conversation_id: int, content: CreateTextMessage):
    await validate_user_in_conversation(user_id=sender_id, conversation_id=conversation_id)

    create_text_message_extended_obj = CreateTextMessageExtended(
        content=content.content,
        status=MessagesStatus.SENT,
        type=MessagesTypes.TEXT,
    )
    await insert_text_message_to_db(
        sender_id=sender_id,
        conversation_id=conversation_id,
        message_data=create_text_message_extended_obj
    )


async def create_media_message(sender_id: int, conversation_id: int, content: CreateMediaMessage):

    async def is_voice_message(_message_type):
        if _message_type != MessagesTypes.AUDIO:
            new_message_type = _message_type
        elif content.is_voice_message:
            new_message_type = MessagesTypes.VOICE
        else:
            new_message_type = MessagesTypes.AUDIO

        return new_message_type

    async def get_message_type():
        file_manager = FileManager()
        _message_type = file_manager.detect_file_type(file_type=content.file_type)
        await file_manager.validate_file(
            file_content=content.file,
            file_type=content.file_type,
            file_type_filter=_message_type
        )
        _message_type = await is_voice_message(_message_type)

        return _message_type

    async def save_media_to_file():
        avatar_save_path = generic_settings.MEDIA_FOLDER / "messages" / file_name
        await FileManager().write_file(file_path=avatar_save_path, file_data=content.file)

    await validate_user_in_conversation(user_id=sender_id, conversation_id=conversation_id)

    message_type = await get_message_type()
    message_id = await insert_empty_message(sender_id=sender_id, conversation_id=conversation_id)
    file_name = f"{message_id}.{content.file_name.split('.')[-1]}"
    create_media_message_extended_obj = CreateMediaMessageDB(
        file_content_name=file_name,
        file_content_type=content.file_type,
        status=MessagesStatus.SENT,
        type=message_type,
        content=content.caption
    )

    await save_media_to_file()
    await insert_media_message_to_db(
        message_id=message_id,
        message_data=create_media_message_extended_obj
    )


async def update_message(sender_id: int, message_id: int, message_data: UpdateMessage):
    await validate_user_is_message_owner(user_id=sender_id, message_id=message_id)

    await update_message_in_db(
        message_id=message_id,
        message_data=message_data
    )


async def get_messages(sender_id: int, conversation_id: int, limit: int, offset: int) -> list[GetMessages]:
    await validate_user_in_conversation(user_id=sender_id, conversation_id=conversation_id)

    raw_messages = await fetch_filtered_messages_from_db(
        conversation_id=conversation_id,
        limit=limit,
        offset=offset
    )
    messages_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_messages,
        pydantic_model=GetMessages
    )

    return messages_objs


async def get_message_media_path(sender_id: int, message_id: int) -> Path:
    await validate_user_have_access_to_message(user_id=sender_id, message_id=message_id)

    message_obj = await get_message_from_db(message_id=message_id)
    filepath = generic_settings.MEDIA_FOLDER / "messages" / f"{message_obj.file_content_name}"
    if not await FileManager().file_exists(file_path=filepath):
        raise FileNotFound()

    return filepath


async def get_messages_media_paths(sender_id: int, messages_ids: list[int]) -> list[Path]:
    await validate_user_have_access_to_messages(user_id=sender_id, messages_ids=messages_ids)

    messages_paths = list()
    avatar_base_path = generic_settings.MEDIA_FOLDER / "messages"
    raw_messages = await get_messages_from_db(
        messages_ids=messages_ids
    )
    messages_objs = await many_sqlalchemy_to_pydantic(
        sqlalchemy_models=raw_messages,
        pydantic_model=GetMessages
    )
    for message_obj in messages_objs:
        if message_obj.file_content_name is None:
            continue

        messages_paths.append(avatar_base_path / message_obj.file_content_name)

    if not messages_paths:
        raise FileNotFound()

    return messages_paths


async def delete_all_messages(current_user_id: int, chat_id: int):
    await validate_user_in_chat(user_id=current_user_id, chat_id=chat_id)

    await delete_conversation_messages_from_db(conversation_id=chat_id)


async def delete_messages(current_user_id: int, messages_ids: list[int]):
    await validate_user_can_manage_messages(user_id=current_user_id, messages_ids=messages_ids)

    await delete_messages_from_db(messages_ids=messages_ids)
