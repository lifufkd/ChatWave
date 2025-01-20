from dependencies import validate_user_in_conversation
from repository import insert_text_message_to_db, insert_empty_message, insert_media_message_to_db
from schemas import CreateTextMessage, CreateTextMessageExtended, CreateMediaMessage, CreateMediaMessageDB
from utilities import MessagesStatus, MessagesTypes, FileManager, generic_settings


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
        file_manager.validate_file(
            file_content=content.file,
            file_type=content.file_type,
            file_type_filter=_message_type
        )
        _message_type = await is_voice_message(_message_type)

        return _message_type

    async def save_media_to_file():
        avatar_save_path = generic_settings.MEDIA_FOLDER / "messages" / file_name
        FileManager.write_file(path=avatar_save_path, content=content.file)

    await validate_user_in_conversation(user_id=sender_id, conversation_id=conversation_id)

    message_type = await get_message_type()
    message_id = await insert_empty_message(sender_id=sender_id, conversation_id=conversation_id)
    file_name = f"{message_id}.{content.file_name.split('.')[-1]}"
    create_media_message_extended_obj = CreateMediaMessageDB(
        file_content_name=file_name,
        file_content_type=content.file_type,
        status=MessagesStatus.SENT,
        type=message_type
    )

    await save_media_to_file()
    await insert_media_message_to_db(
        message_id=message_id,
        message_data=create_media_message_extended_obj
    )

