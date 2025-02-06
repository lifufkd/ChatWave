from schemas.unread_messages import AddUnreadMessages, UnreadMessageExistedDTO, AddUnreadMessagesDB
from validators import (
    validate_user_is_message_owner,
    validate_users_in_conversation,
    validate_unread_message_doesnt_exist,
    verify_users_is_existed
)
from repository import (
    insert_unread_messages
)
from utilities import (SameUsersIds)


async def add_unread_messages(
        user_id: int,
        conversation_id: int,
        entity_data: AddUnreadMessages,
        users_ids: list[int]
) -> None:
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
