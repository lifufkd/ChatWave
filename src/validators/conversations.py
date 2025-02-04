from repository import (
    is_conversation_exists,
    fetch_user_from_db,
    fetch_conversation_type_from_db,
    fetch_conversation_from_db,
    get_conversation_member_role_from_db
)
from models import Users
from utilities import (
    ConversationNotFoundError,
    AccessDeniedError,
    ConversationTypes,
    IsNotAGroupError,
    IsNotAChatError,
    ConversationMemberRoles,
    ChatAlreadyExists, UserNotInConversation
)


async def get_conversations_ids_from_user_obj(user_obj: Users) -> list[int]:
    temp = list()
    for conversation_obj in user_obj.conversations:
        temp.append(conversation_obj.id)

    return temp


async def get_chats_ids_from_user_obj(user_obj: Users) -> list[int]:
    temp = list()
    for conversation_obj in user_obj.conversations:
        if conversation_obj.type == ConversationTypes.PRIVATE:
            temp.append(conversation_obj.id)

    return temp


async def conversation_is_existed(conversation_id: int) -> None:
    if not (await is_conversation_exists(conversation_id=conversation_id)):
        raise ConversationNotFoundError(conversation_id=conversation_id)


async def conversations_is_existed(conversations_ids: list[int]) -> None:
    for conversation_id in conversations_ids:
        await conversation_is_existed(conversation_id=conversation_id)


async def conversation_is_group(conversation_id: int) -> None:
    if not (await fetch_conversation_type_from_db(conversation_id=conversation_id)) == ConversationTypes.GROUP:
        raise IsNotAGroupError(conversation_id=conversation_id)


async def conversation_is_chat(conversation_id: int) -> None:
    if not (await fetch_conversation_type_from_db(conversation_id=conversation_id)) == ConversationTypes.PRIVATE:
        raise IsNotAChatError(conversation_id=conversation_id)


async def validate_user_in_group(user_id: int, group_id: int):
    await conversation_is_existed(conversation_id=group_id)
    await conversation_is_group(conversation_id=group_id)

    current_user_obj = await fetch_user_from_db(user_id)
    current_user_conversations_ids = await get_conversations_ids_from_user_obj(current_user_obj)
    if group_id not in current_user_conversations_ids:
        raise UserNotInConversation(user_id=user_id, conversation_id=group_id)


async def validate_user_in_groups(user_id: int, groups_ids: list[int]):
    await conversations_is_existed(conversations_ids=groups_ids)

    user_obj = await fetch_user_from_db(user_id=user_id)
    user_conversations_ids = await get_conversations_ids_from_user_obj(user_obj)
    for group_id in groups_ids:
        await conversation_is_group(conversation_id=group_id)

        if group_id not in user_conversations_ids:
            raise UserNotInConversation(user_id=user_id, conversation_id=group_id)


async def validate_user_in_chat(user_id: int, chat_id: int):
    await conversation_is_existed(conversation_id=chat_id)
    await conversation_is_chat(conversation_id=chat_id)

    current_user_obj = await fetch_user_from_db(user_id)
    current_user_conversations_ids = await get_conversations_ids_from_user_obj(current_user_obj)
    if chat_id not in current_user_conversations_ids:
        raise UserNotInConversation(user_id=user_id, conversation_id=chat_id)


async def validate_users_in_same_chat(user_id: int, recipient_id: int):
    user_obj = await fetch_user_from_db(user_id=user_id)
    recipient_obj = await fetch_user_from_db(user_id=recipient_id)

    user_chats_ids = await get_chats_ids_from_user_obj(user_obj)
    recipient_chats_ids = await get_chats_ids_from_user_obj(recipient_obj)

    for user_chat_id in user_chats_ids:
        if user_chat_id in recipient_chats_ids:
            raise ChatAlreadyExists(chat_id=user_chat_id)


async def validate_user_in_conversation(user_id: int, conversation_id: int) -> None:
    await conversation_is_existed(conversation_id=conversation_id)

    current_user_obj = await fetch_user_from_db(user_id=user_id)
    current_user_conversations_ids = await get_conversations_ids_from_user_obj(current_user_obj)
    if conversation_id not in current_user_conversations_ids:
        raise UserNotInConversation(user_id=user_id, conversation_id=conversation_id)


async def validate_users_in_conversation(users_ids: list[int], conversation_id: int) -> None:
    await conversation_is_existed(conversation_id=conversation_id)

    for user_id in users_ids:
        current_user_obj = await fetch_user_from_db(user_id=user_id)
        current_user_conversations_ids = await get_conversations_ids_from_user_obj(current_user_obj)
        if conversation_id not in current_user_conversations_ids:
            raise UserNotInConversation(user_id=user_id, conversation_id=conversation_id)


async def validate_user_in_conversations(user_id: int, conversations_ids: list[int]) -> None:
    current_user_obj = await fetch_user_from_db(user_id=user_id)
    current_user_conversations_ids = await get_conversations_ids_from_user_obj(current_user_obj)

    for conversation_id in conversations_ids:
        await conversation_is_existed(conversation_id=conversation_id)

        if conversation_id not in current_user_conversations_ids:
            raise UserNotInConversation(user_id=user_id, conversation_id=conversation_id)


async def validate_user_can_manage_conversation(user_id: int, conversation_id: int) -> None:
    await conversation_is_existed(conversation_id=conversation_id)

    conversation_obj = await fetch_conversation_from_db(conversation_id=conversation_id)
    conversation_type = conversation_obj.type
    user_role = await get_conversation_member_role_from_db(
        user_id=user_id,
        conversation_id=conversation_id
    )

    if user_role is None:
        raise UserNotInConversation(user_id=user_id, conversation_id=conversation_id)

    if conversation_type == ConversationTypes.GROUP:
        if user_role == ConversationMemberRoles.MEMBER:
            raise AccessDeniedError()
