from pathlib import Path

from schemas.unread_messages import AddUnreadMessages, UnreadMessageExistedDTO, AddUnreadMessagesDB
from validators import (
    validate_user_in_conversation,
    validate_user_is_message_owner,
    validate_user_have_access_to_message,
    validate_user_have_access_to_messages,
    validate_user_can_manage_messages, validate_users_in_conversation, validate_unread_message_doesnt_exist,
    verify_users_is_existed
)
from repository import (
    insert_text_message,
    insert_empty_message,
    insert_media_message,
    update_message,
    get_filtered_messages,
    get_message,
    get_messages,
    delete_messages, insert_unread_messages
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
    MediaPatches,
    SameUsersIds
)


async def add_unread_messages(user_id: int, conversation_id: int, entity_data: AddUnreadMessages, users_ids: list[int]) -> None:
    if user_id in users_ids:
        raise SameUsersIds()
    if entity_data.message_id is not None:
        message_id = entity_data.message_id
        await validate_user_is_message_owner(user_id=user_id, message_id=message_id)
    else:
        call_id = entity_data.call_id
    await verify_users_is_existed(users_ids=users_ids)
    await validate_users_in_conversation(conversation_id=conversation_id, users_ids=[*users_ids, user_id])

    for _user_id in users_ids:
        await validate_unread_message_doesnt_exist(
            filter_conditions=UnreadMessageExistedDTO(
                user_id=_user_id,
                conversation_id=conversation_id,
                **entity_data.model_dump(exclude_none=True)
            )
        )

    await insert_unread_messages(
        unread_messages_data=AddUnreadMessagesDB(
            users_ids=users_ids,
            conversation_id=conversation_id,
            **entity_data.model_dump(exclude_none=True)
        )
    )

