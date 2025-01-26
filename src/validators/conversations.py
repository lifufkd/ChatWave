from repository import check_is_conversation_existed, get_user_from_db, get_conversation_type, get_conversation_from_db, \
    get_conversation_member_role_from_db
from models import Users
from utilities import ConversationNotFoundError, AccessDeniedError, ConversationTypes, IsNotAGroupError, \
    IsNotAChatError, ConversationMemberRoles


async def get_user_conversation_ids(user_obj: Users) -> list[int]:
    temp = list()
    for conversation_obj in user_obj.conversations:
        temp.append(conversation_obj.id)

    return temp


async def conversation_is_existed(conversation_id: int) -> None:
    if not (await check_is_conversation_existed(conversation_id=conversation_id)):
        raise ConversationNotFoundError()


async def conversation_is_group(conversation_id: int) -> None:
    if not (await get_conversation_type(conversation_id=conversation_id)) == ConversationTypes.GROUP:
        raise IsNotAGroupError()


async def conversation_is_chat(conversation_id: int) -> None:
    if not (await get_conversation_type(conversation_id=conversation_id)) == ConversationTypes.PRIVATE:
        raise IsNotAChatError()


async def validate_user_in_group(user_id: int, group_id: int):
    await conversation_is_existed(conversation_id=group_id)
    await conversation_is_group(conversation_id=group_id)

    current_user_obj = await get_user_from_db(user_id)
    current_user_conversations_ids = await get_user_conversation_ids(current_user_obj)
    if group_id not in current_user_conversations_ids:
        raise AccessDeniedError()


async def validate_user_in_chat(user_id: int, chat_id: int):
    await conversation_is_existed(conversation_id=chat_id)
    await conversation_is_chat(conversation_id=chat_id)

    current_user_obj = await get_user_from_db(user_id)
    current_user_conversations_ids = await get_user_conversation_ids(current_user_obj)
    if chat_id not in current_user_conversations_ids:
        raise AccessDeniedError()


async def validate_user_in_conversation(user_id: int, conversation_id: int) -> None:
    await conversation_is_existed(conversation_id=conversation_id)
    current_user_obj = await get_user_from_db(user_id=user_id)
    current_user_conversations_ids = await get_user_conversation_ids(current_user_obj)
    if conversation_id not in current_user_conversations_ids:
        raise AccessDeniedError()


async def validate_user_in_conversations(user_id: int, conversations_ids: list[int]) -> None:
    current_user_obj = await get_user_from_db(user_id=user_id)
    current_user_conversations_ids = await get_user_conversation_ids(current_user_obj)

    for conversation_id in conversations_ids:
        await conversation_is_existed(conversation_id=conversation_id)
    if not set(current_user_conversations_ids).intersection(set(conversations_ids)):
        raise AccessDeniedError()


async def validate_user_can_manage_group(user_id: int, group_id: int) -> None:
    await conversation_is_existed(conversation_id=group_id)
    await conversation_is_group(conversation_id=group_id)

    user_role = await get_conversation_member_role_from_db(
        user_id=user_id,
        conversation_id=group_id
    )

    if user_role is None:
        raise AccessDeniedError()

    if user_role == ConversationMemberRoles.MEMBER:
        raise AccessDeniedError()


async def validate_user_can_manage_conversation(user_id: int, conversation_id: int) -> None:
    await conversation_is_existed(conversation_id=conversation_id)

    conversation_obj = await get_conversation_from_db(conversation_id=conversation_id)
    conversation_type = conversation_obj.type
    user_role = await get_conversation_member_role_from_db(
        user_id=user_id,
        conversation_id=conversation_id
    )

    if user_role is None:
        raise AccessDeniedError()

    if conversation_type == ConversationTypes.GROUP:
        if user_role == ConversationMemberRoles.MEMBER:
            raise AccessDeniedError()
