from dependencies.conversations import conversation_is_existed
from repository import check_message_is_existed, get_message_from_db, check_messages_is_existed, get_messages_from_db, \
    get_user_from_db, get_conversation_member_role_from_db
from utilities import MessageNotFound, AccessDeniedError, ConversationTypes, ConversationMemberRoles
from dependencies import validate_user_in_conversation, validate_user_in_conversations


async def message_is_existed(message_id: int) -> None:
    if not (await check_message_is_existed(message_id=message_id)):
        raise MessageNotFound()


async def messages_is_existed(messages_ids: list[int]) -> None:
    if not (await check_messages_is_existed(messages_ids=messages_ids)):
        raise MessageNotFound()


async def get_conversations_ids_from_messages(messages_objs: list) -> list[int]:
    temp = list()
    for message_obj in messages_objs:
        temp.append(message_obj.conversation_id)

    return temp


async def validate_user_is_message_owner(user_id: int, message_id: int) -> None:
    await message_is_existed(message_id=message_id)

    message_obj = await get_message_from_db(message_id=message_id)
    if message_obj.sender_id != user_id:
        raise AccessDeniedError()

    await validate_user_in_conversation(user_id=user_id, conversation_id=message_obj.conversation_id)


async def validate_user_have_access_to_message(user_id: int, message_id: int) -> None:
    await message_is_existed(message_id=message_id)

    message_obj = await get_message_from_db(message_id=message_id)
    await validate_user_in_conversation(user_id=user_id, conversation_id=message_obj.conversation_id)


async def validate_user_have_access_to_messages(user_id: int, messages_ids: list[int]) -> None:
    await messages_is_existed(messages_ids=messages_ids)

    messages_objs = await get_messages_from_db(messages_ids=messages_ids)
    conversations_ids = await get_conversations_ids_from_messages(messages_objs=messages_objs)
    await validate_user_in_conversations(user_id=user_id, conversations_ids=conversations_ids)


async def validate_user_can_manage_messages(user_id: int, messages_ids: list[int]) -> None:
    await messages_is_existed(messages_ids=messages_ids)

    messages_objs = await get_messages_from_db(messages_ids=messages_ids)

    for message_obj in messages_objs:
        await conversation_is_existed(conversation_id=message_obj.conversation_id)

        conversation_type = message_obj.conversation.type
        user_role = await get_conversation_member_role_from_db(
            user_id=user_id,
            conversation_id=message_obj.conversation_id
        )

        if user_role is None:
            raise AccessDeniedError()

        if conversation_type == ConversationTypes.GROUP:
            if user_role == ConversationMemberRoles.MEMBER:
                raise AccessDeniedError()

